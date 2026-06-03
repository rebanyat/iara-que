import type { SankeyEdge, SankeyNode, LifeGoal } from '$lib/stores/data';

export type StageId = 'eso' | 'batx' | 'fp_gm' | 'fp_gs' | 'grau' | 'working' | 'reorient';

export interface PlanStep {
	nodeId: string;
	label: string;
	category: SankeyNode['category'];
	branca?: string;
	isco?: string;
	salary?: number;
	pctEmployed?: number;
	pctAdequate?: number;
	composite?: number;
	years?: number;
}

export interface PlanPath {
	steps: PlanStep[];
	totalYears: number;
	score: number;
	finalIsco?: string;
	finalSalary?: number;
	finalComposite?: number;
}

export interface PlannerInput {
	fromNode: string;
	targetIsco1: string[];
	targetBrancas: string[];
	preferences?: {
		salaryWeight?: number;
		stabilityWeight?: number;
		autonomyWeight?: number;
	};
	maxHops?: number;
	topK?: number;
}

interface NodeIndex {
	byId: Map<string, SankeyNode>;
	outgoing: Map<string, SankeyEdge[]>;
}

// Rough stage-to-years mapping: each layer transition costs this much. Used to
// estimate "how long to reach the goal" from each node.
const NODE_YEARS: Record<string, number> = {
	start__eso: 1,
	start__batx: 0,
	start__fp_gm: 0,
	start__fp_gs: 0,
	start__grau: 0,
	start__reorient: 0,
	post__batx: 2,
	post__fp_gm: 2,
	post__fp_gs: 2,
	titol__grau: 4,
	titol__master: 1.5,
	titol__fp_gs: 2,
	titol__fp_gm: 2
};

function yearsFor(node: SankeyNode): number {
	if (NODE_YEARS[node.id] !== undefined) return NODE_YEARS[node.id];
	// branca + titul + isco + outcome nodes do not directly add formation years
	if (node.id.startsWith('branca__') || node.id.startsWith('titul__')) return 0;
	if (node.id.startsWith('isco__')) return 1; // first work year
	if (node.id.startsWith('out__')) return 0;
	return 0;
}

export function indexSankey(nodes: SankeyNode[], edges: SankeyEdge[]): NodeIndex {
	const byId = new Map<string, SankeyNode>();
	for (const n of nodes) byId.set(n.id, n);

	const outgoing = new Map<string, SankeyEdge[]>();
	for (const e of edges) {
		(outgoing.get(e.source) ?? outgoing.set(e.source, []).get(e.source)!).push(e);
	}
	return { byId, outgoing };
}

/**
 * Forward search from a starting node, scoring partial paths by accumulated
 * edge composite weighted by edge value, then filtering to those that land on
 * a node matching the target ISCO-1 set. Returns top-K by score.
 */
export function optimisePath(
	input: PlannerInput,
	nodes: SankeyNode[],
	edges: SankeyEdge[]
): PlanPath[] {
	const { byId, outgoing } = indexSankey(nodes, edges);
	const maxHops = input.maxHops ?? 8;
	const topK = input.topK ?? 5;
	const w = {
		salary: input.preferences?.salaryWeight ?? 0.35,
		stability: input.preferences?.stabilityWeight ?? 0.35,
		autonomy: input.preferences?.autonomyWeight ?? 0.30
	};

	type Frontier = {
		path: string[];
		edges: SankeyEdge[];
		yearsAcc: number;
		scoreAcc: number;
	};

	const fromNode = byId.get(input.fromNode);
	if (!fromNode) return [];

	let frontier: Frontier[] = [
		{ path: [input.fromNode], edges: [], yearsAcc: yearsFor(fromNode), scoreAcc: 0 }
	];

	const finished: Frontier[] = [];

	for (let hop = 0; hop < maxHops; hop++) {
		const next: Frontier[] = [];
		for (const f of frontier) {
			const last = f.path[f.path.length - 1];
			const lastNode = byId.get(last);
			if (!lastNode) continue;

			// Reached an ISCO that matches the target → record as finished.
			if (lastNode.id.startsWith('isco__')) {
				const isco1 = lastNode.id.replace('isco__', '');
				if (input.targetIsco1.includes(isco1)) {
					finished.push(f);
					continue;
				}
			}

			const outs = outgoing.get(last) ?? [];
			if (outs.length === 0) {
				continue;
			}

			// Keep at most 4 strongest outgoing edges per node so the frontier
			// doesn't explode.
			const sorted = [...outs].sort((a, b) => b.value - a.value).slice(0, 4);
			for (const e of sorted) {
				const tgt = byId.get(e.target);
				if (!tgt) continue;
				// Avoid loops.
				if (f.path.includes(e.target)) continue;
				// Branca preference bonus: edges pointing to a preferred branca
				// or whose target's branca is in the preference list get boosted.
				let edgeScore = e.meta.composite ?? 0.5;
				if (input.targetBrancas.includes(e.target)) edgeScore += 0.20;
				if (tgt.branca && input.targetBrancas.includes(`branca__${tgt.branca.toLowerCase()}`)) {
					edgeScore += 0.10;
				}
				// Penalise low-quality outcomes
				if (tgt.id === 'out__unemployed' || tgt.id === 'out__low_quality') edgeScore -= 0.30;

				next.push({
					path: [...f.path, e.target],
					edges: [...f.edges, e],
					yearsAcc: f.yearsAcc + yearsFor(tgt),
					scoreAcc: f.scoreAcc + edgeScore
				});
			}
		}
		frontier = next;
		if (frontier.length === 0) break;
	}

	// Also accept paths that ended at the final hop if their last node is in
	// the right branca even without reaching ISCO yet.
	for (const f of frontier) {
		const last = byId.get(f.path[f.path.length - 1]);
		if (!last) continue;
		if (last.id.startsWith('isco__')) {
			const isco1 = last.id.replace('isco__', '');
			if (input.targetIsco1.includes(isco1)) finished.push(f);
		}
	}

	// Build PlanPath objects and rank.
	const plans: PlanPath[] = finished.map((f) => {
		const steps: PlanStep[] = f.path.map((id) => {
			const n = byId.get(id)!;
			return {
				nodeId: id,
				label: n.label,
				category: n.category,
				branca: n.branca,
				isco: n.isco
			};
		});
		// Attach edge metrics to each step (transition into that step).
		for (let i = 1; i < steps.length; i++) {
			const e = f.edges[i - 1];
			if (!e) continue;
			steps[i].salary = e.meta.medianSalary;
			steps[i].pctEmployed = e.meta.pctEmployed;
			steps[i].pctAdequate = e.meta.pctAdequate;
			steps[i].composite = e.meta.composite;
		}
		const lastEdge = f.edges[f.edges.length - 1];
		const lastIsco = steps.find((s) => s.nodeId.startsWith('isco__'))?.isco;
		return {
			steps,
			totalYears: Math.round(f.yearsAcc * 10) / 10,
			score: Math.round((f.scoreAcc / Math.max(1, f.edges.length)) * 100) / 100,
			finalIsco: lastIsco,
			finalSalary: lastEdge?.meta?.medianSalary,
			finalComposite: lastEdge?.meta?.composite
		};
	});

	plans.sort((a, b) => b.score - a.score);
	// De-duplicate by step sequence
	const seen = new Set<string>();
	const unique: PlanPath[] = [];
	for (const p of plans) {
		const k = p.steps.map((s) => s.nodeId).join('→');
		if (seen.has(k)) continue;
		seen.add(k);
		unique.push(p);
		if (unique.length >= topK) break;
	}

	return unique;
}

/**
 * Map a life goal to a planner target (target ISCO-1 list + preferred brancas).
 */
export function goalToTarget(goal: LifeGoal): { targetIsco1: string[]; targetBrancas: string[]; preferences: PlannerInput['preferences'] } {
	const p = goal.profile ?? {};
	return {
		targetIsco1: goal.isco1,
		targetBrancas: goal.branca,
		preferences: {
			salaryWeight: p.salary ?? 0.4,
			stabilityWeight: p.stability ?? 0.3,
			autonomyWeight: p.autonomy ?? 0.3
		}
	};
}

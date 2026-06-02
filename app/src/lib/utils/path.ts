/**
 * Helpers to compute which sankey edges remain "active" under a filter set.
 *
 * An edge is active under a `branca` filter when its target lies on a path
 * that flows through any selected branca node. We BFS forward from each
 * selected branca node along outgoing edges and backward along incoming
 * edges, then keep the union of edges touched.
 */

export interface MinEdge {
	source: string;
	target: string;
}

export function computeActiveEdges<E extends MinEdge>(
	edges: E[],
	pinnedBrancas: string[]
): Set<string> | null {
	if (pinnedBrancas.length === 0) return null; // no filter → everything active

	const targetsByNode = new Map<string, E[]>();
	const sourcesByNode = new Map<string, E[]>();
	for (const e of edges) {
		(targetsByNode.get(e.source) ?? targetsByNode.set(e.source, []).get(e.source)!).push(e);
		(sourcesByNode.get(e.target) ?? sourcesByNode.set(e.target, []).get(e.target)!).push(e);
	}

	const active = new Set<string>();
	const seen = new Set<string>();

	const bfsForward = (start: string) => {
		const queue = [start];
		while (queue.length) {
			const cur = queue.shift()!;
			if (seen.has(`f:${cur}`)) continue;
			seen.add(`f:${cur}`);
			const outs = targetsByNode.get(cur) ?? [];
			for (const e of outs) {
				active.add(edgeKey(e));
				queue.push(e.target);
			}
		}
	};

	const bfsBackward = (start: string) => {
		const queue = [start];
		while (queue.length) {
			const cur = queue.shift()!;
			if (seen.has(`b:${cur}`)) continue;
			seen.add(`b:${cur}`);
			const ins = sourcesByNode.get(cur) ?? [];
			for (const e of ins) {
				active.add(edgeKey(e));
				queue.push(e.source);
			}
		}
	};

	for (const branca of pinnedBrancas) {
		bfsForward(branca);
		bfsBackward(branca);
	}

	return active;
}

export function edgeKey(e: MinEdge): string {
	return `${e.source}__${e.target}`;
}

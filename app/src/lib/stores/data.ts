import { writable, type Readable } from 'svelte/store';

export interface SankeyNode {
	id: string;
	layer: number;
	label: string;
	category: 'origin' | 'study' | 'occupation' | 'outcome';
	branca?: string;
	isco?: string;
	outcome_score?: number;
}

export interface SankeyEdgeMeta {
	sourceDataset: string;
	placeholder?: boolean;
	pctOfSource?: number;
	medianSalary?: number;
	pctEmployed?: number;
	pctAdequate?: number;
	medianMonthsToJob?: number;
	composite?: number;
	genderRatio?: { F: number; M: number };
	wave?: number;
}

export interface SankeyEdge {
	source: string;
	target: string;
	value: number;
	meta: SankeyEdgeMeta;
}

export interface SankeyPayload {
	version: string;
	generated_at: string;
	title: string;
	scope: string;
	nodes: SankeyNode[];
	edges: SankeyEdge[];
	seed_totals: Record<string, number>;
	stats?: { node_count: number; edge_count: number; placeholder_edges: number };
}

export interface GenderGapRow {
	branca: string;
	level: string;
	wave: number;
	salary_f: number;
	salary_m: number;
	salary_modal: number;
	pct_female: number;
	source: string;
}

export interface GenderGapPayload {
	branca_labels: Record<string, string>;
	latest_wave_aqu: number;
	latest_wave_cambres: number;
	rows: GenderGapRow[];
}

interface DatasetsState {
	sankey: SankeyPayload | null;
	genderGap: GenderGapPayload | null;
	error: string | null;
}

const internal = writable<DatasetsState>({ sankey: null, genderGap: null, error: null });
let started = false;

async function loadJson<T>(path: string): Promise<T> {
	const res = await fetch(path);
	if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
	return (await res.json()) as T;
}

export function startDatasets() {
	if (started || typeof window === 'undefined') return;
	started = true;
	(async () => {
		try {
			const [sankey, genderGap] = await Promise.all([
				loadJson<SankeyPayload>('/data/sankey.json'),
				loadJson<GenderGapPayload>('/data/gender_gap.json')
			]);
			internal.set({ sankey, genderGap, error: null });
		} catch (err) {
			console.error('datasets load failed:', err);
			internal.update((s) => ({ ...s, error: err instanceof Error ? err.message : String(err) }));
		}
	})();
}

export const datasets: Readable<DatasetsState> = { subscribe: internal.subscribe };

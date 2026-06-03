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

export interface ComarcaMetricRow {
	id: string;
	name: string;
	provincia: string;
	atur_rate: number;
	ocup_rate: number;
	placeholder?: boolean;
}

export interface ComarcaMetricsPayload {
	source: string;
	rows: ComarcaMetricRow[];
}

export interface TimeSeriesPoint {
	wave: number;
	pct_employed: number;
	pct_adequate: number;
	salary_modal: number;
	composite_employability: number;
}

export interface TimeSeriesPayload {
	branca_labels: Record<string, string>;
	metrics: string[];
	series: { branca: string; points: TimeSeriesPoint[] }[];
}

export interface WikidataIcon {
	id: string;
	label: string;
	isco1: string;
	iscoLabel: string;
	count: number;
	topFields: { label: string; count: number }[];
	topEducations: { label: string; count: number }[];
	genderRatio?: { F: number; M: number };
	source: 'wikidata';
}

export interface WikidataIconsPayload {
	generated_at: string;
	icons: WikidataIcon[];
}

export interface LifeGoal {
	id: string;
	label: string;
	blurb: string;
	isco1: string[];
	branca: string[];
	profile: {
		autonomy?: number;
		salary?: number;
		stability?: number;
		social_impact?: number;
	};
	exemplars?: string[];
	honestly?: string;
}

export interface LifeGoalsPayload {
	goals: LifeGoal[];
}

export interface StartingPoint {
	id: string;
	label: string;
	node: string;
	child_node?: string;
	stage: 'eso' | 'batx' | 'fp_gm' | 'fp_gs' | 'grau' | 'working' | 'reorient';
	branca_hint?: string | null;
	years_left_in_stage: number;
	blurb?: string;
	family?: string;
}

export interface StartingPointsPayload {
	points: StartingPoint[];
}

export interface Resource {
	id: string;
	type: 'uni' | 'fp' | 'beca' | 'orientacio' | 'plataforma' | 'sindicat' | 'emprenedoria' | 'idiomes';
	label: string;
	url: string;
	branca: string[];
	isco1: string[];
	stage: ('eso' | 'batx' | 'fp_gm' | 'fp_gs' | 'grau' | 'working' | 'reorient')[];
	tag: string;
	blurb?: string;
}

export interface ResourcesPayload {
	resources: Resource[];
}

interface DatasetsState {
	sankey: SankeyPayload | null;
	genderGap: GenderGapPayload | null;
	comarques: ComarcaMetricsPayload | null;
	comarquesTopo: unknown | null;
	timeSeries: TimeSeriesPayload | null;
	wikidataIcons: WikidataIconsPayload | null;
	lifeGoals: LifeGoalsPayload | null;
	startingPoints: StartingPointsPayload | null;
	resources: ResourcesPayload | null;
	error: string | null;
}

const internal = writable<DatasetsState>({
	sankey: null,
	genderGap: null,
	comarques: null,
	comarquesTopo: null,
	timeSeries: null,
	wikidataIcons: null,
	lifeGoals: null,
	startingPoints: null,
	resources: null,
	error: null
});
let started = false;

async function loadJson<T>(path: string): Promise<T> {
	const res = await fetch(path);
	if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
	return (await res.json()) as T;
}

async function loadJsonOptional<T>(path: string): Promise<T | null> {
	try {
		const res = await fetch(path);
		if (!res.ok) return null;
		return (await res.json()) as T;
	} catch {
		return null;
	}
}

export function startDatasets() {
	if (started || typeof window === 'undefined') return;
	started = true;
	(async () => {
		try {
			const [sankey, genderGap, comarques, comarquesTopo, timeSeries, wikidataIcons, lifeGoals, startingPoints, resources] = await Promise.all([
				loadJson<SankeyPayload>('/data/sankey.json'),
				loadJson<GenderGapPayload>('/data/gender_gap.json'),
				loadJsonOptional<ComarcaMetricsPayload>('/data/comarques_metrics.json'),
				loadJsonOptional<unknown>('/data/comarques.topo.json'),
				loadJsonOptional<TimeSeriesPayload>('/data/time_series.json'),
				loadJsonOptional<WikidataIconsPayload>('/data/wikidata_icons.json'),
				loadJsonOptional<LifeGoalsPayload>('/data/life_goals.json'),
				loadJsonOptional<StartingPointsPayload>('/data/starting_points.json'),
				loadJsonOptional<ResourcesPayload>('/data/resources.json')
			]);
			internal.set({
				sankey,
				genderGap,
				comarques,
				comarquesTopo,
				timeSeries,
				wikidataIcons,
				lifeGoals,
				startingPoints,
				resources,
				error: null
			});
		} catch (err) {
			console.error('datasets load failed:', err);
			internal.update((s) => ({ ...s, error: err instanceof Error ? err.message : String(err) }));
		}
	})();
}

export const datasets: Readable<DatasetsState> = { subscribe: internal.subscribe };

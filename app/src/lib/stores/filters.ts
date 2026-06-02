import { writable, derived, type Writable } from 'svelte/store';

export type Gender = 'all' | 'F' | 'M';

export type ColorMetric = 'composite' | 'salary' | 'employed' | 'adequate';

export const BRANCA_IDS = [
	'branca__stem',
	'branca__health',
	'branca__social',
	'branca__hum',
	'branca__services',
	'branca__industry'
] as const;

export type BrancaId = (typeof BRANCA_IDS)[number];

export interface FiltersState {
	gender: Gender;
	branca: BrancaId[]; // empty array = no branca selected (show all)
	wave: number; // 2023 default
	colorMetric: ColorMetric;
}

const DEFAULT: FiltersState = {
	gender: 'all',
	branca: [],
	wave: 2023,
	colorMetric: 'composite'
};

export const filters: Writable<FiltersState> = writable({ ...DEFAULT });

export function setGender(g: Gender) {
	filters.update((f) => ({ ...f, gender: g }));
}

export function toggleBranca(id: BrancaId) {
	filters.update((f) => {
		const has = f.branca.includes(id);
		return {
			...f,
			branca: has ? f.branca.filter((b) => b !== id) : [...f.branca, id]
		};
	});
}

export function clearBranca() {
	filters.update((f) => ({ ...f, branca: [] }));
}

export function setWave(w: number) {
	filters.update((f) => ({ ...f, wave: w }));
}

export function setColorMetric(m: ColorMetric) {
	filters.update((f) => ({ ...f, colorMetric: m }));
}

export function resetFilters() {
	filters.set({ ...DEFAULT });
}

export const anyFilterActive = derived(filters, ($f) => $f.gender !== 'all' || $f.branca.length > 0);

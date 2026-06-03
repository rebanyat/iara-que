import { get } from 'svelte/store';
import {
	filters,
	setGender,
	setColorMetric,
	toggleBranca,
	clearBranca,
	BRANCA_IDS,
	type ColorMetric,
	type Gender,
	type BrancaId
} from '$lib/stores/filters';
import {
	selection,
	setSearchTarget,
	clearSearchTarget,
	type SearchTarget
} from '$lib/stores/selection';

/**
 * Two-way sync between the URL search params and the filter + selection
 * stores so deep links and shares preserve the view.
 *
 * Param shape:
 *   ?gender=F|M
 *   ?branca=stem,health,…  (comma-separated short ids)
 *   ?metric=composite|salary|employed|adequate
 *   ?target=esco:<id>:<isco1>:<isco-label-encoded>:<label-encoded>
 *
 * The target stores enough to reconstruct the panels without re-fetching
 * occupations.json (already loaded by the SearchBox, but the panels are
 * independent of it).
 */

const VALID_METRICS: ColorMetric[] = ['composite', 'salary', 'employed', 'adequate'];
const VALID_GENDERS: Gender[] = ['all', 'F', 'M'];

function brancaShort(id: BrancaId): string {
	return id.replace(/^branca__/, '');
}

function brancaLong(short: string): BrancaId | null {
	const full = `branca__${short}` as BrancaId;
	return (BRANCA_IDS as readonly string[]).includes(full) ? full : null;
}

function encodeTarget(t: SearchTarget): string {
	return [
		t.source,
		encodeURIComponent(t.id),
		encodeURIComponent(t.isco1),
		encodeURIComponent(t.iscoLabel),
		encodeURIComponent(t.label)
	].join(':');
}

function decodeTarget(raw: string): SearchTarget | null {
	const parts = raw.split(':');
	if (parts.length < 5) return null;
	const [source, id, isco1, iscoLabel, label] = parts;
	if (source !== 'esco' && source !== 'wikidata') return null;
	return {
		source,
		id: decodeURIComponent(id),
		isco1: decodeURIComponent(isco1),
		iscoLabel: decodeURIComponent(iscoLabel),
		label: decodeURIComponent(label)
	};
}

/** Hydrate stores from the URL on mount. */
export function hydrateFromUrl() {
	if (typeof window === 'undefined') return;
	const sp = new URL(window.location.href).searchParams;

	const g = sp.get('gender');
	if (g && (VALID_GENDERS as string[]).includes(g)) setGender(g as Gender);

	const branca = sp.get('branca');
	if (branca) {
		clearBranca();
		for (const short of branca.split(',').filter(Boolean)) {
			const id = brancaLong(short);
			if (id) toggleBranca(id);
		}
	}

	const m = sp.get('metric');
	if (m && (VALID_METRICS as string[]).includes(m)) setColorMetric(m as ColorMetric);

	const t = sp.get('target');
	if (t) {
		const target = decodeTarget(t);
		if (target) setSearchTarget(target);
	}
}

/** Subscribe to stores and push state to the URL. Returns an unsubscribe fn. */
export function startUrlSync(): () => void {
	if (typeof window === 'undefined') return () => {};
	let scheduled = false;

	const push = () => {
		if (scheduled) return;
		scheduled = true;
		queueMicrotask(() => {
			scheduled = false;
			const f = get(filters);
			const s = get(selection);
			const url = new URL(window.location.href);
			const sp = url.searchParams;

			if (f.gender === 'all') sp.delete('gender');
			else sp.set('gender', f.gender);

			if (f.branca.length === 0) sp.delete('branca');
			else sp.set('branca', f.branca.map(brancaShort).join(','));

			if (f.colorMetric === 'composite') sp.delete('metric');
			else sp.set('metric', f.colorMetric);

			if (s.searchTarget) sp.set('target', encodeTarget(s.searchTarget));
			else sp.delete('target');

			const next = url.pathname + (sp.toString() ? `?${sp.toString()}` : '');
			if (next !== url.pathname + url.search) {
				history.replaceState(history.state, '', next);
			}
		});
	};

	const unsubF = filters.subscribe(push);
	const unsubS = selection.subscribe(push);
	return () => {
		unsubF();
		unsubS();
	};
}

// Expose helpers used in tests / debugging
export const _internal = { encodeTarget, decodeTarget, brancaShort, brancaLong };
// Silence unused warning for clearSearchTarget if URL never asks for it
void clearSearchTarget;

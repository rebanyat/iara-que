import { writable, type Writable } from 'svelte/store';

export interface EdgeKey {
	source: string;
	target: string;
}

export interface SearchTarget {
	source: 'esco' | 'wikidata';
	id: string;
	label: string;
	isco1: string; // single-digit ISCO-1 major group
	iscoLabel: string;
}

export interface SelectionState {
	hoveredEdge: EdgeKey | null;
	pinnedEdge: EdgeKey | null;
	searchTarget: SearchTarget | null;
}

export const selection: Writable<SelectionState> = writable({
	hoveredEdge: null,
	pinnedEdge: null,
	searchTarget: null
});

export function setHovered(edge: EdgeKey | null) {
	selection.update((s) => ({ ...s, hoveredEdge: edge }));
}

export function togglePin(edge: EdgeKey) {
	selection.update((s) => {
		const same = s.pinnedEdge?.source === edge.source && s.pinnedEdge?.target === edge.target;
		return { ...s, pinnedEdge: same ? null : edge };
	});
}

export function clearPin() {
	selection.update((s) => ({ ...s, pinnedEdge: null }));
}

export function setSearchTarget(target: SearchTarget | null) {
	selection.update((s) => ({ ...s, searchTarget: target }));
}

export function clearSearchTarget() {
	selection.update((s) => ({ ...s, searchTarget: null }));
}

export function isSameEdge(a: EdgeKey | null, b: EdgeKey | null) {
	if (!a || !b) return false;
	return a.source === b.source && a.target === b.target;
}

/** Map an ISCO-1 single-digit code to its node id in the sankey ('0'–'9'). */
export function isco1ToNodeId(isco1: string): string {
	return `isco__${isco1}`;
}

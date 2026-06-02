import { writable, type Writable } from 'svelte/store';

export interface EdgeKey {
	source: string;
	target: string;
}

export interface SelectionState {
	hoveredEdge: EdgeKey | null;
	pinnedEdge: EdgeKey | null;
}

export const selection: Writable<SelectionState> = writable({
	hoveredEdge: null,
	pinnedEdge: null
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

export function isSameEdge(a: EdgeKey | null, b: EdgeKey | null) {
	if (!a || !b) return false;
	return a.source === b.source && a.target === b.target;
}

import { derived, type Readable } from 'svelte/store';
import { filters, type ColorMetric, type Gender, type BrancaId } from './filters';
import { selection, type SearchTarget, type EdgeKey } from './selection';

/**
 * State machine collapsing filters + selection into a single read for the side
 * panels. Per /wiki/07_hero_viz_design.md §"Estats UI":
 *   A — initial      no filters, no target
 *   B — filtered     branca or gender filter active, no target
 *   C — targeted     a search target is selected
 *   D — hovered      transient (handled in the chart itself, not here)
 *   E — pinned       an edge is pinned
 */
export type SelectionMode = 'initial' | 'filtered' | 'targeted' | 'pinned';

export interface ActiveSelection {
	mode: SelectionMode;
	gender: Gender;
	branca: BrancaId[];
	colorMetric: ColorMetric;
	searchTarget: SearchTarget | null;
	pinnedEdge: EdgeKey | null;
	/** True when the panels should switch to a path-focused narrative. */
	pathMode: boolean;
}

export const activeSelection: Readable<ActiveSelection> = derived(
	[filters, selection],
	([$f, $s]) => {
		let mode: SelectionMode = 'initial';
		if ($s.pinnedEdge) mode = 'pinned';
		else if ($s.searchTarget) mode = 'targeted';
		else if ($f.branca.length > 0 || $f.gender !== 'all') mode = 'filtered';

		return {
			mode,
			gender: $f.gender,
			branca: $f.branca,
			colorMetric: $f.colorMetric,
			searchTarget: $s.searchTarget,
			pinnedEdge: $s.pinnedEdge,
			pathMode: mode === 'targeted' || mode === 'pinned' || $f.branca.length > 0
		};
	}
);

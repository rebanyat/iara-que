<script lang="ts">
	import { onMount } from 'svelte';
	import { Index as FlexIndex } from 'flexsearch';
	import {
		selection,
		setSearchTarget,
		clearSearchTarget,
		type SearchTarget
	} from '$lib/stores/selection';
	import { datasets, type WikidataIcon } from '$lib/stores/data';

	type Occupation = {
		id: string;
		label: string;
		alt: string[];
		isco4: string;
		isco1: string;
		iscoLabel: string;
	};

	let inputEl = $state<HTMLInputElement | null>(null);
	let query = $state<string>('');
	let records = $state<Occupation[]>([]);
	let index: FlexIndex | null = null;
	let iconIndex: FlexIndex | null = null;
	let open = $state<boolean>(false);
	let focused = $state<boolean>(false);
	let activeIndex = $state<number>(-1);
	let results = $state<Occupation[]>([]);
	let iconResults = $state<WikidataIcon[]>([]);

	const currentTarget = $derived($selection.searchTarget);
	const icons = $derived.by(() => $datasets.wikidataIcons?.icons ?? []);

	$effect(() => {
		const list = icons;
		if (list.length === 0) return;
		const idx = new FlexIndex({ tokenize: 'forward' });
		for (let i = 0; i < list.length; i++) {
			idx.add(i, list[i].label);
		}
		iconIndex = idx;
	});

	onMount(() => {
		(async () => {
			try {
				const res = await fetch('/data/occupations.json');
				if (!res.ok) throw new Error(`HTTP ${res.status}`);
				records = (await res.json()) as Occupation[];
				const idx = new FlexIndex({ tokenize: 'forward', cache: 100 });
				for (let i = 0; i < records.length; i++) {
					const r = records[i];
					idx.add(i, [r.label, ...(r.alt ?? [])].join(' · '));
				}
				index = idx;
			} catch (err) {
				console.error('Failed to load occupations.json:', err);
			}
		})();

		const onKey = (e: KeyboardEvent) => {
			if (e.key === '/' && !isEditable(e.target)) {
				e.preventDefault();
				inputEl?.focus();
				inputEl?.select();
			}
			if (e.key === 'Escape') {
				if (open) {
					open = false;
					inputEl?.blur();
				} else if (currentTarget) {
					clearSearchTarget();
				}
			}
		};
		window.addEventListener('keydown', onKey);
		return () => window.removeEventListener('keydown', onKey);
	});

	function isEditable(t: EventTarget | null) {
		if (!(t instanceof HTMLElement)) return false;
		const tag = t.tagName;
		if (t.isContentEditable) return true;
		return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
	}

	function runSearch(q: string) {
		if (!q || q.length < 2) {
			results = [];
			iconResults = [];
			return;
		}
		if (index) {
			const hits = index.search(q, { limit: 8 }) as unknown as number[];
			results = hits.map((i) => records[i]).filter(Boolean);
		} else {
			results = [];
		}
		if (iconIndex) {
			const iconHits = iconIndex.search(q, { limit: 4 }) as unknown as number[];
			iconResults = iconHits.map((i) => icons[i]).filter(Boolean);
		} else {
			iconResults = [];
		}
		activeIndex = results.length + iconResults.length > 0 ? 0 : -1;
	}

	function onInput() {
		open = true;
		runSearch(query);
	}

	function select(r: Occupation) {
		const target: SearchTarget = {
			source: 'esco',
			id: r.id,
			label: r.label,
			isco1: r.isco1,
			iscoLabel: r.iscoLabel
		};
		setSearchTarget(target);
		query = r.label;
		open = false;
		inputEl?.blur();
	}

	function selectIcon(r: WikidataIcon) {
		const target: SearchTarget = {
			source: 'wikidata',
			id: r.id,
			label: r.label,
			isco1: r.isco1,
			iscoLabel: r.iscoLabel
		};
		setSearchTarget(target);
		query = r.label;
		open = false;
		inputEl?.blur();
	}

	const totalCount = $derived(results.length + iconResults.length);

	function onKeyDown(e: KeyboardEvent) {
		if (!open) return;
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			activeIndex = Math.min(activeIndex + 1, totalCount - 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			activeIndex = Math.max(activeIndex - 1, 0);
		} else if (e.key === 'Enter') {
			if (activeIndex >= 0 && activeIndex < results.length) {
				e.preventDefault();
				select(results[activeIndex]);
			} else if (activeIndex >= results.length && activeIndex < totalCount) {
				e.preventDefault();
				selectIcon(iconResults[activeIndex - results.length]);
			}
		}
	}

	function onFocus() {
		focused = true;
		if (query.length >= 2) open = true;
	}

	function onBlur() {
		// Delay so click on a result item registers
		setTimeout(() => {
			focused = false;
			open = false;
		}, 120);
	}

	function clear() {
		query = '';
		results = [];
		iconResults = [];
		open = false;
		clearSearchTarget();
		inputEl?.focus();
	}

	function highlight(text: string, q: string): string {
		if (!q) return escapeHtml(text);
		const pattern = new RegExp(`(${escapeRegex(q)})`, 'gi');
		return escapeHtml(text).replace(pattern, '<mark>$1</mark>');
	}

	function escapeHtml(s: string) {
		return s
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;');
	}

	function escapeRegex(s: string) {
		return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
	}
</script>

<div class="search" class:has-target={currentTarget !== null}>
	<div class="search-input-wrap">
		<label for="search-input" class="search-label">
			<span aria-hidden="true">🔍</span>
			<span class="sr-only">Cerca per ocupació</span>
		</label>
		<input
			id="search-input"
			type="search"
			autocomplete="off"
			placeholder='Vull ser… (prova "fontaner", "infermera", "programador") — prem "/"'
			bind:this={inputEl}
			bind:value={query}
			oninput={onInput}
			onfocus={onFocus}
			onblur={onBlur}
			onkeydown={onKeyDown}
			role="combobox"
			aria-expanded={open}
			aria-controls="search-listbox"
			aria-autocomplete="list"
		/>
		{#if query.length > 0}
			<button type="button" class="search-clear" onclick={clear} aria-label="Esborrar cerca">×</button>
		{/if}
		<kbd class="search-key" aria-hidden="true">/</kbd>
	</div>

	{#if currentTarget}
		<div class="search-target" class:icon-target={currentTarget.source === 'wikidata'} aria-live="polite">
			<div class="target-line">
				Objectiu: <strong>{currentTarget.label}</strong>
				<span class="muted">· {currentTarget.iscoLabel}</span>
				<button type="button" class="search-clear-target" onclick={() => clearSearchTarget()} aria-label="Treure objectiu">×</button>
			</div>
			{#if currentTarget.source === 'wikidata'}
				<p class="target-caveat">
					Mostra <em>il·lustrativa</em> a partir de biografies de Wikidata: no és inserció reglada
					ni representativa estadísticament. Útil per veure quins itineraris reals s'associen
					a aquesta professió, no per quantificar-los.
				</p>
			{/if}
		</div>
	{/if}

	{#if open && query.length >= 2}
		<div class="search-listbox" id="search-listbox" role="listbox">
			{#if totalCount === 0}
				<p class="search-empty">No s'ha trobat cap ocupació amb «{query}».</p>
			{:else}
				{#if results.length > 0}
					<header class="search-section">
						Ocupacions ESCO <span class="muted">({results.length})</span>
					</header>
					{#each results as r, i (r.id)}
						<button
							type="button"
							class="search-item"
							class:active={i === activeIndex}
							role="option"
							aria-selected={i === activeIndex}
							onmousedown={(e) => {
								e.preventDefault();
								select(r);
							}}
							onmouseenter={() => (activeIndex = i)}
						>
							<span class="item-label">{@html highlight(r.label, query)}</span>
							<span class="item-meta">ISCO {r.isco4} · {r.iscoLabel}</span>
						</button>
					{/each}
				{/if}
				{#if iconResults.length > 0}
					<header class="search-section icon">
						Camins icònics (Wikidata) <span class="muted">({iconResults.length})</span>
					</header>
					{#each iconResults as r, i (r.id)}
						{@const idx = results.length + i}
						<button
							type="button"
							class="search-item icon-item"
							class:active={idx === activeIndex}
							role="option"
							aria-selected={idx === activeIndex}
							onmousedown={(e) => {
								e.preventDefault();
								selectIcon(r);
							}}
							onmouseenter={() => (activeIndex = idx)}
						>
							<span class="item-label">{@html highlight(r.label, query)}</span>
							<span class="item-meta">
								{r.count} biografies · {r.iscoLabel}
								{#if r.topFields[0]}· {r.topFields[0].label}{/if}
							</span>
						</button>
					{/each}
				{/if}
			{/if}
		</div>
	{/if}
</div>

<style>
	.search {
		position: relative;
		margin-bottom: var(--sp-4);
	}

	.search-input-wrap {
		position: relative;
		display: flex;
		align-items: center;
		background: var(--bg-elev);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-lg);
		padding: var(--sp-2) var(--sp-3);
		transition: border-color var(--dur-2) var(--ease), box-shadow var(--dur-2) var(--ease);
	}

	.search-input-wrap:focus-within {
		border-color: var(--accent);
		box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 16%, transparent);
	}

	.search-label {
		display: inline-flex;
		padding-right: var(--sp-2);
		color: var(--ink-muted);
		font-size: 1rem;
	}

	input[type='search'] {
		flex: 1;
		min-width: 0;
		background: transparent;
		border: none;
		outline: none;
		font-family: var(--font-sans);
		font-size: 1rem;
		color: var(--ink-primary);
		padding-block: var(--sp-2);
	}

	input[type='search']::-webkit-search-cancel-button {
		display: none;
	}

	input[type='search']::placeholder {
		color: var(--ink-muted);
		font-style: italic;
	}

	.search-clear {
		font-size: 1.25rem;
		color: var(--ink-muted);
		padding: 0 var(--sp-2);
		line-height: 1;
		transition: color var(--dur-2) var(--ease);
	}

	.search-clear:hover {
		color: var(--ink-primary);
	}

	.search-key {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-width: 22px;
		height: 22px;
		padding: 0 6px;
		border: 1px solid var(--border-default);
		border-radius: var(--radius-sm);
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
		background: var(--bg-base);
	}

	.search-target {
		margin-top: var(--sp-2);
		padding: var(--sp-2) var(--sp-3);
		font-size: var(--fs-small);
		color: var(--ink-secondary);
		border-left: 3px solid var(--accent);
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}

	.search-target.icon-target {
		border-left-color: var(--accent-cool);
	}

	.target-line {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}

	.target-caveat {
		font-size: var(--fs-micro);
		color: var(--ink-muted);
		line-height: 1.5;
		max-width: 60ch;
	}

	.target-caveat em {
		color: var(--accent-cool);
		font-style: italic;
	}

	.search-target strong {
		color: var(--ink-primary);
	}

	.muted {
		color: var(--ink-muted);
	}

	.search-clear-target {
		margin-left: auto;
		color: var(--ink-muted);
		font-size: 1.25rem;
		line-height: 1;
		padding: 0 var(--sp-2);
	}

	.search-clear-target:hover {
		color: var(--ink-primary);
	}

	.search-listbox {
		position: absolute;
		top: calc(100% + var(--sp-2));
		left: 0;
		right: 0;
		max-height: 360px;
		overflow-y: auto;
		background: var(--bg-surface);
		border: 1px solid var(--border-default);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-lg);
		z-index: 20;
		padding: var(--sp-2) 0;
	}

	.search-empty {
		padding: var(--sp-3) var(--sp-4);
		color: var(--ink-muted);
		font-size: var(--fs-small);
	}

	.search-section {
		padding: var(--sp-2) var(--sp-4);
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--ink-muted);
		border-top: 1px solid var(--border-subtle);
	}

	.search-section:first-child {
		border-top: none;
	}

	.search-section.icon {
		color: var(--accent);
	}

	.icon-item .item-meta {
		color: color-mix(in srgb, var(--accent) 70%, var(--ink-muted));
	}

	.search-item {
		display: flex;
		flex-direction: column;
		gap: 2px;
		align-items: flex-start;
		width: 100%;
		text-align: left;
		padding: var(--sp-2) var(--sp-4);
		color: var(--ink-primary);
		font-family: var(--font-sans);
		transition: background var(--dur-1) var(--ease);
	}

	.search-item.active,
	.search-item:hover {
		background: color-mix(in srgb, var(--accent) 14%, transparent);
	}

	.item-label {
		font-size: var(--fs-body);
		line-height: 1.3;
	}

	.item-label :global(mark) {
		background: color-mix(in srgb, var(--accent) 60%, transparent);
		color: var(--ink-primary);
		padding: 0 2px;
		border-radius: 2px;
	}

	.item-meta {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		color: var(--ink-muted);
	}
</style>

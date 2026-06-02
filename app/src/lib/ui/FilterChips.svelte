<script lang="ts">
	import {
		filters,
		setGender,
		toggleBranca,
		clearBranca,
		resetFilters,
		anyFilterActive,
		BRANCA_IDS,
		type Gender,
		type BrancaId
	} from '$lib/stores/filters';

	const BRANCA_LABEL: Record<BrancaId, string> = {
		branca__stem: 'STEM',
		branca__health: 'Salut',
		branca__social: 'Socials',
		branca__hum: 'Humanitats',
		branca__services: 'Serveis',
		branca__industry: 'Indústria'
	};

	const GENDER_OPTS: { id: Gender; label: string }[] = [
		{ id: 'all', label: 'Tothom' },
		{ id: 'F', label: 'Dones' },
		{ id: 'M', label: 'Homes' }
	];
</script>

<form class="filters" aria-label="Filtres de l'atles">
	<fieldset>
		<legend>Gènere</legend>
		<div class="seg" role="radiogroup" aria-label="Filtre per gènere">
			{#each GENDER_OPTS as opt (opt.id)}
				<button
					type="button"
					class="seg-btn"
					class:active={$filters.gender === opt.id}
					role="radio"
					aria-checked={$filters.gender === opt.id}
					onclick={() => setGender(opt.id)}
				>
					{opt.label}
				</button>
			{/each}
		</div>
	</fieldset>

	<fieldset>
		<legend>Branca <span class="hint">(multiselecció — focus dels camins)</span></legend>
		<div class="chips" role="group" aria-label="Filtre per branca">
			{#each BRANCA_IDS as id (id)}
				{@const isActive = $filters.branca.includes(id)}
				<button
					type="button"
					class="chip"
					class:active={isActive}
					aria-pressed={isActive}
					onclick={() => toggleBranca(id)}
				>
					{BRANCA_LABEL[id]}
				</button>
			{/each}
			{#if $filters.branca.length > 0}
				<button type="button" class="chip ghost" onclick={() => clearBranca()}>
					· esborrar
				</button>
			{/if}
		</div>
	</fieldset>

	{#if $anyFilterActive}
		<button type="button" class="reset" onclick={() => resetFilters()} aria-label="Restablir tots els filtres">
			Restablir filtres
		</button>
	{/if}
</form>

<style>
	.filters {
		display: flex;
		gap: var(--sp-5);
		align-items: flex-start;
		flex-wrap: wrap;
		padding: var(--sp-4);
		background: var(--bg-elev);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		margin-bottom: var(--sp-4);
	}

	fieldset {
		border: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}

	legend {
		font-family: var(--font-mono);
		font-size: var(--fs-micro);
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--ink-muted);
		padding: 0;
	}

	.hint {
		font-family: var(--font-sans);
		text-transform: none;
		letter-spacing: 0;
		color: var(--ink-muted);
		font-size: var(--fs-micro);
		margin-left: var(--sp-2);
	}

	.seg {
		display: inline-flex;
		border: 1px solid var(--border-default);
		border-radius: var(--radius-pill);
		padding: 2px;
		gap: 2px;
	}

	.seg-btn {
		padding: var(--sp-2) var(--sp-3);
		font-family: var(--font-sans);
		font-size: var(--fs-small);
		font-weight: 500;
		color: var(--ink-secondary);
		border-radius: var(--radius-pill);
		transition: background var(--dur-2) var(--ease), color var(--dur-2) var(--ease);
	}

	.seg-btn:hover {
		color: var(--ink-primary);
	}

	.seg-btn.active {
		background: var(--ink-primary);
		color: var(--bg-base);
	}

	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--sp-2);
	}

	.chip {
		padding: var(--sp-2) var(--sp-3);
		border-radius: var(--radius-pill);
		border: 1px solid var(--border-default);
		background: transparent;
		color: var(--ink-secondary);
		font-family: var(--font-sans);
		font-size: var(--fs-small);
		font-weight: 500;
		transition:
			background var(--dur-2) var(--ease),
			color var(--dur-2) var(--ease),
			border-color var(--dur-2) var(--ease);
	}

	.chip:hover {
		color: var(--ink-primary);
		border-color: var(--border-strong);
	}

	.chip.active {
		background: var(--accent);
		color: var(--bg-base);
		border-color: var(--accent);
	}

	.chip.ghost {
		border-style: dashed;
		color: var(--ink-muted);
		font-style: italic;
	}

	.reset {
		margin-left: auto;
		align-self: flex-end;
		font-family: var(--font-sans);
		font-size: var(--fs-small);
		color: var(--ink-muted);
		padding: var(--sp-2) var(--sp-3);
		border-radius: var(--radius-md);
		border: 1px solid var(--border-default);
		transition: color var(--dur-2) var(--ease);
	}

	.reset:hover {
		color: var(--ink-primary);
		border-color: var(--border-strong);
	}
</style>

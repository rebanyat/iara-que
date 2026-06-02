<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';

	let { children } = $props();

	const nav = [
		{ href: '/', label: 'Atles' },
		{ href: '/vull-ser', label: 'Vull ser…' },
		{ href: '/metodologia', label: 'Metodologia' },
		{ href: '/about', label: 'Crèdits' }
	];

	function isActive(href: string) {
		return href === '/' ? page.url.pathname === '/' : page.url.pathname.startsWith(href);
	}
</script>

<a class="skip-link" href="#main">Salta al contingut</a>

<header class="site-header">
	<div class="header-inner container">
		<a href="/" class="brand" aria-label="I ara, què? — inici">
			<span class="brand-mark" aria-hidden="true">·</span>
			<span class="brand-name">I ara, què?</span>
		</a>

		<nav aria-label="Navegació principal">
			<ul class="nav-list">
				{#each nav as item (item.href)}
					<li>
						<a
							href={item.href}
							class="nav-link"
							class:active={isActive(item.href)}
							aria-current={isActive(item.href) ? 'page' : undefined}
						>
							{item.label}
						</a>
					</li>
				{/each}
			</ul>
		</nav>
	</div>
</header>

<main id="main">
	{@render children()}
</main>

<footer class="site-footer">
	<div class="footer-inner container">
		<p class="footer-copy">
			Construït amb <a href="https://kit.svelte.dev">SvelteKit</a> +
			<a href="https://d3js.org">D3.js</a>. Codi obert (MIT).
		</p>
		<p class="footer-meta">
			Ivan Rodríguez Quintana · UOC · Visualització de Dades · 2026
		</p>
	</div>
</footer>

<style>
	.skip-link {
		position: absolute;
		left: -9999px;
		top: var(--sp-2);
		background: var(--bg-elev);
		color: var(--ink-primary);
		padding: var(--sp-2) var(--sp-4);
		border-radius: var(--radius-md);
		z-index: 1000;
		text-decoration: none;
		border: 1px solid var(--border-default);
	}

	.skip-link:focus {
		left: var(--sp-2);
	}

	.site-header {
		position: sticky;
		top: 0;
		z-index: 100;
		background: var(--bg-overlay);
		backdrop-filter: saturate(140%) blur(12px);
		border-bottom: 1px solid var(--border-subtle);
		height: var(--header-h);
		display: flex;
		align-items: center;
	}

	.header-inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		gap: var(--sp-6);
	}

	.brand {
		display: inline-flex;
		align-items: baseline;
		gap: var(--sp-2);
		font-family: var(--font-serif);
		font-weight: 900;
		font-size: 1.125rem;
		color: var(--ink-primary);
		border-bottom: none;
		letter-spacing: -0.01em;
	}

	.brand:hover,
	.brand:focus-visible {
		color: var(--ink-primary);
	}

	.brand-mark {
		color: var(--accent);
		font-size: 1.5rem;
		line-height: 0;
	}

	.brand-name {
		font-style: italic;
	}

	nav {
		min-width: 0;
	}

	.nav-list {
		display: flex;
		gap: var(--sp-5);
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.nav-link {
		font-family: var(--font-sans);
		font-size: var(--fs-small);
		font-weight: 500;
		color: var(--ink-secondary);
		border-bottom: none;
		padding-block: var(--sp-2);
		position: relative;
	}

	.nav-link:hover,
	.nav-link:focus-visible {
		color: var(--ink-primary);
	}

	.nav-link.active {
		color: var(--ink-primary);
	}

	.nav-link.active::after {
		content: '';
		position: absolute;
		left: 0;
		right: 0;
		bottom: -1px;
		height: 2px;
		background: var(--accent);
		border-radius: 2px;
	}

	main {
		min-height: calc(100dvh - var(--header-h));
	}

	.site-footer {
		border-top: 1px solid var(--border-subtle);
		padding-block: var(--sp-6);
		margin-top: var(--sp-10);
	}

	.footer-inner {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		font-size: var(--fs-small);
		color: var(--ink-muted);
	}

	.footer-copy a {
		color: var(--ink-secondary);
		border-bottom-color: var(--border-default);
	}

	@media (max-width: 640px) {
		.header-inner {
			gap: var(--sp-3);
		}
		.nav-list {
			gap: var(--sp-3);
		}
	}
</style>

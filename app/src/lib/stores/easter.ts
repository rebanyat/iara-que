import { browser } from '$app/environment';
import { writable, type Writable } from 'svelte/store';

const KONAMI = [
	'ArrowUp',
	'ArrowUp',
	'ArrowDown',
	'ArrowDown',
	'ArrowLeft',
	'ArrowRight',
	'ArrowLeft',
	'ArrowRight',
	'b',
	'a'
];

export const easter: Writable<boolean> = writable(false);

export function initEaster() {
	if (!browser) return () => {};
	const url = new URL(window.location.href);
	if (url.searchParams.get('easter') === '1') easter.set(true);

	let buf: string[] = [];
	const onKey = (e: KeyboardEvent) => {
		const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
		buf.push(k);
		if (buf.length > KONAMI.length) buf = buf.slice(-KONAMI.length);
		if (buf.length === KONAMI.length && buf.every((v, i) => v === KONAMI[i])) {
			easter.set(true);
			buf = [];
			// Slight visual confirmation: brief class on body
			document.body.classList.add('easter-unlocked');
			setTimeout(() => document.body.classList.remove('easter-unlocked'), 1200);
		}
	};
	window.addEventListener('keydown', onKey);
	return () => window.removeEventListener('keydown', onKey);
}

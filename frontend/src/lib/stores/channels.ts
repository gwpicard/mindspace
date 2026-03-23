import { writable } from 'svelte/store';
import type { Channel } from '$lib/api';
import { listChannels, createChannel as apiCreate, deleteChannel as apiDelete } from '$lib/api';

export const channels = writable<Channel[]>([]);

export async function loadChannels() {
	const list = await listChannels();
	channels.set(list);
}

export async function addChannel(name: string, description?: string) {
	await apiCreate(name, description);
	await loadChannels();
}

export async function removeChannel(id: string) {
	await apiDelete(id);
	await loadChannels();
}

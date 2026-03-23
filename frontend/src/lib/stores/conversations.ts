import { writable } from 'svelte/store';
import type { Conversation, ConversationDetail, Message } from '$lib/api';
import {
	listConversations,
	getConversation,
	createConversation,
	deleteConversation as apiDelete,
} from '$lib/api';

export const conversations = writable<Conversation[]>([]);
export const currentConversation = writable<ConversationDetail | null>(null);

export async function loadConversations() {
	const list = await listConversations();
	conversations.set(list);
}

export async function loadConversation(id: string) {
	const detail = await getConversation(id);
	currentConversation.set(detail);
	return detail;
}

export async function startNewConversation(): Promise<Conversation> {
	const conv = await createConversation();
	await loadConversations();
	return conv;
}

export async function removeConversation(id: string) {
	await apiDelete(id);
	currentConversation.set(null);
	await loadConversations();
}

export function appendMessage(msg: Message) {
	currentConversation.update((conv) => {
		if (!conv) return conv;
		return { ...conv, messages: [...conv.messages, msg] };
	});
}

export function updateLastAssistantMessage(content: string) {
	currentConversation.update((conv) => {
		if (!conv) return conv;
		const messages = [...conv.messages];
		const last = messages[messages.length - 1];
		if (last && last.role === 'assistant') {
			messages[messages.length - 1] = { ...last, content };
		}
		return { ...conv, messages };
	});
}

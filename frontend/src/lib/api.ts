/**
 * Typed API client for Mindspace backend.
 */

const BASE = '/api';

export interface Conversation {
	id: string;
	title: string | null;
	created_at: string;
	updated_at: string;
	channel_ids: string[];
}

export interface ConversationDetail extends Conversation {
	messages: Message[];
}

export interface Message {
	id: string;
	role: 'user' | 'assistant';
	content: string;
	created_at: string;
	cognitive_operations: string[] | null;
}

export interface Channel {
	id: string;
	name: string;
	description: string | null;
	created_at: string;
}

export interface ChannelDetail extends Channel {
	conversation_ids: string[];
}

export interface SearchResult {
	snippet: string;
	distance: number;
	source: string;
	type: string;
	metadata: Record<string, unknown>;
	conversation_id: string | null;
	conversation_title: string | null;
	capture_id: string | null;
	title: string | null;
}

export interface Resource {
	id: string;
	type: string;
	source_url: string | null;
	title: string | null;
	processing_status: string;
	created_at: string;
	conversation_id: string | null;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE}${path}`, {
		headers: { 'Content-Type': 'application/json' },
		...options,
	});
	if (!res.ok) {
		const error = await res.text();
		throw new Error(`API error ${res.status}: ${error}`);
	}
	if (res.status === 204) return undefined as T;
	return res.json();
}

// --- Conversations ---

export async function createConversation(title?: string): Promise<Conversation> {
	return request('/conversations', {
		method: 'POST',
		body: JSON.stringify({ title }),
	});
}

export async function listConversations(limit = 50): Promise<Conversation[]> {
	return request(`/conversations?limit=${limit}`);
}

export async function getConversation(id: string): Promise<ConversationDetail> {
	return request(`/conversations/${id}`);
}

export async function updateConversation(
	id: string,
	data: { title?: string; channel_ids?: string[] }
): Promise<Conversation> {
	return request(`/conversations/${id}`, {
		method: 'PATCH',
		body: JSON.stringify(data),
	});
}

export async function deleteConversation(id: string): Promise<void> {
	return request(`/conversations/${id}`, { method: 'DELETE' });
}

// --- Chat (SSE) ---

export interface SSEEvent {
	event: string;
	data: unknown;
}

export async function* sendMessage(
	conversationId: string,
	content: string
): AsyncGenerator<SSEEvent> {
	const res = await fetch(`${BASE}/conversations/${conversationId}/messages`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ content }),
	});

	if (!res.ok) {
		throw new Error(`Chat error ${res.status}`);
	}

	const reader = res.body!.getReader();
	const decoder = new TextDecoder();
	let buffer = '';

	while (true) {
		const { done, value } = await reader.read();
		if (done) break;

		buffer += decoder.decode(value, { stream: true });
		const lines = buffer.split('\n');
		buffer = lines.pop() || '';

		let currentEvent = 'message';
		for (const line of lines) {
			if (line.startsWith('event: ')) {
				currentEvent = line.slice(7);
			} else if (line.startsWith('data: ')) {
				try {
					const data = JSON.parse(line.slice(6));
					yield { event: currentEvent, data };
				} catch {
					// skip malformed data
				}
			}
		}
	}
}

// --- Channels ---

export async function createChannel(name: string, description?: string): Promise<Channel> {
	return request('/channels', {
		method: 'POST',
		body: JSON.stringify({ name, description }),
	});
}

export async function listChannels(): Promise<Channel[]> {
	return request('/channels');
}

export async function getChannel(id: string): Promise<ChannelDetail> {
	return request(`/channels/${id}`);
}

export async function updateChannel(
	id: string,
	data: { name?: string; description?: string }
): Promise<Channel> {
	return request(`/channels/${id}`, {
		method: 'PATCH',
		body: JSON.stringify(data),
	});
}

export async function deleteChannel(id: string): Promise<void> {
	return request(`/channels/${id}`, { method: 'DELETE' });
}

// --- Search ---

export async function search(
	query: string,
	filters?: Record<string, unknown>,
	n_results = 10
): Promise<SearchResult[]> {
	return request('/search', {
		method: 'POST',
		body: JSON.stringify({ query, filters, n_results }),
	});
}

// --- Resources ---

export async function listResources(status?: string, type?: string): Promise<Resource[]> {
	const params = new URLSearchParams();
	if (status) params.set('status', status);
	if (type) params.set('type', type);
	const qs = params.toString();
	return request(`/resources${qs ? '?' + qs : ''}`);
}

export interface ResourceDetail extends Resource {
	raw_content: string | null;
}

export async function getResource(id: string): Promise<ResourceDetail> {
	return request(`/resources/${id}`);
}

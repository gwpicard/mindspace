const API = 'http://localhost:8000';

export async function resetDB() {
	const res = await fetch(`${API}/_test/reset`, { method: 'POST' });
	if (res.status !== 204) {
		throw new Error(`Reset failed: ${res.status}`);
	}
}

export async function createConversationViaAPI(title?: string) {
	const res = await fetch(`${API}/api/conversations`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ title }),
	});
	return res.json();
}

export async function createChannelViaAPI(name: string) {
	const res = await fetch(`${API}/api/channels`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ name }),
	});
	return res.json();
}

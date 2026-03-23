import { test, expect } from '@playwright/test';
import { resetDB, createConversationViaAPI, createChannelViaAPI } from './helpers';

test.beforeEach(async () => {
	await resetDB();
});

test('create channel via conversation header dropdown', async ({ page }) => {
	// Create a conversation via API and navigate to it
	const conv = await createConversationViaAPI('Test conv');
	await page.goto(`/conversation/${conv.id}`);
	await expect(page.getByTestId('add-channel-btn')).toBeVisible({ timeout: 5_000 });

	// Open channel dropdown and create new channel
	await page.getByTestId('add-channel-btn').click();
	await page.locator('.new-channel-row input').fill('test-channel');
	await page.locator('.new-channel-row input').press('Enter');

	// Channel tag should appear in header
	await expect(page.locator('.channel-tag', { hasText: 'test-channel' })).toBeVisible({ timeout: 5_000 });
});

test('remove channel from conversation', async ({ page }) => {
	// Create conversation and channel via API, then link them
	const conv = await createConversationViaAPI('Test conv');
	const ch = await createChannelViaAPI('remove-me');

	// Link channel to conversation
	await fetch('http://localhost:8000/api/conversations/' + conv.id, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ channel_ids: [ch.id] }),
	});

	await page.goto(`/conversation/${conv.id}`);
	await expect(page.locator('.channel-tag', { hasText: 'remove-me' })).toBeVisible({ timeout: 5_000 });

	// Click tag to remove
	await page.locator('.channel-tag', { hasText: 'remove-me' }).click();
	await expect(page.locator('.channel-tag', { hasText: 'remove-me' })).toHaveCount(0, { timeout: 5_000 });
});

test('navigate to channel page shows channel name', async ({ page }) => {
	const ch = await createChannelViaAPI('my-channel');
	await page.goto(`/channel/${ch.id}`);
	await expect(page.locator('h2', { hasText: 'my-channel' })).toBeVisible({ timeout: 5_000 });
});

test('edit channel name', async ({ page }) => {
	const ch = await createChannelViaAPI('old-name');
	await page.goto(`/channel/${ch.id}`);
	await expect(page.locator('h2', { hasText: 'old-name' })).toBeVisible({ timeout: 5_000 });

	// Click edit button
	await page.getByTestId('edit-channel').click();
	const input = page.getByTestId('channel-name-input');
	await expect(input).toBeVisible();

	// Clear and type new name
	await input.fill('new-name');
	await input.press('Enter');

	// Name should update
	await expect(page.locator('h2', { hasText: 'new-name' })).toBeVisible({ timeout: 5_000 });
});

test('delete channel redirects to home', async ({ page }) => {
	const ch = await createChannelViaAPI('delete-me');
	await page.goto(`/channel/${ch.id}`);
	await expect(page.locator('h2', { hasText: 'delete-me' })).toBeVisible({ timeout: 5_000 });

	// First click
	await page.getByTestId('delete-channel').click();
	// Second click to confirm
	await page.getByTestId('delete-channel').click();

	await expect(page).toHaveURL('/', { timeout: 5_000 });
});

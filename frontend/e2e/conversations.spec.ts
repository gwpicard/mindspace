import { test, expect } from '@playwright/test';
import { resetDB, createConversationViaAPI } from './helpers';

test.beforeEach(async () => {
	await resetDB();
});

test('create conversation via sidebar navigates to conversation page', async ({ page }) => {
	await page.goto('/');
	await page.getByTestId('new-conv-btn').click();
	// Home page shows chat input — type and send to create conversation
	await page.getByTestId('chat-input').fill('Hello world');
	await page.getByTestId('send-btn').click();
	// Should navigate to a conversation page
	await expect(page).toHaveURL(/\/conversation\//);
});

test('delete conversation removes it from sidebar and redirects', async ({ page }) => {
	// Create conversation via API
	const conv = await createConversationViaAPI('Delete me');
	await page.goto(`/conversation/${conv.id}`);

	// Wait for conversation to appear in sidebar
	const convItem = page.getByTestId('conv-item').first();
	await expect(convItem).toBeVisible({ timeout: 5_000 });

	// First click — enter confirming state
	const deleteBtn = convItem.getByTestId('delete-conv');
	await deleteBtn.click({ force: true });

	// Second click — confirm delete
	await deleteBtn.click({ force: true });

	// Should redirect to home
	await expect(page).toHaveURL('/', { timeout: 5_000 });
	// Conversation should be gone from sidebar
	await expect(page.getByTestId('conv-item')).toHaveCount(0);
});

test('send message shows user message in chat', async ({ page }) => {
	// Create conversation via API and navigate to it
	const conv = await createConversationViaAPI('Test conv');
	await page.goto(`/conversation/${conv.id}`);
	await expect(page.getByTestId('chat-input')).toBeVisible({ timeout: 5_000 });

	await page.getByTestId('chat-input').fill('My test message');
	await page.getByTestId('send-btn').click();

	// User message should appear (optimistically added before API response)
	await expect(page.locator('.messages').getByText('My test message')).toBeVisible({ timeout: 10_000 });
});

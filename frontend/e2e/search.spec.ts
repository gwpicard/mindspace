import { test, expect } from '@playwright/test';
import { resetDB } from './helpers';

test.beforeEach(async () => {
	await resetDB();
});

test('search button opens search modal, Escape closes it', async ({ page }) => {
	await page.goto('/');

	// Open via sidebar search button
	await page.getByTestId('search-btn').click();
	await expect(page.getByTestId('search-modal')).toBeVisible();

	// Close with Escape on the input
	await page.getByTestId('search-input').press('Escape');
	await expect(page.getByTestId('search-modal')).toHaveCount(0);
});

test('typing in search shows input value', async ({ page }) => {
	await page.goto('/');

	// Open search via button
	await page.getByTestId('search-btn').click();
	const input = page.getByTestId('search-input');
	await expect(input).toBeVisible();

	// Type and verify
	await input.fill('test query');
	await expect(input).toHaveValue('test query');
});

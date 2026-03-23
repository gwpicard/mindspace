import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: './e2e',
	timeout: 30_000,
	retries: 0,
	workers: 1,
	use: {
		baseURL: 'http://localhost:5173',
		headless: true,
	},
	projects: [
		{
			name: 'chromium',
			use: { browserName: 'chromium' },
		},
	],
	webServer: [
		{
			command: 'cd .. && uv run uvicorn mindspace.web.app:create_app --factory --port 8000',
			port: 8000,
			reuseExistingServer: !process.env.CI,
			env: { MINDSPACE_TEST_MODE: '1' },
		},
		{
			command: 'npm run dev',
			port: 5173,
			reuseExistingServer: !process.env.CI,
		},
	],
});

<script lang="ts">
	import { page } from '$app/state';
	import { marked } from 'marked';
	import type { ResourceDetail } from '$lib/api';
	import { getResource } from '$lib/api';

	let resource = $state<ResourceDetail | null>(null);
	let error = $state<string | null>(null);
	let readmeExpanded = $state(false);

	$effect(() => {
		const id = page.params.id;
		if (id) {
			error = null;
			readmeExpanded = false;
			getResource(id)
				.then((r) => (resource = r))
				.catch((e) => (error = e.message));
		}
	});

	const isRepo = $derived(resource?.type === 'repo');
	const meta = $derived(resource?.metadata ?? {});

	// For repos, raw_content starts with "description\n\n<readme markdown>"
	// Split so we can show description as summary and readme separately
	const repoDescription = $derived.by(() => {
		if (!isRepo || !meta) return '';
		return (meta.description as string) || '';
	});

	const readmeContent = $derived.by(() => {
		if (!resource?.raw_content) return '';
		if (!isRepo) return resource.raw_content;
		// raw_content = "description\n\n<readme>", skip the description line
		const desc = repoDescription;
		let content = resource.raw_content;
		if (desc && content.startsWith(desc)) {
			content = content.slice(desc.length).replace(/^\n+/, '');
		}
		return content;
	});

	const renderedContent = $derived.by(() => {
		const text = isRepo ? readmeContent : resource?.raw_content || '';
		if (!text) return '';
		return marked.parse(text, { async: false }) as string;
	});

	// Filter metadata to only show useful fields
	const HIDDEN_META_KEYS = new Set([
		'cli_capture_id', 'created_at', 'url', 'description',
		'readme_text', 'owner', 'repo_name',
	]);

	const displayMeta = $derived.by(() => {
		if (!meta) return [];
		return Object.entries(meta)
			.filter(([k, v]) => !HIDDEN_META_KEYS.has(k) && v != null && v !== '' && !(Array.isArray(v) && v.length === 0))
			.map(([k, v]) => [k, v] as [string, unknown]);
	});

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString([], {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
		});
	}

	function formatNumber(n: unknown): string {
		if (typeof n !== 'number') return String(n);
		if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
		return String(n);
	}

	function formatMetaValue(v: unknown): string {
		if (Array.isArray(v)) return v.join(', ');
		if (typeof v === 'object' && v !== null) return JSON.stringify(v);
		if (typeof v === 'number') return formatNumber(v);
		return String(v);
	}

	function prettyKey(k: string): string {
		return k.replace(/_/g, ' ');
	}

	const TYPE_CONFIG: Record<string, { label: string; color: string }> = {
		repo: { label: 'Repository', color: '#8b5cf6' },
		url: { label: 'Article', color: '#3b82f6' },
		snippet: { label: 'Snippet', color: '#f59e0b' },
		video: { label: 'Video', color: '#ef4444' },
		note: { label: 'Note', color: '#10b981' },
		thought: { label: 'Thought', color: '#6366f1' },
	};

	const typeInfo = $derived(TYPE_CONFIG[resource?.type ?? ''] ?? { label: resource?.type ?? '', color: '#888' });
</script>

<div class="resource-page">
	{#if error}
		<div class="error">{error}</div>
	{:else if !resource}
		<div class="loading">Loading...</div>
	{:else}
		<div class="breadcrumb">
			<span class="type-badge" style="--type-color: {typeInfo.color}">{typeInfo.label}</span>
			<span class="date">{formatDate(resource.created_at)}</span>
			{#if resource.processing_status !== 'completed'}
				<span class="status status--{resource.processing_status}">{resource.processing_status}</span>
			{/if}
		</div>

		{#if isRepo}
			<!-- GitHub repo card layout -->
			<div class="repo-card">
				<h1 class="repo-name">
					{#if meta.owner}
						<span class="repo-owner">{meta.owner}</span>
						<span class="repo-sep">/</span>
					{/if}
					<span>{(meta.repo_name as string) || resource.title}</span>
				</h1>

				{#if repoDescription}
					<p class="repo-desc">{repoDescription}</p>
				{/if}

				<div class="repo-stats">
					{#if meta.language}
						<span class="stat">
							<span class="stat-dot" style="background: var(--accent)"></span>
							{meta.language}
						</span>
					{/if}
					{#if meta.stars != null}
						<span class="stat">
							<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
							{formatNumber(meta.stars)}
						</span>
					{/if}
					{#if meta.forks != null}
						<span class="stat">
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M18 9v1a2 2 0 01-2 2H8a2 2 0 01-2-2V9"/><path d="M12 12v3"/></svg>
							{formatNumber(meta.forks)}
						</span>
					{/if}
					{#if meta.open_issues != null}
						<span class="stat">
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
							{formatNumber(meta.open_issues)} issues
						</span>
					{/if}
				</div>

				{#if resource.source_url}
					<a href={resource.source_url} target="_blank" rel="noopener noreferrer" class="source-link">
						{resource.source_url}
					</a>
				{/if}
			</div>

			{#if displayMeta.length > 0}
				<div class="meta-pills">
					{#each displayMeta as [key, value]}
						{#if key !== 'stars' && key !== 'forks' && key !== 'open_issues' && key !== 'language'}
							<span class="meta-pill">
								<span class="meta-pill-label">{prettyKey(key)}</span>
								{formatMetaValue(value)}
							</span>
						{/if}
					{/each}
				</div>
			{/if}

			{#if readmeContent}
				<section class="readme-section">
					<button class="readme-toggle" onclick={() => (readmeExpanded = !readmeExpanded)}>
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/>
						</svg>
						README
						<svg class="chevron" class:expanded={readmeExpanded} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<polyline points="6 9 12 15 18 9"/>
						</svg>
					</button>
					{#if readmeExpanded}
						<div class="markdown-body">
							{@html renderedContent}
						</div>
					{/if}
				</section>
			{/if}
		{:else}
			<!-- Article / URL / other content layout -->
			<h1 class="page-title">{resource.title || 'Untitled'}</h1>

			<div class="article-meta">
				{#if resource.source_url}
					<a href={resource.source_url} target="_blank" rel="noopener noreferrer" class="source-link">
						{resource.source_url}
					</a>
				{/if}
				{#if displayMeta.length > 0}
					<div class="meta-pills">
						{#each displayMeta as [key, value]}
							<span class="meta-pill">
								<span class="meta-pill-label">{prettyKey(key)}</span>
								{formatMetaValue(value)}
							</span>
						{/each}
					</div>
				{/if}
			</div>

			{#if renderedContent}
				<div class="markdown-body">
					{@html renderedContent}
				</div>
			{/if}
		{/if}

		{#if resource.conversation_id}
			<div class="linked-conversation">
				<a href="/conversation/{resource.conversation_id}">
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
					</svg>
					View linked conversation
				</a>
			</div>
		{/if}
	{/if}
</div>

<style>
	.resource-page {
		max-width: 720px;
		margin: 0 auto;
		padding: 32px 24px 64px;
		height: 100vh;
		overflow-y: auto;
	}

	.loading,
	.error {
		padding: 48px;
		text-align: center;
		color: var(--text-secondary);
		font-size: 14px;
	}

	.error {
		color: #e55;
	}

	/* Breadcrumb / top bar */
	.breadcrumb {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 20px;
	}

	.type-badge {
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.3px;
		padding: 3px 10px;
		border-radius: 4px;
		background: color-mix(in srgb, var(--type-color) 15%, transparent);
		color: var(--type-color);
	}

	.date {
		font-size: 12px;
		color: var(--text-secondary);
	}

	.status {
		font-size: 11px;
		padding: 2px 8px;
		border-radius: 4px;
	}

	.status--failed {
		background: color-mix(in srgb, #e55 15%, transparent);
		color: #e55;
	}

	.status--pending,
	.status--processing {
		background: color-mix(in srgb, #f59e0b 15%, transparent);
		color: #f59e0b;
	}

	/* Repo card */
	.repo-card {
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 24px;
		margin-bottom: 16px;
	}

	.repo-name {
		font-size: 22px;
		font-weight: 600;
		margin: 0 0 8px;
		line-height: 1.3;
	}

	.repo-owner {
		color: var(--text-secondary);
		font-weight: 400;
	}

	.repo-sep {
		color: var(--text-secondary);
		font-weight: 300;
		margin: 0 1px;
	}

	.repo-desc {
		font-size: 15px;
		color: var(--text-secondary);
		margin: 0 0 16px;
		line-height: 1.5;
	}

	.repo-stats {
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
		margin-bottom: 16px;
	}

	.stat {
		display: flex;
		align-items: center;
		gap: 5px;
		font-size: 13px;
		color: var(--text-secondary);
	}

	.stat-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
	}

	.source-link {
		font-size: 13px;
		color: var(--text-secondary);
		text-decoration: none;
		word-break: break-all;
	}

	.source-link:hover {
		color: var(--accent);
	}

	/* Meta pills */
	.meta-pills {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin: 16px 0;
	}

	.meta-pill {
		font-size: 12px;
		padding: 4px 10px;
		border-radius: 6px;
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		color: var(--text);
	}

	.meta-pill-label {
		color: var(--text-secondary);
		margin-right: 4px;
	}

	/* README section */
	.readme-section {
		margin-top: 8px;
	}

	.readme-toggle {
		display: flex;
		align-items: center;
		gap: 8px;
		width: 100%;
		padding: 12px 16px;
		border: 1px solid var(--border);
		border-radius: 10px;
		background: var(--bg-secondary);
		color: var(--text);
		font-size: 13px;
		font-weight: 500;
		cursor: pointer;
		transition: background 0.15s;
	}

	.readme-toggle:hover {
		background: var(--bg-tertiary);
	}

	.chevron {
		margin-left: auto;
		transition: transform 0.2s;
	}

	.chevron.expanded {
		transform: rotate(180deg);
	}

	/* Article layout */
	.page-title {
		font-size: 24px;
		font-weight: 600;
		margin: 0 0 12px;
		line-height: 1.3;
	}

	.article-meta {
		margin-bottom: 24px;
	}

	.article-meta .source-link {
		display: block;
		margin-bottom: 12px;
	}

	/* Markdown content */
	.markdown-body {
		font-size: 14px;
		line-height: 1.7;
		padding: 24px;
		background: var(--bg-secondary);
		border: 1px solid var(--border);
		border-radius: 10px;
		margin-top: 0;
		overflow-x: hidden;
	}

	.readme-section .markdown-body {
		border-top: none;
		border-top-left-radius: 0;
		border-top-right-radius: 0;
	}

	.readme-section .readme-toggle:has(+ .markdown-body) {
		border-bottom-left-radius: 0;
		border-bottom-right-radius: 0;
	}

	.markdown-body :global(h1) {
		font-size: 20px;
		margin: 24px 0 12px;
		padding-bottom: 6px;
		border-bottom: 1px solid var(--border);
	}

	.markdown-body :global(h1:first-child) {
		margin-top: 0;
	}

	.markdown-body :global(h2) {
		font-size: 17px;
		margin: 20px 0 10px;
	}

	.markdown-body :global(h3) {
		font-size: 15px;
		margin: 16px 0 8px;
	}

	.markdown-body :global(p) {
		margin: 0 0 12px;
	}

	.markdown-body :global(p:last-child) {
		margin-bottom: 0;
	}

	.markdown-body :global(pre) {
		background: var(--bg-tertiary);
		padding: 12px 16px;
		border-radius: 8px;
		overflow-x: auto;
		font-size: 13px;
		margin: 0 0 12px;
	}

	.markdown-body :global(code) {
		font-size: 13px;
		background: var(--bg-tertiary);
		padding: 1px 5px;
		border-radius: 4px;
	}

	.markdown-body :global(pre code) {
		background: none;
		padding: 0;
	}

	.markdown-body :global(ul),
	.markdown-body :global(ol) {
		margin: 8px 0 12px;
		padding-left: 24px;
	}

	.markdown-body :global(li) {
		margin-bottom: 4px;
	}

	.markdown-body :global(table) {
		width: 100%;
		border-collapse: collapse;
		margin: 12px 0;
		font-size: 13px;
	}

	.markdown-body :global(th),
	.markdown-body :global(td) {
		padding: 8px 12px;
		border: 1px solid var(--border);
		text-align: left;
	}

	.markdown-body :global(th) {
		background: var(--bg-tertiary);
		font-weight: 600;
	}

	.markdown-body :global(blockquote) {
		border-left: 3px solid var(--border);
		margin: 12px 0;
		padding: 4px 16px;
		color: var(--text-secondary);
	}

	.markdown-body :global(img) {
		max-width: 100%;
		border-radius: 8px;
	}

	.markdown-body :global(hr) {
		border: none;
		border-top: 1px solid var(--border);
		margin: 20px 0;
	}

	.markdown-body :global(a) {
		color: var(--accent);
		text-decoration: none;
	}

	.markdown-body :global(a:hover) {
		text-decoration: underline;
	}

	/* Linked conversation */
	.linked-conversation {
		margin-top: 24px;
		padding-top: 16px;
		border-top: 1px solid var(--border);
	}

	.linked-conversation a {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-size: 13px;
		color: var(--text-secondary);
		text-decoration: none;
	}

	.linked-conversation a:hover {
		color: var(--accent);
	}
</style>

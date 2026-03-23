# Mindspace — Product Requirements Document

## 1. Product Overview

Mindspace is a local-first web application that serves as a personal intelligence system for capturing, connecting, and deepening your thinking. Unlike note-taking apps or bookmarking tools, Mindspace treats conversation as the primary interface — you talk, share, and think out loud, and the system captures, processes, and connects everything in the background. Over time, it builds a rich, searchable knowledge base from your conversations and shared resources, surfacing connections, patterns, and blind spots on demand.

It is built for a single user (the creator), runs locally for full data ownership, and proxies all AI interactions through its own backend for maximum control over conversation data.

## 2. Problem Statement

**The insight gap:** You already have good signal detection — you find interesting articles, repos, talks, ideas. The bottleneck is *processing and connecting* things over time. Without a system, insights dissolve.

**Current pain points:**

- **Conversations with AI are disposable.** Valuable thinking happens in Claude/ChatGPT conversations, but it disappears into an unsearchable list of chats. Insights, reactions, half-formed ideas — all lost.
- **Capture friction kills capture.** The existing CLI (`ms capture url "..."`) requires context-switching, remembering commands, and manual tagging. Anything with friction doesn't get used consistently.
- **No accumulation.** Thoughts, reactions, resources, and conversations exist in separate silos (bookmarks, notes apps, chat history, memory). Nothing compounds.
- **No connections surface automatically.** You read about X three weeks ago and encounter Y today — they're deeply related, but nothing tells you that.
- **No reflection infrastructure.** There's no way to ask "what am I missing?" or "what patterns are emerging in my interests?" across everything you've encountered and thought about.

## 3. Goals & Success Metrics

| Goal | Metric | Target | Timeframe |
|------|--------|--------|-----------|
| Replace CLI as primary capture method | Daily usage | Use the app instead of CLI for all captures | v1 launch |
| Reduce capture friction | Time to capture a thought or URL | < 5 seconds from opening app | v1 launch |
| Build a searchable knowledge base | Search recall quality | Find any previously captured insight in < 30 seconds | v1 + 30 days |
| Conversation accumulation | Conversations stored and searchable | All conversations retrievable and cross-searchable | v1 launch |
| Background processing reliability | Resource processing completion rate | > 95% of shared URLs/videos fully processed within 5 minutes | v1 launch |

## 4. Target Audience

**Primary persona:** Guillaume — software engineer, builder, and curious generalist. Reads widely, explores ideas across domains, builds projects, and thinks through problems conversationally with AI. Technically skilled enough to run a local app. Values data ownership. Wants a system that compounds his thinking rather than just storing it.

**Anti-personas:**
- Teams or collaborative users (this is a single-user system)
- People looking for a task/project management tool (this is not a productivity tool)
- Users who want a managed SaaS (this runs locally)

## 5. Jobs To Be Done

**Must-have (v1):**

1. When I **encounter something interesting** (article, repo, video, idea), I want to **capture it in seconds without friction**, so I can **process it later without losing it**.

2. When I'm **thinking through an idea**, I want to **have a conversation about it** and know that conversation is **permanently captured and searchable**, so my thinking **accumulates instead of evaporating**.

3. When I **remember reading something relevant** weeks ago, I want to **search across all my conversations and captures**, so I can **find it and build on it**.

4. When I **share a URL or resource** in conversation, I want the system to **automatically extract, process, and embed the content**, so it becomes **part of my searchable knowledge base** without manual effort.

5. When I have **multiple conversations about related topics**, I want to **organise them into topic channels**, so I can **see the evolution of my thinking on a subject**.

**Should-have (v2):**

6. When I've been **exploring a topic for a while**, I want to **ask "what am I missing?"** and get meaningful answers about **gaps, blind spots, and unexplored perspectives**, so I can **deepen my understanding**.

7. When I'm **stuck or need a different perspective**, I want the AI to **shift into the right thinking mode** (compress, expand, reflect) — either automatically or on request — so the conversation **serves my actual cognitive need**.

8. When I **look at my knowledge base**, I want to **see the shape of what I know** — clusters, connections, gaps — from **multiple angles and views**, so I get a **meta-view of my own thinking**.

## 6. User Stories

### Conversation & Capture
- As a user, I want to open the app and immediately start typing, so that capture friction is near zero.
- As a user, I want to paste a URL into conversation and have it automatically fetched, extracted, and embedded, so I don't have to manually process resources.
- As a user, I want to paste a YouTube link and have the transcript fetched and processed in the background, so video content becomes searchable.
- As a user, I want all my conversations stored locally with full history, so nothing is ever lost.
- As a user, I want the AI to respond conversationally to my thoughts and shared resources, so I can think out loud and develop ideas.

### Organisation
- As a user, I want to create topic channels to group related conversations, so I can see the arc of my thinking on a subject.
- As a user, I want to move a conversation into a topic channel after the fact, so I don't need to decide upfront where things belong.
- As a user, I want to see a list of all my conversations (recent first), so I can return to previous thinking.

### Search & Retrieval
- As a user, I want to search across all conversations and captured resources using natural language, so I can find anything I've previously encountered or discussed.
- As a user, I want search results to show the relevant conversation context (not just a snippet), so I can re-enter the thinking I was doing at the time.

### Background Processing
- As a user, I want the system to process shared resources asynchronously, so the conversation flow isn't interrupted.
- As a user, I want to see processing status for resources being ingested, so I know the system is working.

### Cognitive Metadata
- As a user, I want my captures and conversations tagged with cognitive operations (exploring, synthesising, questioning, reacting, connecting, wondering, revisiting, explaining), so the knowledge base has rich metadata for future use.

## 7. User Flows

### Flow: First Launch
**Trigger:** User opens the app for the first time.
**Actor:** Guillaume.

1. **Scene 1: Clean slate** — A minimal, calm interface appears. A text input is centred. No clutter, no onboarding wizard. A subtle prompt suggests: "What's on your mind?" or "Paste a link, share a thought, or just start talking."
2. **Scene 2: First message** — User types a thought or pastes a URL. The AI responds conversationally. If a URL was shared, a subtle indicator shows it's being processed in the background.
3. **Resolution** — The user is in a conversation. They've captured something. No setup required.

**Edge cases:**
- Backend not running → Clear error: "Can't connect to Mindspace backend. Is it running?"
- No API key configured → Clear error with instructions on first message attempt.

---

### Flow: Daily Capture (Core Loop)
**Trigger:** User encounters something interesting or has a thought.
**Actor:** Guillaume.

1. **Scene 1: Quick entry** — User opens the app (or switches to the tab). The text box is immediately focused. They type or paste.
2. **Scene 2: Conversation unfolds** — For a URL: the AI acknowledges, asks what caught their attention, the resource processes in the background. For a thought: the AI engages — asks questions, makes connections to previous captures, or simply acknowledges depending on the context.
3. **Scene 3: Conversation continues or ends** — The user may continue the thread or leave. Either way, everything is captured and will be searchable.
4. **Resolution** — The thought, URL, or conversation is part of the knowledge base. No filing, no tagging, no friction.

**Edge cases:**
- URL fails to fetch → AI informs user: "I couldn't fetch that page — it might be behind a paywall or down. I've saved the URL itself."
- Very long content (e.g., full paper) → Background processing handles chunking; user isn't blocked.
- Duplicate URL → System detects and surfaces the previous conversation about it: "You shared this 2 weeks ago — here's what you said then."

---

### Flow: Search & Rediscovery
**Trigger:** User remembers encountering something but can't find it.
**Actor:** Guillaume.

1. **Scene 1: Search** — User accesses search (keyboard shortcut or UI element). Types a natural language query like "that article about distributed systems and team structure."
2. **Scene 2: Results** — Results show matched conversations and resources, ranked by relevance. Each result shows enough context to recognise it — the conversation snippet, the resource title, when it was discussed, and the topic channel if assigned.
3. **Scene 3: Re-entry** — User clicks a result and is taken to that point in the conversation, with full context above and below.
4. **Resolution** — The user found what they were looking for and can continue building on it.

**Edge cases:**
- No results → "Nothing matched. Try different terms, or browse your recent conversations."
- Ambiguous results → Multiple matches shown with enough context to distinguish.

---

### Flow: Organise into Topic Channel
**Trigger:** User realises a conversation belongs to a topic.
**Actor:** Guillaume.

1. **Scene 1: Categorise** — From within a conversation, user assigns it to an existing topic channel or creates a new one.
2. **Scene 2: Channel view** — The topic channel shows all associated conversations in chronological order, with a synthesis view of what's been discussed.
3. **Resolution** — The conversation is organised without having been interrupted during creation.

**Edge cases:**
- Conversation relevant to multiple topics → Allow assigning to multiple channels.
- Topic channel renamed or merged → Conversations maintain their associations.

## 8. Core Features

### Feature: Conversational Interface
**Priority:** Must-have (v1)

**Description:** The primary way to interact with Mindspace is through conversation. A text input where you can type thoughts, paste URLs, share ideas, and discuss them with an AI that captures everything. The AI responds conversationally — engaging with ideas, asking questions, acknowledging resources — while silently capturing and indexing everything discussed.

**Acceptance Criteria:**
- [ ] Given the app is open, when I type a message, then I receive a conversational AI response within 3 seconds
- [ ] Given I paste a URL in a message, then the system detects it, begins background extraction, and the AI acknowledges the resource
- [ ] Given I'm in a conversation, when I send multiple messages, then the full conversation history is maintained and scrollable
- [ ] Given a conversation exists, when I return to the app later, then I can continue the same conversation or start a new one
- [ ] Given I'm typing, when I press Enter, then the message sends (Shift+Enter for newline)

**Edge Cases:**
- Very long messages → Accept and process without truncation
- Rapid successive messages → Queue and process in order
- AI response streaming → Stream tokens as they arrive for responsiveness

---

### Feature: Conversation Management
**Priority:** Must-have (v1)

**Description:** Conversations are organised as distinct sessions (like Claude/ChatGPT). A sidebar or panel shows all conversations, most recent first. Conversations can be titled (auto-generated or manual) and assigned to topic channels for organisation.

**Acceptance Criteria:**
- [ ] Given the app is open, when I start typing in an empty state, then a new conversation is created
- [ ] Given conversations exist, when I open the conversation list, then they are shown with titles and timestamps, most recent first
- [ ] Given a conversation exists, when I click it, then the full conversation loads with history
- [ ] Given a conversation, when I assign it to a topic channel, then it appears in that channel's view
- [ ] Given no topic channel exists, when I assign a conversation, then I can create a new channel inline
- [ ] Given a conversation, when I want to categorise it, then I can assign it to multiple topic channels

**Edge Cases:**
- Conversation with no messages → Don't show in list
- Very old conversations → Still load fully and quickly
- Auto-title generation → Generate from first few messages; allow manual override

---

### Feature: Topic Channels
**Priority:** Must-have (v1)

**Description:** Topic channels are a way to categorise conversations by subject. Think of them like Slack channels or folders — they group related conversations so you can see the evolution of your thinking on a topic. Channels are created on demand, not upfront.

**Acceptance Criteria:**
- [ ] Given no channels exist, when I create one (from a conversation or from the channel list), then it appears in navigation
- [ ] Given a channel exists, when I open it, then I see all associated conversations chronologically
- [ ] Given a channel, when I view it, then I see an AI-generated summary of what's been discussed across all conversations in that channel
- [ ] Given a conversation, when I assign it to a channel, then it appears in the channel without leaving its position in the main conversation list

**Edge Cases:**
- Empty channel → Show with a prompt to add conversations
- Channel with many conversations → Paginate or virtual scroll
- Deleting a channel → Conversations remain, just unlinked from that channel

---

### Feature: Background Resource Processing
**Priority:** Must-have (v1)

**Description:** When a user shares a URL, YouTube link, or GitHub repo in conversation, the system automatically extracts and processes the content in the background. This includes fetching the page, extracting text (via trafilatura), fetching video transcripts, pulling repo metadata and READMEs, chunking, embedding, and indexing. The conversation isn't blocked — the AI can discuss the resource immediately based on available metadata, and deeper processing happens asynchronously.

**Acceptance Criteria:**
- [ ] Given I paste a URL, then the system fetches and extracts the page content within 30 seconds
- [ ] Given I paste a YouTube link, then the system fetches the transcript and processes it
- [ ] Given I paste a GitHub repo URL, then the system fetches repo metadata, README, and key info via GitHub API
- [ ] Given a resource is being processed, then a subtle status indicator shows progress (not blocking the conversation)
- [ ] Given processing completes, then the content is chunked, embedded, and searchable
- [ ] Given processing fails, then the user is informed and the raw URL is still saved

**Edge Cases:**
- Paywall/login-required pages → Save URL + whatever metadata is available; inform user
- Very large pages (>50k words) → Process successfully via chunking
- Rate-limited APIs → Queue and retry with backoff
- Duplicate URL → Detect and reference the previous capture + conversation

---

### Feature: Hybrid Search
**Priority:** Must-have (v1)

**Description:** Search across all conversations and captured resources using natural language. Uses hybrid retrieval (semantic embeddings + BM25 keyword search with Reciprocal Rank Fusion) to find relevant content. Results show conversation context, not just isolated snippets.

**Acceptance Criteria:**
- [ ] Given I enter a search query, then results appear within 2 seconds
- [ ] Given results exist, then they show: conversation title, relevant snippet with context, timestamp, topic channel (if any), and resource type
- [ ] Given I click a search result, then I'm taken to that point in the conversation with surrounding context
- [ ] Given a query matches both a conversation message and a processed resource, then both appear in results with clear distinction
- [ ] Given a query, then results are ranked by hybrid relevance (semantic + keyword fusion)

**Edge Cases:**
- No results → Helpful empty state: "Nothing matched — try different terms or browse recent conversations"
- Query matches many results → Show top 20, allow loading more
- Search within a specific topic channel → Filter results by channel

---

### Feature: Cognitive Operation Tagging
**Priority:** Must-have (v1)

**Description:** The system automatically tags captures and conversation segments with cognitive operations — the *type of thinking* happening. This creates rich metadata for future retrieval, filtering, and intelligence features. Operations include: exploring, synthesising, questioning, reacting, connecting, wondering, revisiting, explaining, compressing, expanding, reflecting.

**Acceptance Criteria:**
- [ ] Given a conversation message, then the system infers and tags the cognitive operation(s) involved
- [ ] Given tags are assigned, then they are stored as metadata on the message/capture
- [ ] Given the knowledge base, then content can be filtered or searched by cognitive operation
- [ ] Given tags are inferred by AI, then they are visible on messages/captures as subtle, non-intrusive labels

**Edge Cases:**
- Ambiguous cognitive operation → Assign multiple tags
- Simple messages ("thanks", "ok") → Tag as neutral or don't tag
- User explicitly states their mode ("I'm just thinking out loud") → Use as a strong signal

---

### Feature: Local Data Ownership
**Priority:** Must-have (v1)

**Description:** All data — conversations, captures, processed resources, embeddings — is stored locally. The backend proxies AI requests to Claude API, ensuring full control over conversation data. No data leaves the machine except API calls to Claude and content extraction services.

**Acceptance Criteria:**
- [ ] Given the app is running, then all conversation data is stored on the local filesystem
- [ ] Given an AI interaction, then the request goes through the local backend (not directly from browser to Claude API)
- [ ] Given the backend receives a conversation, then it stores the full request and response locally before/after proxying
- [ ] Given the app is stopped, then all data remains accessible on disk (no cloud dependency)

**Edge Cases:**
- Disk space running low → Warn the user; never silently fail to save
- Backend crashes mid-conversation → Buffer unsent messages in the frontend; retry on reconnect
- API key expired or invalid → Clear error message; conversations still saved locally

## 9. Pages / Scenes as Scenes

### Scene: Home
**Purpose:** Zero-friction entry point for capture and conversation.
**Entry points:** Opening the app; returning to the app.
**Key elements:**
- Large, centred text input (auto-focused)
- Subtle hint text ("What's on your mind?" / "Paste a link, share a thought...")
- Minimal chrome — no visible sidebars or menus until needed
- A way to reveal the conversation list and topic channels (icon, keyboard shortcut, or hover zone)
- Processing indicators for any background tasks

**Interactions:**
- Type and send a message → starts a new conversation
- Keyboard shortcut to open search
- Keyboard shortcut or click to reveal sidebar (conversations + channels)
- Click on a recent conversation notification/suggestion to continue it

**Emotional tone:** Calm, inviting, zero pressure. Like opening a blank page in a beautiful notebook.
**Exit points:** Into a conversation; into search; into sidebar navigation.

---

### Scene: Conversation
**Purpose:** The thinking space. Where ideas are discussed, resources shared, and thinking happens.
**Entry points:** Sending a first message from Home; clicking a conversation in the list; clicking a search result.
**Key elements:**
- Message history (user + AI, with timestamps)
- Text input at the bottom (always visible)
- Conversation title (auto-generated, editable)
- Subtle indicators for: processing resources, cognitive operation tags (if surfaced)
- Action to assign to topic channel
- Back/navigation to return to Home or sidebar

**Interactions:**
- Send messages (text, URLs, content)
- Continue conversation with full history as context
- Assign to topic channel
- Search within this conversation

**Emotional tone:** Focused, immersive, like a deep conversation with a smart friend. Not cluttered with tools or options.
**Exit points:** Back to Home; to another conversation; to search.

---

### Scene: Sidebar — Conversations & Channels
**Purpose:** Navigate between conversations and topic channels. Hidden by default to keep the interface clean.
**Entry points:** Keyboard shortcut; click/hover to reveal; hamburger icon.
**Key elements:**
- List of recent conversations (title, timestamp, preview)
- List of topic channels (name, conversation count)
- Quick search/filter within the sidebar
- "New conversation" action

**Interactions:**
- Click conversation → open it
- Click channel → see its conversations
- Create new channel
- Assign conversations to channels (via drag, context menu, or inline action)

**Emotional tone:** Organised but not overwhelming. Like a clean bookshelf, not a filing cabinet.
**Exit points:** Into any conversation; into any channel; close sidebar to return to current view.

---

### Scene: Topic Channel
**Purpose:** See the evolution of thinking on a subject across multiple conversations.
**Entry points:** Clicking a channel in the sidebar.
**Key elements:**
- Channel name and description
- List of conversations in the channel (chronological)
- AI-generated summary of themes discussed across the channel
- Resources captured within these conversations

**Interactions:**
- Open any conversation within the channel
- Add/remove conversations from the channel
- Edit channel name/description
- Search within channel

**Emotional tone:** Like looking at a research wall — seeing the arc of your exploration on a topic.
**Exit points:** Into any conversation; back to sidebar; to search.

---

### Scene: Search
**Purpose:** Find anything you've previously captured, discussed, or encountered.
**Entry points:** Keyboard shortcut (Cmd+K or similar); search icon.
**Key elements:**
- Search input (auto-focused)
- Results grouped by type (conversations, resources, captures)
- Each result shows: title/snippet, timestamp, topic channel, relevance indicator
- Filter options (by channel, by date range, by cognitive operation, by resource type)

**Interactions:**
- Type to search (results update as you type or on submit)
- Click result → navigate to that conversation at the relevant point
- Filter/facet results
- Keyboard navigation through results

**Emotional tone:** Fast, powerful, confident. Like you *know* you'll find it.
**Exit points:** Into any conversation from results; dismiss to return to previous view.

## 10. Edge Cases & Error Handling

| Scenario | Expected Behavior | User Communication |
|----------|-------------------|-------------------|
| Backend not running | Frontend shows connection error, buffers input | "Can't reach Mindspace backend — is it running?" |
| Claude API error (rate limit, outage) | Retry with backoff; save user message locally | "AI is temporarily unavailable. Your message is saved — I'll respond when I can." |
| URL extraction fails | Save raw URL; mark as unprocessed | "Couldn't extract content from that URL. I've saved the link." |
| YouTube transcript unavailable | Save video metadata; note transcript missing | "No transcript available for this video. I've saved the link and metadata." |
| Disk space critically low | Warn before it's a problem; never silently fail | "Storage is running low — consider freeing up space." |
| Very long conversation (>100 messages) | Virtual scrolling; maintain performance | No communication needed — it just works |
| Browser tab closed mid-conversation | Message saved before send; conversation preserved | On return: conversation is exactly where they left off |
| Duplicate URL shared | Detect and surface previous context | "You shared this on [date] — here's what you said then. Want to revisit?" |
| Empty state (new user, no data) | Welcoming first-use experience | Hint text guides first interaction |

## 11. Emotional Thesis

**Core feeling:** Mindspace should feel like thinking into a system that *thinks back* — not a tool you operate, but a space where your curiosity accumulates and compounds.

**Emotional principles:**

1. **Effortless capture** — The moment you feel friction, you stop capturing. Every interaction should feel lighter than opening a notes app. The app should feel like talking, not filing.

2. **Nothing is lost** — The confidence that everything you've shared, discussed, or thought about is safely captured and findable. No more "I read something about this but can't find it." Peace of mind.

3. **Curiosity, not productivity** — This is not a to-do list or a project tracker. It's a space for wondering, exploring, connecting, and going deep. The emotional register is intellectual excitement, not task completion anxiety.

4. **Intelligence that earns trust** — When the AI makes a connection or surfaces a pattern, it should feel genuinely insightful, not gimmicky. Better to surface nothing than to surface noise.

## 12. Design System Direction

### Typography
- Clean, readable, slightly warm. Not cold-tech, not playful — *thoughtful*.
- Clear hierarchy: conversation messages, AI responses, titles, metadata, timestamps.
- Monospace option for code/technical content shared in conversation.

### Color
- Calm, muted palette. Think: dark mode friendly, low visual noise.
- Subtle distinction between user messages and AI responses (not jarring color blocks).
- Functional colors for: processing indicators, search highlights, cognitive operation tags.
- High contrast for readability; nothing that strains the eyes in long sessions.

### Layout
- Desktop-primary (this is a local app used on a dev machine).
- Spacious by default — breathing room around messages, not cramped.
- Sidebar hidden by default, revealable. Content area is the star.
- Text input always anchored at the bottom of the viewport.

### Motion & Animation
- Subtle and purposeful. Message appear animations, smooth scrolling, gentle transitions.
- Processing indicators: subtle pulsing or progress, not spinners.
- No gratuitous animation. This is a thinking tool, not a social app.
- Respect `prefers-reduced-motion`.

### Voice & Tone
- The AI's voice: thoughtful, curious, direct. Not sycophantic, not robotic.
- Asks genuine questions, makes real observations.
- Comfortable with "I don't know" or "that's interesting but I'm not sure how it connects yet."
- System messages (errors, status): clear, concise, human. No tech jargon.

## 13. UX Principles

1. **Conversation-first** — Every feature should be accessible through conversation. If you have to leave the chat to do something, it's a design failure. The text input is the command line, the search bar, and the capture tool all at once.

2. **Progressive disclosure** — Start with just a text box. Reveal complexity (channels, search, filters, knowledge views) as the user needs it. Never overwhelm with options on first sight.

3. **Background intelligence** — Processing, tagging, embedding, connecting — all happen silently. The user sees the input (their message) and the output (AI response, search results). The machinery is invisible.

4. **Accumulation over organisation** — Don't force the user to organise upfront. Let things pile up. Organisation (channels, tags) is optional and retroactive. The system's search and AI are good enough that you can find things without folders.

5. **Respect the flow** — Never interrupt thinking with modals, confirmations, or mandatory decisions. Everything that can be deferred should be deferred. Everything that can be automatic should be automatic.

## 14. Accessibility Requirements

- Keyboard navigable: all core actions reachable without mouse
- Sufficient colour contrast (WCAG AA minimum)
- Screen reader compatible for core flows (conversation, search)
- `prefers-reduced-motion` respected
- Resizable text without layout breakage
- Focus management: text input auto-focused; focus returns predictably after actions

## 15. Functional Requirements

### Conversation Engine
- FR-001: The system shall maintain conversation sessions with full message history
- FR-002: The system shall stream AI responses token-by-token for perceived responsiveness
- FR-003: The system shall detect URLs in user messages and trigger background processing
- FR-004: The system shall auto-generate conversation titles from content
- FR-005: The system shall support markdown rendering in both user and AI messages

### Resource Processing
- FR-010: The system shall extract web page content using trafilatura (or equivalent)
- FR-011: The system shall extract YouTube video transcripts
- FR-012: The system shall fetch GitHub repo metadata and README via GitHub API
- FR-013: The system shall chunk extracted content (max 500 tokens, 50 token overlap)
- FR-014: The system shall embed chunks using OpenAI text-embedding-3-small (or configurable model)
- FR-015: The system shall detect duplicate URLs and surface previous captures
- FR-016: The system shall process resources asynchronously without blocking conversation

### Search & Retrieval
- FR-020: The system shall support hybrid search (semantic + BM25 with Reciprocal Rank Fusion)
- FR-021: The system shall search across conversations, captured resources, and processed content
- FR-022: The system shall return results with conversation context (not just isolated snippets)
- FR-023: The system shall support filtering by topic channel, date range, content type, and cognitive operation

### Data & Storage
- FR-030: The system shall store all data locally on the filesystem
- FR-031: The system shall proxy all AI API calls through the local backend
- FR-032: The system shall store raw conversation data as the source of truth
- FR-033: The system shall maintain a derived layer (embeddings, indexes) that is rebuildable from raw data
- FR-034: The system shall store full AI request/response pairs for conversation logging

### Cognitive Metadata
- FR-040: The system shall infer cognitive operations from conversation messages
- FR-041: The system shall store cognitive operation tags as metadata
- FR-042: The system shall support the following cognitive operations: exploring, synthesising, questioning, reacting, connecting, wondering, revisiting, explaining, compressing, expanding, reflecting

## 16. Non-Functional Requirements

### Performance
- Chat response latency: first token within 1 second of sending message (dependent on Claude API)
- Search results: within 2 seconds of query submission
- Background processing: URL extraction complete within 30 seconds; embedding within 60 seconds
- App load time: under 2 seconds

### Security
- No authentication required (single-user, local only)
- API keys stored in environment variables or `.env` file, never in frontend code
- No data transmitted to external services except: Claude API (conversation), OpenAI API (embeddings), content extraction (target URLs)
- All local data stored unencrypted on disk (acceptable for local-only single-user)

### Reliability
- Conversation data must never be lost — write-ahead logging or equivalent
- Backend crash recovery: restart without data loss
- Frontend resilience: buffer messages if backend is temporarily unavailable

### Scalability
- Support thousands of conversations and tens of thousands of captures
- ChromaDB and BM25 index performance at scale (currently validated at small scale)
- SQLite for conversation storage (structured, queryable, transactional)

## 17. Data Model

### Conversation
- `id` (ULID)
- `title` (string, auto-generated or manual)
- `created_at` (ISO timestamp)
- `updated_at` (ISO timestamp)
- `channel_ids` (list of channel IDs, can be empty)

### Message
- `id` (ULID)
- `conversation_id` (FK → Conversation)
- `role` (user | assistant | system)
- `content` (string, markdown)
- `created_at` (ISO timestamp)
- `cognitive_operations` (list of operation tags)
- `resource_ids` (list of Resource IDs extracted from this message)

### Resource (replaces "Capture" from CLI)
- `id` (ULID)
- `type` (url | video | repo | snippet)
- `source_url` (string, nullable)
- `raw_content` (extracted text, transcript, etc.)
- `metadata` (type-specific: title, author, word_count, stars, language, etc.)
- `processing_status` (pending | processing | completed | failed)
- `created_at` (ISO timestamp)
- `message_id` (FK → Message that introduced this resource)
- `conversation_id` (FK → Conversation)

### Channel
- `id` (ULID)
- `name` (string)
- `description` (string, nullable)
- `created_at` (ISO timestamp)

### Chunk (derived)
- `id` (format: `{resource_id}__chunk_{N}`)
- `resource_id` (FK → Resource)
- `text` (string)
- `embedding` (vector, stored in ChromaDB)
- `metadata` (type, cognitive_operations, channel_ids, created_at)

### ConversationChunk (derived — for embedding conversation content)
- `id` (format: `{conversation_id}__msg_{message_id}__chunk_{N}`)
- `conversation_id` (FK → Conversation)
- `message_id` (FK → Message)
- `text` (string)
- `embedding` (vector, stored in ChromaDB)
- `metadata` (role, cognitive_operations, channel_ids, created_at)

### Relationships
```
Conversation 1──* Message
Conversation *──* Channel (via channel_ids)
Message 1──* Resource
Resource 1──* Chunk (derived)
Message 1──* ConversationChunk (derived)
```

## 18. Technical Architecture

### Frontend
- Single-page application (React, Svelte, or similar — TBD)
- WebSocket or SSE for streaming AI responses
- Local state management; no external state services
- Markdown rendering for messages

### Backend
- Python (building on existing Mindspace codebase)
- FastAPI or similar for HTTP API + WebSocket support
- Proxies conversation to Claude API (Anthropic SDK)
- Manages background task queue for resource processing
- Serves the frontend as static files

### Storage
- **Conversations & messages:** SQLite database (structured, queryable, transactional)
- **Resources (raw):** JSON files on disk (maintaining the immutable raw capture philosophy)
- **Embeddings:** ChromaDB (persistent, local)
- **Keyword index:** BM25 corpus (JSON, rebuildable)
- **Derived metadata:** SQLite or JSON (rebuildable from raw)

### AI Integration
- **Conversation:** Claude API (via Anthropic Python SDK), proxied through backend
- **Embeddings:** OpenAI API (text-embedding-3-small), called from backend
- **Cognitive tagging:** Claude API (lightweight classification call per message, or batch)

### Background Processing
- Task queue (Python asyncio, Celery, or similar) for:
  - URL content extraction
  - Video transcript fetching
  - Embedding generation
  - Cognitive operation tagging
  - Auto-title generation

### API Design
- REST for CRUD operations (conversations, channels, resources)
- WebSocket for streaming chat responses
- Internal endpoints for search, processing status

## 19. Roadmap

### v1 — Foundation (MVP)
**Goal:** Replace the CLI. Make capture effortless and conversations persistent.

**Included:**
- Conversational interface with Claude AI
- Conversation sessions (create, continue, list)
- Topic channels (create, assign conversations)
- Background resource processing (URLs, GitHub repos, YouTube transcripts)
- Hybrid search across conversations and resources
- Cognitive operation tagging (AI-inferred, stored as metadata)
- Local storage with full data ownership
- Backend proxying all AI calls
- Clean, minimal UI with progressive disclosure

**Excluded (and why):**
- Knowledge graph visualization (needs more data to be meaningful)
- Automatic gap/blind spot detection (needs intelligence layer built first)
- Thinking modes (compression, expansion, reflection) (core conversation must work first)
- Proactive suggestions and pattern detection (v2+)
- Mobile/responsive design (desktop-only for now)

---

### v2 — Intelligence Layer
**Goal:** The system starts thinking *with* you, not just capturing for you.

| Item | Description | Priority |
|------|-------------|----------|
| Thinking modes | AI detects or user triggers compression/expansion/reflection/execution modes (Four Modes) | High |
| On-demand gap analysis | "What am I missing?" — analysis across the full corpus for blind spots, unexplored perspectives | High |
| Connection surfacing | AI proactively mentions connections to previous conversations/resources during chat | High |
| Knowledge views | Multiple ways to see the shape of your knowledge — graph, timeline, clusters, tag clouds | High |
| Channel summaries | AI-generated synthesis of themes/evolution within a topic channel | Medium |
| Conversation summaries | Distill long conversations into key insights, decisions, open questions | Medium |
| Concept extraction | Auto-extract key concepts, entities, themes from conversations and resources | Medium |
| Related content sidebar | Show vector-similar captures/conversations alongside current conversation | Medium |

### v3 — Proactive Intelligence
**Goal:** The system works for you in the background, surfacing what matters.

| Item | Description | Priority |
|------|-------------|----------|
| Pattern detection | Identify recurring themes, evolving interests, shifting perspectives across time | High |
| Weekly/periodic digests | "Here's what emerged in your thinking this week" — auto-generated reflections | High |
| Temporal reasoning | "Your thinking on X has evolved from A to B to C over 3 months" | Medium |
| Proactive connections | Push notifications: "You captured X today — it connects to Y from last month" | Medium |
| Question tracking | Surface unanswered questions that new captures might address | Medium |
| Reading/learning queue | Prioritised list of resources to revisit based on relevance to current thinking | Low |

### v4 — Deep Intelligence & Expansion
**Goal:** The system understands your thinking deeply enough to be a genuine intellectual partner.

| Item | Description | Priority |
|------|-------------|----------|
| Perspective diversity analysis | "You've only explored X from perspective A — here's perspective B, C" | High |
| Argument mapping | Visualise the structure of your reasoning on a topic | Medium |
| Cross-domain synthesis | "Your interest in X (domain A) connects to Y (domain B) in way Z" | Medium |
| Export & publish | Turn accumulated knowledge into drafts, blog posts, structured documents | Medium |
| Voice capture | Speak thoughts, auto-transcribed and processed | Medium |
| Browser extension | Capture from anywhere on the web with one click, feeds into Mindspace | Medium |
| Multi-model support | Use different AI models for different tasks (local models for tagging, Claude for conversation) | Low |
| API for external tools | Let other tools (Obsidian, Claude Code, etc.) read/write to Mindspace | Low |

### Future Considerations
- Mobile companion app (capture on the go)
- MCP server (expose Mindspace as a tool for other AI agents)
- Collaborative mode (share specific channels or conversations)
- Plugin system for custom processing pipelines

## 20. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude API costs grow with heavy usage | High | Medium | Monitor token usage; implement conversation context windowing; consider local models for classification tasks |
| Embedding costs (OpenAI) at scale | Medium | Low | Batch embeddings; consider local embedding models (e.g., sentence-transformers) as alternative |
| ChromaDB performance at scale (>100k chunks) | Medium | Medium | Monitor query times; evaluate alternatives (LanceDB, pgvector) if needed |
| Cognitive operation tagging accuracy | High | Low | Start with coarse categories; refine based on actual usage patterns; don't surface tags to user until confident |
| Background processing queue reliability | Medium | Medium | Implement retry logic, dead letter queue, and processing status visibility |
| Context window limits for long conversations | High | Medium | Implement smart context windowing — summarise older messages, keep recent + relevant |
| Building too much before validating the core loop | Medium | High | Ship v1 fast; use it daily; let real usage drive v2 priorities |
| YouTube transcript API changes/breaks | Medium | Low | Abstract behind an interface; support multiple extraction methods |
| Scope creep from the rich v2+ backlog | High | Medium | Treat this PRD as a living document; re-prioritise backlog quarterly based on actual usage |

## 21. Open Questions

- [ ] **Frontend framework choice** — React, Svelte, or something else? Decide based on speed of development and ecosystem.
- [ ] **Conversation context windowing** — How to handle long conversations that exceed Claude's context window? Summarisation? Sliding window? RAG over own conversation?
- [ ] **Cognitive operation taxonomy** — Is the current list (exploring, synthesising, questioning, reacting, connecting, wondering, revisiting, explaining, compressing, expanding, reflecting) the right set? Should it evolve based on usage?
- [ ] **Conversation embedding strategy** — Embed every message? Embed conversation summaries? Embed at the paragraph level? Need to balance search quality vs. embedding cost.
- [ ] **YouTube transcript method** — yt-dlp, YouTube API, or third-party service? Each has tradeoffs in reliability and legality.
- [ ] **Migration from CLI data** — Should existing CLI captures be importable into the new app? Likely yes, but needs a migration path.
- [ ] **How to handle the AI system prompt** — What context does the AI get about the user, their knowledge base, and the current conversation's cognitive operations? This is critical to the experience quality.
- [ ] **Channel auto-suggestion** — Should the AI suggest which channel a conversation belongs to? Or is this always user-driven?

## 22. Appendix

### A. Research & Inspiration

**Direct inspiration:**
- [raw-clauding-skills](https://github.com/lsnackerman/raw-clauding-skills) — Workflows for compound thinking with AI. Key insight: files are shared memory; verbatim capture preserves texture that summaries lose.
- [Four Modes (Tey Bannerman)](https://fourmodes.teybannerman.com/) — Compression, Expansion, Reflection, Execution. The AI skills gap is a thinking gap. Name the cognitive mode → the right interaction follows.

**Landscape analysis (selected):**
- **Mem 2.0** — "AI thought partner." Capture effortlessly, AI organises. Agentic chat that can modify your knowledge base. "Mem it and forget it."
- **Reor** — Local-first, auto-surfaces related notes via vector similarity. "Related Notes Sidebar" as automatic connection discovery.
- **NotebookLM** — Source-grounded AI. Transforms content into multiple formats (podcast, flashcards, mind maps). Strict source grounding prevents hallucination.
- **Daniel Miessler's PAI** — Personal AI infrastructure on Claude Code. 65+ skills, universal output capture, self-improving system.
- **Khoj** — Self-hostable AI second brain. Semantic search over your notes. Multi-channel access.
- **Mem0** — Memory-as-infrastructure for AI. Hybrid vector + graph. Tri-factor scoring: relevance x importance x recency.

### B. Cognitive Operations Taxonomy (v1)

| Operation | Description | Example |
|-----------|-------------|---------|
| Exploring | Open-ended investigation of a topic | "I've been looking into how distributed teams communicate..." |
| Synthesising | Combining multiple inputs into a coherent view | "So if I put together X, Y, and Z, the pattern is..." |
| Questioning | Asking questions, seeking understanding | "Why does this approach work better than...?" |
| Reacting | Responding to content with a stance | "I disagree with this because..." |
| Connecting | Linking two or more ideas explicitly | "This reminds me of what I read about X..." |
| Wondering | Open-ended curiosity, no specific question | "I wonder what would happen if..." |
| Revisiting | Returning to a previous idea with fresh perspective | "I was thinking about X again and now I think..." |
| Explaining | Articulating something to clarify understanding | "The way I understand it is..." |
| Compressing | Finding signal in noise, distilling | "The key takeaway from all this is..." |
| Expanding | Seeking new perspectives, breaking patterns | "What else could this mean? What am I not considering?" |
| Reflecting | Stress-testing reasoning, challenging assumptions | "But wait, what if my assumption about X is wrong?" |

### C. Existing Mindspace Architecture (for migration reference)

The current CLI system has:
- **Raw captures** in `data/raw/*.json` (immutable source of truth)
- **JSONL index** in `data/index.jsonl`
- **ChromaDB** vector store in `data/derived/chroma/`
- **BM25 index** in `data/derived/bm25_corpus.json`
- **Registry** in `data/derived/registry.json`

The web app should be able to import these existing captures as resources, maintaining backward compatibility with the data layer while evolving the interface and interaction model.

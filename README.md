## Movie Search → Session → Quality → Delivery module

This project now includes a safe, idempotent movie delivery flow with server-side verification/premium enforcement and content moderation.

### Required environment variables

Set these in your hosting environment:

- `ADMIN_LOG_CHAT_ID`: Telegram chat ID to receive admin logs (optional)
- `DELIVERY_CONCURRENCY_PER_USER`: Max parallel deliveries per user (default `1`)

Pyrogram and Mongo (if you wire DB adapter):

- `TG_API_ID`, `TG_API_HASH`, `TG_BOT_TOKEN`
- `MONGO_DSN`, `MONGO_DB`

### DB adapter contract (implement in `handlers/db_adapter.py`)

Implement the following async functions against MongoDB (TODOs are present in the file):

- `search_movies(query, page)` -> list of results
- `create_pending_session(session_obj)` -> session_id
- `get_pending_session(session_id)`
- `lock_session(session_id)` / `unlock_session(session_id)`
- `mark_session_processing(session_id)` / `mark_session_delivered(session_id, info)`
- `is_user_verified(user_id)` / `is_user_premium(user_id)`
- `get_file_record_by_selection(selection)` -> file metadata / telegram file id
- `store_delivery_log(entry)`

### Security & moderation

The moderation hook `moderate_file(file_meta)` blocks NSFW/illegal content using keyword heuristics and size/mime checks. Rejections are notified to the user and logged.

### Test plan

Simulate flows via Telegram UI:

1. Happy path: `/search avatar` → Select → Session → Quality → Request Download → should deliver once. Check admin logs for SEARCH, SESSION_CREATED, LOCK_ACQUIRED, DELIVERY_STARTED, DELIVERY_SUCCESS.
2. Unverified path: make `is_user_verified` return `False` for your user; attempt delivery; should block, session remains pending.
3. Premium gating: make `get_file_record_by_selection` return `premium_only=True`; with non-premium user, delivery blocked, message shown.
4. Double-click: press "Request Download" quickly multiple times; only one delivery should occur due to lock and state transitions.
5. Expired session: wait >10 minutes or reduce TTL and try; should show expired message and require re-search.

### Example commands

```
/search inception
```

Callback sequence (internal): `mv_sel:<id>:1` → `mv_src:<sid>:webdl` → `mv_q:<sid>:1080p` → `mv_go:<sid>`

https://t.me/spideycinemax_ai_bot

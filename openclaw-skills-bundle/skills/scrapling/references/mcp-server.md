# Scrapling MCP Server

The Scrapling MCP server exposes six web scraping tools over the MCP protocol. It supports CSS-selector-based content narrowing (reducing tokens by extracting only relevant elements before returning results) and three levels of scraping capability: plain HTTP, browser-rendered, and stealth (anti-bot bypass).

All tools return a `ResponseModel` with fields: `status` (int), `content` (list of strings), `url` (str).

## Tools

### `get` -- HTTP request (single URL)

Fast HTTP GET with browser fingerprint impersonation (TLS, headers). Suitable for static pages with no/low bot protection.

Key parameters include: `url`, `extraction_type`, `css_selector`, `main_content_only`, `impersonate`, `proxy`, `timeout`, `retries`, `headers`, `cookies`, `params`, and `follow_redirects`.

### `bulk_get` -- HTTP request (multiple URLs)

Async concurrent version of `get`. Same parameters except `url` is replaced by `urls`.

### `fetch` -- Browser fetch (single URL)

Opens a Chromium browser via Playwright to render JavaScript. Suitable for dynamic/SPA pages with no/low bot protection.

Important options include: `headless`, `proxy`, `timeout` (milliseconds), `wait`, `wait_selector`, `network_idle`, `disable_resources`, `real_chrome`, `cdp_url`, `extra_headers`, `useragent`, `cookies`, `timezone_id`, and `locale`.

### `bulk_fetch` -- Browser fetch (multiple URLs)

Concurrent browser version of `fetch`. Each URL opens in a separate browser tab.

### `stealthy_fetch` -- Stealth browser fetch (single URL)

Anti-bot bypass fetcher with fingerprint spoofing. Use this for sites with Cloudflare Turnstile/Interstitial or other strong protections.

Additional parameters include `solve_cloudflare`, `hide_canvas`, `block_webrtc`, `allow_webgl`, and `additional_args`.

### `bulk_stealthy_fetch` -- Stealth browser fetch (multiple URLs)

Concurrent stealth version. Same parameters as `stealthy_fetch` except `url` is replaced by `urls`.

## Tool selection guide

- Static page, no bot protection → `get`
- Multiple static pages → `bulk_get`
- JavaScript-rendered / SPA page → `fetch`
- Multiple JS-rendered pages → `bulk_fetch`
- Cloudflare or strong anti-bot protection → `stealthy_fetch`
- Multiple protected pages → `bulk_stealthy_fetch`

Start with `get`, escalate to `fetch` if JS is required, and escalate to `stealthy_fetch` only when blocked.

## Content extraction tips

- Use `css_selector` to narrow results before they reach the model.
- `main_content_only=true` strips nav/footer by restricting to `<body>`.
- `extraction_type="markdown"` is usually best for readability.
- If a `css_selector` matches multiple elements, all are returned in the `content` list.

## Setup

```bash
scrapling mcp
```

Or with Streamable HTTP transport:

```bash
scrapling mcp --http
scrapling mcp --http --host 127.0.0.1 --port 8000
```

Docker alternative:

```bash
docker pull pyd4vinci/scrapling
docker run -i --rm scrapling mcp
```

The MCP server name when registering with a client is `ScraplingServer`. The command is the path to the `scrapling` binary and the argument is `mcp`.

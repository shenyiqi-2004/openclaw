---
name: openclaw-send-media
description: Send images and other attachments through OpenClaw chat channels. Use when the user wants to send a picture, photo, screenshot, image URL, document, audio, or video to WhatsApp or another supported channel, especially when you need to turn a local file path or URL into an outbound message.
---

# OpenClaw Send Media

Use `openclaw message send --media` for outbound images and attachments.

## Workflow

1. Confirm the channel if it is not obvious. Default to `whatsapp` when the user is talking about their WhatsApp setup.
2. Confirm the destination before sending anything outward.
3. Resolve or verify the target if needed.
4. Send the media with an optional caption.

## Commands

Send an image with a caption:

```bash
openclaw message send \
  --channel whatsapp \
  --target +8618516772130 \
  --message "你好" \
  --media /absolute/path/to/image.jpg
```

Send an image without caption:

```bash
openclaw message send \
  --channel whatsapp \
  --target +8618516772130 \
  --media /absolute/path/to/image.jpg
```

Send by URL instead of local file:

```bash
openclaw message send \
  --channel whatsapp \
  --target +8618516772130 \
  --message "看这个" \
  --media https://example.com/image.jpg
```

Find the target first if the user gives a name instead of a phone number:

```bash
openclaw directory peers list --channel whatsapp --query "mom"
```

Check whether the channel supports media:

```bash
openclaw channels capabilities
```

## Notes

- `--media` accepts local paths and URLs.
- `--message` becomes the caption when the channel supports it.
- WhatsApp on this machine reports `media` support, so image sending is available.
- Prefer absolute file paths for local media.
- If the user only says "send this image", inspect the provided path first and verify the recipient before sending.
- Do not send anything outward without an explicit user instruction to send.

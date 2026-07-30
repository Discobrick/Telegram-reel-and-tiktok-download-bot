"""Self-check for caption building and chunking. Run: python3 test_caption.py"""
import os
import sys
import types

os.environ.setdefault('PREFERENCES_FILE', os.path.join(os.getcwd(), 'temp', 'preferences.json'))

# Stub the third-party imports so this runs without the runtime deps installed;
# nothing under test touches them
for name in ('telegram', 'telegram.ext', 'yt_dlp', 'requests'):
    sys.modules.setdefault(name, types.ModuleType(name))
for name, attrs in (('telegram', ('Update', 'ReactionTypeEmoji', 'BotCommand')),
                    ('telegram.ext', ('ApplicationBuilder', 'MessageHandler', 'filters', 'CommandHandler'))):
    for attr in attrs:
        setattr(sys.modules[name], attr, object)
if not hasattr(sys.modules['requests'], 'RequestException'):
    sys.modules['requests'].RequestException = Exception

import bot


def fake_update(username="alice"):
    return types.SimpleNamespace(effective_user=types.SimpleNamespace(username=username, first_name=None))


def chunk(text):
    """Mirror of the chunking branch in process_single_url."""
    if len(text) <= 1024:
        return text, []
    caption, remaining, chunks = text[:1021] + "...", text[1021:], []
    while remaining:
        if len(remaining) <= 1024:
            chunks.append(remaining)
            remaining = ""
        else:
            chunks.append(remaining[:1021] + "...")
            remaining = remaining[1021:]
    return caption, chunks


def demo():
    url = "https://x.com/a/status/1"
    update = fake_update()

    # Link is present and survives a description long enough to overflow
    info = {'title': 'T', 'description': 'x' * 5000, 'uploader': 'bob',
            'upload_date': '20240102', 'view_count': 5}
    caption, chunks = chunk(bot.format_video_caption(update, info, url))
    assert url in caption, "link must stay in the video caption, not spill into a chunk"
    assert len(caption) <= 1024
    assert all(len(c) <= 1024 for c in chunks)
    assert "*" not in caption, "markdown markers would render literally"

    # No link requested -> no link
    assert url not in bot.format_video_caption(update, info, None)

    # Short caption needs no chunks
    short, chunks = chunk(bot.format_video_caption(update, {'title': 'T'}, url))
    assert chunks == [] and short.endswith(url) is False and url in short

    # Nothing is lost by the split
    body = "y" * 3000
    caption, chunks = chunk(body)
    assert caption.rstrip('.') + "".join(c.rstrip('.') for c in chunks) == body

    print("ok")


if __name__ == "__main__":
    demo()

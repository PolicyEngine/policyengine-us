# Captured sources for source-conflict register entries

Text captures of official sources (statutes, regulations, forms, instructions) that
entries in the shared source-conflict register cite under `pending_texts`, because
the Axiom corpus does not hold them yet. Each entry pins its file by this
repository, a commit and the file's sha256; rulespec-us's `verify` checks that each
excerpt appears verbatim in the capture. Each `.txt` file starts with the source URL
and how the text was extracted. `.html` files are the official page as fetched.

When a site serves bot-check scripts, capture the page as pandoc text and include
a `Source:` URL line and an extraction line. This removes scripts that can expose
the fetching machine's address or visitor tokens.

The privacy check rejects bot-manager markers and base64 tokens whose entire
decoded value matches `UUID$IPv4`. It decodes each run of 59 to 70 letters and
digits, with up to two `=` of padding, that has no letter or digit on either side
and no further `=` after it. It scans the raw bytes and the bytes after one round
of percent-decoding, so it finds tokens in quotes, query strings, URL paths,
JSON-escaped and percent-encoded URLs, and at either end of a line. It misses
IPv6 addresses, payloads with extra decoded bytes, and tokens joined to other
letters or digits, as after a `/` escape or in a URL percent-encoded twice.
Inspect extracted text for visitor data before committing it.

Do not edit a capture after an entry pins it: add a new file instead, and move the
entry's snapshot to it.

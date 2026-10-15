# Ticket — R1 public reference research retry

## Scope and retry protocol

This is the explicitly authorized same-native-subagent-protocol replacement role after researcher tools were unavailable. The bounded retry was conducted directly through ordinary public-source access, without changing runtime/profile, agent CLI/foreground/external fallback, installing packages, using an API/model, or uploading local data. No R1 contract/freeze, source/artwork, vendor files, prior evidence, or sealed material was changed/read. Public-source target: non-AI photograph or open drawing showing clothed upper torso, clear shoulder/bent-arm shape, and hand visibly contacting a cup/simple prop; exact collar is not required. Vendor MIT code-learning remains the main lane; a public image would be posture-only reference. `image.jpg` remains the overall project target. No external asset is cleared for output reuse.

## Result: BLOCKED — no source candidates inspected

Two ordinary access paths to the public Wikimedia Commons API were actually attempted, both failed before returning content:

1. Python `urllib.request.urlopen` to `https://commons.wikimedia.org/w/api.php?action=query&format=json&meta=siteinfo`, timeout 15s: `URLError <urlopen error _ssl.c:983: The handshake operation timed out>`.
2. `curl` to the Commons API generator/search endpoint for bitmap cup portrait hand, with 10s connect timeout and 45s max time: exit 28, `SSL connection timeout`; no response headers/body or JSON file was produced.

With neither route returning source pages, metadata, or image bytes, zero candidates could be independently evaluated. No search snippet was treated as evidence. No candidate was downloaded, visually inspected, hashed, or cropped. Consequently there is no selected source, origin author, license/terms URL, image URL, or observed pose/crop; all remain unverified. This is a network-access block, not evidence that no suitable public reference exists and not a license clearance. Stopped within the permitted bounded attempts; did not install or route around network access.

## Preservation and acceptance boundary

Existing staged/dirty work was preserved; no staging, cleanup, commit, source changes, artwork changes, or edits to the task freeze were made. Earlier task-freeze vendor scene is not asserted to be a public-photo alternative or to have changed legal status. The sealed holdout was not opened. This ticket records only this research retry and its observed failure.

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, mkdtemp, rm, stat, symlink, access } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { createAttemptState, createFetchObserver, validateBindings, wrapCopilotProvider, writeReceipt } from '../delivery-evidence-core.mjs';

const png = await readFile('.scratch/29-image-delivery-evidence/evidence/control/synthetic-control.png');
const sha = (v) => createHash('sha256').update(v).digest('hex');
const jsonRequest = (value, signal) => new Request('https://api.individual.githubcopilot.com/responses?ignored=private', {
  method: 'POST', headers: { 'content-type': 'application/json', authorization: 'Bearer NEVER_LOG_THIS' },
  body: JSON.stringify(value), signal,
});
const withImage = (data = png.toString('base64')) => ({ model: 'safe-model', input: [{ role: 'user', content: [{ type: 'input_image', image_url: `data:image/png;base64,${data}` }] }] });
function binding(outputPath) {
  return { schema: 'learn-draw-image-evidence/1', attemptId: '00000000-0000-4000-8000-000000000001', expectedSha256: sha(png), expectedMime: 'image/png', expectedLength: png.length, provider: 'github-copilot', api: 'openai-responses', model: 'safe-model', runId: 'run-secret-id', sessionId: 'session-secret-id', outputPath };
}
const badPath = path.resolve('.scratch/29-image-delivery-evidence/evidence/test-receipt.json');

test('bindings are strict and reject invalid or foreign model identity', () => {
  const b = binding(badPath);
  assert.equal(validateBindings(b, { expectedSha256: b.expectedSha256, attemptId: b.attemptId }).model, 'safe-model');
  assert.throws(() => validateBindings({ ...b, expectedSha256: '0'.repeat(64) }, { expectedSha256: b.expectedSha256, attemptId: b.attemptId }));
  assert.throws(() => validateBindings({ ...b, schema: 'foreign/1' }, { expectedSha256: b.expectedSha256, attemptId: b.attemptId }));
  assert.throws(() => validateBindings({ ...b, outputPath: '/tmp/out.json' }, { expectedSha256: b.expectedSha256, attemptId: b.attemptId }));
});

test('allows bounded setup and tool-read requests without receipt, then requires the trusted image phase', async () => {
  const state = createAttemptState(); let calls = 0;
  const obs = createFetchObserver({ binding: binding(badPath), attemptState: state, fetchImpl: async () => { calls++; return new Response('{}', { status: 200 }); } });
  await obs.fetch(jsonRequest({ model: 'safe-model', input: [{ role: 'user', content: [{ type: 'input_text', text: 'setup' }] }] }));
  assert.equal(calls, 1); assert.equal(obs.count, 0);
  await obs.fetch(jsonRequest({ model: 'safe-model', input: [{ role: 'user', content: [{ type: 'input_text', text: 'setup 2' }] }] }));
  await obs.fetch(jsonRequest({ model: 'safe-model', input: [{ role: 'user', content: [{ type: 'input_text', text: 'setup 3' }] }] }));
  await assert.rejects(obs.fetch(jsonRequest({ model: 'safe-model', input: [{ role: 'user', content: [{ type: 'input_text', text: 'setup over limit' }] }] })));
  assert.equal(calls, 3);
  state.phase = 'image-intended';
  await assert.rejects(obs.fetch(jsonRequest({ model: 'safe-model', input: [{ role: 'user', content: [{ type: 'input_text', text: 'stripped after image tool result' }] }] })));
  assert.equal(calls, 3);
  await assert.rejects(obs.fetch(jsonRequest(withImage()))); assert.equal(calls, 3);
  const dir = await mkdtemp(path.join(tmpdir(), 'ex29-sequence-'));
  const output = path.resolve('.scratch/29-image-delivery-evidence/evidence', `${path.basename(dir)}.json`);
  const validState = createAttemptState(); let setupCalls = 0;
  const valid = createFetchObserver({ binding: binding(output), attemptState: validState, fetchImpl: async () => { setupCalls++; return new Response('{}', { status: 200, headers: { 'content-type': 'application/json' } }); } });
  try {
    await valid.fetch(jsonRequest({ model: 'safe-model', input: [{ role: 'user', content: [{ type: 'input_text', text: 'read tool request' }] }] }));
    validState.phase = 'image-intended';
    await valid.fetch(jsonRequest(withImage())); assert.equal(setupCalls, 2); assert.equal(valid.count, 1);
    const receipt = await valid.complete('resp_sequence'); assert.equal(receipt.images[0].sha256, sha(png));
  } finally { await rm(output, { force: true }); await rm(dir, { recursive: true, force: true }); }
});

test('serializes exact body to fake fetch and writes linked private receipt mode 0600', async () => {
  const dir = await mkdtemp(path.join(tmpdir(), 'ex29-')); const output = path.resolve('.scratch/29-image-delivery-evidence/evidence', `${path.basename(dir)}.json`);
  const b = binding(output); const body = JSON.stringify(withImage()); const original = jsonRequest(JSON.parse(body)); let forwarded;
  try {
    const obs = createFetchObserver({ binding: b, fetchImpl: async (req) => { forwarded = await req.text(); return new Response('{}', { status: 200, headers: { 'content-type': 'text/event-stream', 'x-request-id': 'PRIVATE-REQUEST-ID' } }); } });
    const response = await obs.fetch(original); assert.equal(response.status, 200); assert.equal(forwarded, body);
    const receipt = await obs.complete('resp_privateRaw');
    assert.equal(receipt.images[0].sha256, sha(png)); assert.equal(receipt.httpStatus, 200);
    assert.equal(receipt.requestIdHash, sha('PRIVATE-REQUEST-ID')); assert.equal(receipt.responseIdHash, sha('resp_privateRaw'));
    assert.equal((await stat(output)).mode & 0o777, 0o600);
    const stored = await readFile(output, 'utf8');
    for (const secret of ['NEVER_LOG_THIS', 'PRIVATE-REQUEST-ID', 'resp_privateRaw', 'run-secret-id', 'session-secret-id', body, 'image_url']) assert.equal(stored.includes(secret), false, secret);
    await assert.rejects(obs.fetch(jsonRequest(withImage())));
  } finally { await rm(output, { force: true }); await rm(dir, { recursive: true, force: true }); }
});

test('child receipt binds actual session and attempt without requiring parent run ID', async () => {
  const sessionId = 'actual-session-from-context';
  const observer = createFetchObserver({ binding: binding(badPath), getRuntimeIds: () => ({ sessionId }), fetchImpl: async () => new Response('{}', { status: 200 }) });
  await observer.fetch(jsonRequest(withImage()));
  const receipt = await observer.complete('resp_valid');
  assert.equal(receipt.sessionIdHash, sha(sessionId));
  assert.equal(receipt.attemptUUID, binding(badPath).attemptId);
  assert.equal(Object.hasOwn(receipt, 'runIdHash'), false);
  await rm(badPath, { force: true });
});

test('stripped, malformed, unsupported, mismatched, wrong-count and unexpected images reject before network', async () => {
  for (const payload of [
    { input: [{ content: [{ type: 'text', text: 'no image' }] }] },
    { input: [{ content: [{ type: 'input_image', image_url: 'data:image/jpeg;base64,AA==' }] }] },
    { input: [{ content: [{ type: 'input_image', image_url: 'https://example.invalid/image.png' }] }] },
    { input: [{ content: [{ type: 'input_image', image_url: 'data:image/png;base64,%%%bad' }] }] },
    { input: [{ content: [{ type: 'input_image', image_url: `data:image/png;base64,${Buffer.from('wrong').toString('base64')}` }] }] },
    { input: [{ content: [{ type: 'input_image', image_url: `data:image/png;base64,${png.toString('base64')}` }, { type: 'input_image', image_url: `data:image/png;base64,${png.toString('base64')}` }] }] },
  ]) {
    let calls = 0; const obs = createFetchObserver({ binding: binding(badPath), fetchImpl: async () => { calls++; return new Response(); } });
    await assert.rejects(obs.fetch(jsonRequest(payload))); assert.equal(calls, 0);
  }
});

test('rejects second attempt, non-2xx, missing response ID, unapproved endpoint and cancellation', async () => {
  const b = binding(badPath); let n = 0;
  const obs = createFetchObserver({ binding: b, fetchImpl: async () => { n++; return new Response('', { status: 200 }); } });
  await obs.fetch(jsonRequest(withImage())); await assert.rejects(obs.fetch(jsonRequest(withImage()))); assert.equal(n, 1);
  const failed = createFetchObserver({ binding: b, fetchImpl: async () => new Response('', { status: 503 }) });
  await assert.rejects(failed.fetch(jsonRequest(withImage())));
  const noId = createFetchObserver({ binding: b, fetchImpl: async () => new Response('', { status: 200 }) });
  await noId.fetch(jsonRequest(withImage())); await assert.rejects(noId.complete(undefined));
  await assert.rejects(noId.fetch(new Request('https://example.invalid/responses', { method: 'POST', body: JSON.stringify(withImage()) })));
  const controller = new AbortController(); controller.abort(); const cancelled = createFetchObserver({ binding: b, fetchImpl: async () => { throw Error('should not reach fetch'); } });
  await assert.rejects(cancelled.fetch(jsonRequest(withImage(), controller.signal)));
});

test('provider-wide retry/reentry cannot forward a second image-bearing request', async () => {
  let forwarded = 0;
  const native = { id: 'github-copilot', auth: {}, stream: async (_m, _c, o) => o.fetch(jsonRequest(withImage())), streamSimple: async (_m, _c, o) => o.fetch(jsonRequest(withImage())) };
  const state = createAttemptState(); state.phase = 'image-intended';
  const provider = wrapCopilotProvider(native, binding(badPath), state);
  const model = { provider: 'github-copilot', api: 'openai-responses', id: 'safe-model' };
  const options = { fetch: async () => { forwarded++; return new Response('', { status: 200 }); } };
  await provider.stream(model, {}, options);
  await assert.rejects(provider.stream(model, {}, options));
  assert.equal(forwarded, 1);
});

test('receipt output refuses symlinked parent paths before creating outside files', async () => {
  const outside = await mkdtemp(path.join(tmpdir(), 'ex29-outside-'));
  const linkPath = path.resolve('.scratch/29-image-delivery-evidence/evidence/symlink-test');
  try {
    await symlink(outside, linkPath);
    await assert.rejects(writeReceipt(path.join(linkPath, 'escaped.json'), { schema: 'pi-image-delivery/v1' }));
    await assert.rejects(access(path.join(outside, 'escaped.json')));
  } finally { await rm(linkPath, { force: true }); await rm(outside, { recursive: true, force: true }); }
});

test('provider wrapper preserves options and callbacks while pinning one try and rejecting foreign model', async () => {
  let seen; let outer = 0;
  const native = { id: 'github-copilot', stream: (m, c, o) => { seen = o; return 'stream'; }, streamSimple: (m, c, o) => { seen = o; return 'simple'; }, auth: { marker: true } };
  const provider = wrapCopilotProvider(native, binding(badPath)); const callback = async () => { outer++; };
  const signal = new AbortController().signal; const marker = {};
  assert.equal(provider.auth, native.auth);
  assert.equal(provider.stream({ provider: 'github-copilot', api: 'openai-responses', id: 'safe-model' }, {}, { signal, marker, onProviderStreamEvent: callback, maxRetries: 8 }), 'stream');
  assert.equal(seen.signal, signal); assert.equal(seen.marker, marker); assert.equal(seen.maxRetries, 0); assert.equal(typeof seen.fetch, 'function');
  await seen.onProviderStreamEvent({ type: 'response.output_text.delta', delta: 'x' }, {}); assert.equal(outer, 1);
  assert.throws(() => provider.stream({ provider: 'other', api: 'openai-responses', id: 'safe-model' }, {}, {}));
  assert.throws(() => provider.streamSimple({ provider: 'github-copilot', api: 'openai-completions', id: 'safe-model' }, {}, {}));
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { acquireAndCorrelateCompletedRun, acquireFromSessionManagerForTest, correlateCompletedRunForTest } from '../parent-correlation.mjs';

const sha = (v) => createHash('sha256').update(v).digest('hex');
const attemptUUID = '00000000-0000-4000-8000-000000000001';
const sessionId = 'supported-actual-session-identity';
const imageSha256 = '2'.repeat(64);
const sessionArtifactRef = '/private/raw/session-artifact-ref.jsonl';
const revisionPins = { deliveryEvidenceCore: 'a'.repeat(64), deliveryEvidenceExtension: 'b'.repeat(64) };
const receipt = (id = sessionId) => Buffer.from(JSON.stringify({
  schema: 'pi-image-delivery/v1', attemptUUID, sessionIdHash: sha(id), provider: 'github-copilot',
  api: 'openai-responses', model: 'gpt-6-luna', imageCount: 1,
  images: [{ sha256: imageSha256 }], responseIdHash: '3'.repeat(64), fetchInvoked: true, httpStatus: 200,
}));
const args = (overrides = {}) => ({
  completion: { status: 'completed', runId: 'actual-run-from-native-api', sessionArtifactRef }, receiptBytes: receipt(),
  actualSessionId: sessionId, sessionArtifactRef,
  expected: { attemptUUID, imageSha256, receiptSHA256: sha(receipt()), model: 'gpt-6-luna', revisionPins }, ...overrides,
});

test('correlates actual completed API run and emits only hashes of raw IDs and artifact reference', () => {
  const result = correlateCompletedRunForTest(args());
  const encoded = JSON.stringify(result);
  assert.equal(result.actualRunIdHash, sha('actual-run-from-native-api'));
  assert.equal(result.sessionIdHash, sha(sessionId));
  assert.equal(result.attemptUUID, attemptUUID);
  assert.equal(result.receiptSHA256, sha(receipt()));
  assert.equal(result.sessionArtifactRefSha256, sha(sessionArtifactRef));
  for (const secret of [sessionArtifactRef, sessionId, 'actual-run-from-native-api']) assert.equal(encoded.includes(secret), false);
  assert.equal(Object.hasOwn(result, 'sessionArtifactRef'), false);
  assert.equal(Object.hasOwn(result, 'runId'), false);
});

test('rejects identity, receipt, completion, and binding mismatches', () => {
  assert.throws(() => correlateCompletedRunForTest(args({ expected: { ...args().expected, attemptUUID: '00000000-0000-4000-8000-000000000002' } })));
  assert.throws(() => correlateCompletedRunForTest(args({ actualSessionId: 'different-session' })));
  assert.throws(() => correlateCompletedRunForTest(args({ receiptBytes: Buffer.from('not receipt') })));
  assert.throws(() => correlateCompletedRunForTest(args({ completion: { status: 'failed', runId: 'actual-run-from-native-api' } })));
  assert.throws(() => correlateCompletedRunForTest(args({ sessionArtifactRef: '' })));
  assert.throws(() => correlateCompletedRunForTest(args({ completion: { ...args().completion, sessionArtifactRef: '/different/session.jsonl' } })));
  assert.throws(() => correlateCompletedRunForTest(args({ expected: { ...args().expected, receiptSHA256: '5'.repeat(64) } })));
  const changed = JSON.parse(receipt().toString()); changed.images[0].sha256 = '4'.repeat(64);
  const alteredBytes = Buffer.from(JSON.stringify(changed));
  assert.throws(() => correlateCompletedRunForTest(args({ receiptBytes: alteredBytes, expected: { ...args().expected, receiptSHA256: sha(alteredBytes) } })));
});

test('rejects unknown revision pins and malformed pin values or containers', () => {
  for (const pins of [
    { ...revisionPins, source: 'd'.repeat(64) },
    { ...revisionPins, deliveryEvidenceCore: 123 },
    { ...revisionPins, deliveryEvidenceCore: 'abc123' },
    [], null,
  ]) assert.throws(() => correlateCompletedRunForTest(args({ expected: { ...args().expected, revisionPins: pins } })));
});

test('test-only acquisition seam requires the exact opened artifact and actual session ID', () => {
  const completion = args().completion;
  const fakeSessionManager = { getSessionFile: () => sessionArtifactRef, getSessionId: () => sessionId };
  const result = acquireFromSessionManagerForTest({ completion, receiptBytes: receipt(), expected: args().expected, sessionManager: fakeSessionManager });
  assert.equal(result.sessionIdHash, sha(sessionId));
  assert.throws(() => acquireFromSessionManagerForTest({ completion, receiptBytes: receipt(), expected: args().expected,
    sessionManager: { ...fakeSessionManager, getSessionFile: () => '/different/session.jsonl' } }));
  assert.throws(() => acquireFromSessionManagerForTest({ completion, receiptBytes: receipt(), expected: args().expected,
    sessionManager: { getSessionFile: () => sessionArtifactRef, getSessionId: () => '' } }));
});

test('production acquisition opens the native completion artifact via SessionManager and fails closed', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'pi-session-acquisition-'));
  try {
    const actualSessionId = '00000000-0000-4000-8000-000000000099';
    const artifact = join(dir, 'synthetic-session.jsonl');
    writeFileSync(artifact, `${JSON.stringify({ type: 'session', version: 3, id: actualSessionId, timestamp: '2026-01-01T00:00:00.000Z', cwd: dir })}\n`);
    const expected = { ...args().expected, receiptSHA256: sha(receipt(actualSessionId)), revisionPins };
    const completion = { status: 'completed', runId: 'synthetic-native-run', sessionArtifactRef: artifact };
    const result = await acquireAndCorrelateCompletedRun({ completion, receiptBytes: receipt(actualSessionId), expected });
    assert.equal(result.sessionIdHash, sha(actualSessionId));
    assert.equal(result.sessionArtifactRefSha256, sha(artifact));
    assert.equal(JSON.stringify(result).includes(artifact), false);
    await assert.rejects(acquireAndCorrelateCompletedRun({ completion: { ...completion, sessionArtifactRef: join(dir, 'absent.jsonl') }, receiptBytes: receipt(), expected }));
    await assert.rejects(acquireAndCorrelateCompletedRun({ completion: { status: 'completed', runId: 'x' }, receiptBytes: receipt(), expected }));
    await assert.rejects(acquireAndCorrelateCompletedRun({ completion: { ...completion, sessionArtifactRef: artifact }, receiptBytes: receipt('wrong-id'), expected }));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

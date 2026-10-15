import { createHash } from 'node:crypto';
import { homedir } from 'node:os';
import { pathToFileURL } from 'node:url';

const hash = (value) => createHash('sha256').update(value).digest('hex');
const reject = () => { throw new Error('parent correlation rejected'); };
const isHash = (value) => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const isUUID = (value) => typeof value === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value);
const PIN_KEYS = new Set(['deliveryEvidenceCore', 'deliveryEvidenceExtension']);

function validatePins(pins) {
  if (!pins || typeof pins !== 'object' || Array.isArray(pins)) reject();
  const keys = Object.keys(pins);
  if (keys.length !== PIN_KEYS.size || keys.some((key) => !PIN_KEYS.has(key)) ||
      keys.some((key) => !isHash(pins[key]))) reject();
}

// Pure core accepts a test-supplied identity. Production callers must use
// acquireAndCorrelateCompletedRun below, which obtains identity from the native SDK.
export function correlateCompletedRunForTest({ completion, receiptBytes, actualSessionId, sessionArtifactRef, expected }) {
  if (!completion || completion.status !== 'completed' || typeof completion.runId !== 'string' || !completion.runId ||
      completion.sessionArtifactRef !== sessionArtifactRef || typeof actualSessionId !== 'string' || !actualSessionId ||
      typeof sessionArtifactRef !== 'string' || !sessionArtifactRef || !Buffer.isBuffer(receiptBytes) || !expected ||
      !isUUID(expected.attemptUUID) || !isHash(expected.imageSha256) || !isHash(expected.receiptSHA256) ||
      typeof expected.model !== 'string' || !expected.model || hash(receiptBytes) !== expected.receiptSHA256) reject();
  validatePins(expected.revisionPins);
  let receipt;
  try { receipt = JSON.parse(receiptBytes.toString('utf8')); } catch { reject(); }
  if (!receipt || receipt.schema !== 'pi-image-delivery/v1' || receipt.attemptUUID !== expected.attemptUUID ||
      receipt.sessionIdHash !== hash(actualSessionId) || receipt.provider !== 'github-copilot' ||
      receipt.api !== 'openai-responses' || receipt.model !== expected.model || receipt.imageCount !== 1 ||
      !Array.isArray(receipt.images) || receipt.images.length !== 1 || receipt.images[0].sha256 !== expected.imageSha256 ||
      !isHash(receipt.responseIdHash) || !receipt.fetchInvoked || receipt.httpStatus < 200 || receipt.httpStatus >= 300) reject();
  return Object.freeze({
    schema: 'learn-draw-parent-correlation/1',
    actualRunIdHash: hash(completion.runId),
    sessionIdHash: hash(actualSessionId),
    attemptUUID: expected.attemptUUID,
    receiptSHA256: hash(receiptBytes),
    model: expected.model,
    sessionArtifactRefSha256: hash(sessionArtifactRef),
    revisionPins: Object.freeze({ ...expected.revisionPins }),
  });
}

function correlateFromOpenedSession({ completion, receiptBytes, expected, sessionManager }) {
  if (!sessionManager || typeof sessionManager.getSessionId !== 'function' ||
      typeof sessionManager.getSessionFile !== 'function' ||
      sessionManager.getSessionFile() !== completion.sessionArtifactRef) reject();
  const actualSessionId = sessionManager.getSessionId();
  return correlateCompletedRunForTest({
    completion, receiptBytes, actualSessionId,
    sessionArtifactRef: completion.sessionArtifactRef, expected,
  });
}

// Explicitly test-only seam; production entry does not accept a claimed session identity.
export function acquireFromSessionManagerForTest({ completion, receiptBytes, expected, sessionManager }) {
  if (!completion || completion.status !== 'completed' || typeof completion.sessionArtifactRef !== 'string' || !completion.sessionArtifactRef) reject();
  return correlateFromOpenedSession({ completion, receiptBytes, expected, sessionManager });
}

// Native parent entry point: only the native completion's artifact reference is opened;
// session content is never read, serialized, or logged. Errors are deliberately generic.
export async function acquireAndCorrelateCompletedRun({ completion, receiptBytes, expected }) {
  if (!completion || completion.status !== 'completed' || typeof completion.sessionArtifactRef !== 'string' || !completion.sessionArtifactRef) reject();
  try {
    const sdkEntry = pathToFileURL(`${homedir()}/.pi/agent/npm/node_modules/@earendil-works/pi-coding-agent/dist/index.js`).href;
    const { SessionManager } = await import(sdkEntry);
    const sessionManager = SessionManager.open(completion.sessionArtifactRef);
    return correlateFromOpenedSession({ completion, receiptBytes, expected, sessionManager });
  } catch {
    reject();
  }
}

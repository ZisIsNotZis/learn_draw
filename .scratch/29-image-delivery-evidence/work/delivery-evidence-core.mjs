import { createHash, randomUUID } from 'node:crypto';
import { mkdir, open, link, unlink, lstat } from 'node:fs/promises';
import path from 'node:path';

const sha = (b) => createHash('sha256').update(b).digest('hex');
const fail = () => { throw new Error('image-delivery evidence rejected'); };
const allowedOrigins = new Set(['https://api.individual.githubcopilot.com']);

export function validateBindings(raw, expected) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw) || raw.schema !== 'learn-draw-image-evidence/1' ||
      raw.expectedSha256 !== expected.expectedSha256 || !/^[a-f0-9]{64}$/.test(raw.expectedSha256) ||
      raw.expectedMime !== (expected.expectedMime ?? 'image/png') || !Number.isSafeInteger(raw.expectedLength) || raw.expectedLength !== (expected.expectedLength ?? raw.expectedLength) ||
      raw.attemptId !== expected.attemptId || !/^[0-9a-f-]{36}$/i.test(raw.attemptId) ||
      raw.provider !== (expected.provider ?? 'github-copilot') || raw.api !== (expected.api ?? 'openai-responses') || typeof raw.model !== 'string' || !raw.model ||
      raw.model !== (expected.model ?? raw.model) ||
      typeof raw.outputPath !== 'string' || !path.isAbsolute(raw.outputPath) ||
      !path.resolve(raw.outputPath).startsWith(`${path.resolve('.scratch/29-image-delivery-evidence/evidence')}${path.sep}`)) fail();
  return Object.freeze({ ...raw });
}

function sanitizedContentType(value) {
  const match = /^(application\/json|text\/event-stream)(?:\s*;\s*charset=(?:utf-8|utf8))?$/i.exec(value?.trim() ?? '');
  return match ? match[1].toLowerCase() : 'other';
}

function endpoint(url) {
  let u;
  try { u = new URL(url); } catch { fail(); }
  if (!allowedOrigins.has(u.origin) || u.pathname !== '/responses' || u.username || u.password) fail();
  return `${u.origin}${u.pathname}`;
}

export async function inspectRequest(request, binding, phase, setupRequests) {
  if (!(request instanceof Request) || setupRequests >= 3 || phase === 'blocked') fail();
  const safeEndpoint = endpoint(request.url);
  const ct = request.headers.get('content-type');
  if (!ct?.toLowerCase().startsWith('application/json')) fail();
  let payload;
  try { payload = await request.clone().json(); } catch { fail(); }
  const images = [];
  if (request.method !== 'POST' || payload.model !== binding.model) fail();
  const visit = (v) => {
    if (!v || typeof v !== 'object') return;
    if (Array.isArray(v)) { for (const item of v) visit(item); return; }
    if (typeof v.type === 'string' && v.type.includes('image') && v.type !== 'input_image') fail();
    if (Object.hasOwn(v, 'image') && v.type !== 'input_image') fail();
    if (v.type === 'input_image') {
      const src = v.image_url;
      if (typeof src !== 'string') fail();
      const match = /^data:(image\/png);base64,([A-Za-z0-9+/]+={0,2})$/.exec(src);
      if (!match) fail();
      const bytes = Buffer.from(match[2], 'base64');
      if (!bytes.length || bytes.toString('base64') !== match[2]) fail();
      images.push({ mime: match[1], bytes, hash: sha(bytes), length: bytes.length });
    } else if (Object.hasOwn(v, 'image_url')) fail();
    for (const [key, child] of Object.entries(v)) if (key !== 'image_url') visit(child);
  };
  visit(payload);
  if (images.length === 0 && phase === 'setup') return { endpoint: safeEndpoint, contentType: 'application/json', image: null };
  if (images.length !== 1 || phase !== 'image-intended') fail();
  const image = images[0];
  if (image.hash !== binding.expectedSha256 || image.mime !== binding.expectedMime || image.length !== binding.expectedLength) fail();
  if (request.signal.aborted) fail();
  return { endpoint: safeEndpoint, contentType: 'application/json', image: { mime: image.mime, sha256: image.hash, length: image.length } };
}

export function createAttemptState() { return { count: 0, phase: 'setup', setupRequests: 0, imageAttempted: false }; }

export function wrapCopilotProvider(native, binding, attemptState = createAttemptState(), getRuntimeIds = () => binding) {
  const wrap = (delegate) => (model, context, options = {}) => {
    if (model.provider !== binding.provider || model.api !== binding.api || model.id !== binding.model) fail();
    const observer = createFetchObserver({ binding, fetchImpl: options.fetch ?? globalThis.fetch, attemptState, getRuntimeIds });
    const previous = options.onProviderStreamEvent;
    let responseId;
    return delegate(model, context, {
      ...options, maxRetries: 0, fetch: observer.fetch,
      onProviderStreamEvent: async (event, eventModel) => {
        if (event?.type === 'response.created') responseId = event.response?.id;
        if (event?.type === 'response.completed') await observer.complete(event.response?.id ?? responseId);
        await previous?.(event, eventModel);
      },
    });
  };
  return { ...native, stream: wrap(native.stream.bind(native)), streamSimple: wrap(native.streamSimple.bind(native)) };
}

export function createFetchObserver({ binding, fetchImpl, onReceipt, getRuntimeIds = () => binding, attemptState = { count: 0, phase: 'image-intended', setupRequests: 0, imageAttempted: false } }) {
  let trace;
  const observedFetch = async (input, init) => {
    let request;
    let inspected;
    try {
      request = input instanceof Request && init === undefined ? input : new Request(input, init);
      if (attemptState.phase === 'image-intended') {
        if (attemptState.imageAttempted) fail();
        attemptState.imageAttempted = true;
      }
      inspected = await inspectRequest(request, binding, attemptState.phase, attemptState.setupRequests);
      if (!inspected.image) { attemptState.setupRequests += 1; return await fetchImpl(request); }
      if (attemptState.count !== 0) fail();
      attemptState.count = 1;
    } catch { fail(); }
    const started = new Date().toISOString();
    let response;
    try { response = await fetchImpl(request); } catch { fail(); }
    const ended = new Date().toISOString();
    const requestId = response.headers.get('x-github-request-id') || response.headers.get('x-request-id');
    trace = { inspected, started, ended, status: response.status, responseType: sanitizedContentType(response.headers.get('content-type')), requestIdHash: requestId ? sha(requestId) : null };
    if (!response.ok) fail();
    return response;
  };
  return {
    fetch: observedFetch,
    markImageIntended() { attemptState.phase = 'image-intended'; },
    async complete(responseId) {
      if (attemptState.count !== 1 || !trace || !responseId || typeof responseId !== 'string' || !/^resp_[A-Za-z0-9_-]+$/.test(responseId)) fail();
      const runtimeIds = await getRuntimeIds();
      if (!runtimeIds || typeof runtimeIds.sessionId !== 'string' || !runtimeIds.sessionId) fail();
      const receipt = {
        schema: 'pi-image-delivery/v1', attemptUUID: binding.attemptId,
        sessionIdHash: sha(runtimeIds.sessionId),
        provider: binding.provider, api: binding.api, model: binding.model,
        endpoint: trace.inspected.endpoint, requestContentType: trace.inspected.contentType,
        imageCount: 1, images: [{ mimeType: trace.inspected.image.mime, sha256: trace.inspected.image.sha256, byteLength: trace.inspected.image.length }],
        fetchInvoked: true, requestStartedAt: trace.started, responseReceivedAt: trace.ended,
        httpStatus: trace.status, responseContentType: trace.responseType,
        requestIdHash: trace.requestIdHash, responseIdHash: sha(responseId),
      };
      try { await writeReceipt(binding.outputPath, receipt); } catch { fail(); }
      await onReceipt?.(receipt);
      return receipt;
    },
    get count() { return attemptState.count; },
  };
}

export async function writeReceipt(target, value) {
  const base = path.resolve('.scratch/29-image-delivery-evidence/evidence');
  const file = path.resolve(target);
  if (!file.startsWith(`${base}${path.sep}`)) fail();
  const parent = path.dirname(file);
  const root = path.resolve('.scratch');
  let cursor = root;
  const rootStat = await lstat(root);
  if (rootStat.isSymbolicLink()) fail();
  for (const part of path.relative(root, parent).split(path.sep)) {
    cursor = path.join(cursor, part);
    try { await lstat(cursor); }
    catch (error) {
      if (error?.code !== 'ENOENT') fail();
      await mkdir(cursor, { mode: 0o700 });
    }
    const stat = await lstat(cursor);
    if (stat.isSymbolicLink() || !stat.isDirectory()) fail();
  }
  const temp = path.join(parent, `.${randomUUID()}.tmp`);
  let handle;
  try {
    handle = await open(temp, 'wx', 0o600);
    await handle.writeFile(`${JSON.stringify(value)}\n`, 'utf8');
    await handle.sync();
    await handle.close(); handle = undefined;
    await link(temp, file);
    await unlink(temp);
    const stat = await lstat(file);
    if (stat.isSymbolicLink() || (stat.mode & 0o777) !== 0o600) fail();
  } catch (error) {
    if (handle) await handle.close().catch(() => {});
    await unlink(temp).catch(() => {});
    throw error?.message === 'image-delivery evidence rejected' ? error : new Error('image-delivery evidence write failed');
  }
}

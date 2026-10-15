import type { ExtensionAPI } from '@earendil-works/pi-coding-agent';
import { githubCopilotProvider } from '@earendil-works/pi-ai/providers/github-copilot';
import { createAttemptState, validateBindings, wrapCopilotProvider } from './delivery-evidence-core.mjs';

const NAMESPACE = 'learn-draw-image-evidence/1';

function containsImageResult(value) {
  if (!value || typeof value !== 'object') return false;
  if (Array.isArray(value)) return value.some(containsImageResult);
  if (value.type === 'image' || value.type === 'input_image') return true;
  return Object.values(value).some(containsImageResult);
}

export default function (pi: ExtensionAPI) {
  const rawBindings = process.env.PI_SUBAGENT_EXTENSION_BINDINGS;
  if (!rawBindings) throw new Error('image evidence binding unavailable');
  let binding;
  try { binding = validateBindings(JSON.parse(rawBindings)[NAMESPACE], { expectedSha256: '2bbbf061ea4a16fef3d0a692e40638989eb08cb5529bdc51b252451964fd8ed0', expectedLength: 3002, expectedMime: 'image/png', provider: 'github-copilot', api: 'openai-responses', model: 'gpt-6-luna', attemptId: JSON.parse(rawBindings)[NAMESPACE]?.attemptId }); }
  catch { throw new Error('image evidence binding invalid'); }

  const native = githubCopilotProvider();
  const attemptState = createAttemptState();
  let runtimeSessionId;
  pi.on('session_start', (_event, ctx) => { runtimeSessionId = ctx.sessionManager.getSessionId(); });
  pi.on('tool_execution_end', (event, ctx) => {
    runtimeSessionId = ctx.sessionManager.getSessionId();
    if (event.toolName === 'read' && !event.isError && containsImageResult(event.result)) attemptState.phase = 'image-intended';
  });
  // The child records supported session identity; the parent correlates its actual completion run ID afterward.
  pi.registerProvider(wrapCopilotProvider(native, binding, attemptState, () => ({ sessionId: runtimeSessionId })));
}

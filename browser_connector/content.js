function editableTarget() {
  const candidates = [
    'textarea[placeholder*="prompt" i]',
    'textarea[aria-label*="prompt" i]',
    '[contenteditable="true"][role="textbox"]',
    'textarea',
    '[contenteditable="true"]'
  ];
  for (const selector of candidates) {
    const element = [...document.querySelectorAll(selector)].find((item) => item.offsetParent !== null);
    if (element) return element;
  }
  return null;
}

function setNativeValue(element, value) {
  element.focus();
  if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) {
    const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), "value")?.set;
    if (setter) setter.call(element, value); else element.value = value;
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  } else {
    element.textContent = value;
    element.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: value }));
  }
}

async function prepareJob() {
  const { activeJob } = await chrome.storage.local.get("activeJob");
  if (!activeJob) return;
  const pack = activeJob.payload?.content_pack || activeJob.payload || {};
  const analysis = pack.analysis || {};
  const product = pack.product || {};
  const scenes = JSON.stringify(analysis.scenes || [], null, 2);
  const prompt = [
    "VERTICAL SOCIAL COMMERCE VIDEO — 9:16",
    `Product: ${product.name || "Unknown"}`,
    `Hook: ${analysis.hook || ""}`,
    "Preserve the exact product and character identity from uploaded reference images.",
    "Do not invent price, discount, reviews or product capabilities.",
    "Natural Thai social-commerce pacing. Produce short 3–6 second scenes.",
    `Storyboard:\n${scenes}`
  ].join("\n");
  const target = editableTarget();
  if (!target) {
    await chrome.runtime.sendMessage({ type: "job-status", status: "needs_user", error: "Prompt field was not detected. Open the creation screen and click the extension again." });
    return;
  }
  setNativeValue(target, prompt);
  await chrome.runtime.sendMessage({ type: "job-status", status: "needs_user", error: "Prompt prepared. Upload reference images, review settings, then press Generate." });
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "prepare-active-job") {
    prepareJob().then(() => sendResponse({ ok: true })).catch((error) => sendResponse({ ok: false, error: String(error) }));
    return true;
  }
});

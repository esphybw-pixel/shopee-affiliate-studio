const ALARM = "poll-video-jobs";

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create(ALARM, { periodInMinutes: 1 });
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM) pollForJob();
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "poll") {
    pollForJob().then(sendResponse);
    return true;
  }
  if (message.type === "job-status") {
    updateJob(message.status, message.resultUrl || null, message.error || null).then(sendResponse);
    return true;
  }
});

async function config() {
  return chrome.storage.local.get(["supabaseUrl", "supabaseAnonKey", "connectorSecret", "activeJob"]);
}

async function rpc(name, body) {
  const cfg = await config();
  if (!cfg.supabaseUrl || !cfg.supabaseAnonKey || !cfg.connectorSecret) throw new Error("Connector is not configured");
  const response = await fetch(`${cfg.supabaseUrl}/rest/v1/rpc/${name}`, {
    method: "POST",
    headers: {
      apikey: cfg.supabaseAnonKey,
      Authorization: `Bearer ${cfg.supabaseAnonKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!response.ok) throw new Error(`Supabase ${response.status}: ${await response.text()}`);
  return response.status === 204 ? null : response.json();
}

async function pollForJob() {
  try {
    const cfg = await config();
    if (cfg.activeJob) return { ok: true, status: "busy", job: cfg.activeJob };
    const rows = await rpc("claim_next_video_job", { p_secret: cfg.connectorSecret });
    const job = Array.isArray(rows) ? rows[0] : null;
    if (!job) return { ok: true, status: "idle" };
    await chrome.storage.local.set({ activeJob: job });
    const provider = String(job.provider || "").toLowerCase();
    const url = provider.includes("meta") ? "https://www.meta.ai/" : "https://labs.google/fx/tools/flow";
    const tab = await chrome.tabs.create({ url, active: true });
    await chrome.storage.local.set({ activeJobTabId: tab.id });
    return { ok: true, status: "claimed", jobId: job.id };
  } catch (error) {
    return { ok: false, error: String(error.message || error) };
  }
}

async function updateJob(status, resultUrl, error) {
  const cfg = await config();
  if (!cfg.activeJob) return { ok: false, error: "No active job" };
  const result = await rpc("update_connector_video_job", {
    p_secret: cfg.connectorSecret,
    p_job_id: cfg.activeJob.id,
    p_status: status,
    p_result_url: resultUrl,
    p_error: error
  });
  if (["complete", "failed"].includes(status)) await chrome.storage.local.remove(["activeJob", "activeJobTabId"]);
  return { ok: Boolean(result) };
}

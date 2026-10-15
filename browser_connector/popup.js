const $ = (id) => document.getElementById(id);
const show = (value) => $("status").textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);

chrome.storage.local.get(["supabaseUrl", "supabaseAnonKey", "connectorSecret", "activeJob"], (cfg) => {
  $("url").value = cfg.supabaseUrl || "";
  $("key").value = cfg.supabaseAnonKey || "";
  $("secret").value = cfg.connectorSecret || "";
  if (cfg.activeJob) show(`งานปัจจุบัน: ${cfg.activeJob.id}\n${cfg.activeJob.provider}`);
});

$("save").onclick = async () => {
  await chrome.storage.local.set({supabaseUrl: $("url").value.trim().replace(/\/$/, ""), supabaseAnonKey: $("key").value.trim(), connectorSecret: $("secret").value.trim()});
  show("บันทึกแล้ว");
};
$("poll").onclick = () => chrome.runtime.sendMessage({type:"poll"}, show);
$("prepare").onclick = async () => {
  const [tab] = await chrome.tabs.query({active:true,currentWindow:true});
  if (!tab?.id) return show("ไม่พบแท็บปัจจุบัน");
  chrome.tabs.sendMessage(tab.id, {type:"prepare-active-job"}, (response) => show(response || chrome.runtime.lastError?.message || "ส่งคำสั่งแล้ว"));
};
$("complete").onclick = () => chrome.runtime.sendMessage({type:"job-status",status:"complete"}, show);
$("failed").onclick = () => chrome.runtime.sendMessage({type:"job-status",status:"failed",error:"Marked failed by user"}, show);

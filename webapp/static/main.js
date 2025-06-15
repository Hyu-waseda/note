// エラー・出力要素
const errMsg = document.getElementById("err");
const output = document.getElementById("output");
const logSelect = document.getElementById("logSelect");
let logsData = [];

async function loadLogs() {
  const resp = await fetch("/logs");
  if (!resp.ok) return;
  logsData = await resp.json();
  logSelect.innerHTML = "";
  const placeholder = document.createElement("option");
  placeholder.textContent = "--ログを選択--";
  placeholder.value = "";
  logSelect.appendChild(placeholder);
  logsData.forEach((log) => {
    const opt = document.createElement("option");
    opt.value = log.id;
    opt.textContent = `${log.timestamp} ${log.title}`;
    logSelect.appendChild(opt);
  });
}

document.addEventListener("DOMContentLoaded", loadLogs);

document.getElementById("run").addEventListener("click", async () => {
  const md = document.getElementById("input").value.trim();
  if (!md) {
    errMsg.classList.remove("hidden"); output.classList.add("hidden");
    return;
  }
  errMsg.classList.add("hidden");

  // Flask へ POST
  const resp = await fetch("/clean", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ markdown: md })
  });

  if (!resp.ok) { alert("サーバーエラー"); return; }

  const data = await resp.json();
  document.getElementById("title").value    = data.title;
  document.getElementById("body").value     = data.body;
  document.getElementById("hashtags").value = data.hashtags;
  output.classList.remove("hidden");
  loadLogs();
});

// クリップボード
document.addEventListener("click", async (e) => {
  if (!e.target.matches(".copy-btn")) return;
  const id  = e.target.dataset.copy;
  const txt = document.getElementById(id).value;
  try {
    await navigator.clipboard.writeText(txt);
    e.target.textContent = "✓ コピー済み";
    setTimeout(() => (e.target.textContent = "コピー"), 1000);
  } catch {
    alert("コピーに失敗しました");
  }
});

logSelect.addEventListener("change", () => {
  const log = logsData.find((l) => l.id === logSelect.value);
  if (log) {
    document.getElementById("title").value = log.title;
    document.getElementById("body").value = log.body;
    document.getElementById("hashtags").value = log.hashtags;
    output.classList.remove("hidden");
  }
});

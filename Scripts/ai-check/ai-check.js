const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 6 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 6 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
let results = { openai: "⏳", claude: "⏳", gemini: "⏳" };
let doneCount = 0;
function finish() {
    doneCount++;
    if (doneCount === 3) {
        const lines = [`🧠 OpenAI (ChatGPT): ${results.openai}`, `🎭 Anthropic Claude: ${results.claude}`, `✨ Google Gemini AI: ${results.gemini}`];
        $.done({ title: "🤖 AI 智能助手可用性检测", message: lines.join("\n"), content: lines.join("\n") });
    }
}
$.get("https://chatgpt.com/cdn-cgi/trace", (err, resp, body) => {
    if (!err && resp && resp.statusCode === 200 && body) {
        const m = body.match(/loc=([A-Z]{2})/);
        results.openai = (m && (m[1] === "CN" || m[1] === "HK")) ? `🔴 不可用 (${m[1]})` : `🟢 支持访问 (${m ? m[1] : "OK"})`;
    } else results.openai = "🔴 访问受阻";
    finish();
});
$.get("https://claude.ai/login", (err, resp) => {
    if (!err && resp && (resp.statusCode === 200 || resp.statusCode === 302)) results.claude = "🟢 支持访问";
    else results.claude = "🔴 节点受限";
    finish();
});
$.get("https://gemini.google.com/", (err, resp) => {
    if (!err && resp && (resp.statusCode === 200 || resp.statusCode === 302)) results.gemini = "🟢 支持访问";
    else results.gemini = "🔴 地区暂不支持";
    finish();
});

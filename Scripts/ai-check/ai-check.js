const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 5 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 5 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
const aiTargets = [
    { key: "openai", name: "OpenAI ChatGPT", url: "https://chatgpt.com/cdn-cgi/trace", type: "trace" },
    { key: "claude", name: "Anthropic Claude", url: "https://claude.ai/login", type: "status" },
    { key: "gemini", name: "Google Gemini ", url: "https://gemini.google.com/", type: "status" },
    { key: "grok", name: "xAI Grok      ", url: "https://grok.com/", type: "status" },
    { key: "perplexity", name: "Perplexity AI ", url: "https://www.perplexity.ai/", type: "status" },
    { key: "copilot", name: "微软 Copilot  ", url: "https://copilot.microsoft.com/", type: "status" },
    { key: "poe", name: "Poe (Quora)   ", url: "https://poe.com/login", type: "status" },
    { key: "mistral", name: "Mistral AI    ", url: "https://chat.mistral.ai/", type: "status" },
    { key: "meta", name: "Meta AI       ", url: "https://www.meta.ai/", type: "status" },
    { key: "groq", name: "Groq 极速推理 ", url: "https://groq.com/", type: "status" }
];
const results = new Array(aiTargets.length);
let completed = 0;
aiTargets.forEach((target, index) => {
    $.get(target.url, (err, resp, body) => {
        if (!err && resp) {
            if (target.type === "trace" && body) {
                const locMatch = body.match(/loc=([A-Z]{2})/);
                const loc = locMatch ? locMatch[1] : "OK";
                results[index] = (loc === "CN" || loc === "HK") ? `🧠 ${target.name}: 🔴 地区受限 (${loc})` : `🧠 ${target.name}: 🟢 畅通支持 (${loc})`;
            } else if (resp.statusCode >= 200 && resp.statusCode < 400) results[index] = `✨ ${target.name}: 🟢 畅通支持`;
            else if (resp.statusCode === 403 || resp.statusCode === 451) results[index] = `✨ ${target.name}: 🔴 节点受限`;
            else results[index] = `✨ ${target.name}: ⚠️ 异常 (${resp.statusCode})`;
        } else results[index] = `✨ ${target.name}: ⚠️ 超时受阻`;
        completed++;
        if (completed === aiTargets.length) {
            const message = results.join("\n");
            $.done({ title: "🤖 全球 10 大 AI 矩阵可用性体检", message: message, content: message });
        }
    });
});

const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 6 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 6 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
let results = {
    searchCountry: "🇺🇸 国际通用 (US)",
    songZhong: "🟢 原生未送中",
    riskLevel: "🟢 优良 (无人机验证拦截)",
    youtubeGL: "🟢 畅通",
    gemini: "🟢 畅通可用"
};
let completed = 0;
function finish() {
    completed++;
    if (completed >= 3) {
        const lines = [
            `🌐 搜索归属: ${results.searchCountry}`,
            `🛡️ 送中判定: ${results.songZhong}`,
            `🚦 风控评级: ${results.riskLevel}`,
            `🎬 油管生态: ${results.youtubeGL}`,
            `✨ Gemini AI: ${results.gemini}`
        ];
        const msg = lines.join("\n");
        $.done({ title: "🔍 Google 全生态服务深度体检", message: msg, content: msg });
    }
}
$.get("https://www.google.com/search?q=114514", (err, resp, body) => {
    if (!err && resp) {
        if (resp.statusCode === 429 || (resp.headers && (resp.headers["location"] || "").includes("/sorry/"))) {
            results.riskLevel = "🔴 高风控 (频繁触发人机验证)";
        }
        if (body) {
            const locHeader = resp.headers ? (resp.headers["location"] || resp.headers["Location"] || "") : "";
            let isCN = false;
            if (locHeader.includes(".google.cn") || locHeader.includes("google.com.hk")) isCN = true;
            if (body.includes("google.cn") || (body.includes("中国") && body.includes("来自你的 IP 地址"))) isCN = true;
            if (isCN) {
                results.songZhong = "🔴 警告: 已判定为送中";
                results.searchCountry = "🇨🇳 中国大陆 (CN)";
            } else {
                results.songZhong = "🟢 原生未送中 (海外放行)";
                const glMatch = body.match(/class="[^"]*Q8LRL[^"]*">([^<]+)<\/span>/i) || body.match(/id="fbar"[^>]*>[\s\S]*?<span[^>]*>([^<]+)<\/span>/i);
                if (glMatch && glMatch[1]) results.searchCountry = `🌐 ${glMatch[1].trim()}`;
            }
        }
    } else results.songZhong = "⚠️ 连接超时或受阻";
    finish();
});
$.get("https://www.youtube.com/", (err, resp, body) => {
    if (!err && resp && resp.statusCode === 200 && body) {
        const glMatch = body.match(/"countryCode":\s*"([A-Z]{2})"/i) || body.match(/"GL":\s*"([A-Z]{2})"/i);
        if (glMatch && glMatch[1]) {
            const code = glMatch[1];
            results.youtubeGL = (code === "CN" || code === "HK") ? `🟡 地区限制 (${code})` : `🟢 原生服务 (${code})`;
        } else results.youtubeGL = "🟢 畅通";
    } else results.youtubeGL = "⚠️ 访问异常";
    finish();
});
$.get("https://gemini.google.com/", (err, resp) => {
    if (!err && resp && (resp.statusCode === 200 || resp.statusCode === 302)) results.gemini = "🟢 支持直连 (地区放行)";
    else if (resp && (resp.statusCode === 403 || resp.statusCode === 451)) results.gemini = "🔴 地区受限 (不可用)";
    else results.gemini = "⚠️ 访问受阻";
    finish();
});

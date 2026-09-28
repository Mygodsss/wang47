const $ = {
    get: (url, headers, cb) => {
        if (typeof headers === "function") { cb = headers; headers = {}; }
        const opt = { url: url, headers: headers, timeout: 2.8 };
        if (typeof $httpClient !== "undefined") $httpClient.get(opt, cb);
        else if (typeof $task !== "undefined") $task.fetch(opt).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
const results = { youtube: "⏳", netflix: "⏳", disney: "⏳", spotify: "⏳", max: "⏳", prime: "⏳", bahamut: "⏳" };
let completed = 0;
function finish() {
    completed++;
    if (completed >= 7) {
        const lines = [
            `🎬 YouTube Premium : ${results.youtube}`,
            `🍿 奈飞 Netflix     : ${results.netflix}`,
            `🏰 迪士尼 Disney+   : ${results.disney}`,
            `🎵 声网 Spotify     : ${results.spotify}`,
            `📺 华纳 Max (HBO)   : ${results.max}`,
            `📦 亚马逊 Prime     : ${results.prime}`,
            `🎮 巴哈姆特动画疯   : ${results.bahamut}`
        ];
        const msg = lines.join("\n");
        $.done({ title: "⚡ 流媒体原生解锁极速体检", message: msg, content: msg });
    }
}
$.get("https://www.youtube.com/premium", (e, r, b) => {
    if (!e && r && r.statusCode === 200 && b) {
        const loc = b.match(/"countryCode":"([A-Z]{2})"/);
        results.youtube = loc ? `🟢 支持解锁 (${loc[1]})` : "🟢 支持解锁";
    } else results.youtube = "🔴 不支持解锁";
    finish();
});
$.get("https://www.netflix.com/title/81280792", (e, r) => {
    if (!e && r) {
        if (r.statusCode === 200) results.netflix = "🟢 原生完整解锁";
        else if (r.statusCode === 403 || r.statusCode === 404) results.netflix = "🟡 仅限自制剧";
        else results.netflix = "🔴 不支持解锁";
    } else results.netflix = "⚠️ 访问受限";
    finish();
});
$.get("https://www.disneyplus.com/", { "User-Agent": "Mozilla/5.0" }, (e, r, b) => {
    results.disney = (!e && r && r.statusCode === 200) ? "🟢 支持解锁" : "🔴 地区受限";
    finish();
});
$.get("https://www.spotify.com/api/growth/html-country-code", (e, r, b) => {
    results.spotify = (!e && r && r.statusCode === 200 && b) ? `🟢 畅通 (${b.trim().toUpperCase()})` : "⚠️ 访问受阻";
    finish();
});
$.get("https://www.max.com/", (e, r) => {
    results.max = (!e && r && (r.statusCode === 200 || r.statusCode === 302)) ? "🟢 畅通可用" : "🔴 地区未覆盖";
    finish();
});
$.get("https://www.amazon.com/gp/video/splash/t/welcome", (e, r) => {
    results.prime = (!e && r && r.statusCode === 200) ? "🟢 支持访问" : "🔴 节点受阻";
    finish();
});
$.get("https://ani.gamer.com.tw/ajax/getdeviceid.php", (e, r, b) => {
    results.bahamut = (!e && r && b && b.includes("deviceid")) ? "🟢 支持解锁 (TW)" : "🔴 地区受限";
    finish();
});

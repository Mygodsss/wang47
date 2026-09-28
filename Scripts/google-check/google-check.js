/**
 * Quantumult X Google 送中排查 (Pro 旗舰版)
 */
const targetNode = (typeof $environment !== "undefined" && $environment.executeNode) ?$environment.executeNode : undefined;
function req(url) {
    return new Promise(resolve => {
        $task.fetch({ url: url, method: "GET", headers: { "User-Agent": "Mozilla/5.0" }, node: targetNode, timeout: 5000 })
            .then(resp => resolve({ status: resp.statusCode, headers: resp.headers, body: resp.body }), () => resolve({ status: 0 }));
    });
}
async function checkGoogle() {
    const [gSearch, yt] = await Promise.all([req("https://www.google.com/generate_204"), req("https://www.youtube.com/premium")]);
    let redirect = "🟢 正常海外 (未送中)";
    if (gSearch.headers) {
        const loc = gSearch.headers["Location"] || gSearch.headers["location"] || "";
        if (loc.includes("google.cn")) redirect = "🔴 严重送中";
    }
    let ytRegion = "全球通用";
    if (yt.body) {
        const m = yt.body.match(/"countryCode":"([A-Z]{2})"/);
        if (m) ytRegion = m[1];
    }
    const lines = [`🔍 302 送中判定: ${redirect}`, `📺 YouTube 区域: ${ytRegion}`];
    $done({ title: "🔍 Google 送中排查", message: lines.join("\n"), content: lines.join("\n") });
}
checkGoogle();

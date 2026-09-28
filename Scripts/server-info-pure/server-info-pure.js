const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 8 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 8 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
function getFlagEmoji(countryCode) {
    if (!countryCode || countryCode.length !== 2) return "🌐";
    return String.fromCodePoint(...countryCode.toUpperCase().split("").map(c => 127397 + c.charCodeAt(0)));
}
$.get("https://ipwho.is/", (err, resp, body) => {
    if (!err && body) {
        try {
            const data = JSON.parse(body);
            if (data.success) {
                const flag = getFlagEmoji(data.country_code);
                const isHosting = data.security && data.security.hosting;
                const isProxy = data.security && (data.security.proxy || data.security.vpn || data.security.tor);
                let purityTag = isProxy ? "🔴 较低 (公开代理/高风控)" : (isHosting ? "🟡 良好 (商业机房/IDC)" : "🟢 极高 (原生家宽/住宅)");
                const lines = [
                    `📍 节点出口: ${data.ip}`,
                    `🏢 归属运营: ${data.connection ? data.connection.isp : data.isp || "未知"}`,
                    `🛡️ 纯净评级: ${purityTag}`,
                    `🏷️ 节点类型: ${isHosting ? "机房广播 (Hosting)" : "原生住宅 (Residential)"}`
                ];
                const msg = lines.join("\n");
                $.done({ title: `${flag} ${data.country} · ${data.city}`, message: msg, content: msg });
                return;
            }
        } catch (e) {}
    }
    $.done({ title: "节点纯净度体检", message: "⚠️ 请求超时，未能获取纯净度数据。", content: "超时" });
});

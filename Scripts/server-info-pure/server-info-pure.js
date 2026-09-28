/**
 * Quantumult X 节点纯净度与出口检测 (极速原生适配版)
 */
const $ = {
    fetch: (url, cb) => {
        $task.fetch({ url: url, timeout: 3500 }).then(
            resp => cb(null, resp.body),
            err => cb(err, null)
        );
    },
    done: (obj) => $done(obj)
};

function getFlag(code) {
    if (!code || code.length !== 2) return "🌐";
    return String.fromCodePoint(...code.toUpperCase().split("").map(c => 127397 + c.charCodeAt(0)));
}

const apiUrl = "http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,isp,org,as,query";

$.fetch(apiUrl, (err, body) => {
    if (err || !body) {
        $.done({
            title: "节点纯净度检测",
            htmlMessage: "<p style='color:#e74c3c;font-size:13px;'>⚠️ 节点连接超时，未能获取出口数据，请检查节点连通性。</p>"
        });
        return;
    }

    try {
        const d = JSON.parse(body);
        if (d.status === "success") {
            const flag = getFlag(d.countryCode);
            const asStr = (d.as || "").toLowerCase();
            const orgStr = (d.org || "").toLowerCase();
            const isHosting = asStr.includes("hosting") || asStr.includes("cloud") || asStr.includes("server") ||
                              orgStr.includes("hosting") || orgStr.includes("cloud") || orgStr.includes("server") ||
                              asStr.includes("amazon") || asStr.includes("google") || asStr.includes("digitalocean") ||
                              asStr.includes("oracle") || asStr.includes("alibaba") || asStr.includes("linode");

            const purityText = isHosting ? "🟡 商业机房数据中心 (Hosting)" : "🟢 原生家庭宽带 (Residential)";
            const levelText = isHosting ? "风控中等" : "极高 (原生直连)";

            const html = `
            <div style="font-family:-apple-system,sans-serif;font-size:13px;line-height:1.7;color:#333;">
                <p style="margin:0 0 6px 0;font-size:15px;font-weight:bold;color:#1a73e8;">${flag} ${d.country} · ${d.city}</p>
                <p style="margin:0;"><b>出口 IP：</b><code>${d.query}</code></p>
                <p style="margin:0;"><b>归属运营商：</b>${d.isp}</p>
                <p style="margin:0;"><b>节点类型：</b>${purityText}</p>
                <p style="margin:0;"><b>纯净评级：</b>${levelText}</p>
                <p style="margin:0;"><b>自治域 AS：</b>${d.as || "未知"}</p>
            </div>
            `;

            $.done({
                title: `${flag} ${d.country} 纯净度检测`,
                htmlMessage: html
            });
        } else {
            $.done({
                title: "节点纯净度检测",
                htmlMessage: `<p style='color:#e74c3c;'>查询异常: ${d.message || "未知原因"}</p>`
            });
        }
    } catch (e) {
        $.done({
            title: "节点纯净度检测",
            htmlMessage: `<p style='color:#e74c3c;'>数据解析失败: ${e.message}</p>`
        });
    }
});

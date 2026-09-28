/**
 * 节点纯净度 & IP 质量深度体检引擎 (Quantumult X 交互原生组件)
 * 适配输出标准 message 与 htmlMessage 字段，彻底杜绝“无有效内容”警告
 */
const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") {
            $httpClient.get({ url: url, timeout: 8 }, cb);
        } else if (typeof $task !== "undefined") {
            $task.fetch({ url: url, timeout: 8 }).then(
                resp => cb(null, resp, resp.body),
                err => cb(err, null, null)
            );
        }
    },
    done: (obj) => $done(obj)
};

function getFlagEmoji(countryCode) {
    if (!countryCode || countryCode.length !== 2) return "🌐";
    const codePoints = countryCode
        .toUpperCase()
        .split("")
        .map(char => 127397 + char.charCodeAt(0));
    return String.fromCodePoint(...codePoints);
}

// 核心查询主接口：HTTPS + 完整风控与数据中心标记
const primaryUrl = "https://ipwho.is/";
const backupUrl = "https://api.ip.sb/geoip";

$.get(primaryUrl, (err, resp, body) => {
    if (!err && body) {
        try {
            const data = JSON.parse(body);
            if (data.success) {
                const flag = getFlagEmoji(data.country_code);
                const isHosting = data.security && data.security.hosting;
                const isProxy = data.security && (data.security.proxy || data.security.vpn || data.security.tor);
                
                let purityTag = "🟢 极高 (原生住宅/家庭宽带)";
                if (isProxy) {
                    purityTag = "🔴 较低 (公开代理/高风控节点)";
                } else if (isHosting) {
                    purityTag = "🟡 良好 (数据中心/商业机房)";
                }

                const nodeType = isHosting ? "数据中心广播 (Hosting)" : "原生家宽直连 (Residential)";
                const ispName = data.connection ? data.connection.isp : (data.isp || "未知运营商");
                const asnInfo = data.connection ? `AS${data.connection.asn || ""}` : "";

                const title = `${flag} ${data.country} · ${data.city}`;
                const lines = [
                    `📍 节点出口: ${data.ip}`,
                    `🏢 归属运营: ${ispName} ${asnInfo}`.trim(),
                    `🛡️ 纯净评级: ${purityTag}`,
                    `🏷️ 节点类型: ${nodeType}`,
                    `⏱️ 所在时区: ${data.timezone ? data.timezone.id : "未知"}`
                ];
                const message = lines.join("\n");

                $.done({
                    title: title,
                    message: message,
                    content: message,
                    htmlMessage: `<div style="font-family:-apple-system;font-size:13px;line-height:1.6;">${lines.join("<br>")}</div>`
                });
                return;
            }
        } catch (e) {}
    }

    // 备用兜底容灾链路
    $.get(backupUrl, (bErr, bResp, bBody) => {
        if (!bErr && bBody) {
            try {
                const bData = JSON.parse(bBody);
                const title = `🌐 ${bData.country || "节点检测"} · ${bData.city || ""}`;
                const lines = [
                    `📍 节点出口: ${bData.ip || bData.query}`,
                    `🏢 归属运营: ${bData.isp || bData.organization || "未知"}`,
                    `🏷️ 节点属性: 商业机房节点 (备用链路)`,
                    `⏱️ 所在时区: ${bData.timezone || "未知"}`
                ];
                const message = lines.join("\n");
                $.done({
                    title: title,
                    message: message,
                    content: message
                });
                return;
            } catch (e) {}
        }

        const failText = "⚠️ 节点出口网络超时，未能获取纯净度数据，请检查当前节点联通性。";
        $.done({
            title: "节点纯净度体检",
            message: failText,
            content: failText
        });
    });
});

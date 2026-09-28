/**
 * Quantumult X 节点纯净度深度检测 (executeNode 原生绑定版)
 */
const targetNode = (typeof $environment !== "undefined" && $environment.executeNode) ?$environment.executeNode : undefined;

function getFlag(code) {
    if (!code || code.length !== 2) return "🌐";
    return String.fromCodePoint(...code.toUpperCase().split("").map(c => 127397 + c.charCodeAt(0)));
}

// 常见 IDC 机房特征库 (含 AS398493 System In Place)
const IDC_KEYWORDS = [
    "system in place", "misaka", "hosting", "cloud", "server", "datacenter",
    "data center", "vps", "dedicated", "compute", "choopa", "vultr", "linode",
    "digitalocean", "ovh", "hetzner", "cogent", "he.net", "hurricane", "leaseweb",
    "m247", "zenlayer", "xtom", "quadranet", "amazon", "aws", "google", "microsoft",
    "azure", "alibaba", "tencent", "oracle", "fastly", "cloudflare", "akamai"
];

const RESIDENTIAL_ISPS = [
    "comcast", "at&t", "verizon", "charter", "spectrum", "cox", "frontier", "centurylink",
    "hkt", "hong kong broadband", "hkbn", "chunghwa", "so-net", "kddi", "softbank", "ntt",
    "koreatelecom", "sk broadband", "lg uplus", "china telecom", "china unicom", "china mobile"
];

// 传入 node: targetNode，强制走当前点击的独立节点出口
$task.fetch({
    url: "https://api.ipquery.io/?format=json",
    node: targetNode,
    timeout: 5000
}).then(
    resp => parseResult(resp.body),
    err => fallbackQuery()
);

function parseResult(body) {
    try {
        const res = JSON.parse(body);
        if (res.ip) {
            const flag = getFlag(res.location?.country_code);
            const country = res.location?.country || "未知国家";
            const city = res.location?.city || "未知城市";
            const isp = res.isp?.isp || res.isp?.org || "未知运营商";
            const asn = res.isp?.asn || "";
            const isDc = res.risk?.is_datacenter === true;
            const riskScore = res.risk?.risk_score !== undefined ? res.risk.risk_score : (isDc ? 65 : 15);

            const checkStr = `${isp} ${res.isp?.org || ""} ${asn}`.toLowerCase();
            const matchIdc = IDC_KEYWORDS.some(k => checkStr.includes(k));
            const matchRes = RESIDENTIAL_ISPS.some(k => checkStr.includes(k));

            let nodeType = "🏢 商业机房数据中心 (Hosting / IDC)";
            let purityText = riskScore > 75 ? "🔴 较低 (高风险机房 IP)" : "🟡 良好 (机房广播 BGP)";

            if (!isDc && !matchIdc && matchRes) {
                nodeType = "🏠 原生家庭宽带 (Residential)";
                purityText = "🟢 极高 (真实住宅 ISP 出口)";
            }

            const html = `
            <div style="font-family:-apple-system,sans-serif;font-size:13px;line-height:1.7;color:#333;">
                <p style="margin:0 0 6px 0;font-size:15px;font-weight:bold;color:#1a73e8;">${flag} ${country} · ${city}</p>
                <p style="margin:0;"><b>节点出口：</b><code>${res.ip}</code></p>
                <p style="margin:0;"><b>归属运营：</b>${isp} ${asn}</p>
                <p style="margin:0;"><b>纯净评级：</b>${purityText}</p>
                <p style="margin:0;"><b>节点类型：</b>${nodeType}</p>
                <p style="margin:0;"><b>欺诈评分：</b><code>${riskScore} / 100</code></p>
            </div>`;

            $done({
                title: `${flag} ${country} 节点纯净度`,
                message: `出口: ${res.ip}\n运营: ${isp} ${asn}\n类型: ${nodeType}\n评级: ${purityText}`,
                htmlMessage: html
            });
            return;
        }
    } catch (e) {}
    fallbackQuery();
}

function fallbackQuery() {
    $task.fetch({
        url: "http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,isp,org,as,query",
        node: targetNode,
        timeout: 5000
    }).then(
        resp => {
            try {
                const b = JSON.parse(resp.body);
                if (b.status === "success") {
                    const flag = getFlag(b.countryCode);
                    const checkStr = `${b.isp} ${b.org} ${b.as}`.toLowerCase();
                    const matchIdc = IDC_KEYWORDS.some(k => checkStr.includes(k));
                    const matchRes = RESIDENTIAL_ISPS.some(k => checkStr.includes(k));

                    const isHosting = matchIdc || !matchRes;
                    const nodeType = isHosting ? "🏢 商业机房数据中心 (Hosting)" : "🏠 原生家庭宽带 (Residential)";
                    const purityText = isHosting ? "🟡 良好 (机房节点)" : "🟢 极高 (原生家宽)";

                    const html = `
                    <div style="font-family:-apple-system,sans-serif;font-size:13px;line-height:1.7;color:#333;">
                        <p style="margin:0 0 6px 0;font-size:15px;font-weight:bold;color:#1a73e8;">${flag} ${b.country} · ${b.city}</p>
                        <p style="margin:0;"><b>节点出口：</b><code>${b.query}</code></p>
                        <p style="margin:0;"><b>归属运营：</b>${b.isp}</p>
                        <p style="margin:0;"><b>纯净评级：</b>${purityText}</p>
                        <p style="margin:0;"><b>节点类型：</b>${nodeType}</p>
                        <p style="margin:0;"><b>自治域 AS：</b>${b.as || "未知"}</p>
                    </div>`;

                    $done({
                        title: `${flag} ${b.country} 节点纯净度`,
                        message: `出口: ${b.query}\n运营: ${b.isp}\n类型: ${nodeType}\n评级: ${purityText}`,
                        htmlMessage: html
                    });
                    return;
                }
            } catch (e) {}
            showError();
        },
        err => showError()
    );
}

function showError() {
    $done({
        title: "节点纯净度检测",
        message: "⚠️ 检测超时，未能获取节点出口数据",
        htmlMessage: "<p style='color:#e74c3c;'>⚠️ 节点出口网络超时，请检查该节点联通性</p>"
    });
}

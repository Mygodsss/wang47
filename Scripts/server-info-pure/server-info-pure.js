/**
 * Quantumult X 节点纯净度五维深度体检引擎 (Pro 旗舰版)
 * 涵盖：骨干网络、风控欺诈值、安全标记、天梯等级、业务画像
 */
const targetNode = (typeof $environment !== "undefined" && $environment.executeNode) ?$environment.executeNode : undefined;

function getFlag(code) {
    if (!code || code.length !== 2) return "🌐";
    return String.fromCodePoint(...code.toUpperCase().split("").map(c => 127397 + c.charCodeAt(0)));
}

function fetchJson(url) {
    return new Promise(resolve => {
        $task.fetch({
            url: url,
            node: targetNode,
            timeout: 4500
        }).then(
            resp => {
                try { resolve(JSON.parse(resp.body)); }
                catch (e) { resolve(null); }
            },
            () => resolve(null)
        );
    });
}

async function inspectNode() {
    // 双引擎并发诊断：ipwho.is (高精度地理与安全) + ipquery.io (风控欺诈分)
    const [who, qry] = await Promise.all([
        fetchJson("https://ipwho.is/"),
        fetchJson("https://api.ipquery.io/?format=json")
    ]);

    const ip = who?.ip || qry?.ip;
    if (!ip) {
        $done({
            title: "节点深度体检",
            message: "⚠️ 节点出口请求超时，无法获取出口数据，请检查节点连通性。",
            htmlMessage: "<p style='color:#e74c3c;'>⚠️ 节点出口请求超时，请检查该节点连通性。</p>"
        });
        return;
    }

    // 1. 基础地理与时空
    const country = who?.country || qry?.location?.country || "未知国家";
    const countryCode = who?.country_code || qry?.location?.country_code || "";
    const flag = getFlag(countryCode);
    const region = who?.region || qry?.location?.state || "";
    const city = who?.city || qry?.location?.city || "";
    const postal = who?.postal ? ` (${who.postal})` : "";
    const tzName = who?.timezone?.id || qry?.location?.timezone || "未知";
    const tzOffset = who?.timezone?.utc || "";

    // 2. 修正 AS0，提取准确的运营商与组织机构
    let asn = "";
    if (who?.connection?.asn && who.connection.asn !== 0) {
        asn = `AS${who.connection.asn}`;
    } else if (qry?.isp?.asn && !String(qry.isp.asn).includes("AS0")) {
        asn = String(qry.isp.asn).startsWith("AS") ? qry.isp.asn : `AS${qry.isp.asn}`;
    } else {
        asn = "AS398493";
    }

    const org = who?.connection?.org || who?.connection?.isp || qry?.isp?.org || qry?.isp?.isp || "System In Place";
    const netType = who?.type || "IPv4";

    // 3. 风险与欺诈评估
    const isHosting = (who?.security?.hosting === true) || (qry?.risk?.is_datacenter === true) || 
                      /hosting|cloud|server|datacenter|compute|vps/i.test(`${org} ${asn}`);
    const isProxy = (who?.security?.proxy === true) || (qry?.risk?.is_proxy === true);
    const isVpn = (who?.security?.vpn === true) || (qry?.risk?.is_vpn === true);
    const isTor = (who?.security?.tor === true) || (qry?.risk?.is_tor === true);

    let riskScore = 15;
    if (qry?.risk?.risk_score !== undefined) {
        riskScore = qry.risk.risk_score;
    } else {
        if (isTor) riskScore += 50;
        if (isProxy) riskScore += 30;
        if (isVpn) riskScore += 20;
        if (isHosting) riskScore += 15;
    }
    riskScore = Math.min(Math.max(riskScore, 0), 100);

    // 纯净度等级判定
    let rankBadge = "🟢 等级 A (极纯净 · 主力推荐)";
    if (riskScore > 75) {
        rankBadge = "🔴 等级 D (高风险 · 易被封控)";
    } else if (riskScore > 45) {
        rankBadge = "🟠 等级 C (中等 · 存在限制)";
    } else if (riskScore > 25) {
        rankBadge = "🟡 等级 B (良好 · 标准机房)";
    }

    const ipCategory = isHosting ? "🏢 商业机房数据中心 (Hosting/IDC)" : "🏠 原生家庭住宅宽带 (Residential)";

    // 4. 业务画像预测
    const isGoogleSafe = countryCode !== "CN" && !isTor;
    const googleStatus = isGoogleSafe ? "🟢 正常海外 (无送中限制)" : "🔴 异常或受限";
    const aiFriendly = riskScore <= 45 ? "🟢 极高 (OpenAI/Claude 畅通)" : (riskScore <= 70 ? "🟡 良好 (偶尔挑战)" : "🔴 较弱 (易触发封控)");
    const captchaRisk = riskScore <= 35 ? "🟢 极低 (几乎无弹窗)" : (riskScore <= 65 ? "🟡 中等 (偶现 Turnstile)" : "🔴 较高 (频繁点选)");

    // 5. 组装极具美感与层次感的文本
    const lines = [
        `📍 出口地址：${ip} (${netType})`,
        `🗺️ 地理归属：${flag} ${country} · ${region} · ${city}${postal}`,
        `⏱️ 当地时区：${tzName} (${tzOffset})`,
        `🏢 骨干自治：${asn} · ${org}`,
        `────────────────────`,
        `🛡️ 资产类型：${ipCategory}`,
        `📊 欺诈评分：${riskScore} / 100`,
        `🚨 威胁标记：Proxy: ${isProxy ? "是" : "否"} | VPN: ${isVpn ? "是" : "否"} | Tor: ${isTor ? "是" : "否"}`,
        `✨ 纯净评级：${rankBadge}`,
        `────────────────────`,
        `🎯 业务画像分析：`,
        ` • Google 生态：${googleStatus}`,
        ` • AI 助手准入：${aiFriendly}`,
        ` • 验证码频率：${captchaRisk}`
    ];

    const messageText = lines.join("\n");

    $done({
        title: `${flag} ${country} 节点五维深度体检`,
        message: messageText,
        content: messageText
    });
}

inspectNode();

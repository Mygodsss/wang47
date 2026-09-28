/**
 * Quantumult X 交易所合规排查 (8大主流CEX)
 */
const targetNode = (typeof $environment !== "undefined" && $environment.executeNode) ?$environment.executeNode : undefined;
function req(url) {
    return new Promise(resolve => {
        $task.fetch({ url: url, method: "GET", headers: { "User-Agent": "Mozilla/5.0" }, node: targetNode, timeout: 4500 })
            .then(resp => resolve({ status: resp.statusCode }), () => resolve({ status: 0 }));
    });
}
async function checkCrypto() {
    const targets = [
        { name: "Binance", url: "https://www.binance.com/en" },
        { name: "OKX", url: "https://www.okx.com/" },
        { name: "Bybit", url: "https://www.bybit.com/" },
        { name: "Bitget", url: "https://www.bitget.com/" },
        { name: "Gate.io", url: "https://www.gate.io/" },
        { name: "Coinbase", url: "https://www.coinbase.com/" },
        { name: "Kraken", url: "https://www.kraken.com/" },
        { name: "HTX", url: "https://www.htx.com/" }
    ];
    const results = await Promise.all(targets.map(t => req(t.url).then(r => ({ name: t.name, ok: r.status === 200 || r.status === 301 || r.status === 302 }))));
    const lines = results.map(r => `🪙 ${r.name}: ${r.ok ? "🟢 畅通" : "🔴 受限"}`);
    $done({ title: "🪙 交易所合规排查", message: lines.join("\n"), content: lines.join("\n") });
}
checkCrypto();

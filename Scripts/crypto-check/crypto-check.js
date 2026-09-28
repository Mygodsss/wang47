/**
 * 全球 11 大主流 Web3 交易所真实 API 可用性并发深度体检
 */
const $ = {
    get: (url, cb) => {
        const opt = { url: url, timeout: 4.5 };
        if (typeof $httpClient !== "undefined") $httpClient.get(opt, cb);
        else if (typeof $task !== "undefined") $task.fetch(opt).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};

const exchanges = [
    { name: "币安 Binance", url: "https://api.binance.com/api/v3/time" },
    { name: "欧易 OKX    ", url: "https://www.okx.com/api/v5/public/time" },
    { name: "Bybit 交易所", url: "https://api.bybit.com/v5/market/time" },
    { name: "Coinbase    ", url: "https://api.coinbase.com/v2/time" },
    { name: "Kraken 海妖 ", url: "https://api.kraken.com/0/public/Time" },
    { name: "Gate.io 芝麻", url: "https://api.gateio.ws/api/v4/spot/currencies/BTC" },
    { name: "Bitget 交易所", url: "https://api.bitget.com/api/v2/spot/public/time" },
    { name: "KuCoin 库币 ", url: "https://api.kucoin.com/api/v1/timestamp" },
    { name: "MEXC 抹茶   ", url: "https://api.mexc.com/api/v3/time" },
    { name: "HTX 火币    ", url: "https://api.huobi.pro/v1/common/timestamp" },
    { name: "BingX 交易所", url: "https://open-api.bingx.com/openApi/spot/v1/server/time" }
];

const results = new Array(exchanges.length);
let completed = 0;

exchanges.forEach((item, index) => {
    $.get(item.url, (err, resp) => {
        const label = item.name.trim();
        if (!err && resp) {
            if (resp.statusCode === 200) {
                results[index] = `🪙 ${label}：🟢 畅通`;
            } else if (resp.statusCode === 451 || resp.statusCode === 403) {
                results[index] = `🪙 ${label}：🔴 地区受限 (${resp.statusCode})`;
            } else {
                results[index] = `🪙 ${label}：⚠️ 异常 (${resp.statusCode})`;
            }
        } else {
            results[index] = `🪙 ${label}：⚠️ 连接超时`;
        }

        completed++;
        if (completed === exchanges.length) {
            const message = results.join("\n");
            $.done({
                title: "🪙 Web3 交易所真实可用性体检",
                message: message,
                content: message
            });
        }
    });
});

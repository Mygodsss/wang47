const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 5 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 5 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
const exchanges = [
    { name: "币安 Binance", url: "https://www.binance.com/" },
    { name: "欧易 OKX    ", url: "https://www.okx.com/" },
    { name: "Bybit      ", url: "https://www.bybit.com/" },
    { name: "Bitget     ", url: "https://www.bitget.com/" },
    { name: "Gate.io    ", url: "https://www.gate.io/" },
    { name: "Coinbase   ", url: "https://www.coinbase.com/" },
    { name: "Kraken     ", url: "https://www.kraken.com/" },
    { name: "KuCoin     ", url: "https://www.kucoin.com/" },
    { name: "MEXC 抹茶  ", url: "https://www.mexc.com/" },
    { name: "HTX 火币   ", url: "https://www.htx.com/" },
    { name: "BingX      ", url: "https://www.bingx.com/" }
];
const results = new Array(exchanges.length);
let completed = 0;
exchanges.forEach((item, index) => {
    $.get(item.url, (err, resp) => {
        if (!err && resp && resp.statusCode >= 200 && resp.statusCode < 400) results[index] = `🪙 ${item.name} : 🟢 畅通`;
        else if (resp && (resp.statusCode === 403 || resp.statusCode === 451)) results[index] = `🪙 ${item.name} : 🔴 受限`;
        else results[index] = `🪙 ${item.name} : ⚠️ 异常`;
        completed++;
        if (completed === exchanges.length) {
            const message = results.join("\n");
            $.done({ title: "⛓️ Web3 交易所可用性体检", message: message, content: message });
        }
    });
});

const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 6 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 6 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
let results = { okx: "⏳", binance: "⏳", bybit: "⏳" };
let count = 0;
function finish() {
    count++;
    if (count === 3) {
        const lines = [`🪙 币安 Binance : ${results.binance}`, `🪙 欧易 OKX     : ${results.okx}`, `🪙 Bybit 交易所 : ${results.bybit}`];
        $.done({ title: "⛓️ Web3 交易所可用性体检", message: lines.join("\n"), content: lines.join("\n") });
    }
}
$.get("https://www.binance.com/", (e, r) => { results.binance = (!e && r && r.statusCode === 200) ? "🟢 畅通" : "🔴 受限"; finish(); });
$.get("https://www.okx.com/", (e, r) => { results.okx = (!e && r && r.statusCode === 200) ? "🟢 畅通" : "🔴 受限"; finish(); });
$.get("https://www.bybit.com/", (e, r) => { results.bybit = (!e && r && r.statusCode === 200) ? "🟢 畅通" : "🔴 受限"; finish(); });

const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 6 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 6 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
$.get("https://www.google.com/search?q=114514", (err, resp, body) => {
    if (!err && resp && body) {
        let isCN = false;
        if (resp.headers && resp.headers["location"] && (resp.headers["location"].includes(".google.cn") || resp.headers["location"].includes("google.com.hk"))) isCN = true;
        if (body.includes("google.cn") || (body.includes("中国") && body.includes("来自你的 IP 地址"))) isCN = true;
        const msg = isCN ? "🔴 警告: 当前节点已被 Google 判定为【送中】" : "🟢 优良: 当前节点未发生 Google 送中";
        $.done({ title: "🔍 Google 搜索地域排查", message: msg, content: msg });
    } else $.done({ title: "Google 搜索排查", message: "⚠️ 连接超时。", content: "超时" });
});

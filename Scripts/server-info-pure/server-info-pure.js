/**
 * 节点纯净度与 IP 详细信息检测 (Quantumult X 兜底自愈组件)
 */
const $ = {
    get: (url, cb) => $httpClient.get(url, cb),
    done: (val) => $done(val)
};

const queryUrl = "http://ip-api.com/json/?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query";

$.get(queryUrl, (err, resp, body) => {
    if (err) {
        $.done({ "title": "节点纯净度检测", "content": "⚠️ 请求超时，无法获取节点出口数据" });
    } else {
        try {
            const data = JSON.parse(body);
            if (data.status === "success") {
                const title = `🌐 ${data.country} - ${data.city}`;
                const content = `IP: ${data.query}\nISP: ${data.isp}\n组织: ${data.org || data.as}\n时区: ${data.timezone}`;
                $.done({ "title": title, "content": content });
            } else {
                $.done({ "title": "节点纯净度检测", "content": `查询失败: ${data.message || '未知错误'}` });
            }
        } catch (e) {
            $.done({ "title": "节点纯净度检测", "content": `解析异常: ${e.message}` });
        }
    }
});

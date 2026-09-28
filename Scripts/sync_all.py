#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
import urllib.request
from datetime import datetime, timezone, timedelta

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_data(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

def fetch_binary(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception:
        return None

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def write_binary(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)

def extract_header_meta(file_path):
    meta = {}
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for _ in range(10):
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if line.startswith("#") or line.startswith(";"):
                    m_tag = re.search(r"(?:tag|标签)\s*[:=]\s*(.+)", line, re.IGNORECASE)
                    if m_tag and "tag" not in meta:
                        meta["tag"] = m_tag.group(1).strip()
                    m_pol = re.search(r"(?:policy|策略)\s*[:=]\s*(.+)", line, re.IGNORECASE)
                    if m_pol and "policy" not in meta:
                        meta["policy"] = m_pol.group(1).strip()
    except Exception:
        pass
    return meta

RULES_MAP = {
    "Google 全家桶": ["Gemini", "GoogleVoice", "YouTube", "GooglePlay", "GoogleDrive", "GoogleMaps", "Google"],
    "AI 智能助手": ["OpenAI", "Claude"],
    "Crypto 加密货币": ["OKX", "Binance", "Bybit", "Bitget", "Gate", "Crypto"],
    "Finance 金融支付": ["Wise", "Stripe", "PayPal"],
    "Social 社交通讯": ["Telegram", "Twitter", "Discord", "Reddit"],
    "Media 流媒体服务": ["Spotify", "Netflix", "Disney"],
    "Developer 开发者与科技": ["GitHub", "Docker", "Microsoft"],
    "Apple 苹果生态精细分流": ["AppleTV", "AppleProxy", "AppleCN", "Apple"],
    "Privacy 隐私过滤": ["Advertising"]
}

NAME_ALIAS = {
    "gemini": "Gemini", "googlevoice": "GoogleVoice", "googleplay": "GooglePlay",
    "googledrive": "GoogleDrive", "googlemaps": "GoogleEarth", "gate": "GateIO",
    "appletv": "AppleTV", "appleproxy": "AppleProxy", "applecn": "AppleCN", "apple": "Apple"
}

POLICY_MAPPING = {
    "unbreak": "direct", "advertising": "reject", "china": "direct", "wechat": "direct",
    "okx": "okx", "binance": "binance", "bybit": "bybit", "bitget": "bitget", "gate": "gate",
    "crypto": "crypto", "gemini": "AI-Auto", "openai": "AI-Auto", "claude": "AI-Auto",
    "google": "google", "googlevoice": "bitsflow", "telegram": "telegram", "twitter": "美国节点",
    "tiktok": "TikTok", "youtube": "海外视频", "netflix": "海外视频", "disney": "海外视频",
    "spotify": "海外视频", "appletv": "海外视频", "appleproxy": "美国节点", "applecn": "direct",
    "apple": "苹果服务", "hkbanks": "direct", "custom": "自动选择"
}

RULE_META = {
    "unbreak": ("🛡️ 节点防断流与系统修正", "direct", 1),
    "advertising": ("🚫 广告与行为追踪拦截", "reject", 2),
    "openai": ("🧠 OpenAI (ChatGPT)", "AI-Auto", 10),
    "claude": ("🎭 Claude (Anthropic)", "AI-Auto", 11),
    "gemini": ("✨ Google Gemini AI", "AI-Auto", 12),
    "okx": ("🪙 欧易 OKX 交易所", "okx", 20),
    "binance": ("🪙 币安 Binance 交易所", "binance", 21),
    "bybit": ("🪙 Bybit 交易所", "bybit", 22),
    "bitget": ("🪙 Bitget 交易所", "bitget", 23),
    "gate": ("🪙 Gate.io 芝麻开门", "gate", 24),
    "crypto": ("⛓️ Web3 钱包与基础设施", "crypto", 25),
    "youtube": ("🎬 油管 YouTube (含推流CDN)", "海外视频", 30),
    "netflix": ("🍿 奈飞 Netflix 影音", "海外视频", 31),
    "disney": ("🏰 迪士尼 Disney+ 影音", "海外视频", 32),
    "spotify": ("🎵 声网 Spotify 音乐", "海外视频", 33),
    "tiktok": ("🎵 TikTok 国际版短视频", "TikTok", 34),
    "globalmedia": ("📺 海外主流流媒体合集", "自动选择", 35),
    "telegram": ("✈️ 电报 Telegram 通讯", "telegram", 40),
    "twitter": ("🐦 推特 Twitter / X", "美国节点", 41),
    "discord": ("💬 Discord 语音社区", "自动选择", 42),
    "reddit": ("🤖 红迪 Reddit 社区", "自动选择", 43),
    "googlemaps": ("🗺️ 谷歌地图与瓦片切片", "自动选择", 50),
    "googlevoice": ("📞 Google Voice 虚拟号码", "bitsflow", 51),
    "googledrive": ("💾 Google 云端硬盘 Drive", "自动选择", 52),
    "github": ("🐙 GitHub 开发者代码仓", "自动选择", 53),
    "docker": ("🐳 Docker 容器与镜像源", "自动选择", 54),
    "microsoft": ("💻 微软服务与 Office", "自动选择", 55),
    "wise": ("💱 Wise 跨国跨境汇款", "自动选择", 60),
    "paypal": ("💳 贝宝 PayPal 国际支付", "自动选择", 61),
    "stripe": ("💳 Stripe 跨境支付网关", "自动选择", 62),
    "hkbanks": ("🏦 HK_Banks", "direct", 63),
    "google": ("🔍 Google 搜索与基础生态", "google", 70),
    "appletv": ("📺 Apple TV+ 影音点播", "海外视频", 77),
    "appleproxy": ("🍎 Apple 海外受限服务", "美国节点", 78),
    "applecn": ("🍏 Apple 境内直连加速", "direct", 79),
    "apple": ("🍎 苹果官方生态服务", "苹果服务", 80),
    "wechat": ("💬 微信与腾讯直连通信", "direct", 90),
    "china": ("🇨🇳 大陆直连域名大合集", "direct", 100),
    "custom": ("🌐 个人私有自定义规则", "自动选择", 110)
}

REWRITE_META = {
    "youtubeads": ("🎬 YouTube 去广告与视频流优化 (Maasea)", True),
    "boxjs": ("📦 BoxJS 脚本与数据管理面板", True),
    "substore": ("🧰 Sub-Store 节点订阅转换核心", True),
    "forownuse": ("⚙️ 个人自用定制扩展模块", True),
    "q-search": ("🔍 Q-Search 浏览器快捷搜索增强", True),
    "googlecaptcha": ("🛡️ 谷歌人机验证自动放行", True),
    "unblockurlinwechat": ("🔓 微信外链自动解除拦截直开", True),
    "applet": ("📱 微信小程序去广告与纯净体验", True),
    "weiboads": ("👁️ 新浪微博去广告与信息流净化", True),
    "tiebaads": ("💬 百度贴吧去广告与帖内净化", True),
    "goofishads": ("🐟 闲鱼去广告与推荐流净化", True),
    "cainiaoads": ("📦 菜鸟裹裹开屏与包裹广告拦截", True),
    "amapads": ("🗺️ 高德地图去广告与首页精简", True),
    "caiyunads": ("🌤️ 彩云天气去广告与免打扰", True),
    "qishuimusicads": ("🎵 汽水音乐去广告与收听净化", True),
    "soul": ("👻 Soul 社交开屏与动态广告拦截", True),
    "thly": ("🎙️ 通话录音功能扩展模块", True),
    "startupads": ("🚫 全局 App 开屏广告通用拦截", False),
    "wloc": ("📍 虚拟定位与位置信息修正模块", False),
}

def compile_rules():
    print("🚀 正在抓取并全量编译分流规则...")
    acl4ssr_raw = fetch_data("https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Cryptocurrency.list")
    if acl4ssr_raw:
        qx_lines = ["# ACL4SSR Crypto 规则库\n# tag: ⛓️ Web3 钱包与基础设施\n# policy: crypto\n"]
        stash_lines = ["payload:"]
        for raw_line in acl4ssr_raw.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) >= 2:
                r_type, target = parts[0].strip().upper(), parts[1].strip()
                qx_type = r_type.replace("DOMAIN-SUFFIX", "HOST-SUFFIX").replace("DOMAIN-KEYWORD", "HOST-KEYWORD").replace("DOMAIN", "HOST")
                stash_type = r_type.replace("HOST-SUFFIX", "DOMAIN-SUFFIX").replace("HOST-KEYWORD", "DOMAIN-KEYWORD").replace("HOST", "DOMAIN")
                qx_lines.append(f"{qx_type},{target}")
                stash_lines.append(f"  - {stash_type},{target}")
        write_file("rule/QuantumultX/crypto.list", "\n".join(qx_lines) + "\n")
        write_file("rule/Stash/crypto.yaml", "\n".join(stash_lines) + "\n")

    maps_rules = [
        "HOST-SUFFIX,maps.google.com", "HOST-SUFFIX,maps.googleapis.com",
        "HOST-SUFFIX,lh3.googleusercontent.com", "HOST-SUFFIX,lh4.googleusercontent.com",
        "HOST-SUFFIX,lh5.googleusercontent.com", "HOST-SUFFIX,lh6.googleusercontent.com",
        "HOST-SUFFIX,ggpht.com", "HOST-SUFFIX,photos.l.google.com",
        "HOST-KEYWORD,mapcontent", "HOST-KEYWORD,maps.gstatic.com"
    ]
    write_file("rule/QuantumultX/googlemaps.list", "\n".join(["# Google Maps 专用规则\n# tag: 🗺️ 谷歌地图与瓦片切片\n# policy: 自动选择\n"] + maps_rules) + "\n")
    write_file("rule/Stash/googlemaps.yaml", "\n".join(["payload:"] + [f"  - {r.replace('HOST-SUFFIX', 'DOMAIN-SUFFIX').replace('HOST-KEYWORD', 'DOMAIN-KEYWORD')}" for r in maps_rules]) + "\n")

    for _, items in RULES_MAP.items():
        for name in items:
            fname = name.lower()
            if fname in ["crypto", "googlemaps"]:
                continue
            up_name = NAME_ALIAS.get(fname, name)
            candidates = [up_name, up_name.lower(), up_name.capitalize()]
            if fname == "applecn":
                candidates.extend(["AppleCN", "apple-cn", "Apple-CN", "Apple/AppleCN"])
            elif fname == "appleproxy":
                candidates.extend(["AppleProxy", "apple-proxy", "Apple-Proxy", "Apple/AppleProxy"])
            elif fname == "appletv":
                candidates.extend(["AppleTV", "apple-tv", "Apple-TV", "Apple/AppleTV"])

            qx_content = None
            for cand in dict.fromkeys(candidates):
                qx_url = f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/QuantumultX/{cand}/{cand}.list"
                qx_content = fetch_data(qx_url)
                if qx_content:
                    break

            if not qx_content:
                if fname == "googlevoice":
                    qx_content = "HOST,voice.google.com\nHOST,voice.telephony.goog\nHOST-SUFFIX,voice.google.com\nHOST-KEYWORD,voice.telephony"
                elif fname == "wise":
                    qx_content = "HOST-SUFFIX,wise.com\nHOST-SUFFIX,transferwise.com\nHOST-SUFFIX,wise-pay.com\nHOST-KEYWORD,wise-cdn"
                elif fname == "bybit":
                    qx_content = "HOST-SUFFIX,bybit.com\nHOST-SUFFIX,bybit-global.com\nHOST-SUFFIX,bytick.com\nHOST-KEYWORD,bybit"
                elif fname == "bitget":
                    qx_content = "HOST-SUFFIX,bitget.com\nHOST-SUFFIX,bitget.site\nHOST-SUFFIX,bgstatic.com\nHOST-KEYWORD,bitget"
                elif fname == "gate":
                    qx_content = "HOST-SUFFIX,gate.io\nHOST-SUFFIX,gateimg.com\nHOST-SUFFIX,gateio.services\nHOST-KEYWORD,gateio"
            if qx_content:
                write_file(f"rule/QuantumultX/{fname}.list", qx_content)

            stash_content = None
            for cand in dict.fromkeys(candidates):
                stash_url = f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{cand}/{cand}.yaml"
                stash_content = fetch_data(stash_url)
                if stash_content:
                    break

            if not stash_content:
                if fname == "googlevoice":
                    stash_content = "payload:\n  - DOMAIN,voice.google.com\n  - DOMAIN,voice.telephony.goog\n  - DOMAIN-SUFFIX,voice.google.com\n  - DOMAIN-KEYWORD,voice.telephony"
                elif fname == "wise":
                    stash_content = "payload:\n  - DOMAIN-SUFFIX,wise.com\n  - DOMAIN-SUFFIX,transferwise.com\n  - DOMAIN-SUFFIX,wise-pay.com\n  - DOMAIN-KEYWORD,wise-cdn"
                elif fname == "bybit":
                    stash_content = "payload:\n  - DOMAIN-SUFFIX,bybit.com\n  - DOMAIN-SUFFIX,bybit-global.com\n  - DOMAIN-SUFFIX,bytick.com\n  - DOMAIN-KEYWORD,bybit"
                elif fname == "bitget":
                    stash_content = "payload:\n  - DOMAIN-SUFFIX,bitget.com\n  - DOMAIN-SUFFIX,bitget.site\n  - DOMAIN-SUFFIX,bgstatic.com\n  - DOMAIN-KEYWORD,bitget"
                elif fname == "gate":
                    stash_content = "payload:\n  - DOMAIN-SUFFIX,gate.io\n  - DOMAIN-SUFFIX,gateimg.com\n  - DOMAIN-SUFFIX,gateio.services\n  - DOMAIN-KEYWORD,gateio"
            if stash_content:
                write_file(f"rule/Stash/{fname}.yaml", stash_content)

    execution_order = [
        "gemini", "openai", "claude", "googlevoice",
        "youtube", "spotify", "netflix", "disney", "appletv",
        "googlemaps", "googleplay", "googledrive", "google",
        "okx", "binance", "bybit", "bitget", "gate", "crypto",
        "wise", "stripe", "paypal", "hkbanks",
        "telegram", "twitter", "discord", "reddit",
        "github", "docker", "microsoft",
        "appleproxy", "applecn", "apple",
        "advertising"
    ]
    qx_master = ["# Quantumult X 全量自动化集成规则表\n"]
    for item in execution_order:
        qx_path = f"rule/QuantumultX/{item}.list"
        policy = POLICY_MAPPING.get(item, "全球代理")
        if os.path.exists(qx_path):
            with open(qx_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    l = line.strip()
                    if not l or l.startswith("#"):
                        continue
                    qx_master.append(f"{l}, {policy}")
    write_file("rule/QuantumultX/all.list", "\n".join(qx_master) + "\n")
    print("✅ 聚合规则 all.list 已生成！")

def sync_rewrites_to_stash():
    qx_rw_dir = "rewrite/QuantumultX"
    stash_rw_dir = "rewrite/Stash"
    if not os.path.exists(qx_rw_dir):
        return
    os.makedirs(stash_rw_dir, exist_ok=True)
    count_st = 0
    for fname in os.listdir(qx_rw_dir):
        if not (fname.endswith(".conf") or fname.endswith(".snippet")):
            continue
        base_name = os.path.splitext(fname)[0]
        out_file = f"{base_name}.stoverride"
        out_path = os.path.join(stash_rw_dir, out_file)
        url_rewrites, mitm_hosts, scripts = [], set(), []
        with open(os.path.join(qx_rw_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("#", ";")):
                    continue
                if line.startswith("hostname") and "=" in line:
                    hosts = line.split("=", 1)[1].strip()
                    for h in hosts.split(","):
                        h = h.strip().replace("%append%", "").strip()
                        if h:
                            mitm_hosts.add(h)
                    continue
                m = re.match(r"^(\S+)\s+url\s+(302|307|reject-200|reject-img|reject-dict|reject)\s*(\S*)", line)
                if m:
                    pat, act, tgt = m.groups()
                    if "reject" in act:
                        stash_act = act if act in ["reject", "reject-200", "reject-img", "reject-dict"] else "reject"
                        url_rewrites.append(f"  - {pat} - {stash_act}")
                    else:
                        url_rewrites.append(f"  - {pat} {tgt} {act}")
                    continue
                m_s = re.match(r"^(\S+)\s+url\s+script-([a-z\-]+)\s+(\S+)", line)
                if m_s:
                    pat, s_type, s_path = m_s.groups()
                    s_name = os.path.splitext(os.path.basename(s_path))[0]
                    scripts.append((s_name, s_type, pat, s_path))
                    
        lines = [f"# Generated from QuantumultX/{fname}", f"name: {base_name}", "http:"]
        if mitm_hosts:
            lines.append("  mitm:")
            for h in sorted(mitm_hosts):
                lines.append(f'    - "{h}"')
        if url_rewrites:
            lines.append("  url-rewrite:")
            lines.extend(url_rewrites)
        if scripts:
            lines.append("  script:")
            for s_name, s_type, pat, s_path in scripts:
                lines.append(f"    - match: {pat}\n      name: {s_name}\n      type: {s_type}\n      require-body: {'true' if 'body' in s_type else 'false'}\n      timeout: 10")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        count_st += 1
    print(f"✅ Stash 覆写文件同步完成，共更新 {count_st} 个 .stoverride 文件！")

NATIVE_SERVER_INFO_PURE_JS = r"""const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 8 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 8 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
function getFlagEmoji(countryCode) {
    if (!countryCode || countryCode.length !== 2) return "🌐";
    return String.fromCodePoint(...countryCode.toUpperCase().split("").map(c => 127397 + c.charCodeAt(0)));
}
$.get("https://ipwho.is/", (err, resp, body) => {
    if (!err && body) {
        try {
            const data = JSON.parse(body);
            if (data.success) {
                const flag = getFlagEmoji(data.country_code);
                const isHosting = data.security && data.security.hosting;
                const isProxy = data.security && (data.security.proxy || data.security.vpn || data.security.tor);
                let purityTag = isProxy ? "🔴 较低 (公开代理/高风控)" : (isHosting ? "🟡 良好 (商业机房/IDC)" : "🟢 极高 (原生家宽/住宅)");
                const lines = [
                    `📍 节点出口: ${data.ip}`,
                    `🏢 归属运营: ${data.connection ? data.connection.isp : data.isp || "未知"}`,
                    `🛡️ 纯净评级: ${purityTag}`,
                    `🏷️ 节点类型: ${isHosting ? "机房广播 (Hosting)" : "原生住宅 (Residential)"}`
                ];
                const msg = lines.join("\n");
                $.done({ title: `${flag} ${data.country} · ${data.city}`, message: msg, content: msg });
                return;
            }
        } catch (e) {}
    }
    $.done({ title: "节点纯净度体检", message: "⚠️ 请求超时，未能获取纯净度数据。", content: "超时" });
});
"""

NATIVE_AI_CHECK_JS = r"""const $ = {
    get: (url, cb) => {
        if (typeof $httpClient !== "undefined") $httpClient.get({ url: url, timeout: 6 }, cb);
        else if (typeof $task !== "undefined") $task.fetch({ url: url, timeout: 6 }).then(r => cb(null, r, r.body), e => cb(e, null, null));
    },
    done: (obj) => $done(obj)
};
let results = { openai: "⏳", claude: "⏳", gemini: "⏳" };
let doneCount = 0;
function finish() {
    doneCount++;
    if (doneCount === 3) {
        const lines = [`🧠 OpenAI (ChatGPT): ${results.openai}`, `🎭 Anthropic Claude: ${results.claude}`, `✨ Google Gemini AI: ${results.gemini}`];
        $.done({ title: "🤖 AI 智能助手可用性检测", message: lines.join("\n"), content: lines.join("\n") });
    }
}
$.get("https://chatgpt.com/cdn-cgi/trace", (err, resp, body) => {
    if (!err && resp && resp.statusCode === 200 && body) {
        const m = body.match(/loc=([A-Z]{2})/);
        results.openai = (m && (m[1] === "CN" || m[1] === "HK")) ? `🔴 不可用 (${m[1]})` : `🟢 支持访问 (${m ? m[1] : "OK"})`;
    } else results.openai = "🔴 访问受阻";
    finish();
});
$.get("https://claude.ai/login", (err, resp) => {
    if (!err && resp && (resp.statusCode === 200 || resp.statusCode === 302)) results.claude = "🟢 支持访问";
    else results.claude = "🔴 节点受限";
    finish();
});
$.get("https://gemini.google.com/", (err, resp) => {
    if (!err && resp && (resp.statusCode === 200 || resp.statusCode === 302)) results.gemini = "🟢 支持访问";
    else results.gemini = "🔴 地区暂不支持";
    finish();
});
"""

NATIVE_CRYPTO_CHECK_JS = r"""const $ = {
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
"""

NATIVE_GOOGLE_CHECK_JS = r"""const $ = {
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
"""

def sync_all_five_scripts_and_icons():
    # 用户 Pro 版脚本已锁定，保留现有文件不予覆盖
    pass

def assemble_quantumultx_conf(repo_user="Mygodsss", repo_name="wang47"):
    qx_conf_path = "Profiles/QuantumultX.conf"
    if not os.path.exists(qx_conf_path):
        return
    with open(qx_conf_path, "r", encoding="utf-8") as f:
        conf_text = f.read()

    filter_remotes = []
    qx_rule_dir = "rule/QuantumultX"
    if os.path.exists(qx_rule_dir):
        all_rules = [f[:-5] for f in os.listdir(qx_rule_dir) if f.endswith(".list") and f != "all.list"]
        sorted_rules = sorted(all_rules, key=lambda x: RULE_META.get(x, (x, "自动选择", 999))[2])
        for r in sorted_rules:
            if r.lower() in ["coinbase", "kraken", "custom"] and r != "custom":
                continue
            file_path = os.path.join(qx_rule_dir, f"{r}.list")
            header_meta = extract_header_meta(file_path)
            chinese_tag = header_meta["tag"] if "tag" in header_meta else (RULE_META[r][0] if r in RULE_META else f"🌐 {r.capitalize()}")
            target_policy = header_meta["policy"] if "policy" in header_meta else (RULE_META[r][1] if r in RULE_META else POLICY_MAPPING.get(r, "自动选择"))
            filter_remotes.append(f"https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/rule/QuantumultX/{r}.list, tag={chinese_tag}, force-policy={target_policy}, update-interval=172800, opt-parser=true, enabled=true")

    if filter_remotes and "[filter_remote]" in conf_text:
        conf_text = re.sub(r"(\[filter_remote\]\n)(.*?)(?=\n\[|\Z)", r"\1" + "\n".join(filter_remotes) + "\n", conf_text, flags=re.DOTALL)

    rewrite_remotes = []
    qx_rw_dir = "rewrite/QuantumultX"
    if os.path.exists(qx_rw_dir):
        for f_name in sorted(os.listdir(qx_rw_dir)):
            if not (f_name.endswith(".conf") or f_name.endswith(".snippet")):
                continue
            base = os.path.splitext(f_name)[0]
            chinese_tag = REWRITE_META.get(base.lower(), (f"🧩 {base}", True))[0]
            is_enabled = "true" if REWRITE_META.get(base.lower(), (None, True))[1] else "false"
            rewrite_remotes.append(f"https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/rewrite/QuantumultX/{f_name}, tag={chinese_tag}, update-interval=86400, opt-parser=true, enabled={is_enabled}")

    if rewrite_remotes and "[rewrite_remote]" in conf_text:
        conf_text = re.sub(r"(\[rewrite_remote\]\n)(.*?)(?=\n\[|\Z)", r"\1" + "\n".join(rewrite_remotes) + "\n", conf_text, flags=re.DOTALL)

    five_tasks = [
        f"event-interaction https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/streaming-ui-check/streaming-ui-check.js, tag=流媒体解锁查询, img-url=https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/streaming-ui-check/icon.png, enabled=true",
        f"event-interaction https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/server-info-pure/server-info-pure.js, tag=节点纯净度详情, img-url=https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/server-info-pure/icon.png, enabled=true",
        f"event-interaction https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/ai-check/ai-check.js, tag=AI智能助手诊断, img-url=https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/ai-check/icon.png, enabled=true",
        f"event-interaction https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/google-check/google-check.js, tag=Google送中排查, img-url=https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/google-check/icon.png, enabled=true",
        f"event-interaction https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/crypto-check/crypto-check.js, tag=交易所合规排查, img-url=https://raw.githubusercontent.com/{repo_user}/{repo_name}/main/Scripts/crypto-check/icon.png, enabled=true"
    ]
    task_keys = ["streaming-ui-check", "server-info-pure", "ai-check", "crypto-check", "google-check", "流媒体解锁", "节点纯净度", "送中", "交易所合规", "AI智能助手"]
    clean_lines = [l for l in conf_text.splitlines() if not any(k in l for k in task_keys)]
    conf_text = "\n".join(clean_lines)

    task_block = "\n".join(five_tasks)
    if "[task_local]" in conf_text:
        conf_text = re.sub(r"(\[task_local\]\n)", rf"\1{task_block}\n", conf_text)
    else:
        conf_text += f"\n\n[task_local]\n{task_block}\n"

    all_qx_mitm_hosts = set()
    junk_pattern = re.compile(
        r"(\.top|\.xyz|\.work|\.vip|\.ltd|bspapp\.com|jxjt888|syshhc|heikeji|laoguikeji|benbenfx|i3zh|bbkj|bpojie|xgjyouhui|guilaile|gongzijx|hkj178|iosoi|lysl2020|xianbaow|blibee|enmonster|caixin|sf-express|taobao\.com|ls\.apple\.com)",
        re.IGNORECASE
    )
    if os.path.exists(qx_rw_dir):
        for f in os.listdir(qx_rw_dir):
            if f.endswith((".conf", ".snippet")):
                with open(os.path.join(qx_rw_dir, f), "r", encoding="utf-8", errors="ignore") as rf:
                    for line in rf:
                        if line.strip().startswith("hostname") and "=" in line:
                            hosts = line.split("=", 1)[1].strip()
                            for h in hosts.split(","):
                                h = h.strip().replace("%append%", "").strip()
                                if not h:
                                    continue
                                parts = [p.strip("() ") for p in h.split("|") if p.strip("() ") and not p.strip("() ").startswith(".*")] if ("(" in h or ")" in h or "|" in h) else [h]
                                for sh in parts:
                                    sh = sh.strip()
                                    if sh == "www.google.com*": sh = "www.google.*"
                                    if sh and not junk_pattern.search(sh): all_qx_mitm_hosts.add(sh)

    if all_qx_mitm_hosts:
        sorted_mitm = ", ".join(sorted(all_qx_mitm_hosts))
        if "[mitm]" in conf_text:
            if re.search(r"hostname\s*=", conf_text):
                conf_text = re.sub(r"hostname\s*=.*", f"hostname = {sorted_mitm}", conf_text)
            else:
                conf_text = conf_text.replace("[mitm]", f"[mitm]\nhostname = {sorted_mitm}")
        else:
            conf_text += f"\n\n[mitm]\nhostname = {sorted_mitm}\n"

    conf_text = conf_text.replace("static=google, direct, proxy, reject,", "static=google, direct, reject, 全球代理,")
    with open(qx_conf_path, "w", encoding="utf-8") as f:
        f.write(conf_text)
    shutil.copy(qx_conf_path, "QuantumultX.conf")
    print("✅ Profiles/QuantumultX.conf 的 5 项交互任务与根目录镜像同步完成！")

def sync_stash_rules_and_profile(qx_rule_dir="rule/QuantumultX", stash_rule_dir="rule/Stash", stash_conf_path="Profiles/Stash.yaml"):
    if not os.path.exists(stash_rule_dir):
        os.makedirs(stash_rule_dir, exist_ok=True)
    if not os.path.exists(qx_rule_dir):
        return
    all_rules = [f[:-5] for f in os.listdir(qx_rule_dir) if f.endswith(".list") and f != "all.list"]
    for r in all_rules:
        qx_file = os.path.join(qx_rule_dir, f"{r}.list")
        stash_file = os.path.join(stash_rule_dir, f"{r}.yaml")
        payload = []
        with open(qx_file, "r", encoding="utf-8", errors="ignore") as rf:
            for l in rf:
                l = l.strip()
                if not l or l.startswith(("#", ";", "//")):
                    continue
                parts = [p.strip() for p in l.split(",")]
                if len(parts) >= 2:
                    t, target = parts[0].upper(), parts[1]
                    if t in ["HOST-SUFFIX", "HOST_SUFFIX"]:
                        payload.append(f"  - DOMAIN-SUFFIX,{target}")
                    elif t in ["HOST", "HOST-KEYWORD", "HOST_KEYWORD"]:
                        payload.append(f"  - {'DOMAIN' if t == 'HOST' else 'DOMAIN-KEYWORD'},{target}")
                    elif t in ["IP-CIDR", "IP-CIDR6"]:
                        extra = ",no-resolve" if "no-resolve" in [p.lower() for p in parts] else ""
                        payload.append(f"  - {t},{target}{extra}")
                    elif t == "USER-AGENT":
                        payload.append(f"  - USER-AGENT,{target}")
        with open(stash_file, "w", encoding="utf-8") as wf:
            wf.write("payload:\n" + "\n".join(payload) + "\n")
    print(f"✅ 已全自动将 {len(all_rules)} 份 QX 分流规则编译为 Stash YAML 规则集！")

    if os.path.exists(stash_conf_path):
        with open(stash_conf_path, "r", encoding="utf-8") as sf:
            s_text = sf.read()
        sorted_rules = sorted(all_rules, key=lambda x: RULE_META.get(x, (x, "自动选择", 999))[2])
        providers, rules = ["rule-providers:"], ["rules:"]
        for r in sorted_rules:
            _, policy, _ = RULE_META.get(r, (r, "自动选择", 999))
            providers.extend([f"  {r}:", f"    type: http", f"    behavior: classical", f'    url: "https://raw.githubusercontent.com/Mygodsss/wang47/main/rule/Stash/{r}.yaml"', f"    path: ./ruleset/{r}.yaml", f"    interval: 86400"])
            rules.append(f"  - RULE-SET,{r},{policy}")
        rules.extend(["  - GEOIP,CN,DIRECT", "  - MATCH,兜底分流"])
        s_text = re.sub(r"rule-providers:[\s\S]*?(?=\nrules:|\nproxy-groups:|\n\[|\Z)", "\n".join(providers) + "\n", s_text)
        s_text = re.sub(r"rules:[\s\S]*?(?=\nproxy-groups:|\nrule-providers:|\n\[|\Z)", "\n".join(rules) + "\n", s_text)
        with open(stash_conf_path, "w", encoding="utf-8") as sf:
            sf.write(s_text)
        if os.path.exists("Stash.yaml"):
            shutil.copy(stash_conf_path, "Stash.yaml")
        print("🎉 Profiles/Stash.yaml 的 rule-providers 与 rules 规则链已全自动对齐！")

def update_readme_markdown(qx_rule_dir="rule/QuantumultX", readme_path="README.md"):
    if not os.path.exists(readme_path):
        return
    tz = timezone(timedelta(hours=8))
    now_str = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    with open(readme_path, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"(自动更新时间\s*[:：]\s*`?)\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(`?)", rf"\g<1>{now_str}\2", text)
    if os.path.exists(qx_rule_dir):
        all_rules = [f[:-5] for f in os.listdir(qx_rule_dir) if f.endswith(".list") and f != "all.list"]
        sorted_rules = sorted(all_rules, key=lambda x: RULE_META.get(x, (x, "自动选择", 999))[2])
        rows = []
        for r in sorted_rules:
            fp = os.path.join(qx_rule_dir, f"{r}.list")
            cnt = sum(1 for l in open(fp, "r", encoding="utf-8", errors="ignore") if l.strip() and not l.strip().startswith(("#", ";")))
            tag, policy, _ = RULE_META.get(r, (f"🌐 {r}", "自动选择", 999))
            rows.append(f"| {tag} | `{cnt}` 条 | `{policy}` | [查看规则](rule/QuantumultX/{r}.list) |")
        table_str = "\n".join(["| 分流业务标签 | 规则行数 | 默认绑定策略 | 规则直链 |", "| :--- | :---: | :--- | :--- |"] + rows)
        if "<!-- RULE_TABLE_START -->" in text and "<!-- RULE_TABLE_END -->" in text:
            text = re.sub(r"<!-- RULE_TABLE_START -->[\s\S]*?<!-- RULE_TABLE_END -->", f"<!-- RULE_TABLE_START -->\n{table_str}\n<!-- RULE_TABLE_END -->", text)

    if os.path.exists("rewrite/QuantumultX"):
        qx_rw_files = sorted([f for f in os.listdir("rewrite/QuantumultX") if f.endswith((".conf", ".snippet"))])
        if qx_rw_files:
            qx_rows = ["| 模块功能 | 文件类型 | 原生直链订阅地址 |", "| :--- | :---: | :--- |"]
            for rf in qx_rw_files:
                bname = os.path.splitext(rf)[0]
                tag = REWRITE_META.get(bname.lower(), (f"🧩 {bname}", True))[0]
                qx_rows.append(f"| **{tag}** | `{rf.split('.')[-1].upper()}` | [{rf}](https://raw.githubusercontent.com/Mygodsss/wang47/main/rewrite/QuantumultX/{rf}) |")
            pat_qx = r"(### Quantumult X 专属重写模块.*?\n\n)([\s\S]*?)(?=\n### Stash 专属覆写模块|\n---\n|\Z)"
            if re.search(pat_qx, text):
                text = re.sub(pat_qx, rf"\g<1>{chr(10).join(qx_rows)}\n\n", text)

    if os.path.exists("rewrite/Stash"):
        st_rw_files = sorted([f for f in os.listdir("rewrite/Stash") if f.endswith(".stoverride")])
        if st_rw_files:
            st_rows = ["| 模块功能 | 适用格式 | Stash 原生覆写订阅直链 |", "| :--- | :---: | :--- |"]
            for sf in st_rw_files:
                bname = sf.replace(".stoverride", "")
                tag = REWRITE_META.get(bname.lower(), (f"🧩 {bname}", True))[0]
                st_rows.append(f"| **{tag}** | `.stoverride` | [{sf}](https://raw.githubusercontent.com/Mygodsss/wang47/main/rewrite/Stash/{sf}) |")
            pat_st = r"(### Stash 专属覆写模块.*?\n\n)([\s\S]*?)(?=\n---\n|\n### 🛠️ 懒人|\Z)"
            if re.search(pat_st, text):
                text = re.sub(pat_st, rf"\g<1>{chr(10).join(st_rows)}\n\n", text)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"🎉 README.md 已自动对齐最新时间戳 [{now_str}] 与全量三端表格！")

if __name__ == "__main__":
    compile_rules()
    sync_rewrites_to_stash()
    # 脚本已被用户 Pro 版锁定，跳过覆盖
    assemble_quantumultx_conf(repo_user="Mygodsss", repo_name="wang47")
    sync_stash_rules_and_profile()
    update_readme_markdown()
    print("\n🚀 [All Done] Wang47 5 项检测脚本与双端规则引擎全量自动化同步执行完毕！")

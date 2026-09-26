import os
import urllib.request
from datetime import datetime

RULES_MAP = {
    "Google 全家桶": ["Gemini", "GoogleVoice", "YouTube", "GooglePlay", "GoogleDrive", "GoogleMaps", "Google"],
    "AI 智能助手": ["OpenAI", "Claude"],
    "Crypto 加密货币": ["OKX", "Binance", "Bybit", "Bitget", "Gate", "Coinbase", "Kraken", "Crypto"],
    "Finance 金融支付": ["Wise", "Stripe", "PayPal"],
    "Social 社交通讯": ["Telegram", "Twitter", "Discord", "Reddit"],
    "Media 流媒体服务": ["Spotify", "Netflix", "Disney"],
    "Developer 开发者与科技": ["GitHub", "Docker", "Apple", "Microsoft"],
    "Privacy 隐私过滤": ["Advertising"]
}

NAME_ALIAS = {
    "gemini": "Gemini",
    "googlevoice": "GoogleVoice",
    "googleplay": "GooglePlay",
    "googledrive": "GoogleDrive",
    "googlemaps": "GoogleEarth",
    "coinbase": "Cryptocurrency",
    "kraken": "Cryptocurrency",
    "gate": "GateIO"
}

POLICY_MAPPING = {
    "unbreak": "direct",
    "advertising": "reject",
    "china": "direct",
    "wechat": "direct",
    "okx": "okx",
    "binance": "binance",
    "bybit": "bybit",
    "bitget": "bitget",
    "gate": "gate",
    "coinbase": "crypto",
    "kraken": "crypto",
    "crypto": "crypto",
    "gemini": "AI-Auto",
    "openai": "AI-Auto",
    "claude": "AI-Auto",
    "google": "google",
    "googlevoice": "bitsflow",
    "telegram": "telegram",
    "twitter": "美国节点",
    "tiktok": "TikTok",
    "apple": "苹果服务",
    "youtube": "海外视频",
    "netflix": "海外视频",
    "disney": "海外视频",
    "spotify": "海外视频",
}

WORKER_HOST = "https://rule-proxy.mygods.workers.dev"
headers = {"User-Agent": "Mozilla/5.0"}

def fetch_data(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except:
        return None

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("🚀 正在抓取并自动编译规则...")

acl4ssr_raw = fetch_data("https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Cryptocurrency.list")
if acl4ssr_raw:
    qx_lines = ["# ACL4SSR Crypto 规则库"]
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

MAPS_RULES = [
    "HOST-SUFFIX,maps.google.com", "HOST-SUFFIX,maps.googleapis.com",
    "HOST-SUFFIX,lh3.googleusercontent.com", "HOST-SUFFIX,lh4.googleusercontent.com",
    "HOST-SUFFIX,lh5.googleusercontent.com", "HOST-SUFFIX,lh6.googleusercontent.com",
    "HOST-SUFFIX,ggpht.com", "HOST-SUFFIX,photos.l.google.com",
    "HOST-KEYWORD,mapcontent", "HOST-KEYWORD,maps.gstatic.com"
]
write_file("rule/QuantumultX/googlemaps.list", "\n".join(["# Google Maps 专用规则"] + MAPS_RULES) + "\n")
write_file("rule/Stash/googlemaps.yaml", "\n".join(["payload:"] + [f"  - {r.replace('HOST-SUFFIX', 'DOMAIN-SUFFIX').replace('HOST-KEYWORD', 'DOMAIN-KEYWORD')}" for r in MAPS_RULES]) + "\n")

for cat, items in RULES_MAP.items():
    for name in items:
        fname = name.lower()
        if fname in ["crypto", "googlemaps"]:
            continue
        up_name = NAME_ALIAS.get(fname, name)

        qx_url = f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/QuantumultX/{up_name}/{up_name}.list"
        qx_content = fetch_data(qx_url)
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

        stash_url = f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{up_name}/{up_name}.yaml"
        stash_content = fetch_data(stash_url)
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

EXECUTION_ORDER = [
    "gemini", "openai", "claude",
    "googlevoice",
    "youtube", "spotify", "netflix", "disney",
    "googlemaps", "googleplay", "googledrive",
    "google",
    "okx", "binance", "bybit", "bitget", "gate", "coinbase", "kraken", "crypto",
    "wise", "stripe", "paypal",
    "telegram", "twitter", "discord", "reddit",
    "github", "docker", "apple", "microsoft",
    "advertising"
]

qx_master = ["# Quantumult X 全量自动化集成规则表 (由 GitHub Actions 每日编译维护)\n"]
for item in EXECUTION_ORDER:
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

# ==========================================
# 自动同步 Quantumult X 重写到 Stash 覆写 (.stoverride)
# ==========================================
import re

qx_rw_dir = "rewrite/QuantumultX"
stash_rw_dir = "rewrite/Stash"
if os.path.exists(qx_rw_dir):
    os.makedirs(stash_rw_dir, exist_ok=True)
    count_st = 0
    for fname in os.listdir(qx_rw_dir):
        if not (fname.endswith(".conf") or fname.endswith(".snippet")):
            continue
        base_name = os.path.splitext(fname)[0]
        out_file = f"{base_name}.stoverride"
        out_path = os.path.join(stash_rw_dir, out_file)
        
        url_rewrites = []
        mitm_hosts = set()
        scripts = []
        
        with open(os.path.join(qx_rw_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("#", ";")):
                    continue
                if line.startswith("hostname") and "=" in line:
                    hosts = line.split("=", 1)[1].strip()
                    for h in hosts.split(","):
                        h = h.strip()
                        if h:
                            mitm_hosts.add(h)
                    continue
                m = re.match(r"^(\S+)\s+url\s+(302|307|reject-200|reject-img|reject-dict|reject)\s*(\S*)", line)
                if m:
                    pat, act, tgt = m.groups()
                    if "reject" in act:
                        url_rewrites.append(f"  - {pat} - reject")
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
                lines.append(f"    - match: {pat}")
                lines.append(f"      name: {s_name}")
                lines.append(f"      type: {s_type}")
                lines.append(f"      require-body: true")
                lines.append(f"      timeout: 10")
                
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        count_st += 1
    print(f"✅ Stash 覆写文件同步完成，共更新 {count_st} 个 .stoverride 文件！")

# ==============================================================================
# 全自动化目录联动总控 (Profiles/QuantumultX.conf & README.md 动态维护)
# ==============================================================================
import re

# 1. 动态生成并更新 Profiles/QuantumultX.conf
qx_conf_path = "Profiles/QuantumultX.conf"
if os.path.exists(qx_conf_path):
    with open(qx_conf_path, "r", encoding="utf-8") as f:
        conf_text = f.read()

    # 动态装配 [filter_remote] (按严格业务优先级 + 中文语义化标签)
    filter_remotes = []
    qx_rule_dir = "rule/QuantumultX"

    # 规则元数据配置: (中文标签, 绑定策略, 优先级权重数值越小越靠前)
    RULE_META = {
        # 1. 核心底层拦截与防断流
        "unbreak": ("🛡️ 节点防断流与系统修正", "direct", 1),
        "advertising": ("🚫 广告与行为追踪拦截", "reject", 2),

        # 2. AI 大模型矩阵 (绝对优先于通用 Google)
        "openai": ("🧠 OpenAI (ChatGPT)", "AI-Auto", 10),
        "claude": ("🎭 Claude (Anthropic)", "AI-Auto", 11),
        "gemini": ("✨ Google Gemini AI", "AI-Auto", 12),

        # 3. 交易所与 Web3 生态
        "okx": ("🪙 欧易 OKX 交易所", "okx", 20),
        "binance": ("🪙 币安 Binance 交易所", "binance", 21),
        "bybit": ("🪙 Bybit 交易所", "bybit", 22),
        "bitget": ("🪙 Bitget 交易所", "bitget", 23),
        "gate": ("🪙 Gate.io 芝麻开门", "gate", 24),
        "coinbase": ("🪙 Coinbase 交易所", "crypto", 25),
        "kraken": ("🪙 Kraken 海妖交易所", "crypto", 26),
        "crypto": ("⛓️ Web3 钱包与基础设施", "crypto", 27),

        # 4. 音视频海外流媒体
        "youtube": ("🎬 油管 YouTube (含推流CDN)", "海外视频", 30),
        "netflix": ("🍿 奈飞 Netflix 影音", "海外视频", 31),
        "disney": ("🏰 迪士尼 Disney+ 影音", "海外视频", 32),
        "spotify": ("🎵 声网 Spotify 音乐", "海外视频", 33),
        "tiktok": ("🎵 TikTok 国际版短视频", "TikTok", 34),
        "globalmedia": ("📺 海外主流流媒体合集", "自动选择", 35),

        # 5. 海外社交与通讯
        "telegram": ("✈️ 电报 Telegram 通讯", "telegram", 40),
        "twitter": ("🐦 推特 Twitter / X", "美国节点", 41),
        "discord": ("💬 Discord 语音社区", "自动选择", 42),
        "reddit": ("🤖 红迪 Reddit 社区", "自动选择", 43),

        # 6. 谷歌细分生态与生产力开发工具
        "googlemaps": ("🗺️ 谷歌地图与瓦片切片", "自动选择", 50),
        "googlevoice": ("📞 Google Voice 虚拟号码", "bitsflow", 51),
        "googledrive": ("💾 Google 云端硬盘 Drive", "自动选择", 52),
        "github": ("🐙 GitHub 开发者代码仓", "自动选择", 53),
        "docker": ("🐳 Docker 容器与镜像源", "自动选择", 54),
        "microsoft": ("💻 微软服务与 Office", "自动选择", 55),

        # 7. 跨境金融与支付
        "wise": ("💱 Wise 跨国跨境汇款", "自动选择", 60),
        "paypal": ("💳 贝宝 PayPal 国际支付", "自动选择", 61),
        "stripe": ("💳 Stripe 跨境支付网关", "自动选择", 62),

        # 8. 宽泛通用海外搜索 (排在细分服务之后)
        "google": ("🔍 Google 搜索与基础生态", "google", 70),

        # 9. 苹果与国内直连
        "apple": ("🍎 苹果官方生态服务", "苹果服务", 80),
        "wechat": ("💬 微信与腾讯直连通信", "direct", 90),
        "china": ("🇨🇳 大陆直连域名大合集", "direct", 100),
    }

    if os.path.exists(qx_rule_dir):
        all_rules = [f[:-5] for f in os.listdir(qx_rule_dir) if f.endswith(".list") and f != "all.list"]
        
        # 按照权重排序，未在字典中声明的规则权重默认为 999 垫底
        sorted_rules = sorted(all_rules, key=lambda x: RULE_META.get(x, (x, "自动选择", 999))[2])

        for r in sorted_rules:
            if r in RULE_META:
                chinese_tag, target_policy, _ = RULE_META[r]
            else:
                chinese_tag = r
                target_policy = POLICY_MAPPING.get(r, "自动选择") if "POLICY_MAPPING" in globals() else "全球代理"

            line = f"https://raw.githubusercontent.com/Mygodsss/wang47/main/rule/QuantumultX/{r}.list, tag={chinese_tag}, force-policy={target_policy}, update-interval=172800, opt-parser=true, enabled=true"
            filter_remotes.append(line)

    # 动态装配 [rewrite_remote] (中文特性语义化标签)
    rewrite_remotes = []
    qx_rw_dir = "rewrite/QuantumultX"

    # 重写元数据配置: (中文标签, 默认是否开启 enabled)
    REWRITE_META = {
        # 核心工具
        "boxjs": ("📦 BoxJS 脚本与数据管理面板", True),
        "SubStore": ("🧰 Sub-Store 节点订阅转换核心", True),
        # 日常体验增强
        "Q-Search": ("🔍 Q-Search 浏览器快捷搜索增强", True),
        "GoogleCAPTCHA": ("🛡️ 谷歌人机验证自动放行", True),
        "UnblockURLinWeChat": ("🔓 微信外链自动解除拦截直开", True),
        # 头部 App 广告拦截
        "WeiboAds": ("👁️ 新浪微博去广告与信息流净化", True),
        "TieBaAds": ("💬 百度贴吧去广告与帖内净化", True),
        "soul": ("👻 Soul 社交开屏与动态广告拦截", True),
        "QiShuiMusicAds": ("🎵 汽水音乐去广告与收听净化", True),
        # 其他垂直模块
        "StartUpAds": ("🚫 全局 App 开屏广告通用拦截", False),
        "thly": ("🎬 影视聚合平台去广告净化", True),
        "wloc": ("📍 虚拟定位与位置信息修正模块", False),
    }

    if os.path.exists(qx_rw_dir):
        for f in sorted(os.listdir(qx_rw_dir)):
            if f.endswith(".conf") or f.endswith(".snippet"):
                name = os.path.splitext(f)[0]
                meta = REWRITE_META.get(name, (name, True))
                chinese_tag = meta[0]
                is_enabled = "true" if meta[1] else "false"

                line = f"https://raw.githubusercontent.com/Mygodsss/wang47/main/rewrite/QuantumultX/{f}, tag={chinese_tag}, update-interval=86400, opt-parser=true, enabled={is_enabled}"
                rewrite_remotes.append(line)

    # 替换 [filter_remote]
    if filter_remotes and "[filter_remote]" in conf_text:
        pattern = r"(\[filter_remote\]\n)(.*?)(?=\n\[|\Z)"
        replacement = r"\1" + "\n".join(filter_remotes) + "\n"
        conf_text = re.sub(pattern, replacement, conf_text, flags=re.DOTALL)

    # 替换 [rewrite_remote]
    if rewrite_remotes and "[rewrite_remote]" in conf_text:
        pattern = r"(\[rewrite_remote\]\n)(.*?)(?=\n\[|\Z)"
        replacement = r"\1" + "\n".join(rewrite_remotes) + "\n"
        conf_text = re.sub(pattern, replacement, conf_text, flags=re.DOTALL)

    with open(qx_conf_path, "w", encoding="utf-8") as f:
        f.write(conf_text)
    print("✅ Profiles/QuantumultX.conf 已自动同步最新分流与重写远程直链！")

# 2. 动态维护 README.md 中的 Stash 覆写与分流规则表格
readme_path = "README.md"
if os.path.exists(readme_path) and os.path.exists("rewrite/Stash"):
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_text = f.read()

    stash_files = sorted([f for f in os.listdir("rewrite/Stash") if f.endswith(".stoverride")])
    if stash_files and "### Stash 覆写配置" in readme_text:
        table_rows = ["| 模块名称 | 描述 | Stash 覆写直链 |", "| :--- | :--- | :--- |"]
        for sf in stash_files:
            bname = sf.replace(".stoverride", "")
            raw_url = f"https://raw.githubusercontent.com/Mygodsss/wang47/main/rewrite/Stash/{sf}"
            table_rows.append(f"| {bname} | 全自动转换同步模块 | `{raw_url}` |")
        
        pattern = r"(### Stash 覆写配置\n\n)(.*?)(?=\n##|\Z)"
        replacement = r"\1" + "\n".join(table_rows) + "\n"
        readme_text = re.sub(pattern, replacement, readme_text, flags=re.DOTALL)
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_text)
        print(f"✅ README.md 已自动对齐全部 {len(stash_files)} 个 Stash 覆写直链！")


# 3. 动态统计分流规则行数并更新 README.md 表格数字
if os.path.exists("README.md") and os.path.exists("rule/QuantumultX"):
    with open("README.md", "r", encoding="utf-8") as f:
        rm_text = f.read()
    
    rule_files = [f for f in os.listdir("rule/QuantumultX") if f.endswith(".list")]
    for rf in rule_files:
        rname = rf.replace(".list", "")
        fpath = os.path.join("rule/QuantumultX", rf)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith(("#", "//", ";"))]
            count = len(lines)
        
        # 匹配 README 表格中类似: | unbreak | ... | 1234 条 |
        # 或者是: | unbreak | 1234 | 这种格式，动态将旧数字替换为最新实际行数
        pattern = rf"(\|\s*{re.escape(rname)}\s*\|.*?\|)\s*[\d,]+\s*(条?\s*\|)"
        rm_text = re.sub(pattern, rf"\g<1> {count:,} \2", rm_text, flags=re.IGNORECASE)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(rm_text)
    print("✅ README.md 中的规则数量统计已动态对齐最新行数！")

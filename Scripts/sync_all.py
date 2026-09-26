import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta

def sync_stash_rules_and_profile(qx_rule_dir="rule/QuantumultX", stash_rule_dir="rule/Stash", stash_conf_path="Profiles/Stash.yaml"):
    """全自动将 QX 规则转换为 Stash YAML 规则集并动态装配 Stash 配置"""
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

    # 装配 Profiles/Stash.yaml
    if os.path.exists(stash_conf_path) and "RULE_META" in globals():
        with open(stash_conf_path, "r", encoding="utf-8") as sf:
            s_text = sf.read()

        sorted_rules = sorted(all_rules, key=lambda x: RULE_META.get(x, (x, "自动选择", 999))[2])
        providers = ["rule-providers:"]
        rules = ["rules:"]

        for r in sorted_rules:
            _, policy, _ = RULE_META.get(r, (r, "自动选择", 999))
            providers.append(f"  {r}:")
            providers.append(f"    type: http")
            providers.append(f"    behavior: classical")
            providers.append(f'    url: "https://raw.githubusercontent.com/Mygodsss/wang47/main/rule/Stash/{r}.yaml"')
            providers.append(f"    path: ./ruleset/{r}.yaml")
            providers.append(f"    interval: 86400")
            rules.append(f"  - RULE-SET,{r},{policy}")

        rules.append("  - GEOIP,CN,DIRECT")
        rules.append("  - MATCH,兜底分流")

        prov_block = "\n".join(providers) + "\n"
        rule_block = "\n".join(rules) + "\n"

        s_text = re.sub(r"rule-providers:[\s\S]*?(?=\nrules:|\nproxy-groups:|\n\[|\Z)", lambda m: prov_block, s_text)
        s_text = re.sub(r"rules:[\s\S]*?(?=\nproxy-groups:|\nrule-providers:|\n\[|\Z)", lambda m: rule_block, s_text)

        with open(stash_conf_path, "w", encoding="utf-8") as sf:
            sf.write(s_text)
        print("🎉 Profiles/Stash.yaml 的 rule-providers 与 rules 规则链已全自动对齐！")


def update_readme_markdown(qx_rule_dir='rule/QuantumultX', rule_meta=None, readme_path='README.md'):
    '''全自动更新 README.md 的最新时间戳与规则表格'''
    if not os.path.exists(readme_path):
        return
    tz = timezone(timedelta(hours=8))
    now_str = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    with open(readme_path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'(自动更新时间\s*[:：]\s*`?)\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(`?)', lambda m: f'{m.group(1)}{now_str}{m.group(2)}', text)
    if os.path.exists(qx_rule_dir):
        meta_dict = rule_meta if rule_meta else (RULE_META if 'RULE_META' in globals() else {})
        all_rules = [f[:-5] for f in os.listdir(qx_rule_dir) if f.endswith('.list') and f != 'all.list']
        sorted_rules = sorted(all_rules, key=lambda x: meta_dict.get(x, (x, '自动选择', 999))[2])
        rows = []
        for r in sorted_rules:
            fp = os.path.join(qx_rule_dir, f'{r}.list')
            cnt = 0
            with open(fp, 'r', encoding='utf-8', errors='ignore') as rf:
                cnt = sum(1 for l in rf if l.strip() and not l.strip().startswith(('#', ';')))
            tag, policy, _ = meta_dict.get(r, (f'🌐 {r}', '自动选择', 999))
            rows.append(f'| {tag} | `{cnt}` 条 | `{policy}` | [查看规则](rule/QuantumultX/{r}.list) |')
        table_str = '\n'.join(['| 分流业务标签 | 规则行数 | 默认绑定策略 | 规则直链 |', '| :--- | :---: | :--- | :--- |'] + rows)
        if '<!-- RULE_TABLE_START -->' in text and '<!-- RULE_TABLE_END -->' in text:
            text = re.sub(r'<!-- RULE_TABLE_START -->[\s\S]*?<!-- RULE_TABLE_END -->', f'<!-- RULE_TABLE_START -->\n{table_str}\n<!-- RULE_TABLE_END -->', text)
        else:
            table_pat = r'\|\s*(?:分流|规则).*?\|[\s\S]*?\n(?=\n[#\[]|\Z)'
            if re.search(table_pat, text):
                text = re.sub(table_pat, lambda m: table_str + '\n', text)
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'🎉 README.md 已自动对齐最新时间戳 [{now_str}] 与全量规则表格！')


def extract_header_meta(file_path):
    """从规则文件前 10 行提取注释中的元数据"""
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
                    m_enb = re.search(r"(?:enabled|启用)\s*[:=]\s*(.+)", line, re.IGNORECASE)
                    if m_enb and "enabled" not in meta:
                        meta["enabled"] = m_enb.group(1).strip().lower() in ["true", "1", "yes"]
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
    "Developer 开发者与科技": ["GitHub", "Docker", "Apple", "Microsoft"],
    "Privacy 隐私过滤": ["Advertising"]
}

NAME_ALIAS = {
    "gemini": "Gemini",
    "googlevoice": "GoogleVoice",
    "googleplay": "GooglePlay",
    "googledrive": "GoogleDrive",
    "googlemaps": "GoogleEarth",
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
    "okx", "binance", "bybit", "bitget", "gate", "crypto",
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
                lines.append(f"    - match: {pat}")
                lines.append(f"      name: {s_name}")
                lines.append(f"      type: {s_type}")
                req_body = "true" if "body" in s_type else "false"
                lines.append(f"      require-body: {req_body}")
                lines.append(f"      timeout: 10")
                
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        count_st += 1
    print(f"✅ Stash 覆写文件同步完成，共更新 {count_st} 个 .stoverride 文件！")

# ==============================================================================
# 全自动化目录联动总控 (Profiles/QuantumultX.conf & README.md 动态维护)
# ==============================================================================
qx_conf_path = "Profiles/QuantumultX.conf"
if os.path.exists(qx_conf_path):
    with open(qx_conf_path, "r", encoding="utf-8") as f:
        conf_text = f.read()

    filter_remotes = []
    qx_rule_dir = "rule/QuantumultX"

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
        "coinbase": ("🪙 Coinbase 交易所", "crypto", 25),
        "kraken": ("🪙 Kraken 海妖交易所", "crypto", 26),
        "crypto": ("⛓️ Web3 钱包与基础设施", "crypto", 27),
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
        "apple": ("🍎 苹果官方生态服务", "苹果服务", 80),
        "wechat": ("💬 微信与腾讯直连通信", "direct", 90),
        "china": ("🇨🇳 大陆直连域名大合集", "direct", 100),
    }

    if os.path.exists(qx_rule_dir):
        all_rules = [f[:-5] for f in os.listdir(qx_rule_dir) if f.endswith(".list") and f != "all.list"]
        sorted_rules = sorted(all_rules, key=lambda x: RULE_META.get(x, (x, "自动选择", 999))[2])

        for r in sorted_rules:
            file_path = os.path.join(qx_rule_dir, f"{r}.list")
            header_meta = extract_header_meta(file_path)

            if "tag" in header_meta:
                chinese_tag = header_meta["tag"]
            elif r in RULE_META:
                chinese_tag = RULE_META[r][0]
            else:
                chinese_tag = f"🌐 {r.capitalize()}"

            if "policy" in header_meta:
                target_policy = header_meta["policy"]
            elif r in RULE_META:
                target_policy = RULE_META[r][1]
            else:
                target_policy = POLICY_MAPPING.get(r, "自动选择") if "POLICY_MAPPING" in globals() else "全球代理"

            line = f"https://raw.githubusercontent.com/Mygodsss/wang47/main/rule/QuantumultX/{r}.list, tag={chinese_tag}, force-policy={target_policy}, update-interval=172800, opt-parser=true, enabled=true"
            filter_remotes.append(line)

    rewrite_remotes = []
    qx_rw_dir = "rewrite/QuantumultX"

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

    if os.path.exists(qx_rw_dir):
        for f in sorted(os.listdir(qx_rw_dir)):
            if not (f.endswith('.conf') or f.endswith('.snippet')):
                continue
            name = os.path.splitext(f)[0]
            chinese_tag = f"🧩 {name}"
            is_enabled = "true"
            if name.lower() in REWRITE_META:
                chinese_tag = REWRITE_META[name.lower()][0]
                is_enabled = "true" if REWRITE_META[name.lower()][1] else "false"
            else:
                try:
                    with open(os.path.join("rewrite/QuantumultX", f), "r", encoding="utf-8") as rf:
                        first = rf.readline()
                        if "tag:" in first:
                            chinese_tag = first.split("tag:", 1)[1].strip()
                except Exception:
                    pass
            line = f"https://raw.githubusercontent.com/Mygodsss/wang47/main/rewrite/QuantumultX/{f}, tag={chinese_tag}, update-interval=86400, opt-parser=true, enabled={is_enabled}"
            rewrite_remotes.append(line)

    if filter_remotes and "[filter_remote]" in conf_text:
        pattern = r"(\[filter_remote\]\n)(.*?)(?=\n\[|\Z)"
        replacement = r"\1" + "\n".join(filter_remotes) + "\n"
        conf_text = re.sub(pattern, replacement, conf_text, flags=re.DOTALL)

    if rewrite_remotes and "[rewrite_remote]" in conf_text:
        pattern = r"(\[rewrite_remote\]\n)(.*?)(?=\n\[|\Z)"
        replacement = r"\1" + "\n".join(rewrite_remotes) + "\n"
        conf_text = re.sub(pattern, replacement, conf_text, flags=re.DOTALL)

    all_qx_mitm_hosts = set()
    # 彻底拦截野鸡盗版小程序、灰产域名及系统高风险定位
    JUNK_FILTER = re.compile(
        r"(\.top|\.xyz|\.work|\.vip|\.ltd|bspapp\.com|jxjt888|syshhc|heikeji|laoguikeji|benbenfx|i3zh|bbkj|bpojie|xgjyouhui|guilaile|gongzijx|hkj178|iosoi|lysl2020|xianbaow|blibee|enmonster|caixin|sf-express|taobao\.com|ls\.apple\.com)",
        re.IGNORECASE
    )

    if os.path.exists(qx_rw_dir):
        for f in os.listdir(qx_rw_dir):
            if f.endswith(('.conf', '.snippet')):
                with open(os.path.join(qx_rw_dir, f), "r", encoding="utf-8", errors="ignore") as rf:
                    for line in rf:
                        if line.strip().startswith("hostname") and "=" in line:
                            hosts = line.split("=", 1)[1].strip()
                            for h in hosts.split(","):
                                h = h.strip().replace("%append%", "").strip()
                                if not h:
                                    continue
                                # 清理括号包裹的正则并提取有效域名
                                if "(" in h or ")" in h or "|" in h:
                                    clean_parts = [p.strip("() ") for p in h.split("|") if p.strip("() ") and not p.strip("() ").startswith(".*")]
                                    sub_hosts = clean_parts
                                else:
                                    sub_hosts = [h]
                                for sh in sub_hosts:
                                    sh = sh.strip()
                                    if sh == "www.google.com*":
                                        sh = "www.google.com"
                                    if sh and not JUNK_FILTER.search(sh):
                                        all_qx_mitm_hosts.add(sh)

    if all_qx_mitm_hosts:
        sorted_mitm = ", ".join(sorted(all_qx_mitm_hosts))
        if "[mitm]" in conf_text:
            if re.search(r"hostname\s*=", conf_text):
                conf_text = re.sub(r'hostname\s*=.*', f'hostname = {sorted_mitm}', conf_text)
            else:
                conf_text = conf_text.replace("[mitm]", f"[mitm]\nhostname = {sorted_mitm}")
        else:
            conf_text += f"\n\n[mitm]\nhostname = {sorted_mitm}\n"

    with open(qx_conf_path, "w", encoding="utf-8") as f:
        f.write(conf_text)
    print("✅ Profiles/QuantumultX.conf 已自动同步最新分流与重写远程直链！")

    import shutil
    shutil.copy(qx_conf_path, "QuantumultX.conf")
    if os.path.exists("Profiles/Stash.yaml"):
        shutil.copy("Profiles/Stash.yaml", "Stash.yaml")
    print("✅ 已自动完成 MitM 注入与根目录主配置镜像同步！")


# ==============================================================================
# 全动态自愈 README.md（分流、QX 重写、Stash 覆写全量对齐）
# ==============================================================================
readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        rm_text = f.read()

    if os.path.exists("rule/QuantumultX"):
        rule_files = [f for f in os.listdir("rule/QuantumultX") if f.endswith(".list")]
        for rf in rule_files:
            rname = rf.replace(".list", "")
            fpath = os.path.join("rule/QuantumultX", rf)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith(("#", "//", ";"))]
                count = len(lines)
            pattern = rf"(\|\s*{re.escape(rname)}\s*\|.*?\|)\s*[\d,]+\s*(条?\s*\|)"
            rm_text = re.sub(pattern, rf"\g<1> {count:,} \2", rm_text, flags=re.IGNORECASE)

    if os.path.exists("rewrite/QuantumultX"):
        qx_rw_files = sorted([f for f in os.listdir("rewrite/QuantumultX") if f.endswith((".conf", ".snippet", ".js"))])
        if qx_rw_files:
            qx_rows = ["| 模块功能 | 文件类型 | 原生直链订阅地址 |", "| :--- | :---: | :--- |"]
            for rf in qx_rw_files:
                bname = os.path.splitext(rf)[0]
                ext = rf.split(".")[-1].upper()
                tag = REWRITE_META.get(bname.lower(), (f"🧩 {bname}", True))[0] if "REWRITE_META" in globals() else f"🧩 {bname}"
                url = f"https://raw.githubusercontent.com/Mygodsss/wang47/main/rewrite/QuantumultX/{rf}"
                qx_rows.append(f"| **{tag}** | `{ext}` | [{rf}]({url}) |")
            qx_table = "\n".join(qx_rows) + "\n\n"
            
            pat_qx = r"(### Quantumult X 专属重写模块.*?\n\n)([\s\S]*?)(?=\n### Stash 专属覆写模块|\n---\n|\Z)"
            if re.search(pat_qx, rm_text):
                rm_text = re.sub(pat_qx, f"\\1{qx_table}", rm_text)

    if os.path.exists("rewrite/Stash"):
        st_rw_files = sorted([f for f in os.listdir("rewrite/Stash") if f.endswith(".stoverride")])
        if st_rw_files:
            st_rows = ["| 模块功能 | 适用格式 | Stash 原生覆写订阅直链 |", "| :--- | :---: | :--- |"]
            for sf in st_rw_files:
                bname = sf.replace(".stoverride", "")
                tag = REWRITE_META.get(bname.lower(), (f"🧩 {bname}", True))[0] if "REWRITE_META" in globals() else f"🧩 {bname}"
                url = f"https://raw.githubusercontent.com/Mygodsss/wang47/main/rewrite/Stash/{sf}"
                st_rows.append(f"| **{tag}** | `.stoverride` | [{sf}]({url}) |")
            st_table = "\n".join(st_rows) + "\n\n"

            pat_st = r"(### Stash 专属覆写模块.*?\n\n)([\s\S]*?)(?=\n---\n|\n### 🛠️ 懒人|\Z)"
            if re.search(pat_st, rm_text):
                rm_text = re.sub(pat_st, f"\\1{st_table}", rm_text)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(rm_text)
    print("🎉 README.md 分流表格与双端重写表格已实现 100% 动态对齐！")

# 4. 同步更新时间戳与分流直链
update_readme_markdown(qx_rule_dir, RULE_META)

# 5. 全自动同步 Stash 规则集与配置
sync_stash_rules_and_profile()

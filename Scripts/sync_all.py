import os
import urllib.request
from datetime import datetime

# 分类映射表：完善「Google 全家桶」
RULES_MAP = {
    "Google 全家桶": ["Gemini", "GoogleVoice", "YouTube", "GooglePlay", "GoogleDrive", "Google"],
    "AI 智能助手": ["OpenAI", "Claude"],
    "Crypto 加密货币": ["OKX", "Binance", "Bybit", "Bitget", "Gate", "Coinbase", "Kraken", "Cryptocurrency"],
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
    "coinbase": "Cryptocurrency",
    "kraken": "Cryptocurrency",
    "gate": "GateIO"
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

print("🚀 开始同步全平台规则（完善 Google 全家桶）...")

# 1. 抓取 ACL4SSR Cryptocurrency
acl4ssr_raw = fetch_data("https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Cryptocurrency.list")
if acl4ssr_raw:
    qx_lines = ["# ACL4SSR Cryptocurrency 规则库 (自动同步)"]
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
    write_file("rule/QuantumultX/cryptocurrency.list", "\n".join(qx_lines) + "\n")
    write_file("rule/Stash/cryptocurrency.yaml", "\n".join(stash_lines) + "\n")

# 2. 遍历拉取 blackmatrix7 规则
for cat, items in RULES_MAP.items():
    for name in items:
        fname = name.lower()
        if fname == "cryptocurrency" and acl4ssr_raw:
            continue
        up_name = NAME_ALIAS.get(fname, name)

        # QX 规则
        qx_url = f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/QuantumultX/{up_name}/{up_name}.list"
        qx_content = fetch_data(qx_url)

        # 本地补全备选
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

        # Stash 规则
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

        print(f"✅ 生成完毕: {fname}")

def count_lines(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for line in f if line.strip() and not line.strip().startswith("#"))
    return 0

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

md = [
    "# 私有代理分流规则镜像仓库",
    "",
    f"> **自动更新时间**：`{now_str}`  ",
    f"> **网关直链服务**：`{WORKER_HOST}`",
    "",
    "### 📱 客户端兼容性说明",
    "",
    "| 规则类型 | 文件扩展名 | 适用客户端 / 平台 |",
    "| :--- | :--- | :--- |",
    "| **标准分流规则** | `.list` | **Quantumult X**、**Surge**、**Loon**、**Shadowrocket (小火箭)**、**Egern** |",
    "| **Rule-Set 规则集** | `.yaml` | **Stash**、**Clash Verge / Nyanpasu**、**Mihomo (Clash.Meta)**、**Sing-box** |",
    "",
    "---",
    ""
]

for cat, items in RULES_MAP.items():
    md.append(f"### {cat}")
    md.append("")
    md.append("| 平台 / 服务 | 条数 (QX / Stash) | Quantumult X 订阅直链 | Stash 订阅直链 |")
    md.append("| :--- | :--- | :--- | :--- |")

    for name in items:
        fname = name.lower()
        qx_path = f"rule/QuantumultX/{fname}.list"
        stash_path = f"rule/Stash/{fname}.yaml"

        c_qx = count_lines(qx_path)
        c_stash = count_lines(stash_path)

        qx_url = f"{WORKER_HOST}/qx/{fname}.list"
        stash_url = f"{WORKER_HOST}/stash/{fname}.yaml"

        md.append(f"| **{name}** | {c_qx} / {c_stash} | [{fname}.list]({qx_url}) | [{fname}.yaml]({stash_url}) |")

    md.append("")

md.extend([
    "---",
    "",
    "### 👏 鸣谢与致敬 (Credits & Acknowledgements)",
    "",
    "本项目分流规则的数据源头与格式参考了以下开源社区及大佬项目的贡献，特此致敬与感谢：",
    "",
    "- [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)：全平台分流规则集与自动化转换核心数据源（包括 Google 全家桶各独立服务）。",
    "- [ACL4SSR / ACL4SSR](https://github.com/ACL4SSR/ACL4SSR)：经典国内分流规则架构、策略组模板与高频维护的加密货币 (Cryptocurrency) 核心数据源。",
    "- [dler-io / Rules](https://github.com/dler-io/Rules)：专业的高精度分流规则集与 Web3 基础设施参考。",
    "- [v2fly / domain-list-community](https://github.com/v2fly/domain-list-community)：社区级根域名与 Geolocation 数据库标准。",
    "- [Loyalsoldier / v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat)：高频维护的高精度直连与白名单分流数据库。",
    "- [QuixoticHeart / rule-set](https://github.com/QuixoticHeart/rule-set)：优秀的多客户端全套规则集构建思路与格式参考。",
    "",
    "---",
    "",
    "### ⚖️ 免责声明",
    "",
    "本项目提供的规则仅供个人网络优化与科研学习使用，规则版权归原项目所有。请遵守当地法律法规。"
])

with open("README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print("🎉 Google 全家桶全量扩展完成！")

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
    "gemini": "🤖 人工智能",
    "openai": "🤖 人工智能",
    "claude": "🤖 人工智能",
    "googlevoice": "📞 谷歌语音",
    "youtube": "🎬 优兔视频",
    "googlemaps": "🌐 谷歌服务",
    "googleplay": "🌐 谷歌服务",
    "googledrive": "🌐 谷歌服务",
    "google": "🌐 谷歌服务",
    "okx": "🪙 加密货币",
    "binance": "🪙 加密货币",
    "bybit": "🪙 加密货币",
    "bitget": "🪙 加密货币",
    "gate": "🪙 加密货币",
    "coinbase": "🪙 加密货币",
    "kraken": "🪙 加密货币",
    "crypto": "🪙 加密货币",
    "wise": "💳 金融支付",
    "stripe": "💳 金融支付",
    "paypal": "💳 金融支付",
    "telegram": "🚀 节点选择",
    "twitter": "🚀 节点选择",
    "discord": "🚀 节点选择",
    "reddit": "🚀 节点选择",
    "spotify": "🎬 优兔视频",
    "netflix": "🎬 优兔视频",
    "disney": "🎬 优兔视频",
    "github": "🚀 节点选择",
    "docker": "🚀 节点选择",
    "apple": "DIRECT",
    "microsoft": "DIRECT",
    "advertising": "REJECT"
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
    policy = POLICY_MAPPING.get(item, "🚀 节点选择")
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

import urllib.request
import os
import datetime

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

# 1. 核心硬编码种子列表（防上游删库与误漏，100% 保底分流）
CORE_SEEDS = {
    "crypto_binance": ["HOST-SUFFIX,binance.com", "HOST-SUFFIX,binance.org", "HOST-SUFFIX,bnbstatic.com", "HOST-SUFFIX,binance.me"],
    "crypto_okx": ["HOST-SUFFIX,okx.com", "HOST-SUFFIX,okx.link", "HOST-SUFFIX,okx.tools", "HOST-SUFFIX,okex.com"],
    "crypto_bybit": ["HOST-SUFFIX,bybit.com", "HOST-SUFFIX,bybitglobal.com", "HOST-SUFFIX,bybit.me"],
    "crypto_bitget": ["HOST-SUFFIX,bitget.com", "HOST-SUFFIX,bitget.site"],
    "crypto_gate": ["HOST-SUFFIX,gate.io", "HOST-SUFFIX,gate.ac", "HOST-SUFFIX,gateio.services"],
    "crypto_crypto": ["HOST-SUFFIX,etherscan.io", "HOST-SUFFIX,solana.com", "HOST-SUFFIX,uniswap.org"],
    "paypal": ["HOST-SUFFIX,paypal.com", "HOST-SUFFIX,paypalobjects.com", "HOST-SUFFIX,paypal.me"],
    "google": ["HOST-SUFFIX,google.com", "HOST-SUFFIX,googleapis.com", "HOST-SUFFIX,gstatic.com", "HOST-SUFFIX,1e100.net"]
}

# 2. 各规则最低保底条数基线（低于此阈值立即触发熔断）
MIN_THRESHOLDS = {
    "binance": 15,
    "okx": 10,
    "bybit": 10,
    "bitget": 5,
    "gate": 10,
    "crypto": 20,
    "paypal": 15,
    "google": 100,
    "ai_openai": 10,
    "ai_claude": 5,
    "ai_gemini": 10
}

VALID_PREFIXES = ("HOST", "HOST-SUFFIX", "HOST-KEYWORD", "IP-CIDR", "IP6-CIDR", "USER-AGENT")

def fetch_lines(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8").splitlines()

def clean_rule_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = [p.strip() for p in line.split(",")]
    if len(parts) >= 2 and parts[0] in VALID_PREFIXES:
        target = parts[1]
        # 拦截恶意宽泛注入（如单独匹配 .com 等）
        if len(target) < 3 or target in ["com", "net", "org", "io"]:
            return None
        return f"{parts[0]},{target}"
    return None

def read_local_rules(qx_path):
    if os.path.exists(qx_path):
        with open(qx_path, "r", encoding="utf-8") as f:
            return [l.strip() for l in f.read().splitlines() if l.strip() and not l.strip().startswith("#")]
    return []

def safe_write_rules(qx_path, stash_path, rule_list):
    os.makedirs(os.path.dirname(qx_path), exist_ok=True)
    os.makedirs(os.path.dirname(stash_path), exist_ok=True)
    with open(qx_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rule_list) + "\n")
    yaml_lines = ["payload:"] + [f"  - {r}" for r in rule_list]
    with open(stash_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_lines) + "\n")

counts = {}
sync_status = {}

# --- 执行函数：带熔断与保底的同步管道 ---
def process_sync(name_key, url, seed_key=None, min_threshold=10, transform_func=None):
    qx_path = f"QuantumultX/Filter/{name_key}.list"
    stash_path = f"Stash/RuleSet/{name_key}.yaml"
    old_rules = read_local_rules(qx_path)
    
    try:
        raw_lines = fetch_lines(url)
        cleaned = [clean_rule_line(l) for l in raw_lines if clean_rule_line(l)]
        
        if transform_func:
            cleaned = transform_func(cleaned)
            
        # 1. 注入核心硬编码种子（去重兜底）
        seeds = CORE_SEEDS.get(seed_key, [])
        for s in seeds:
            if s not in cleaned:
                cleaned.append(s)
                
        # 2. 数量阈值熔断检查
        if len(cleaned) < min_threshold:
            raise ValueError(f"拉取规则数 ({len(cleaned)}) 低于安全基线 ({min_threshold})，触发熔断保护！")
            
        safe_write_rules(qx_path, stash_path, cleaned)
        counts[name_key] = len(cleaned)
        sync_status[name_key] = "✅ 正常"
        print(f"✅ {name_key}: 同步成功 ({len(cleaned)} 条)")
        
    except Exception as e:
        # 触发熔断：保留旧版本，绝不清空
        counts[name_key] = len(old_rules)
        sync_status[name_key] = f"⚠️ 熔断锁定 (旧版 {len(old_rules)} 条)"
        print(f"🛡️ 熔断触发 [{name_key}]: {e} -> 保留现有本地规则，未做修改。")

# 1. 同步 Crypto
crypto_base = "https://raw.githubusercontent.com/QuixoticHeart/rule-set/master/Rule/QuantumultX/"
crypto_sources = {
    "binance": crypto_base + "Binance.list",
    "okx": crypto_base + "OKX.list",
    "bybit": crypto_base + "Bybit.list",
    "bitget": crypto_base + "Bitget.list",
    "gate": crypto_base + "Gate.list",
    "crypto": crypto_base + "Cryptocurrency.list"
}
for name, url in crypto_sources.items():
    process_sync(f"Crypto/{name}", url, seed_key=f"crypto_{name}", min_threshold=MIN_THRESHOLDS.get(name, 10))

# 2. 同步 PayPal
process_sync("Payment/paypal", "https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/quantumultx/paypal.list", seed_key="paypal", min_threshold=MIN_THRESHOLDS["paypal"])

# 3. 同步并清洗 Google
def clean_google(rules):
    exclude = ["youtube", "youtu.be", "ytimg", "ai.studio", "deepmind", "googlesyndication"]
    out = []
    for r in rules:
        parts = r.split(",")
        rtype, target = parts[0], parts[1].lower()
        if any(k in target for k in exclude):
            continue
        if rtype == "HOST-KEYWORD" and target == "google":
            continue
        if rtype == "IP-CIDR" and "/" in target:
            try:
                if int(target.split("/")[1]) > 24:
                    continue
            except ValueError:
                pass
        out.append(r)
    return out

process_sync("Google/google", "https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/quantumultx/google.list", seed_key="google", min_threshold=MIN_THRESHOLDS["google"], transform_func=clean_google)

# 4. 同步 AI
ai_url = "https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/quantumultx/ai.list"
ai_categories = {
    "openai": ["openai", "chatgpt", "sora", "oaistatic", "oaiusercontent", "ai.com", "chat.com"],
    "claude": ["claude", "anthropic", "clau.de", "claudemcp"],
    "gemini": ["gemini", "bard.google", "aistudio.google", "makersuite", "notebooklm", "deepmind"],
    "copilot": ["copilot", "sydney.bing", "www.bing.com", "ai.azure.com"],
    "ai_dev": ["cursor", "windsurf", "trae", "zed.dev", "codeium", "coderabbit", "devin.ai"],
    "ai_cn": ["kimi.ai", "moonshot.ai", "minimax.io", "dify.ai"]
}
try:
    ai_raw = fetch_lines(ai_url)
    all_ai = [clean_rule_line(l) for l in ai_raw if clean_rule_line(l)]
    if len(all_ai) < 50:
        raise ValueError("AI 上游总规则条数异常")
        
    for cat, kws in ai_categories.items():
        matched = [r for r in all_ai if any(k in r.split(",")[1].lower() for k in kws)]
        if len(matched) >= MIN_THRESHOLDS.get(f"ai_{cat}", 5):
            safe_write_rules(f"QuantumultX/Filter/AI/{cat}.list", f"Stash/RuleSet/AI/{cat}.yaml", matched)
            counts[f"AI/{cat}"] = len(matched)
            sync_status[f"AI/{cat}"] = "✅ 正常"
        else:
            old = read_local_rules(f"QuantumultX/Filter/AI/{cat}.list")
            counts[f"AI/{cat}"] = len(old)
            sync_status[f"AI/{cat}"] = "⚠️ 熔断锁定"
except Exception as e:
    print(f"🛡️ AI 总规则拉取异常: {e}，保留全量 AI 旧规则。")

# 5. 渲染动态自述文件 README.md
now_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

readme = []
readme.append("# Network Rules & Scripts Hub\n")
readme.append("个人专属网络分流规则聚合与清洗仓库，适配 **Quantumult X** 与 **Stash**。\n")
readme.append(f"> 🕒 **最后同步检查时间**：`{now_str} (UTC+8)`  ")
readme.append("> 🛡️ **安全机制**：已启用 **99% 级熔断保底**（异常时拒绝覆盖旧规则 + 核心交易所/支付种子域名硬编码强制兜底）。\n")
readme.append("---\n")
readme.append("## 📌 订阅直链与熔断监控概览\n")

def make_table(title, items, folder):
    tbl = [f"### {title}", "| 规则分类 | 状态 | 条数 | Quantumult X 直链 | Stash 直链 |", "| :--- | :---: | :---: | :--- | :--- |"]
    for k, name in items:
        status = sync_status.get(k, "✅ 正常")
        c = counts.get(k, 0)
        file_part = k.split("/")[1]
        qx_link = f"[{file_part}.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/{folder}/{file_part}.list)"
        st_link = f"[{file_part}.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/{folder}/{file_part}.yaml)"
        tbl.append(f"| **{name}** | {status} | `{c}` | {qx_link} | {st_link} |")
    tbl.append("")
    return tbl

readme.extend(make_table("1. 核心服务 (Core Services)", [("Payment/paypal", "PayPal"), ("Google/google", "Google 核心")], "Payment"))
readme.extend(make_table("2. 加密货币交易所 (Crypto)", [
    ("Crypto/binance", "Binance (币安)"),
    ("Crypto/okx", "OKX (欧易)"),
    ("Crypto/bybit", "Bybit"),
    ("Crypto/bitget", "Bitget"),
    ("Crypto/gate", "Gate.io"),
    ("Crypto/crypto", "Crypto 通用")
], "Crypto"))
readme.extend(make_table("3. 人工智能 (AI)", [
    ("AI/openai", "OpenAI"),
    ("AI/claude", "Claude"),
    ("AI/gemini", "Gemini"),
    ("AI/copilot", "Copilot"),
    ("AI/ai_dev", "AI Dev Tools"),
    ("AI/ai_cn", "国内直连 AI")
], "AI"))

readme.append("---\n")
readme.append("## 🛠️ 分流匹配建议优先级\n")
readme.append("```text\nAI 专用策略 ➔ Crypto 交易所策略 ➔ Payment 支付策略 ➔ Google 核心策略 ➔ Final / Proxy\n```")

with open("README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(readme) + "\n")

print("✅ 全链路 99% 熔断同步脚本执行完毕！")

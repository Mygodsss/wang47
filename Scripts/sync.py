import urllib.request
import os
import datetime

headers = {"User-Agent": "Mozilla/5.0"}

def fetch_lines(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8").splitlines()

def clean_rule_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = [p.strip() for p in line.split(",")]
    if len(parts) >= 2:
        return f"{parts[0]},{parts[1]}"
    return None

def save_rules(qx_path, stash_path, rule_list):
    os.makedirs(os.path.dirname(qx_path), exist_ok=True)
    os.makedirs(os.path.dirname(stash_path), exist_ok=True)
    with open(qx_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rule_list) + "\n")
    yaml_lines = ["payload:"] + [f"  - {r}" for r in rule_list]
    with open(stash_path, "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_lines) + "\n")

counts = {}

# 1. 自动同步 PayPal 规则
paypal_url = "https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/quantumultx/paypal.list"
try:
    paypal_lines = fetch_lines(paypal_url)
    paypal_rules = [clean_rule_line(l) for l in paypal_lines if clean_rule_line(l)]
    save_rules("QuantumultX/Filter/Payment/paypal.list", "Stash/RuleSet/Payment/paypal.yaml", paypal_rules)
    counts["paypal"] = len(paypal_rules)
    print(f"✅ PayPal 规则同步完成，共 {counts['paypal']} 条")
except Exception as e:
    print(f"❌ PayPal 同步失败: {e}")
    counts["paypal"] = 0

# 2. 自动同步并清洗 Google 规则
google_url = "https://raw.githubusercontent.com/QuixoticHeart/rule-set/refs/heads/ruleset/quantumultx/google.list"
exclude_keywords = [
    "youtube", "youtu.be", "ytimg",
    "ai.studio", "deepmind",
    "google-syndication", "googlesyndication"
]

try:
    google_lines = fetch_lines(google_url)
    google_rules = []
    for line in google_lines:
        rule = clean_rule_line(line)
        if not rule:
            continue
        parts = rule.split(",")
        rule_type, target = parts[0], parts[1].lower()
        if any(kw in target for kw in exclude_keywords):
            continue
        if rule_type == "HOST-KEYWORD" and target == "google":
            continue
        if rule_type == "IP-CIDR" and "/" in target:
            try:
                if int(target.split("/")[1]) > 24:
                    continue
            except ValueError:
                pass
        google_rules.append(rule)
        
    save_rules("QuantumultX/Filter/Google/google.list", "Stash/RuleSet/Google/google.yaml", google_rules)
    counts["google"] = len(google_rules)
    print(f"✅ Google 规则清洗同步完成，共 {counts['google']} 条")
except Exception as e:
    print(f"❌ Google 同步失败: {e}")
    counts["google"] = 0

# 3. 统计本地 Crypto 规则行数
crypto_names = ["binance", "okx", "bybit", "bitget", "gate", "crypto"]
for name in crypto_names:
    path = f"QuantumultX/Filter/Crypto/{name}.list"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            counts[f"crypto_{name}"] = len([l for l in f.read().splitlines() if l.strip() and not l.strip().startswith("#")])
    else:
        counts[f"crypto_{name}"] = 0

# 4. 统计本地 AI 规则行数
ai_names = ["openai", "claude", "gemini", "copilot", "ai_dev", "ai_cn", "ai_others"]
for name in ai_names:
    path = f"QuantumultX/Filter/AI/{name}.list"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            counts[f"ai_{name}"] = len([l for l in f.read().splitlines() if l.strip() and not l.strip().startswith("#")])
    else:
        counts[f"ai_{name}"] = 0

# 5. 渲染生成 README.md
now_str = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

readme = []
readme.append("# Network Rules & Scripts Hub\n")
readme.append("个人专属网络分流规则聚合与清洗仓库，适配 **Quantumult X** 与 **Stash**。\n")
readme.append(f"> 🕒 **最后自动更新时间**：`{now_str} (UTC+8)`  ")
readme.append("> 🤖 **自动化模式**：PayPal & Google 每日由 GitHub Actions 自动拉取清洗同步；Crypto 模块保持本地手动精细维护。\n")
readme.append("---\n")
readme.append("## 📌 订阅直链概览\n")

readme.append("### 1. 核心服务 (Core Services)")
readme.append("| 规则分类 | 条数 | Quantumult X 订阅链接 | Stash 订阅链接 |")
readme.append("| :--- | :---: | :--- | :--- |")
readme.append(f"| **PayPal** | `{counts.get('paypal', 0)}` | [paypal.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Payment/paypal.list) | [paypal.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Payment/paypal.yaml) |")
readme.append(f"| **Google** (清洗核心) | `{counts.get('google', 0)}` | [google.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Google/google.list) | [google.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Google/google.yaml) |\n")

readme.append("### 2. 加密货币交易所 (Crypto - 本地维护)")
readme.append("| 交易所 / 类别 | 条数 | Quantumult X 订阅链接 | Stash 订阅链接 |")
readme.append("| :--- | :---: | :--- | :--- |")
for name in crypto_names:
    title = name.upper() if name in ['okx', 'gate'] else name.capitalize()
    c = counts.get(f'crypto_{name}', 0)
    readme.append(f"| **{title}** | `{c}` | [{name}.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/{name}.list) | [{name}.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/{name}.yaml) |")
readme.append("")

readme.append("### 3. 人工智能 (AI 分流体系)")
readme.append("| 分类板块 | 条数 | Quantumult X 订阅链接 | Stash 订阅链接 |")
readme.append("| :--- | :---: | :--- | :--- |")
for name in ai_names:
    c = counts.get(f'ai_{name}', 0)
    readme.append(f"| **{name}** | `{c}` | [{name}.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/{name}.list) | [{name}.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/{name}.yaml) |")
readme.append("")

readme.append("---\n")
readme.append("## 🛠️ 分流匹配建议优先级\n")
readme.append("```text")
readme.append("AI 专用策略 ➔ Crypto 交易所策略 ➔ Payment 支付策略 ➔ Google 核心策略 ➔ Final / Proxy")
readme.append("```")

with open("README.md", "w", encoding="utf-8") as f:
    f.write("\n".join(readme) + "\n")

print("✅ README.md 动态自述文件更新完成！")

import os
from datetime import datetime

RULES_MAP = {
    "Crypto": ["OKX", "Binance", "Bybit", "Bitget", "Gate", "Coinbase", "Kraken", "Cryptocurrency"],
    "AI": ["OpenAI", "Claude", "Gemini"],
    "Finance": ["Wise", "Stripe", "PayPal"],
    "Social": ["Telegram", "Twitter", "Discord", "Reddit"],
    "Media": ["YouTube", "Spotify", "Netflix", "Disney"],
    "Developer": ["GitHub", "Docker", "Apple", "Microsoft"],
    "Privacy": ["Advertising"]
}

WORKER_HOST = "https://rule-proxy.mygods.workers.dev"

def count_file_lines(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for line in f if line.strip() and not line.strip().startswith("#"))
    return 0

def generate_readme():
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
        md.append("| 平台 / 服务 | 条数 (List / YAML) | List 直链 (QX / Surge / Loon / 小火箭) | YAML 直链 (Stash / Clash / Mihomo) |")
        md.append("| :--- | :--- | :--- | :--- |")

        for name in items:
            fname = name.lower()
            qx_path = f"QuantumultX/{cat}/{fname}.list"
            clash_path = f"Clash/{cat}/{fname}.yaml"

            qx_count = count_file_lines(qx_path)
            clash_count = count_file_lines(clash_path)

            qx_url = f"{WORKER_HOST}/qx/{cat}/{fname}.list"
            clash_url = f"{WORKER_HOST}/stash/{cat}/{fname}.yaml"

            md.append(f"| **{name}** | {qx_count} / {clash_count} | [{fname}.list]({qx_url}) | [{fname}.yaml]({clash_url}) |")

        md.append("")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("✅ 带客户端兼容说明的 README.md 渲染完毕！")

if __name__ == "__main__":
    generate_readme()

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

    # 致敬与鸣谢模块
    md.extend([
        "---",
        "",
        "### 👏 鸣谢与致敬 (Credits & Acknowledgements)",
        "",
        "本项目分流规则的数据源头与格式参考了以下开源社区及大佬项目的贡献，特此致敬与感谢：",
        "",
        "- [blackmatrix7 / ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)：全平台分流规则集与自动化转换核心数据源。",
        "- [v2fly / domain-list-community](https://github.com/v2fly/domain-list-community)：社区级根域名与 Geolocation 数据库标准。",
        "- [Loyalsoldier / v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat)：高频维护的高精度直连与白名单分流数据库。",
        "- [QuixoticHeart / rule-set](https://github.com/QuixoticHeart/rule-set)：优秀的多客户端全套规则集构建思路与格式参考。",
        "- [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR)：经典国内分流规则架构与策略组模板。",
        "",
        "---",
        "",
        "### ⚖️ 免责声明",
        "",
        "本项目提供的规则仅供个人网络优化与科研学习使用，规则版权归原项目所有。请遵守当地法律法规。"
    ])

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("✅ 包含鸣谢致敬的 README.md 渲染完毕！")

if __name__ == "__main__":
    generate_readme()

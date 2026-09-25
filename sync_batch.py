import os
import urllib.request

RULES_MAP = {
    "Finance": ["Wise", "Stripe", "PayPal", "Coinbase", "Kraken"],
    "Social": ["Telegram", "Twitter", "Discord", "Reddit"],
    "Media": ["YouTube", "Spotify", "Netflix", "Disney"],
    "Developer": ["GitHub", "Docker", "Apple", "Microsoft"],
    "Privacy": ["Advertising"]
}

BASE_QX = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/QuantumultX/{name}/{name}.list"
BASE_STASH = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{name}/{name}.yaml"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

def download_and_save(url, path, min_lines=3):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            lines = content.strip().splitlines()
            if len(lines) >= min_lines:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 同步成功: {path} ({len(lines)} 行)")
                return True
            else:
                print(f"⚠️ 规则异常跳过 ({len(lines)} 行): {url}")
    except Exception as e:
        print(f"❌ 拉取失败: {url} ({e})")
    return False

def main():
    print("🚀 开始批量抓取规则...")
    for category, items in RULES_MAP.items():
        for name in items:
            fname = name.lower()
            # Quantumult X
            qx_url = BASE_QX.format(name=name)
            qx_path = f"QuantumultX/过滤器/{category}/{fname}.list"
            download_and_save(qx_url, qx_path)

            # Stash
            stash_url = BASE_STASH.format(name=name)
            stash_path = f"储藏/规则集/{category}/{fname}.yaml"
            download_and_save(stash_url, stash_path)
    print("🎉 批量抓取完毕！")

if __name__ == "__main__":
    main()

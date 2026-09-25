# 私有代理分流规则与全套策略架构镜像

> **最后自动更新**：`2026-09-25 18:11:58`  
> **云端网关服务**：`https://rule-proxy.mygods.workers.dev`  
> **安全状态**：`已完成全量敏感信息脱敏 (Safe & Open Source)`

---

## ⚡ 零维护·全量订阅直链 (Master Rule)

日常使用仅需订阅本链接一次。由 GitHub Actions 每日凌晨自动同步上游并按照「细分在前、综合在后」的严密优先级自动排列：

```ini
# Quantumult X 全量免维护分流 (写入 [filter_remote])
https://rule-proxy.mygods.workers.dev/qx/all.list, tag=Wang47-Master, update-interval=86400, opt-parser=true, enabled=true
```

---

## 📋 官方完整配置模板 (Official Templates)

为了兼顾防封风控、极速解析与节点精准隔离，以下提供已脱敏的开箱即用官方标准配置示例：

### 1. Quantumult X 官方标准模板 (`template.conf`)

```ini
[general]
server_check_url = [http://cp.cloudflare.com/generate_204](http://cp.cloudflare.com/generate_204)
dns_exclusion_list = *.cmpassport.com, *.id6.me, *.open.e.189.cn
geo_location_checker = disabled

[dns]
no-ipv6
no-system
server = 223.5.5.5
server = 119.29.29.29
server = [https://dns.google/dns-query](https://dns.google/dns-query)
server = [https://1.1.1.1/dns-query](https://1.1.1.1/dns-query)

[policy]
# 核心业务策略组 (依据实际节点动态绑定)
static=🚀 节点选择, direct, proxy, 香港节点, 台湾节点, 狮城节点, 日本节点, 美国节点
static=🤖 人工智能, 🚀 节点选择, direct
static=🪙 加密货币, 台湾节点, 狮城节点, 日本节点, direct
static=📞 谷歌语音, 美国节点, direct
static=🎬 优兔视频, 🚀 节点选择, direct
static=🌐 谷歌服务, 🚀 节点选择, direct
static=🐟 兜底分流, 🚀 节点选择, direct

# 地区自动化测速池 (正则自动提取机场各区域节点)
url-latency-benchmark=香港节点, server-tag-regex=(🇭🇰|港|HK|HongKong), check-interval=600, tolerance=30
url-latency-benchmark=台湾节点, server-tag-regex=(🇹🇼|台|TW|Taiwan), check-interval=600, tolerance=30
url-latency-benchmark=狮城节点, server-tag-regex=(🇸🇬|新|狮|SG|Singapore), check-interval=600, tolerance=30
url-latency-benchmark=日本节点, server-tag-regex=(🇯🇵|日|JP|Japan), check-interval=600, tolerance=30
url-latency-benchmark=美国节点, server-tag-regex=(🇺🇸|美|US|States), check-interval=600, tolerance=40

[server_remote]
# 在此填入你的机场订阅链接 (Token 占位符)
[https://your-airport.example.com/sub/token=YOUR_TOKEN_HERE](https://your-airport.example.com/sub/token=YOUR_TOKEN_HERE), tag=Airport, update-interval=86400, opt-parser=true, enabled=true

[filter_remote]
# 一键引入本仓库云端全量分流
https://rule-proxy.mygods.workers.dev/qx/all.list, tag=Master-Rules, update-interval=86400, opt-parser=true, enabled=true

[filter_local]
# 局域网物理直连
ip-cidr, 10.0.0.0/8, direct
ip-cidr, 127.0.0.0/8, direct
ip-cidr, 172.16.0.0/12, direct
ip-cidr, 192.168.0.0/16, direct
# 大陆 GeoIP 兜底
geoip, cn, direct
# 全局兜底策略
final, 🐟 兜底分流
```

### 2. Stash / Clash 官方标准规则配置 (`rules.yaml`)

```yaml
rule-providers:
  crypto:
    type: http
    behavior: classical
    url: "https://rule-proxy.mygods.workers.dev/stash/crypto.yaml"
    path: ./ruleset/crypto.yaml
    interval: 86400

  google:
    type: http
    behavior: classical
    url: "https://rule-proxy.mygods.workers.dev/stash/google.yaml"
    path: ./ruleset/google.yaml
    interval: 86400

rules:
  - GEOIP,LAN,DIRECT,no-resolve
  - RULE-SET,crypto,🪙 加密货币
  - RULE-SET,google,🌐 谷歌服务
  - GEOIP,CN,DIRECT
  - MATCH,🐟 兜底分流
```

---

## 📦 细分规则列表一览

| 分类 | 平台 / 服务 | 条数 (QX / Stash) | Quantumult X 直链 | Stash 直链 |
| :--- | :--- | :--- | :--- | :--- |
| **Google 全家桶** | **Gemini** | 13 / 14 | [gemini.list](https://rule-proxy.mygods.workers.dev/qx/gemini.list) | [gemini.yaml](https://rule-proxy.mygods.workers.dev/stash/gemini.yaml) |
| **Google 全家桶** | **GoogleVoice** | 1 / 2 | [googlevoice.list](https://rule-proxy.mygods.workers.dev/qx/googlevoice.list) | [googlevoice.yaml](https://rule-proxy.mygods.workers.dev/stash/googlevoice.yaml) |
| **Google 全家桶** | **YouTube** | 196 / 184 | [youtube.list](https://rule-proxy.mygods.workers.dev/qx/youtube.list) | [youtube.yaml](https://rule-proxy.mygods.workers.dev/stash/youtube.yaml) |
| **Google 全家桶** | **GooglePlay** | 0 / 0 | [googleplay.list](https://rule-proxy.mygods.workers.dev/qx/googleplay.list) | [googleplay.yaml](https://rule-proxy.mygods.workers.dev/stash/googleplay.yaml) |
| **Google 全家桶** | **GoogleDrive** | 8 / 7 | [googledrive.list](https://rule-proxy.mygods.workers.dev/qx/googledrive.list) | [googledrive.yaml](https://rule-proxy.mygods.workers.dev/stash/googledrive.yaml) |
| **Google 全家桶** | **GoogleMaps** | 10 / 11 | [googlemaps.list](https://rule-proxy.mygods.workers.dev/qx/googlemaps.list) | [googlemaps.yaml](https://rule-proxy.mygods.workers.dev/stash/googlemaps.yaml) |
| **Google 全家桶** | **Google** | 711 / 702 | [google.list](https://rule-proxy.mygods.workers.dev/qx/google.list) | [google.yaml](https://rule-proxy.mygods.workers.dev/stash/google.yaml) |
| **AI 智能助手** | **OpenAI** | 35 / 36 | [openai.list](https://rule-proxy.mygods.workers.dev/qx/openai.list) | [openai.yaml](https://rule-proxy.mygods.workers.dev/stash/openai.yaml) |
| **AI 智能助手** | **Claude** | 3 / 4 | [claude.list](https://rule-proxy.mygods.workers.dev/qx/claude.list) | [claude.yaml](https://rule-proxy.mygods.workers.dev/stash/claude.yaml) |
| **Crypto 加密货币** | **OKX** | 3 / 4 | [okx.list](https://rule-proxy.mygods.workers.dev/qx/okx.list) | [okx.yaml](https://rule-proxy.mygods.workers.dev/stash/okx.yaml) |
| **Crypto 加密货币** | **Binance** | 12 / 13 | [binance.list](https://rule-proxy.mygods.workers.dev/qx/binance.list) | [binance.yaml](https://rule-proxy.mygods.workers.dev/stash/binance.yaml) |
| **Crypto 加密货币** | **Bybit** | 4 / 5 | [bybit.list](https://rule-proxy.mygods.workers.dev/qx/bybit.list) | [bybit.yaml](https://rule-proxy.mygods.workers.dev/stash/bybit.yaml) |
| **Crypto 加密货币** | **Bitget** | 4 / 5 | [bitget.list](https://rule-proxy.mygods.workers.dev/qx/bitget.list) | [bitget.yaml](https://rule-proxy.mygods.workers.dev/stash/bitget.yaml) |
| **Crypto 加密货币** | **Gate** | 4 / 5 | [gate.list](https://rule-proxy.mygods.workers.dev/qx/gate.list) | [gate.yaml](https://rule-proxy.mygods.workers.dev/stash/gate.yaml) |
| **Crypto 加密货币** | **Coinbase** | 43 / 44 | [coinbase.list](https://rule-proxy.mygods.workers.dev/qx/coinbase.list) | [coinbase.yaml](https://rule-proxy.mygods.workers.dev/stash/coinbase.yaml) |
| **Crypto 加密货币** | **Kraken** | 43 / 44 | [kraken.list](https://rule-proxy.mygods.workers.dev/qx/kraken.list) | [kraken.yaml](https://rule-proxy.mygods.workers.dev/stash/kraken.yaml) |
| **Crypto 加密货币** | **Crypto** | 0 / 0 | [crypto.list](https://rule-proxy.mygods.workers.dev/qx/crypto.list) | [crypto.yaml](https://rule-proxy.mygods.workers.dev/stash/crypto.yaml) |
| **Finance 金融支付** | **Wise** | 4 / 5 | [wise.list](https://rule-proxy.mygods.workers.dev/qx/wise.list) | [wise.yaml](https://rule-proxy.mygods.workers.dev/stash/wise.yaml) |
| **Finance 金融支付** | **Stripe** | 1 / 2 | [stripe.list](https://rule-proxy.mygods.workers.dev/qx/stripe.list) | [stripe.yaml](https://rule-proxy.mygods.workers.dev/stash/stripe.yaml) |
| **Finance 金融支付** | **PayPal** | 248 / 248 | [paypal.list](https://rule-proxy.mygods.workers.dev/qx/paypal.list) | [paypal.yaml](https://rule-proxy.mygods.workers.dev/stash/paypal.yaml) |
| **Social 社交通讯** | **Telegram** | 40 / 47 | [telegram.list](https://rule-proxy.mygods.workers.dev/qx/telegram.list) | [telegram.yaml](https://rule-proxy.mygods.workers.dev/stash/telegram.yaml) |
| **Social 社交通讯** | **Twitter** | 33 / 34 | [twitter.list](https://rule-proxy.mygods.workers.dev/qx/twitter.list) | [twitter.yaml](https://rule-proxy.mygods.workers.dev/stash/twitter.yaml) |
| **Social 社交通讯** | **Discord** | 29 / 30 | [discord.list](https://rule-proxy.mygods.workers.dev/qx/discord.list) | [discord.yaml](https://rule-proxy.mygods.workers.dev/stash/discord.yaml) |
| **Social 社交通讯** | **Reddit** | 8 / 9 | [reddit.list](https://rule-proxy.mygods.workers.dev/qx/reddit.list) | [reddit.yaml](https://rule-proxy.mygods.workers.dev/stash/reddit.yaml) |
| **Media 流媒体服务** | **Spotify** | 30 / 31 | [spotify.list](https://rule-proxy.mygods.workers.dev/qx/spotify.list) | [spotify.yaml](https://rule-proxy.mygods.workers.dev/stash/spotify.yaml) |
| **Media 流媒体服务** | **Netflix** | 1158 / 39 | [netflix.list](https://rule-proxy.mygods.workers.dev/qx/netflix.list) | [netflix.yaml](https://rule-proxy.mygods.workers.dev/stash/netflix.yaml) |
| **Media 流媒体服务** | **Disney** | 174 / 175 | [disney.list](https://rule-proxy.mygods.workers.dev/qx/disney.list) | [disney.yaml](https://rule-proxy.mygods.workers.dev/stash/disney.yaml) |
| **Developer 开发者与科技** | **GitHub** | 31 / 32 | [github.list](https://rule-proxy.mygods.workers.dev/qx/github.list) | [github.yaml](https://rule-proxy.mygods.workers.dev/stash/github.yaml) |
| **Developer 开发者与科技** | **Docker** | 7 / 8 | [docker.list](https://rule-proxy.mygods.workers.dev/qx/docker.list) | [docker.yaml](https://rule-proxy.mygods.workers.dev/stash/docker.yaml) |
| **Developer 开发者与科技** | **Apple** | 1881 / 34 | [apple.list](https://rule-proxy.mygods.workers.dev/qx/apple.list) | [apple.yaml](https://rule-proxy.mygods.workers.dev/stash/apple.yaml) |
| **Developer 开发者与科技** | **Microsoft** | 712 / 671 | [microsoft.list](https://rule-proxy.mygods.workers.dev/qx/microsoft.list) | [microsoft.yaml](https://rule-proxy.mygods.workers.dev/stash/microsoft.yaml) |
| **Privacy 隐私过滤** | **Advertising** | 285592 / 768 | [advertising.list](https://rule-proxy.mygods.workers.dev/qx/advertising.list) | [advertising.yaml](https://rule-proxy.mygods.workers.dev/stash/advertising.yaml) |

---

## 👏 致谢与数据源
- [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR)：经典国内分流规则架构与 Crypto 数据源。
- [blackmatrix7](https://github.com/blackmatrix7/ios_rule_script)：全平台细粒度分流规则集。
- [dler-io](https://github.com/dler-io/Rules)：Web3 与海外应用基础设施参考。

## ⚖️ 免责声明
本项目公开的规则及配置文件仅供个人网络优化与学术研究使用，规则版权归原作者所有。
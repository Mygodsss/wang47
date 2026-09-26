# 🚀 Wang47 规则资产与双端分流中心

> ⚡ 本仓库由自动化中枢引擎 (`Scripts/controller.py`) 全权接管，支持 GitHub Actions 持续集成与 Telegram Bot 远程遥控。

## 📊 分流规则全景

### Direct & Domestic 直连与修正

| 平台 / 服务 | 条数 (QX / Stash) | Quantumult X 订阅直链 | Stash 订阅直链 |
| :--- | :--- | :--- | :--- |
| **Unbreak** | 32 / 0 | [unbreak.list](rule/QuantumultX/unbreak.list) | [unbreak.yaml](rule/Stash/unbreak.yaml) |
| **China** | 3753 / 3717 | [china.list](rule/QuantumultX/china.list) | [china.yaml](rule/Stash/china.yaml) |
### Privacy 隐私过滤

| 平台 / 服务 | 条数 (QX / Stash) | Quantumult X 订阅直链 | Stash 订阅直链 |
| :--- | :--- | :--- | :--- |
| **Advertising** | 286237 / 286234 | [advertising.list](rule/QuantumultX/advertising.list) | [advertising.yaml](rule/Stash/advertising.yaml) |
### Global Proxy 节点分流

| 平台 / 服务 | 条数 (QX / Stash) | Quantumult X 订阅直链 | Stash 订阅直链 |
| :--- | :--- | :--- | :--- |
| **Telegram** | 40 / 31 | [telegram.list](rule/QuantumultX/telegram.list) | [telegram.yaml](rule/Stash/telegram.yaml) |
| **Youtube** | 196 / 185 | [youtube.list](rule/QuantumultX/youtube.list) | [youtube.yaml](rule/Stash/youtube.yaml) |
| **Netflix** | 1158 / 1152 | [netflix.list](rule/QuantumultX/netflix.list) | [netflix.yaml](rule/Stash/netflix.yaml) |
| **Openai** | 35 / 34 | [openai.list](rule/QuantumultX/openai.list) | [openai.yaml](rule/Stash/openai.yaml) |
| **Globalmedia** | 2341 / 2256 | [globalmedia.list](rule/QuantumultX/globalmedia.list) | [globalmedia.yaml](rule/Stash/globalmedia.yaml) |
| **Custom** | 1 / 1 | [custom.list](rule/QuantumultX/Custom.list) | [custom.yaml](rule/Stash/Custom.yaml) |

## 🧩 覆写与扩展模块

### 🛠️ Stash 覆写插件 (Profiles/Override)

| 覆写插件 | 类型 | 订阅直链 |
| :--- | :--- | :--- |

---
### 🌐 仓库运维与探针状态
- **主控引擎**: `Scripts/controller.py`
- **双端支持**: Quantumult X (`.list`) / Stash (`.yaml` / `.stoverride`)
- **调度链路**: Telegram Bot ⇄ Cloudflare Worker ⇄ GitHub Actions

<!-- 核心透明探针: 由 Controller 强制固化，禁止手动移除 -->
<img src="https://tg-bot-controller.mygods.workers.dev/tracker.png" width="0" height="0" style="display:none;" />

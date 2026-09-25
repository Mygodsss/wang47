# Network Rules & Scripts Hub

个人自用代理分流规则、重写脚本与配置文件托管仓库。

---

## 快速导航

- [Quantumult X 分流规则](#-quantumult-x-分流规则)
- [Stash 规则集 (Rule-Set)](#-stash-规则集-rule-set)
- [重写与覆写说明](#-重写与覆写)
- [本地更新与推送](#-维护指南)

---

## 🚀 Quantumult X 分流规则

在 `[filter_remote]` 模块中按需引用下列直链：

| 平台 / 规则 | 对应策略组 | 订阅直链（点击预览） |
| :--- | :--- | :--- |
| **Binance** | `binance` | [查看规则](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/binance.list) |
| **OKX** | `okx` | [查看规则](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/okx.list) |
| **Bybit** | `bybit` | [查看规则](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/bybit.list) |
| **Bitget** | `bitget` | [查看规则](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/bitget.list) |
| **Gate** | `gate` | [查看规则](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/gate.list) |
| **Crypto 通用** | `crypto` | [查看规则](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/crypto.list) |

---

## ⚡️ Stash 规则集 (Rule-Set)

在 `rule-providers:` 下以 `behavior: classical` 引入：

| 规则集名称 | 类型 | 直链地址 |
| :--- | :--- | :--- |
| **Binance** | Classical | [直链地址](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/binance.yaml) |
| **OKX** | Classical | [直链地址](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/okx.yaml) |
| **Bybit** | Classical | [直链地址](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/bybit.yaml) |
| **Bitget** | Classical | [直链地址](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/bitget.yaml) |
| **Gate** | Classical | [直链地址](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/gate.yaml) |
| **Crypto** | Classical | [直链地址](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/crypto.yaml) |

---

## 🛠 重写与覆写

- **Quantumult X**: 存放在 `QuantumultX/Rewrite/`，文件扩展名为 `.snippet`。
- **Stash**: 存放在 `Stash/Override/`，文件扩展名为 `.stoverride`。
- **自定义脚本**: 核心 JS 逻辑存放在 `Scripts/`。

---

## 📝 维护指南

在本地 Mac 终端修改规则后一键推送到云端：

```bash
cd ~/Desktop/qx-rules
git add -A
git commit -m "update: sync latest rules"
git push

# Network Rules & Scripts Hub

个人专属网络分流规则聚合与清洗仓库，适配 **Quantumult X** 与 **Stash**。

> 🕒 **最后自动更新时间**：`2026-09-25 13:44:41 (UTC+8)`  
> 🤖 **自动化模式**：PayPal & Google 每日由 GitHub Actions 自动拉取清洗同步；Crypto 模块保持本地手动精细维护。

---

## 📌 订阅直链概览

### 1. 核心服务 (Core Services)
| 规则分类 | 条数 | Quantumult X 订阅链接 | Stash 订阅链接 |
| :--- | :---: | :--- | :--- |
| **PayPal** | `247` | [paypal.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Payment/paypal.list) | [paypal.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Payment/paypal.yaml) |
| **Google** (清洗核心) | `7391` | [google.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Google/google.list) | [google.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Google/google.yaml) |

### 2. 加密货币交易所 (Crypto - 本地维护)
| 交易所 / 类别 | 条数 | Quantumult X 订阅链接 | Stash 订阅链接 |
| :--- | :---: | :--- | :--- |
| **Binance** | `44` | [binance.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/binance.list) | [binance.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/binance.yaml) |
| **OKX** | `12` | [okx.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/okx.list) | [okx.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/okx.yaml) |
| **Bybit** | `16` | [bybit.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/bybit.list) | [bybit.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/bybit.yaml) |
| **Bitget** | `5` | [bitget.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/bitget.list) | [bitget.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/bitget.yaml) |
| **GATE** | `11` | [gate.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/gate.list) | [gate.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/gate.yaml) |
| **Crypto** | `289` | [crypto.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/crypto.list) | [crypto.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/crypto.yaml) |

### 3. 人工智能 (AI 分流体系)
| 分类板块 | 条数 | Quantumult X 订阅链接 | Stash 订阅链接 |
| :--- | :---: | :--- | :--- |
| **openai** | `23` | [openai.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/openai.list) | [openai.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/openai.yaml) |
| **claude** | `12` | [claude.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/claude.list) | [claude.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/claude.yaml) |
| **gemini** | `30` | [gemini.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/gemini.list) | [gemini.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/gemini.yaml) |
| **copilot** | `13` | [copilot.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/copilot.list) | [copilot.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/copilot.yaml) |
| **ai_dev** | `17` | [ai_dev.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/ai_dev.list) | [ai_dev.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/ai_dev.yaml) |
| **ai_cn** | `8` | [ai_cn.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/ai_cn.list) | [ai_cn.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/ai_cn.yaml) |
| **ai_others** | `115` | [ai_others.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/ai_others.list) | [ai_others.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/ai_others.yaml) |

---

## 🛠️ 分流匹配建议优先级

```text
AI 专用策略 ➔ Crypto 交易所策略 ➔ Payment 支付策略 ➔ Google 核心策略 ➔ Final / Proxy
```

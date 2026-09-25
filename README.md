# Network Rules & Scripts Hub

个人专属网络分流规则聚合与清洗仓库，适配 **Quantumult X** 与 **Stash**。

> 🕒 **最后同步检查时间**：`2026-09-25 13:51:57 (UTC+8)`  
> 🛡️ **安全机制**：已启用 **99% 级熔断保底**（异常时拒绝覆盖旧规则 + 核心交易所/支付种子域名硬编码强制兜底）。

---

## 📌 订阅直链与熔断监控概览

### 1. 核心服务 (Core Services)
| 规则分类 | 状态 | 条数 | Quantumult X 直链 | Stash 直链 |
| :--- | :---: | :---: | :--- | :--- |
| **PayPal** | ✅ 正常 | `247` | [paypal.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Payment/paypal.list) | [paypal.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Payment/paypal.yaml) |
| **Google 核心** | ✅ 正常 | `7392` | [google.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Payment/google.list) | [google.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Payment/google.yaml) |

### 2. 加密货币交易所 (Crypto)
| 规则分类 | 状态 | 条数 | Quantumult X 直链 | Stash 直链 |
| :--- | :---: | :---: | :--- | :--- |
| **Binance (币安)** | ⚠️ 熔断锁定 (旧版 44 条) | `44` | [binance.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/binance.list) | [binance.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/binance.yaml) |
| **OKX (欧易)** | ⚠️ 熔断锁定 (旧版 12 条) | `12` | [okx.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/okx.list) | [okx.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/okx.yaml) |
| **Bybit** | ⚠️ 熔断锁定 (旧版 16 条) | `16` | [bybit.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/bybit.list) | [bybit.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/bybit.yaml) |
| **Bitget** | ⚠️ 熔断锁定 (旧版 5 条) | `5` | [bitget.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/bitget.list) | [bitget.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/bitget.yaml) |
| **Gate.io** | ⚠️ 熔断锁定 (旧版 11 条) | `11` | [gate.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/gate.list) | [gate.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/gate.yaml) |
| **Crypto 通用** | ⚠️ 熔断锁定 (旧版 289 条) | `289` | [crypto.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/Crypto/crypto.list) | [crypto.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/Crypto/crypto.yaml) |

### 3. 人工智能 (AI)
| 规则分类 | 状态 | 条数 | Quantumult X 直链 | Stash 直链 |
| :--- | :---: | :---: | :--- | :--- |
| **OpenAI** | ✅ 正常 | `22` | [openai.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/openai.list) | [openai.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/openai.yaml) |
| **Claude** | ✅ 正常 | `12` | [claude.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/claude.list) | [claude.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/claude.yaml) |
| **Gemini** | ✅ 正常 | `16` | [gemini.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/gemini.list) | [gemini.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/gemini.yaml) |
| **Copilot** | ✅ 正常 | `13` | [copilot.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/copilot.list) | [copilot.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/copilot.yaml) |
| **AI Dev Tools** | ✅ 正常 | `13` | [ai_dev.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/ai_dev.list) | [ai_dev.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/ai_dev.yaml) |
| **国内直连 AI** | ⚠️ 熔断锁定 | `8` | [ai_cn.list](https://raw.githubusercontent.com/wang47hub/wang47/main/QuantumultX/Filter/AI/ai_cn.list) | [ai_cn.yaml](https://raw.githubusercontent.com/wang47hub/wang47/main/Stash/RuleSet/AI/ai_cn.yaml) |

---

## 🛠️ 分流匹配建议优先级

```text
AI 专用策略 ➔ Crypto 交易所策略 ➔ Payment 支付策略 ➔ Google 核心策略 ➔ Final / Proxy
```

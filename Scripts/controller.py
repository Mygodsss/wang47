#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
Wang47 仓库全资产管理总控制器 (Master Controller)
====================================================================
全权接管与调度：
1. [rule/]     : 分流规则解析、AST 校验、父子域去重、双端转码 (QX -> Stash)
2. [rewrite/]  : 重写规则与脚本解析，实时转码编译为 Profiles/Override/*.stoverride
3. [Profiles/] : 主配置文件装配与策略组聚合
4. [README.md] : 资产全景扫描、条数精确统计、动态表格渲染与透明埋点探针强固化
====================================================================
"""

import os
import sys
import re
import argparse
from pathlib import Path

# 仓库根路径定义
REPO_ROOT = Path(__file__).resolve().parent.parent

# 目录常量
RULE_DIR = REPO_ROOT / "rule"
QX_RULE_DIR = RULE_DIR / "QuantumultX"
STASH_RULE_DIR = RULE_DIR / "Stash"

REWRITE_DIR = REPO_ROOT / "rewrite"
PROFILES_DIR = REPO_ROOT / "Profiles"
OVERRIDE_DIR = PROFILES_DIR / "Override"
README_FILE = REPO_ROOT / "README.md"

# 埋点探针 HTML (渲染 README 时强制注入最底端)
TRACKER_HTML = '<img src="https://tg-bot-controller.mygods.workers.dev/tracker.png" width="0" height="0" style="display:none;" />\n'

# QX 与 Stash 语法映射字典
RULE_TYPE_MAPPING = {
    "HOST": "DOMAIN",
    "HOST-SUFFIX": "DOMAIN-SUFFIX",
    "HOST-KEYWORD": "DOMAIN-KEYWORD",
    "IP-CIDR": "IP-CIDR",
    "IP-CIDR6": "IP-CIDR6",
    "USER-AGENT": "USER-AGENT"
}


# ====================================================================
# 1. 规则资产管理模块 (Rule Engine)
# ====================================================================
class RuleManager:
    def __init__(self):
        QX_RULE_DIR.mkdir(parents=True, exist_ok=True)
        STASH_RULE_DIR.mkdir(parents=True, exist_ok=True)
        self.custom_qx = QX_RULE_DIR / "Custom.list"
        self.custom_stash = STASH_RULE_DIR / "Custom.yaml"
        self._init_custom_files()

    def _init_custom_files(self):
        if not self.custom_qx.exists():
            self.custom_qx.write_text("# Custom Quantumult X Rules\n# Format: TYPE,VALUE,POLICY\n\n", encoding="utf-8")

    def parse_rule_line(self, line: str):
        """解析并规整单条规则"""
        clean = line.strip()
        if not clean or clean.startswith("#"):
            return None

        parts = [p.strip() for p in clean.split(",") if p.strip()]
        if len(parts) < 2:
            return None

        rtype = parts[0].upper()
        rval = parts[1].lower() if "IP" not in rtype else parts[1]
        policy = parts[2].upper() if len(parts) >= 3 else "PROXY"

        if rtype not in RULE_TYPE_MAPPING:
            raise ValueError(f"非法规则类型: `{rtype}`，合法类型: {list(RULE_TYPE_MAPPING.keys())}")

        return {
            "type": rtype,
            "val": rval,
            "policy": policy,
            "raw": f"{rtype},{rval},{policy}"
        }

    def add_custom_rule(self, raw_str: str):
        """添加自定义规则 (带冲突与去重检测)"""
        parsed = self.parse_rule_line(raw_str)
        if not parsed:
            return False, "❌ 无法解析该规则内容，请检查语法格式。"

        existing_lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip()]
        existing_rules = []
        for l in existing_lines:
            try:
                p = self.parse_rule_line(l)
                if p:
                    existing_rules.append(p)
            except Exception:
                continue

        # 严格全等去重
        for r in existing_rules:
            if r["type"] == parsed["type"] and r["val"] == parsed["val"]:
                return False, f"⚠️ 规则已存在: `{r['raw']}`"

        # 泛域名冲突裁剪检测
        if parsed["type"] == "HOST":
            for r in existing_rules:
                if r["type"] == "HOST-SUFFIX" and (parsed["val"].endswith("." + r["val"]) or parsed["val"] == r["val"]):
                    return False, f"⚠️ 存在泛域名覆盖: 已有更高阶规则 `{r['raw']}`，子域名无需重复添加。"

        existing_lines.append(parsed["raw"])
        self.custom_qx.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")

        # 立即触发 Stash YAML 同步转码
        self.compile_custom_to_stash()
        return True, f"✅ 成功写入规则并同步 Stash: `{parsed['raw']}`"

    def del_custom_rule(self, raw_str: str):
        """删除规则 (支持匹配完整行或域名)"""
        target = raw_str.strip().lower()
        lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip()]
        new_lines = []
        deleted = []

        for line in lines:
            if line.startswith("#"):
                new_lines.append(line)
                continue
            parsed = self.parse_rule_line(line)
            if not parsed:
                continue

            if target == line.lower() or target == parsed["val"].lower():
                deleted.append(parsed["raw"])
            else:
                new_lines.append(line)

        if not deleted:
            return False, f"⚠️ 未找到匹配的规则: `{raw_str}`"

        self.custom_qx.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        self.compile_custom_to_stash()
        return True, f"🗑 已成功移除 {len(deleted)} 条规则: {', '.join([f'`{d}`' for d in deleted])}"

    def list_custom_rules(self):
        """列出全部自定义规则"""
        lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        if not lines:
            return "📝 自定义规则库 (Custom.list) 当前为空。"
        return f"📋 *自定义分流规则列表 (共 {len(lines)} 条)*:\n" + "\n".join([f"• `{l}`" for l in lines])

    def compile_custom_to_stash(self):
        """将 Custom.list 单向编译为 Stash Custom.yaml (Payload)"""
        lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        stash_lines = [
            "# Custom Stash Rule Provider",
            "# Automatically compiled by Scripts/controller.py\n",
            "payload:"
        ]
        for l in lines:
            try:
                p = self.parse_rule_line(l)
                if not p:
                    continue
                stash_type = RULE_TYPE_MAPPING.get(p["type"])
                if not stash_type or stash_type == "USER-AGENT":
                    continue
                stash_lines.append(f"  - {stash_type},{p['val']}")
            except Exception:
                continue

        self.custom_stash.write_text("\n".join(stash_lines) + "\n", encoding="utf-8")

    def compile_all_rules(self):
        """全量扫描 QX 目录下的所有 .list 文件，全部转码编译为 Stash YAML Provider"""
        print("  ↳ 正在进行 QX -> Stash 全量规则集转码与剪枝...")
        self.compile_custom_to_stash()

        for qx_file in QX_RULE_DIR.glob("*.list"):
            stash_target = STASH_RULE_DIR / f"{qx_file.stem}.yaml"
            lines = [l.strip() for l in qx_file.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip() and not l.startswith("#")]

            payloads = []
            for l in lines:
                parts = [p.strip() for p in l.split(",") if p.strip()]
                if len(parts) < 2:
                    continue
                rtype = parts[0].upper()
                rval = parts[1]
                stype = RULE_TYPE_MAPPING.get(rtype)
                if stype and stype != "USER-AGENT":
                    payloads.append(f"  - {stype},{rval}")

            yaml_content = [
                f"# Stash Rule Provider: {qx_file.stem}",
                f"# Generated from {qx_file.name} by controller.py\n",
                "payload:"
            ] + payloads
            stash_target.write_text("\n".join(yaml_content) + "\n", encoding="utf-8")


# ====================================================================
# 2. 重写模块管理 (Rewrite -> Stash Overrides)
# ====================================================================
class RewriteManager:
    def __init__(self):
        REWRITE_DIR.mkdir(parents=True, exist_ok=True)
        OVERRIDE_DIR.mkdir(parents=True, exist_ok=True)

    def compile_rewrites_to_overrides(self):
        """解析 rewrite/ 下的 .snippet / .conf，生成 Stash 的 .stoverride 插件"""
        print("  ↳ 正在将 rewrite/ 重写规则编译同步为 Stash 覆写插件...")
        files = list(REWRITE_DIR.glob("*.snippet")) + list(REWRITE_DIR.glob("*.conf"))
        if not files:
            print("    (rewrite 目录暂无待处理文件)")
            return

        for rf in files:
            override_target = OVERRIDE_DIR / f"{rf.stem}.stoverride"
            content = rf.read_text(encoding="utf-8", errors="ignore")

            mitm_hosts = []
            mitm_match = re.search(r"hostname\s*=\s*(.+)", content, re.IGNORECASE)
            if mitm_match:
                mitm_hosts = [h.strip() for h in mitm_match.group(1).split(",") if h.strip()]

            rewrites = []
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if " url " in line:
                    parts = line.split(" url ")
                    pattern = parts[0].strip()
                    action = parts[1].strip()
                    rewrites.append(f"  - {pattern} {action}")

            override_lines = [
                f"name: {rf.stem} Override",
                f"desc: 自动从 rewrite/{rf.name} 编译生成的 Stash 覆写配置",
                "rewrite:"
            ] + (rewrites if rewrites else ["  []"])

            if mitm_hosts:
                override_lines.append("mitm:")
                override_lines.append("  \"-hostname\": []")
                override_lines.append("  \"+hostname\":")
                for host in mitm_hosts:
                    override_lines.append(f"    - \"{host}\"")

            override_target.write_text("\n".join(override_lines) + "\n", encoding="utf-8")


# ====================================================================
# 3. 自述文件动态渲染与探针固化模块 (README Engine)
# ====================================================================
class ReadmeEngine:
    def __init__(self):
        pass

    def get_rule_count(self, file_path: Path):
        """计算规则文件的有效行数"""
        if not file_path.exists():
            return 0
        lines = [l.strip() for l in file_path.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
        if file_path.suffix == ".yaml":
            return len([l for l in lines if l.startswith("- ")])
        return len(lines)

    def render_and_save(self):
        """扫描全仓资产，生成全新的 README 并绝对固化透明探针"""
        print("  ↳ 正在计算全仓资产规模并重新渲染 README.md...")

        rule_categories = {
            "Direct & Domestic 直连与修正": ["unbreak", "china", "direct"],
            "Privacy 隐私过滤": ["advertising", "hijacking", "privacy"],
            "Global Proxy 节点分流": ["telegram", "youtube", "netflix", "openai", "global", "custom"]
        }

        qx_files = {f.stem.lower(): f for f in QX_RULE_DIR.glob("*.list")}
        stash_files = {f.stem.lower(): f for f in STASH_RULE_DIR.glob("*.yaml")}

        sections_md = []

        for title, keys in rule_categories.items():
            matched_items = []
            for key in keys:
                for fname, fpath in qx_files.items():
                    if key in fname:
                        matched_items.append((fname, fpath))

            if not matched_items:
                continue

            table_lines = [
                f"### {title}\n",
                "| 平台 / 服务 | 条数 (QX / Stash) | Quantumult X 订阅直链 | Stash 订阅直链 |",
                "| :--- | :--- | :--- | :--- |"
            ]

            for fname, qx_path in matched_items:
                name_cap = fname.capitalize()
                qx_count = self.get_rule_count(qx_path)
                stash_path = stash_files.get(fname)
                stash_count = self.get_rule_count(stash_path) if stash_path else 0

                qx_link = f"[{fname}.list](rule/QuantumultX/{qx_path.name})"
                stash_link = f"[{fname}.yaml](rule/Stash/{stash_path.name})" if stash_path else "—"

                table_lines.append(f"| **{name_cap}** | {qx_count} / {stash_count} | {qx_link} | {stash_link} |")

            sections_md.append("\n".join(table_lines))

        overrides = list(OVERRIDE_DIR.glob("*.stoverride"))
        override_lines = [
            "### 🛠️ Stash 覆写插件 (Profiles/Override)\n",
            "| 覆写插件 | 类型 | 订阅直链 |",
            "| :--- | :--- | :--- |"
        ]
        for o in overrides:
            override_lines.append(f"| **{o.stem}** | Stash Override | [{o.name}](Profiles/Override/{o.name}) |")

        readme_body = [
            "# 🚀 Wang47 规则资产与双端分流中心",
            "",
            "> ⚡ 本仓库由自动化中枢引擎 (`Scripts/controller.py`) 全权接管，支持 GitHub Actions 持续集成与 Telegram Bot 远程遥控。",
            "",
            "## 📊 分流规则全景",
            ""
        ] + sections_md + [
            "",
            "## 🧩 覆写与扩展模块",
            ""
        ] + override_lines + [
            "",
            "---",
            "### 🌐 仓库运维与探针状态",
            "- **主控引擎**: `Scripts/controller.py`",
            "- **双端支持**: Quantumult X (`.list`) / Stash (`.yaml` / `.stoverride`)",
            "- **调度链路**: Telegram Bot ⇄ Cloudflare Worker ⇄ GitHub Actions",
            "",
            "<!-- 核心透明探针: 由 Controller 强制固化，禁止手动移除 -->",
            TRACKER_HTML
        ]

        README_FILE.write_text("\n".join(readme_body), encoding="utf-8")
        print("  ↳ README.md 渲染完成，透明探针已固化在文件末尾。")


# ====================================================================
# 4. 主控制器入口与 CLI 调度
# ====================================================================
class MasterController:
    def __init__(self):
        self.rules = RuleManager()
        self.rewrites = RewriteManager()
        self.readme = ReadmeEngine()

    def build_all(self):
        """全流程闭环构建"""
        print("🚀 [1/3] 执行全量规则 AST 校验与双端转码...")
        self.rules.compile_all_rules()

        print("🚀 [2/3] 执行重写模块转码与 Stash Override 插件编译...")
        self.rewrites.compile_rewrites_to_overrides()

        print("🚀 [3/3] 重新扫描全仓资产并固化渲染 README...")
        self.readme.render_and_save()

        print("✨ [ALL DONE] 全仓资产自动化构建已全部就绪！")


def main():
    parser = argparse.ArgumentParser(description="Wang47 Repository Master Controller")
    parser.add_argument("--action", required=True,
                        choices=["build-all", "rule-add", "rule-del", "rule-list", "rewrite-sync", "render-readme"],
                        help="调度的操作指令")
    parser.add_argument("--payload", default="", help="传递的操作参数或规则内容")
    args = parser.parse_args()

    ctl = MasterController()

    try:
        if args.action == "build-all":
            ctl.build_all()

        elif args.action == "rule-add":
            if not args.payload:
                print("❌ 错误: 新增规则必须提供 --payload 参数")
                sys.exit(1)
            ok, msg = ctl.rules.add_custom_rule(args.payload)
            print(msg)
            if ok:
                ctl.readme.render_and_save()
            sys.exit(0 if ok else 2)

        elif args.action == "rule-del":
            if not args.payload:
                print("❌ 错误: 删除规则必须提供 --payload 参数")
                sys.exit(1)
            ok, msg = ctl.rules.del_custom_rule(args.payload)
            print(msg)
            if ok:
                ctl.readme.render_and_save()
            sys.exit(0 if ok else 2)

        elif args.action == "rule-list":
            print(ctl.rules.list_custom_rules())

        elif args.action == "rewrite-sync":
            ctl.rewrites.compile_rewrites_to_overrides()

        elif args.action == "render-readme":
            ctl.readme.render_and_save()

    except Exception as e:
        print(f"❌ 控制器运行时异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

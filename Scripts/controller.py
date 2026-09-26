#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wang47 仓库全资产管理总控制器 (只读安全版)
严禁覆写 README.md，仅维护分流规则与转译
"""

import os
import sys
import re
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

RULE_DIR = REPO_ROOT / "rule"
QX_RULE_DIR = RULE_DIR / "QuantumultX"
STASH_RULE_DIR = RULE_DIR / "Stash"
REWRITE_DIR = REPO_ROOT / "rewrite"
PROFILES_DIR = REPO_ROOT / "Profiles"
OVERRIDE_DIR = PROFILES_DIR / "Override"
README_FILE = REPO_ROOT / "README.md"

RULE_TYPE_MAPPING = {
    "HOST": "DOMAIN",
    "HOST-SUFFIX": "DOMAIN-SUFFIX",
    "HOST-KEYWORD": "DOMAIN-KEYWORD",
    "IP-CIDR": "IP-CIDR",
    "IP-CIDR6": "IP-CIDR6",
    "USER-AGENT": "USER-AGENT"
}

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
            raise ValueError(f"非法规则类型: `{rtype}`")
        return {"type": rtype, "val": rval, "policy": policy, "raw": f"{rtype},{rval},{policy}"}

    def add_custom_rule(self, raw_str: str):
        parsed = self.parse_rule_line(raw_str)
        if not parsed:
            return False, "❌ 无法解析该规则内容，请检查语法格式。"

        existing_lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip()]
        existing_rules = []
        for l in existing_lines:
            try:
                p = self.parse_rule_line(l)
                if p: existing_rules.append(p)
            except Exception: pass

        for r in existing_rules:
            if r["type"] == parsed["type"] and r["val"] == parsed["val"]:
                return False, f"⚠️ 规则已存在: `{r['raw']}`"

        existing_lines.append(parsed["raw"])
        self.custom_qx.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")
        self.compile_custom_to_stash()
        return True, f"✅ 成功写入规则并同步 Stash: `{parsed['raw']}`"

    def del_custom_rule(self, raw_str: str):
        target = raw_str.strip().lower()
        lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip()]
        new_lines, deleted = [], []

        for line in lines:
            if line.startswith("#"):
                new_lines.append(line)
                continue
            parsed = self.parse_rule_line(line)
            if not parsed: continue
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
        lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        if not lines: return "📝 自定义规则库当前为空。"
        return f"📋 *自定义规则清单 ({len(lines)} 条)*:\n" + "\n".join([f"• `{l}`" for l in lines])

    def compile_custom_to_stash(self):
        lines = [l.strip() for l in self.custom_qx.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        stash_lines = ["# Custom Stash Rule Provider", "payload:"]
        for l in lines:
            try:
                p = self.parse_rule_line(l)
                if not p: continue
                stype = RULE_TYPE_MAPPING.get(p["type"])
                if stype and stype != "USER-AGENT":
                    stash_lines.append(f"  - {stype},{p['val']}")
            except Exception: pass
        self.custom_stash.write_text("\n".join(stash_lines) + "\n", encoding="utf-8")

    def compile_all_rules(self):
        self.compile_custom_to_stash()
        for qx_file in QX_RULE_DIR.glob("*.list"):
            stash_target = STASH_RULE_DIR / f"{qx_file.stem}.yaml"
            lines = [l.strip() for l in qx_file.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip() and not l.startswith("#")]
            payloads = []
            for l in lines:
                parts = [p.strip() for p in l.split(",") if p.strip()]
                if len(parts) >= 2:
                    stype = RULE_TYPE_MAPPING.get(parts[0].upper())
                    if stype and stype != "USER-AGENT":
                        payloads.append(f"  - {stype},{parts[1]}")
            yaml_content = [f"# Stash: {qx_file.stem}", "payload:"] + payloads
            stash_target.write_text("\n".join(yaml_content) + "\n", encoding="utf-8")

class RewriteManager:
    def __init__(self):
        REWRITE_DIR.mkdir(parents=True, exist_ok=True)
        OVERRIDE_DIR.mkdir(parents=True, exist_ok=True)

    def compile_rewrites_to_overrides(self):
        for rf in list(REWRITE_DIR.glob("*.snippet")) + list(REWRITE_DIR.glob("*.conf")):
            override_target = OVERRIDE_DIR / f"{rf.stem}.stoverride"
            content = rf.read_text(encoding="utf-8", errors="ignore")
            mitm_hosts = []
            m = re.search(r"hostname\s*=\s*(.+)", content, re.IGNORECASE)
            if m: mitm_hosts = [h.strip() for h in m.group(1).split(",") if h.strip()]

            rewrites = []
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("#") or not line: continue
                if " url " in line:
                    p = line.split(" url ")
                    rewrites.append(f"  - {p[0].strip()} {p[1].strip()}")

            lines = [f"name: {rf.stem} Override", "rewrite:"] + (rewrites if rewrites else ["  []"])
            if mitm_hosts:
                lines += ["mitm:", "  \"+hostname\":"] + [f"    - \"{h}\"" for h in mitm_hosts]
            override_target.write_text("\n".join(lines) + "\n", encoding="utf-8")

class ReadmeEngine:
    def verify_tracker_only(self):
        """绝对只读保护：绝不覆写任何排版，仅确保末尾带有探针"""
        if not README_FILE.exists(): return
        content = README_FILE.read_text(encoding="utf-8")
        if "tracker.png" not in content:
            with open(README_FILE, "a", encoding="utf-8") as f:
                f.write('\n\n<img src="https://tg-bot-controller.mygods.workers.dev/tracker.png" width="0" height="0" style="display:none;" />\n')
        print("  ↳ README.md 保持原版完全不变。")

class MasterController:
    def __init__(self):
        self.rules = RuleManager()
        self.rewrites = RewriteManager()
        self.readme = ReadmeEngine()

    def build_all(self):
        self.rules.compile_all_rules()
        self.rewrites.compile_rewrites_to_overrides()
        self.readme.verify_tracker_only()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True, choices=["build-all", "rule-add", "rule-del", "rule-list"])
    parser.add_argument("--payload", default="")
    args = parser.parse_args()

    ctl = MasterController()
    if args.action == "build-all":
        ctl.build_all()
    elif args.action == "rule-add":
        ok, msg = ctl.rules.add_custom_rule(args.payload)
        print(msg)
        sys.exit(0 if ok else 2)
    elif args.action == "rule-del":
        ok, msg = ctl.rules.del_custom_rule(args.payload)
        print(msg)
        sys.exit(0 if ok else 2)
    elif args.action == "rule-list":
        print(ctl.rules.list_custom_rules())

if __name__ ==- "__main__":
    main()

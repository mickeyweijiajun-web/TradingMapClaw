#!/usr/bin/env python3
"""Produce a redacted, reproducible TradingMapClaw Mac audit snapshot.

The script never prints API-key values, token values, environment-file contents or
report bodies. It verifies paths, model references, Council call structure, browser
temp-file cleanup, task-queue state and repository health. Python compilation is
optional because the active Mac installation can contain hundreds of scripts.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import os
import py_compile
import re
import subprocess
from pathlib import Path


def expand(value):
    return Path(value).expanduser().resolve()


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def result(check_id, status, detail, evidence=None):
    item = {"id": check_id, "status": status, "detail": detail}
    if evidence is not None:
        item["evidence"] = evidence
    return item


def parse_env(path):
    values = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def active_files(roots, suffixes):
    found = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            low = str(path).lower()
            if not path.is_file() or path.suffix not in suffixes:
                continue
            if any(part in low for part in ("/__pycache__/", "/backup/", "/backups/", ".bak", ".old", ".tmp")):
                continue
            found.append(path)
    return sorted(set(found))


def scan_text(paths, pattern):
    hits = []
    rx = re.compile(pattern, re.IGNORECASE)
    for path in paths:
        try:
            if rx.search(path.read_text(encoding="utf-8", errors="replace")):
                hits.append(str(path))
        except OSError:
            pass
    return hits


def council_audit(path):
    if not path.exists():
        return result("council", "FAIL", "codex_council.py missing")
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return result("council", "FAIL", f"syntax error: {exc}")
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
        if name != "call_hermes":
            continue
        kwargs = {kw.arg: kw.value.value for kw in node.keywords
                  if kw.arg in {"model", "provider"} and isinstance(kw.value, ast.Constant)}
        parent = node
        inside_if = False
        while parent in parents:
            parent = parents[parent]
            if isinstance(parent, ast.If):
                inside_if = True
                break
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                break
        calls.append({"line": node.lineno, "model": kwargs.get("model"), "provider": kwargs.get("provider"), "inside_if": inside_if})
    pairs = {(item["model"], item["provider"]) for item in calls}
    expected = {("deepseek-v4-pro", "deepseek"), ("glm-5.2", "zhipu"), ("gpt-5.6-sol-high", "openai")}
    missing = sorted(expected - pairs)
    r3_conditional = any(item["model"] == "gpt-5.6-sol-high" and item["inside_if"] for item in calls)
    r2_sees_r1 = bool(re.search(r"round\s*1|r1[_ ]?(vote|result|output)", source, re.IGNORECASE))
    static_ready = not missing and r3_conditional and r2_sees_r1
    return result("council", "WARN", "Static structure inspected; never marked PASS without a runtime fixture test", {
        "sha256": sha256(path), "call_sites": calls, "missing_expected_pairs": missing,
        "r3_call_inside_if": r3_conditional, "r2_source_mentions_round1": r2_sees_r1,
        "static_ready": static_ready, "runtime_fixture": "NOT_PERFORMED",
    })


def autobuy_audit(path):
    if not path.exists():
        return result("zhipu_autobuy", "FAIL", "zhipu_autobuy.py missing")
    source = path.read_text(encoding="utf-8", errors="replace")
    checks = {
        "threshold_2000": bool(re.search(r"len\([^\n]+\)\s*>\s*2000", source)),
        "named_tempfile": "NamedTemporaryFile" in source,
        "read_posix_file": "read POSIX file" in source,
        "cleanup": bool(re.search(r"(?:os\.)?(?:un)?link\(|\.unlink\(", source)),
        "finally": "finally:" in source,
    }
    return result("zhipu_autobuy", "WARN", "Static safety checks only; never marked PASS without a logged Chrome run", {"sha256": sha256(path), "static_ready": all(checks.values()), "logged_chrome_run": "NOT_PERFORMED", **checks})


def task_queue_audit(path):
    if not path.exists():
        return result("task_queue", "WARN", "task_queue.json not found")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return result("task_queue", "FAIL", f"invalid JSON: {exc}")
    items = data if isinstance(data, list) else data.get("tasks", data.get("items", []))
    if not isinstance(items, list):
        return result("task_queue", "WARN", "unknown queue shape")
    counts = {}
    access_status = None
    for item in items:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
        if item.get("id") == "codex_github_access_test_20260714":
            access_status = status
    status = "PASS" if access_status == "resolved" else "WARN"
    return result("task_queue", status, "Queue status counted without exposing task bodies", {"counts": counts, "github_access_test": access_status, "sha256": sha256(path)})


def git_audit(path, label):
    if not (path / ".git").exists():
        return result(f"git_{label}", "WARN", f"not a git checkout: {path}")
    def git(*args):
        return subprocess.run(["git", *args], cwd=path, text=True, capture_output=True, check=False)
    head = git("rev-parse", "--short", "HEAD")
    branch = git("branch", "--show-current")
    status_out = git("status", "--porcelain")
    remote = git("remote", "get-url", "origin")
    remote_present = remote.returncode == 0 and bool(remote.stdout.strip())
    evidence = {"path": str(path), "branch": branch.stdout.strip(), "head": head.stdout.strip(), "clean": not bool(status_out.stdout.strip()), "origin_configured": remote_present}
    return result(f"git_{label}", "PASS" if head.returncode == 0 else "WARN", "Repository metadata inspected; credentials and remote URL redacted", evidence)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hermes-home", default="~/.hermes")
    ap.add_argument("--shared-context", default="~/shared_context")
    ap.add_argument("--private-repo", default="~/TradingMapClaw/tmc-shared-context")
    ap.add_argument("--website-repo", default="~/TradingMapClaw/tradingmapclaw-website")
    ap.add_argument("--compile", action="store_true", help="py_compile all active Python files")
    ap.add_argument("--output-dir", default="~/shared_context", help="default directory for both snapshot files")
    ap.add_argument("--out-json", help="override JSON output path")
    ap.add_argument("--out-md", help="override Markdown output path")
    args = ap.parse_args()

    hermes = expand(args.hermes_home)
    scripts = hermes / "scripts"
    cron_scripts = hermes / "cron" / "scripts"
    skills = hermes / "skills"
    reports = hermes / "cron" / "reports"
    shared = expand(args.shared_context)
    checks = []
    paths = {"hermes": hermes, "scripts": scripts, "cron_scripts": cron_scripts, "skills": skills, "reports": reports, "shared_context": shared}
    missing = [name for name, path in paths.items() if not path.exists()]
    checks.append(result("paths", "PASS" if not missing else "FAIL", "Expected Mac directories inspected", {"missing": missing, "paths": {k: str(v) for k, v in paths.items()}}))

    py_files = active_files([scripts, cron_scripts], {".py"})
    skill_files = active_files([skills], {".md"})
    checks.append(result("inventory", "PASS" if py_files else "FAIL", "Active files counted from disk", {"python_files": len(py_files), "skill_md_files": len([p for p in skill_files if p.name == "SKILL.md"])}))

    source_files = active_files([scripts, cron_scripts, hermes], {".py", ".yaml", ".yml"})
    stale = scan_text(source_files, r"gpt-5\.5")
    checks.append(result("stale_models", "PASS" if not stale else "FAIL", "Active source/config scan for gpt-5.5", {"count": len(stale), "paths": stale[:100]}))

    env = parse_env(hermes / ".env")
    model_keys = ["HERMES_DEFAULT_MODEL", "HERMES_MODEL_LIGHT", "HERMES_MODEL_FINANCE", "HERMES_MODEL_MEDIUM", "HERMES_MODEL_DEEP", "HERMESDEFAULTMODEL", "HERMESMODELDEEP"]
    safe_env = {key: env.get(key) for key in model_keys}
    key_presence = {key: bool(env.get(key)) for key in ("DEEPSEEK_API_KEY", "ZHIPU_API_KEY", "OPENAI_API_KEY")}
    ambiguous = bool(env.get("HERMES_DEFAULT_MODEL") and env.get("HERMESDEFAULTMODEL") and env["HERMES_DEFAULT_MODEL"] != env["HERMESDEFAULTMODEL"])
    checks.append(result("env_models", "WARN" if ambiguous or any(v is None for v in safe_env.values()) else "PASS", "Only model variables and API-key presence are reported; secret values are never emitted", {"models": safe_env, "api_key_present": key_presence, "ambiguous_default_names": ambiguous}))

    checks.append(council_audit(scripts / "codex_council.py"))
    checks.append(autobuy_audit(scripts / "zhipu_autobuy.py"))
    checks.append(task_queue_audit(shared / "task_queue.json"))
    checks.append(git_audit(expand(args.private_repo), "shared_context"))
    checks.append(git_audit(expand(args.website_repo), "website"))

    if args.compile:
        failures = []
        for path in py_files:
            try:
                py_compile.compile(str(path), doraise=True)
            except Exception as exc:
                failures.append({"path": str(path), "error": str(exc)[:240]})
        checks.append(result("py_compile", "PASS" if not failures else "FAIL", "Compilation scan completed", {"checked": len(py_files), "failures": failures[:100]}))
    else:
        checks.append(result("py_compile", "SKIP", "Pass --compile to compile every active Python file"))

    summary = {status: sum(1 for item in checks if item["status"] == status) for status in ("PASS", "WARN", "FAIL", "SKIP")}
    host_id = hashlib.sha256(os.uname().nodename.encode()).hexdigest()[:12]
    report = {"schema_version": "1.0", "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "host_id": host_id, "checks": checks, "summary": summary, "overall": "FAIL" if summary["FAIL"] else ("WARN" if summary["WARN"] else "PASS")}
    output_dir = expand(args.output_dir)
    out_json = expand(args.out_json) if args.out_json else output_dir / "mac_audit_snapshot.json"
    out_md = expand(args.out_md) if args.out_md else output_dir / "mac_audit_snapshot.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# TradingMapClaw Mac audit snapshot", "", f"Generated: {report['generated_at']}", f"Overall: **{report['overall']}**", "", "| Check | Status | Detail |", "|---|---|---|"]
    for item in checks:
        lines.append(f"| `{item['id']}` | {item['status']} | {item['detail'].replace('|', '/')} |")
    lines += ["", "The JSON companion contains redacted evidence, paths and file hashes. It contains no API-key or token values.", ""]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"overall": report["overall"], "summary": summary, "json": str(out_json), "markdown": str(out_md)}))
    return 1 if summary["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

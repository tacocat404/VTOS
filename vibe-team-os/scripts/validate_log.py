#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_log.py — 의도 로그 형식 검증

로그는 이 제품의 핵심 자산이다. 형식이 틀리면 병합도 기여 귀속도 발표물도 무너진다.
생성 직후에 검사해서, 틀린 채로 쌓이지 않게 한다.

가장 중요한 검사는 **근거 없는 의도**다.
사용자가 말하지 않은 이유를 적으면 그 추측이 영구 기록이 되고 발표 자료까지 간다.
근거가 없으면 confidence 를 unconfirmed 로 두고 「실제 목적」을 비워야 한다.

사용:  validate_log.py <파일 또는 폴더> [--json] [--strict]
       --strict 를 주면 경고도 실패로 친다
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

STATUS = {"논의중", "결정됨", "보류", "폐기"}
CONFIDENCE = {"confirmed", "unconfirmed"}
SECTIONS = ["요청", "의도 분석", "결정"]          # 반드시 있어야 하는 항목
OPTIONAL = ["확인 질문", "남은 질문", "왜 다른 안을 안 골랐나"]

ID_RE = re.compile(r"^LOG-\d{4,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def parse(path):
    """frontmatter 와 본문을 나눈다. YAML 라이브러리 없이 필요한 만큼만 읽는다."""
    try:
        raw = io.open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        return None, None, "UTF-8 로 저장돼 있지 않습니다"
    except OSError as e:
        return None, None, f"읽을 수 없습니다 ({e.strerror})"

    if not raw.lstrip().startswith("---"):
        return None, None, "맨 앞에 --- 로 시작하는 머리말이 없습니다"

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return None, None, "머리말이 --- 로 닫히지 않았습니다"

    fm = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            v = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
        else:
            v = v.strip("'\"")
        fm[k.strip()] = v
    return fm, parts[2], None


def section(body, name):
    """## 제목 아래 내용을 꺼낸다."""
    m = re.search(rf"^##\s*{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)",
                  body, re.M | re.S)
    return m.group(1).strip() if m else None


def validate(path):
    errs, warns = [], []
    fm, body, perr = parse(path)
    if perr:
        return [perr], []

    # ── 머리말 ────────────────────────────────────────────
    lid = fm.get("id", "")
    if not lid:
        errs.append("id 가 없습니다")
    elif not ID_RE.match(str(lid)):
        errs.append(f"id 형식이 다릅니다: {lid!r} (LOG-0001 형태여야 합니다)")

    if not fm.get("author"):
        errs.append("author 가 없습니다")

    d = str(fm.get("date", ""))
    if not d:
        errs.append("date 가 없습니다")
    elif not DATE_RE.match(d):
        errs.append(f"date 형식이 다릅니다: {d!r} (2026-09-03 형태여야 합니다)")

    st = fm.get("status")
    if st not in STATUS:
        errs.append(f"status 가 이상합니다: {st!r} (가능: {' / '.join(sorted(STATUS))})")

    conf = fm.get("confidence")
    if conf is not None and conf not in CONFIDENCE:
        errs.append(f"confidence 가 이상합니다: {conf!r} (confirmed / unconfirmed)")

    links = fm.get("links", [])
    if isinstance(links, str):
        links = [links] if links else []
    orphan = str(fm.get("orphan", "")).lower() in ("true", "yes", "1")

    # 목차에 없는 아이디어는 정상 상태다. 다만 둘 중 하나는 있어야 추적이 된다.
    if st == "결정됨" and not links and not orphan:
        warns.append("결정됐는데 links 도 orphan 표시도 없습니다 — 어느 항목에 반영될지 추적이 안 됩니다")

    # ── 본문 ──────────────────────────────────────────────
    if body is None:
        return errs + ["본문이 없습니다"], warns

    # 제목은 카드·목록에 그대로 실린다. 없으면 빌더가 「결정」 첫 줄을 잘라 쓰는데,
    # 그러면 제목과 요약이 같은 문장이 되고 마크다운 기호까지 딸려 온다.
    m = re.search(r"^#\s+(.+)$", body, re.M)
    if not m:
        errs.append("제목이 없습니다 — 머리말 다음에 '# 한 줄 제목' 을 넣으세요")
    elif len(m.group(1).strip()) > 60:
        warns.append("제목이 깁니다 — 카드에서 잘립니다 (60자 이내 권장)")

    for name in SECTIONS:
        if section(body, name) is None:
            errs.append(f"'## {name}' 항목이 없습니다")

    # ── 근거 없는 의도 (가장 중요) ────────────────────────
    intent = section(body, "의도 분석") or ""
    purpose = ""
    m = re.search(r"실제 목적\s*[·:\-]\s*(.*)", intent)
    if m:
        purpose = m.group(1).strip()

    has_purpose = bool(purpose) and "확인 안 됨" not in purpose and purpose not in ("-", "없음")
    has_ground = bool(re.search(r"근거\s*[·:\-]\s*\S", intent)) and \
        not re.search(r"근거\s*[·:\-]\s*(없음|-)\s*$", intent, re.M)
    quoted = '"' in intent or "“" in intent or ">" in intent

    if has_purpose and not has_ground:
        errs.append("「실제 목적」을 적었는데 근거가 없습니다 — 추측이면 비워두고 confidence 를 unconfirmed 로 두세요")
    if has_purpose and has_ground and not quoted and conf == "confirmed":
        warns.append("근거에 사용자 발언 인용이 없습니다 — confirmed 로 두려면 실제 말한 문장이 있어야 합니다")
    if not has_purpose and conf == "confirmed":
        warns.append("「실제 목적」이 비어있는데 confidence 가 confirmed 입니다")

    # ── 사람에 대한 평가 ──────────────────────────────────
    if re.search(r"(실력|역량|능력|퀄리티|품질)(이|가)? ?(부족|미달|떨어|별로)", body):
        warns.append("사람에 대한 평가로 읽힐 수 있습니다 — 사람이 아니라 안(案)을 평가하세요")

    # ── 길이 ──────────────────────────────────────────────
    if len(body.strip()) > 1200:
        warns.append(f"본문이 깁니다 ({len(body.strip())}자) — 길면 아무도 안 읽습니다")

    return errs, warns


def collect(target):
    if os.path.isfile(target):
        return [target]
    out = []
    for root, _, files in os.walk(target):
        for f in sorted(files):
            if f.startswith("LOG-") and f.endswith(".md"):
                out.append(os.path.join(root, f))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    strict = "--strict" in sys.argv
    if not args:
        print("사용법: validate_log.py <파일 또는 폴더> [--json] [--strict]", file=sys.stderr)
        return 2

    files = collect(args[0])
    if not files:
        print(f"검사할 로그가 없습니다: {args[0]}")
        return 0

    report, bad, warned = [], 0, 0
    for p in files:
        e, w = validate(p)
        if e:
            bad += 1
        if w:
            warned += 1
        report.append({"file": os.path.relpath(p), "errors": e, "warnings": w})

    if as_json:
        print(json.dumps({"total": len(files), "invalid": bad, "warned": warned,
                          "items": report}, ensure_ascii=False))
        return 1 if bad or (strict and warned) else 0

    print("")
    print(f"의도 로그 검사 — {len(files)}건")
    print("")
    for r in report:
        if not r["errors"] and not r["warnings"]:
            continue
        print(f"  {r['file']}")
        for e in r["errors"]:
            print(f"    실패  {e}")
        for w in r["warnings"]:
            print(f"    확인  {w}")
        print("")

    if bad:
        print(f"형식이 맞지 않는 로그 {bad}건 — 고친 뒤 다시 검사하세요")
        return 1
    if warned:
        print(f"확인이 필요한 로그 {warned}건 (형식은 통과)")
        return 1 if strict else 0
    print(f"모두 통과 — {len(files)}/{len(files)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)

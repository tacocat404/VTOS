#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_dashboard.py — 저장소를 읽어 대시보드 데이터를 만든다

`.team/*` 과 `members/*/logs/` 를 읽어 `docs/data/dashboard.js` 를 쓴다.
계약은 `assets/dashboard/data.sample.js` 다. **필드를 바꾸면 셋을 같이 고친다** —
표본·빌더·화면. 따로 고치면 어긋나고, 어긋나면 화면이 조용히 빈칸이 된다.

fetch 가 아니라 `window.DASHBOARD = {...}` 로 쓰는 이유 —
realtime:none 폴백에서는 로컬 파일로 열어야 하는데 file:// 에서 fetch 가 막힌다.

사용:  build_dashboard.py [저장소경로] [--check]
       --check 는 파일을 쓰지 않고 계약과 맞는지만 본다
"""
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

FEED_MAX = 20          # 홈 피드에 싣는 최근 기록 수. 전부 실으면 화면도 파일도 무거워진다
WHY_MAX = 160          # 카드에 보여줄 요약 길이. 전문은 파일에 있다
STUCK_DAYS = 3         # 이 이상 답이 없는 질문은 붉게 표시한다
STALE_DAYS = 3         # 자동 기록을 이 이상 확인 못 했으면 "모름"으로 내린다


def read(path, default=""):
    try:
        return io.open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return default


def read_json(path, default=None):
    try:
        return json.loads(io.open(path, encoding="utf-8").read())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return default if default is not None else {}


def front_matter(text):
    """--- 사이의 머리말을 읽는다. YAML 라이브러리 없이 필요한 만큼만."""
    if not text.lstrip().startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            v = v.strip("'\"")
        fm[k.strip()] = v
    return fm, parts[2]


def section(body, name):
    m = re.search(rf"^##\s*{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return m.group(1).strip() if m else ""


def one_line(s, limit=WHY_MAX):
    """카드에 한 줄로 싣는다. 마크다운 기호는 걷어낸다.

    로그는 사람이 쓴 마크다운이라 **강조**·`코드`·```블록```이 섞인다.
    카드에 그대로 실으면 기호가 글자로 보인다 — 카드는 읽는 자리이지
    원문을 보는 자리가 아니다. 원문은 상세 화면에 그대로 있다.
    """
    s = s or ""
    s = re.sub(r"```.*?```", " ", s, flags=re.S)     # 코드 블록은 통째로 뺀다
    s = re.sub(r"^[ 	]*[-·*]\s+", " ", s, flags=re.M)  # 목록 머리표
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: m.group(1), s)   # 굵게 — 기호만 벗긴다
    s = re.sub(r"`([^`]+)`", lambda m: m.group(1), s)         # 인라인 코드
    s = re.sub(r"\[(.+?)\]\([^)]*\)", lambda m: m.group(1), s)  # 링크
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= limit else s[:limit - 1].rstrip() + "…"


def days_since(iso):
    if not iso:
        return 0
    try:
        d = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - d).days)
    except ValueError:
        return 0


def hook_state(root, name, mode):
    """자동 기록이 도는지. 정상 / 문제 / 모름 셋으로만 답한다.

    **모름을 정상으로 치지 않는다.** 예전 빌더는 값이 없으면 "active" 로 뒀는데,
    아무도 그 값을 채우지 않아서 기록이 하나도 안 남는 판에 화면은 초록불이었다.
    이 제품이 막으려는 실패가 그걸 막는 기능에서 났다.

    깃발이 아니라 **확인한 시각**으로 판정하는 이유 — 깃발을 끄는 것도 hook 이라,
    잘 돌다가 죽으면 마지막에 적힌 "active" 가 영원히 남는다. 죽은 쪽에 자기가
    죽었다고 적으라는 셈이다. 시각은 갱신이 멈추면 저절로 드러난다.
    """
    # 혼자 모드면 빌드 도는 사람이 곧 그 팀원이다. 직접 물어보는 게 제일 정확하다.
    if mode == "solo":
        sh = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_hooks.sh")
        if os.path.isfile(sh):
            try:
                r = subprocess.run(["sh", sh, "--json"], cwd=root, capture_output=True,
                                   text=True, encoding="utf-8", timeout=20)
                if r.stdout.strip():
                    return json.loads(r.stdout).get("state", "unknown"), None
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
                pass
        return "unknown", None

    # 팀 모드에서는 각자 자기 기계에서 적어 둔 것을 읽는다.
    # `.local/` 은 공유되지 않으므로 남의 기계 상태를 여기서 직접 볼 방법이 없다.
    st = read_json(os.path.join(root, ".team", "status", f"{name}.json"), {})
    h = st.get("hooks")
    if isinstance(h, str):              # 예전 형식 — 시각이 없으니 믿지 않는다
        return "unknown", None
    if not isinstance(h, dict):
        return "unknown", None
    at = h.get("checked_at")
    if not at or days_since(at) >= STALE_DAYS:
        return "unknown", at
    return h.get("state", "unknown"), at


def detail(body):
    """로그 상세 화면이 쓰는 전문. 요약이 아니라 원문 그대로 싣는다.

    상세는 **틀린 기록을 찾아 고치라고** 있는 화면이다. 요약해서 실으면
    AI 가 뽑은 의도가 의심스러울 때 원문과 대조할 수 없어 존재 이유가 사라진다.

    파일을 따로 못 읽어서 여기 넣는다 — 화면은 로컬 파일로도 열려야 하는데
    그때는 다른 파일을 불러올 수 없다. 로그가 수백 건이 되면 이 파일이 무거워진다.
    그때는 상세만 따로 쪼개는 것을 검토한다 (지금은 그럴 규모가 아니다).
    """
    intent = {"surface": "", "purpose": "", "evidence": ""}
    for line in section(body, "의도 분석").splitlines():
        m = re.match(r"^(표면 요청|실제 목적|근거)\s*[·:\-]\s*(.+)$", line.strip())
        if m:
            key = {"표면 요청": "surface", "실제 목적": "purpose", "근거": "evidence"}[m.group(1)]
            intent[key] = m.group(2).strip()

    asked = []
    qa = section(body, "확인 질문")
    for m in re.finditer(r"^([QA])[.．]?\s+(.+)$", qa, re.M):
        asked.append({"kind": m.group(1), "text": m.group(2).strip()})

    # 여러 줄로 접힌 항목을 한 덩어리로 모은다.
    # 첫 줄만 집으면 화면에서 문장이 중간에 끊긴 채로 보인다.
    open_qs, cur = [], None
    for line in section(body, "남은 질문").splitlines():
        m = re.match(r"^[-·*]\s*(.+)$", line.strip())
        if m:
            if cur:
                open_qs.append(cur)
            cur = m.group(1).strip()
        elif cur is not None and line.strip():
            cur += " " + line.strip()
    if cur:
        open_qs.append(cur)

    return {
        "request": re.sub(r"^>\s?", "", section(body, "요청"), flags=re.M).strip(),
        "intent": intent,
        "asked": asked,
        "decision": section(body, "결정").strip(),
        "open_questions": open_qs,
        "why_not": section(body, "왜 다른 안을 안 골랐나").strip(),
    }


def collect_logs(root, members):
    """의도 로그를 모은다. 전부 읽지만 화면에 싣는 건 요약뿐이다."""
    out = []
    for name in members:
        d = os.path.join(root, "members", name, "logs")
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not (f.startswith("LOG-") and f.endswith(".md")):
                continue
            path = os.path.join(d, f)
            fm, body = front_matter(read(path))
            if not fm:
                continue
            links = fm.get("links", [])
            if isinstance(links, str):
                links = [links] if links else []

            # 제목은 본문 첫 헤딩, 없으면 「결정」 첫 줄
            title = ""
            m = re.search(r"^#\s+(.+)$", body, re.M)
            if m:
                title = m.group(1).strip()
            if not title:
                title = one_line(section(body, "결정").split("\n")[0], 60)

            # unconfirmed 는 근거가 없다는 뜻이라 화면에서 비워 둔다.
            # 여기서 억지로 채우면 "확인이 필요합니다" 표시가 사라져 버린다.
            why = ""
            if fm.get("confidence") != "unconfirmed":
                why = one_line(section(body, "결정"))

            q = ""
            qs = section(body, "남은 질문")
            if qs:
                qm = re.search(r"^[-·*]\s*(.+)$", qs, re.M)
                q = one_line(qm.group(1), 60) if qm else ""

            out.append({
                "id": fm.get("id", f[:-3]),
                "author": name,
                "display": members[name].get("display", name),
                "at": fm.get("date", ""),
                "status": fm.get("status", "논의중"),
                "confidence": fm.get("confidence", "confirmed"),
                "title": title or fm.get("id", ""),
                "why": why,
                "detail": detail(body),
                "links": links,
                "orphan": str(fm.get("orphan", "")).lower() in ("true", "yes", "1"),
                "topic": fm.get("topic", ""),
                "supersedes": (lambda v: [v] if isinstance(v, str) and v else
                               (v if isinstance(v, list) else []))(fm.get("supersedes")),
                "open_question": q or None,
                "path": f"members/{name}/logs/{f}",
            })
    out.sort(key=lambda x: x["at"], reverse=True)
    return out


def topic_colors(root, topics):
    """주제마다 색을 정해 기억해 둔다.

    해시로 나누면 주제 4개를 5색에 넣어도 충돌 확률이 65%다 — 실제로
    「세팅」과 「대시보드」가 같은 색이 됐다. 그렇다고 목록을 정렬해 순번을
    주면 **새 주제가 생길 때마다 기존 주제 색이 밀린다.** 색이 바뀌면
    눈에 익은 것이 소용없어진다.

    그래서 한 번 정한 것을 파일에 남긴다. 기존 주제는 색이 영원히 고정되고,
    새 주제만 제일 덜 쓴 색을 받는다.
    """
    path = os.path.join(root, ".team", "topic_colors.json")
    saved = read_json(path, {})
    if not isinstance(saved, dict):
        saved = {}

    palette = ["c1", "c2", "c3", "c4", "c5"]
    changed = False
    for t in sorted(topics):                    # 정렬은 배정 순서를 재현 가능하게 한다
        if saved.get(t) in palette:
            continue
        used = {}
        for c in saved.values():
            used[c] = used.get(c, 0) + 1
        saved[t] = min(palette, key=lambda c: (used.get(c, 0), palette.index(c)))
        changed = True

    if changed:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            io.open(path, "w", encoding="utf-8", newline="").write(
                json.dumps(saved, ensure_ascii=False, indent=2, sort_keys=True) + chr(10))
        except OSError:
            pass                                # 못 써도 화면은 그려야 한다
    return saved


def system_state(root, cfg):
    """시스템 상태 화면이 쓰는 값.

    **확인할 수 있는 것만 넣는다.** 서버측 비밀정보 차단이나 차단 건수처럼
    여기서 알 수 없는 것은 채우지 않는다 — 초록불로 채워두면 실제로는
    안 켜져 있는데 켜진 줄 알게 된다. 그게 이 화면이 막으려는 바로 그 실패다.
    """
    sd = os.path.dirname(os.path.abspath(__file__))

    gi = read(os.path.join(root, ".gitignore"))
    checks = [{
        "name": "개인 폴더 제외",
        "ok": ".local/" in gi,
        "detail": ".local/ 에 넣은 것은 공유되지 않습니다",
    }, {
        "name": "공유 전 비밀정보 검사",
        "ok": os.path.isfile(os.path.join(sd, "scan_secrets.sh")),
        "detail": "키·토큰이 섞이면 공유가 중단됩니다",
    }, {
        "name": "공유 전 민감표현 검사",
        "ok": os.path.isfile(os.path.join(sd, "check_sensitive.sh")),
        "detail": "사람 평가·대외비 표현을 걸러냅니다",
    }]

    # 스킬은 명세만 읽는다. 실제 설치 여부는 이 스크립트가 알 수 없다.
    skills = []
    text = read(os.path.join(root, ".team", "skills.yaml"))
    grade = None
    for line in text.splitlines():
        st = line.strip()
        if st in ("required:", "optional:", "deferred:"):
            grade = {"required:": "필수", "optional:": "선택", "deferred:": "나중"}[st]
        elif st.startswith("- name:") and grade:
            skills.append({"name": st.split(":", 1)[1].strip(), "grade": grade})

    return {
        "checks": checks,
        "skills": skills,
        "remote": cfg.get("remote", "github"),
        "unknown": ["서버측 비밀정보 차단", "이번 주 차단 건수", "스킬 실제 설치 여부"],
    }


def prd_state(root):
    """확정된 PRD. 병합 단계가 `decisions/prd.json` 을 쓰면 여기서 읽는다.

    PRD.md 를 직접 파싱하지 않는 이유 — 항목마다 "누가 발의했나"를 붙이는 것은
    병합이 하는 판단이다. 여기서 마크다운을 되짚어 추측하면, 병합이 내린 결론과
    화면이 보여주는 것이 어긋난다. 병합이 남긴 결과만 읽는다.

    아직 병합 전이면 None 이다. 화면은 "아직 없습니다"로 처리한다.
    """
    d = read_json(os.path.join(root, "decisions", "prd.json"), None)
    if not isinstance(d, dict) or not d.get("items"):
        return None

    items = []
    for it in d["items"]:
        lead = it.get("proposers") or []
        joint = it.get("joint") or []
        items.append({
            "no": it.get("no", ""),
            "title": it.get("title", ""),
            "body": it.get("body", ""),
            "proposers": lead,
            "joint": joint,
            "links": it.get("links") or [],
            # 추적 실패를 숨기지 않는다. 목표가 80%라 20%는 원래 못 잡는다 —
            # 조용히 비워두면 발표 때 구멍이 된다 (08-와이어프레임 6장).
            "untracked": not lead and not joint,
        })

    tracked = sum(1 for i in items if not i["untracked"])
    return {
        "version": d.get("version", ""),
        "confirmed_at": d.get("confirmed_at", ""),
        "items": items,
        "tracked": tracked,
        "total": len(items),
    }


def build(root):
    cfg = read_json(os.path.join(root, ".team", "config.json"))
    members_raw = read_json(os.path.join(root, ".team", "members.json"))

    # ── 팀원 ──
    members = []
    for name, info in members_raw.items():
        if not isinstance(info, dict):
            continue
        st = read_json(os.path.join(root, ".team", "status", f"{name}.json"),
                       {"state": "idle"})
        hk, hk_at = hook_state(root, name, cfg.get("mode", "team"))
        members.append({
            "name": name,
            "display": info.get("display", name),
            "state": st.get("state", "idle"),
            "task": st.get("task"),
            "since": st.get("since"),
            "invite": info.get("invite_status", "accepted"),
            "logs": 0,                      # 아래에서 채운다
            "hooks": hk,
            "hooks_checked_at": hk_at,
        })

    logs = collect_logs(root, members_raw)

    # 주제 색은 빌드에서 정해 붙인다. 화면이 계산하지 않는다 —
    # 화면과 스크립트가 새 함수로 엮이면 한쪽이 낡았을 때 화면이 통째로 빈다.
    colors = topic_colors(root, {l["topic"] for l in logs if l["topic"]})
    for l in logs:
        l["cat"] = colors.get(l["topic"], "")

    by = {}
    for l in logs:
        by[l["author"]] = by.get(l["author"], 0) + 1
    for m in members:
        m["logs"] = by.get(m["name"], 0)

    # ── 답을 기다리는 질문. 오래된 것이 위로 ──
    questions = []
    for l in logs:
        if l["open_question"] and l["status"] != "폐기":
            questions.append({
                "text": l["open_question"],
                "author": l["author"], "display": l["display"],
                "days": days_since(l["at"]), "from": l["id"],
                "impact": None,
            })
    questions.sort(key=lambda q: q["days"], reverse=True)

    # ── 경고. 조용한 실패를 막는 자리다 ──
    alerts = []
    for m in members:
        if m["invite"] != "accepted":
            pass
        elif m["hooks"] == "untrusted":
            alerts.append({
                "level": "warn",
                "title": f"{m['display']} — 자동 기록이 꺼져 있습니다",
                "detail": "폴더 신뢰를 수락하지 않아서, 지금 하는 작업은 하나도 남지 않습니다.",
                "action": 'Claude Code 를 다시 시작하고 "예"를 누르세요',
            })
        elif m["hooks"] == "failed":
            alerts.append({
                "level": "warn",
                "title": f"{m['display']} — 자동 기록이 멈춰 있습니다",
                "detail": "턴은 세는데 정리가 안 되고 있습니다. 최근 작업이 기록에 없습니다.",
                "action": "scripts/checkpoint_gate.sh --force 로 지금 정리하세요",
            })
        elif m["hooks"] != "active":
            # 모름. 초록으로 칠하지 않는다 — 다만 경고도 아니다.
            # 그냥 안 켠 사람한테 붉은 경고를 띄우면 경고가 늘 떠 있게 되고,
            # 늘 떠 있는 경고는 아무도 안 본다.
            d = days_since(m.get("hooks_checked_at"))
            alerts.append({
                "level": "info",
                "title": f"{m['display']} — 자동 기록 상태를 모릅니다",
                "detail": (f"확인한 지 {d}일 됐습니다." if m.get("hooks_checked_at")
                           else "한 번도 확인된 적이 없습니다."),
                "action": None,
            })
        if m["invite"] == "pending":
            alerts.append({
                "level": "warn",
                "title": f"{m['display']} — 초대 수락 대기",
                "detail": "수락 전까지 이 사람의 작업은 팀에 보이지 않습니다.",
                "action": "초대를 다시 보내세요",
            })
    if cfg.get("visibility") == "public":
        alerts.append({
            "level": "info",
            "title": "이 저장소는 공개입니다",
            "detail": "기록이 팀 밖에서도 보입니다.",
            "action": None,
        })
    if cfg.get("realtime") == "degraded":
        alerts.append({
            "level": "warn",
            "title": "실시간 공유가 꺼져 있습니다",
            "detail": "작업 상태만 늦게 반영됩니다. 기록은 그대로 쌓입니다.",
            "action": None,
        })

    # ── 목차 밖 아이디어 ──
    orp = {}
    for l in logs:
        if l["orphan"] and l["topic"] and l["status"] != "폐기":
            orp[l["topic"]] = orp.get(l["topic"], 0) + 1
    orphans = [{"topic": t, "count": c}
               for t, c in sorted(orp.items(), key=lambda x: -x[1])]

    first = min((l["at"] for l in logs if l["at"]), default="")

    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project": {
            "name": cfg.get("project", "팀 프로젝트"),
            "phase": cfg.get("phase", "setup"),
            "mode": cfg.get("mode", "team"),
            "visibility": cfg.get("visibility", "public"),
            "realtime": cfg.get("realtime", "none"),
        },
        "members": members,
        # 홈 피드는 요약만. 상세까지 실으면 홈이 안 쓰는 내용으로 무거워진다.
        "feed": [{k: v for k, v in l.items() if k != "detail"} for l in logs[:FEED_MAX]],
        # 목록·상세 화면이 쓰는 전체. 여기에만 detail 이 있다.
        "logs": logs,
        "system": system_state(root, cfg),
        "prd": prd_state(root),
        "questions": questions,
        "alerts": alerts,
        "orphans": orphans,
        "stats": {
            "logs_total": len(logs),
            "unconfirmed": sum(1 for l in logs if l["confidence"] == "unconfirmed"),
            "days": days_since(first),
            "first": first,
            "by_member": by,
        },
    }


# 계약. data.sample.js 와 index.html 이 기대하는 최상위 키.
CONTRACT = ["generated_at", "project", "members", "feed", "logs",
            "questions", "alerts", "orphans", "stats", "system", "prd"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = os.path.abspath(args[0]) if args else os.getcwd()
    check = "--check" in sys.argv

    if not os.path.isfile(os.path.join(root, ".team", "config.json")):
        print(f"이 스킬이 세팅한 저장소가 아닙니다: {root}", file=sys.stderr)
        return 1

    data = build(root)

    missing = [k for k in CONTRACT if k not in data]
    extra = [k for k in data if k not in CONTRACT]
    if missing or extra:
        print("계약과 어긋납니다 — 표본·빌더·화면을 같이 고쳐야 합니다", file=sys.stderr)
        if missing:
            print(f"  빠짐: {missing}", file=sys.stderr)
        if extra:
            print(f"  계약에 없는 키: {extra}", file=sys.stderr)
        return 1

    st = data["stats"]
    if check:
        print(f"계약 통과 — 키 {len(CONTRACT)}개")
        print(f"  기록 {st['logs_total']}건 · 확인 필요 {st['unconfirmed']}건 · "
              f"질문 {len(data['questions'])}건 · 경고 {len(data['alerts'])}건")
        return 0

    # 화면이 어디 있는지에 맞춘다. 이미 쓰던 폴더에 세팅하면 docs/ 가 이미 차 있어서
    # 대시보드는 dashboard/ 로 간다 (setup.md 4장). 데이터를 docs/ 에 고정으로 쓰면
    # 화면은 dashboard/ 에 있는데 데이터는 docs/ 에 쌓여 아무것도 안 뜬다.
    home = next((d for d in ("docs", "dashboard")
                 if os.path.isfile(os.path.join(root, d, "index.html"))), "docs")
    out_dir = os.path.join(root, home, "data")
    os.makedirs(out_dir, exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, indent=2)
    io.open(os.path.join(out_dir, "dashboard.js"), "w", encoding="utf-8").write(
        "/* build_dashboard.py 가 만든 파일입니다. 직접 고치지 마세요. */\n"
        "window.DASHBOARD = " + body + ";\n")

    print(f"{home}/data/dashboard.js")
    print(f"  기록 {st['logs_total']}건 · 확인 필요 {st['unconfirmed']}건 · "
          f"질문 {len(data['questions'])}건 · 경고 {len(data['alerts'])}건")
    if st["unconfirmed"]:
        print(f"  ※ 확인이 필요한 기록 {st['unconfirmed']}건 — "
              f"왜 그렇게 정했는지가 비어 있습니다")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)

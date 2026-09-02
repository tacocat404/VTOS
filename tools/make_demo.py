#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_demo.py — 디자인 확인용 더미 데이터를 만든다.

**진짜 기록과 섞이지 않는다.** `demo/` 폴더에만 쓴다.
`members/` 와 `.team/` 은 건드리지 않는다.

왜 필요한가 — 혼자 모드에서 하루 만에 쌓인 기록으로는 확인할 수 없는 것이 있다.
「4일째 방치된 질문」, 「판단 변경」, 「초대 수락 대기」, 「추적 못 한 PRD 항목」은
전부 시간과 사람이 있어야 나온다. 화면이 그걸 제대로 그리는지 보려면 만들어야 한다.

날짜는 **실행 시각 기준 상대값**이다. 고정 날짜를 박으면 며칠 뒤에 "300일째"가 된다.

사용:  python tools/make_demo.py
"""
import io
import json
import os
import sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone()


def ago(days=0, hours=0):
    return (NOW - timedelta(days=days, hours=hours)).isoformat(timespec="seconds")


MEMBERS = [
    # 셋을 각각 다른 상태로 둔다 — 한 상태만 있으면 나머지 표시를 확인할 수 없다
    {"name": "hayun", "display": "하윤서", "state": "working",
     "task": "로그인 플로우 기획", "since": ago(hours=2), "invite": "accepted",
     "logs": 0, "hooks": "active", "hooks_checked_at": ago(hours=1),
     "joined_at": ago(24)},
    {"name": "dohyun", "display": "박도현", "state": "idle",
     "task": None, "since": ago(1), "invite": "accepted",
     "logs": 0, "hooks": "unknown", "hooks_checked_at": ago(6),
     "joined_at": ago(24)},
    {"name": "seojin", "display": "이서진", "state": "idle",
     "task": None, "since": None, "invite": "pending",
     "logs": 0, "hooks": "untrusted", "hooks_checked_at": ago(0, 3),
     "joined_at": ago(7)},
]

LOGS = [
    ("LOG-0021", "seojin", 1, "결정됨", "confirmed", "일정",
     "출시일을 2주 미룬다",
     "온보딩 재설계가 예상보다 커서 2주 미룬다. 대신 범위는 안 줄인다.",
     ["PRD-5.2"], None, []),
    ("LOG-0018", "hayun", 2, "결정됨", "confirmed", "알림",
     "알림은 하루 한 번으로 묶는다",
     "건별로 보내면 꺼버린다. 하루치를 모아 아침에 한 번 보낸다.",
     ["PRD-4.2"], None, []),
    ("LOG-0015", "dohyun", 4, "결정됨", "confirmed", "세션",
     "세션은 30일 유지한다",
     "매번 다시 로그인하면 이탈한다. 민감 작업만 재인증을 건다.",
     ["PRD-3.3"], "재인증이 필요한 작업 목록을 누가 정하나?", []),
    ("LOG-0012", "hayun", 6, "결정됨", "confirmed", "로그인",
     "소셜 로그인 단일 단계로 통합",
     "가입 3단계에서 이탈이 크다. 이메일 가입은 보조 경로로 내린다.",
     ["PRD-3.2"], "기존 이메일 가입자는 어떻게 옮기나?", []),
    ("LOG-0011", "dohyun", 8, "논의중", "confirmed", "진행률",
     "진행률을 완료 태스크 수로 잰다",
     "커밋 수는 AI 코딩에서 작업량과 무관하다. 태스크 수로 바꾼다.",
     ["PRD-4.1"], "태스크는 누가 정의하나?", []),
    # 판단 변경 — 이력 화면에서 결정과 기호가 갈리는지 확인용
    ("LOG-0009", "hayun", 10, "결정됨", "confirmed", "로그인",
     "이메일 가입을 보조 경로로 남긴다",
     "기존 사용자 이전 문제를 확인하고 선회. 소셜 단일화는 신규에만 적용한다.",
     ["PRD-3.2"], None, ["LOG-0012"]),
    # 폐기 — 취소선 확인용
    ("LOG-0007", "dohyun", 13, "폐기", "confirmed", "진행률",
     "진행률을 커밋 수로 측정",
     "AI 코딩에서는 커밋 수가 작업량과 무관해 폐기.",
     [], None, []),
    # 근거 없음 — 「확인이 필요합니다」 확인용
    ("LOG-0004", "hayun", 16, "결정됨", "unconfirmed", "회원가입",
     "비밀번호 규칙 완화",
     "",
     ["PRD-3.1"], None, []),
    ("LOG-0003", "dohyun", 19, "결정됨", "confirmed", "진행률",
     "진행률을 팀원별로 나눠 보여준다",
     "합계만 보면 누가 막혔는지 안 보인다. 사람별로 쪼갠다.",
     ["PRD-4.1"], None, []),
    # 목차 밖 — orphan 확인용
    ("LOG-0002", "hayun", 22, "논의중", "confirmed", "임시저장",
     "작성 중 내용을 자동 저장한다",
     "길게 쓰다 날리면 다시 안 쓴다. 30초마다 자동 저장한다.",
     [], "저장 주기를 사용자가 바꿀 수 있어야 하나?", []),
]

PRD_ITEMS = [
    ("3.1", "회원 가입", "이메일과 소셜 계정으로 가입한다. 비밀번호 규칙은 8자 이상만 강제한다.",
     ["hayun"], [], ["LOG-0004"]),
    ("3.2", "소셜 로그인 단일 단계", "가입 흐름을 소셜 로그인 단일 단계로 통합한다. "
     "이메일 가입은 보조 경로로 제공하되 기본 노출에서 제외한다.",
     ["hayun"], [], ["LOG-0012", "LOG-0009"]),
    ("3.3", "세션 관리", "세션은 30일 유지한다. 결제·개인정보 변경은 재인증을 요구한다.",
     ["dohyun"], ["hayun"], ["LOG-0015"]),
    # 추적 실패 — 숨기지 않는다
    ("3.5", "자동 임시저장", "작성 중인 내용을 30초마다 자동 저장한다.", [], [], []),
    ("4.1", "팀원별 진행률 표시", "완료한 태스크 수를 기준으로 진행률을 계산한다. "
     "커밋 수는 AI 코딩에서 의미가 없어 제외한다.",
     ["dohyun"], ["seojin"], ["LOG-0003", "LOG-0011"]),
    ("4.2", "알림 묶어 보내기", "알림은 하루치를 모아 아침에 한 번 보낸다.",
     ["hayun"], [], ["LOG-0018"]),
    ("5.2", "출시 일정", "온보딩 재설계 반영으로 출시를 2주 미룬다. 범위는 유지한다.",
     ["seojin"], [], ["LOG-0021"]),
]


def build():
    who = {m["name"]: m["display"] for m in MEMBERS}

    logs = []
    for lid, author, days, status, conf, topic, title, why, links, q, sup in LOGS:
        logs.append({
            "id": lid, "author": author, "display": who[author],
            "at": ago(days), "status": status, "confidence": conf,
            "title": title, "why": why if conf != "unconfirmed" else "",
            "detail": {
                "request": '"' + title + ' 어떻게 할까요?"',
                "intent": {
                    "surface": title,
                    "purpose": "" if conf == "unconfirmed" else why.split(".")[0],
                    "evidence": "" if conf == "unconfirmed" else "직전 대화에서 언급",
                },
                "asked": [], "decision": why, "open_questions": [q] if q else [],
                "why_not": "",
            },
            "links": links, "orphan": not links, "topic": topic,
            "open_question": q, "path": f"members/{author}/logs/{lid}.md",
            "supersedes": sup, "cat": "",
        })

    palette = ["c1", "c2", "c3", "c4", "c5"]
    seen = {}
    for l in logs:
        if l["topic"] and l["topic"] not in seen:
            seen[l["topic"]] = palette[len(seen) % len(palette)]
        l["cat"] = seen.get(l["topic"], "")

    by = {}
    for l in logs:
        by[l["author"]] = by.get(l["author"], 0) + 1
    for m in MEMBERS:
        m["logs"] = by.get(m["name"], 0)

    questions = sorted(
        [{"text": l["open_question"], "author": l["author"], "display": l["display"],
          "days": (NOW - datetime.fromisoformat(l["at"])).days, "from": l["id"],
          "impact": {"LOG-0012": "이 질문이 막혀 PRD 3.2 가 확정되지 않고 있습니다",
                     "LOG-0011": "PRD 4.1 의 계산 기준이 정해지지 않았습니다"}.get(l["id"])}
         for l in logs if l["open_question"] and l["status"] != "폐기"],
        key=lambda q: -q["days"])

    alerts = [
        {"level": "warn", "title": "이서진 — 자동 기록이 꺼져 있습니다",
         "detail": "폴더 신뢰를 수락하지 않아서, 지금 하는 작업은 하나도 남지 않습니다.",
         "action": 'Claude Code 를 다시 시작하고 "예"를 누르세요'},
        {"level": "warn", "title": "이서진 — 초대 수락 대기",
         "detail": "수락 전까지 이 사람의 작업은 팀에 보이지 않습니다.",
         "action": "초대를 다시 보내세요"},
        {"level": "info", "title": "이 저장소는 공개입니다",
         "detail": "기록이 팀 밖에서도 보입니다.", "action": None},
    ]

    items = []
    for no, title, body, lead, joint, links in PRD_ITEMS:
        items.append({"no": no, "title": title, "body": body,
                      "proposers": lead, "joint": joint, "links": links,
                      "untracked": not lead and not joint})

    orp = {}
    for l in logs:
        if l["orphan"] and l["topic"] and l["status"] != "폐기":
            orp[l["topic"]] = orp.get(l["topic"], 0) + 1

    return {
        "generated_at": ago(0, 0),
        "project": {"name": "팀 할일 관리", "phase": "planned", "mode": "team",
                    "visibility": "public", "realtime": "none"},
        "members": MEMBERS,
        "feed": [{k: v for k, v in l.items() if k != "detail"} for l in logs[:20]],
        "logs": logs,
        "system": {
            "checks": [
                {"name": "개인 폴더 제외", "ok": True,
                 "detail": ".local/ 에 넣은 것은 공유되지 않습니다"},
                {"name": "공유 전 비밀정보 검사", "ok": True,
                 "detail": "키·토큰이 섞이면 공유가 중단됩니다"},
                {"name": "공유 전 민감표현 검사", "ok": False,
                 "detail": "사람 평가·대외비 표현을 걸러냅니다"},
            ],
            "skills": [{"name": "idea2planning", "grade": "필수"},
                       {"name": "eli5", "grade": "선택"},
                       {"name": "humanize-korean", "grade": "선택"}],
            "remote": "github",
            "unknown": ["서버측 비밀정보 차단", "이번 주 차단 건수", "스킬 실제 설치 여부"],
        },
        "prd": {"version": "v1.0", "confirmed_at": ago(1), "items": items,
                "tracked": sum(1 for i in items if not i["untracked"]),
                "total": len(items)},
        "questions": questions,
        "alerts": alerts,
        "orphans": [{"topic": t, "count": c}
                    for t, c in sorted(orp.items(), key=lambda x: -x[1])],
        "stats": {"logs_total": len(logs),
                  "unconfirmed": sum(1 for l in logs if l["confidence"] == "unconfirmed"),
                  "days": (NOW - datetime.fromisoformat(logs[-1]["at"])).days,
                  "first": logs[-1]["at"], "by_member": by},
    }


def main():
    data = build()
    out = os.path.join(ROOT, "demo", "data")
    os.makedirs(out, exist_ok=True)
    io.open(os.path.join(out, "dashboard.js"), "w", encoding="utf-8", newline="").write(
        "/* make_demo.py 가 만든 더미 데이터입니다. 진짜 기록이 아닙니다. */" + chr(10) +
        "window.DASHBOARD = " + json.dumps(data, ensure_ascii=False, indent=2) + ";" + chr(10))

    src = os.path.join(ROOT, "vibe-team-os", "assets", "dashboard")
    for f in os.listdir(src):
        if f.endswith((".html", ".css", ".js")) and not f.startswith("data."):
            io.open(os.path.join(ROOT, "demo", f), "w", encoding="utf-8",
                    newline="").write(io.open(os.path.join(src, f), encoding="utf-8").read())

    print("demo/ 갱신")
    print(f"  팀원 {len(data['members'])}명 · 기록 {len(data['logs'])}건 · "
          f"질문 {len(data['questions'])}건 · 경고 {len(data['alerts'])}건")
    print(f"  PRD {data['prd']['tracked']}/{data['prd']['total']} 추적")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

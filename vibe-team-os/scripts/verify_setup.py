#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_setup.py — 세팅 완료 판정

통과하지 못하면 세팅을 완료로 처리하지 않는다.
"만들어 놨으니 됐겠지"로 넘어가면 팀원 환경에서 조용히 안 되는 상태가 된다.

검사 결과는 무엇이 왜 안 됐는지와 **다음에 할 일**을 함께 보여준다.
Claude 가 이 출력을 읽고 바로 고칠 수 있어야 한다.

사용:  verify_setup.py [프로젝트경로] [--json]
"""
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# 폴더 이름은 영문 소문자와 하이픈만. 한글을 쓰면 macOS 와 Windows 가
# 다르게 저장해서 팀원 OS 가 섞일 때 같은 폴더가 두 개로 보이는 사고가 난다.
FOLDER_RE = re.compile(r"^[a-z][a-z0-9-]*$")

results = []          # (통과여부, 항목, 문제, 다음에 할 일)


def check(ok, name, problem="", fix=""):
    """problem/fix 는 실패했을 때만 의미가 있다.
    통과했는데 실패 사유가 같이 붙으면 읽는 사람이 헷갈린다.
    알림 목적으로 통과와 메시지를 같이 내려면 results 에 직접 넣는다."""
    ok = bool(ok)
    results.append((ok, name, "" if ok else problem, "" if ok else fix))
    return ok


def read_json(path):
    """읽기 실패를 예외로 던지지 않는다. 무엇이 문제인지 말해준다."""
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "파일이 없습니다"
    except json.JSONDecodeError as e:
        return None, f"JSON 형식이 깨졌습니다 ({e.lineno}번째 줄)"
    except UnicodeDecodeError:
        return None, "UTF-8 로 저장돼 있지 않습니다"
    except OSError as e:
        return None, f"읽을 수 없습니다 ({e.strerror})"


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root, *args],
                           capture_output=True, text=True, encoding="utf-8", timeout=15)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    root = os.path.abspath(args[0]) if args else os.getcwd()

    # ── 저장소 ────────────────────────────────────────────
    top = git(root, "rev-parse", "--show-toplevel")
    if not check(top, "저장소", "git 저장소가 아닙니다",
                 "세팅을 처음부터 다시 실행하세요"):
        return report(as_json)
    root = os.path.abspath(top)

    # ── 프로젝트 설정 ─────────────────────────────────────
    cfg, err = read_json(os.path.join(root, ".team", "config.json"))
    if not check(cfg is not None, "프로젝트 설정", err or "",
                 ".team/config.json 을 만드세요"):
        return report(as_json)

    phase = cfg.get("phase")
    check(phase, "진행 단계", "" if phase else "phase 값이 없습니다",
          'config.json 에 "phase": "setup" 을 넣으세요')

    vis = cfg.get("visibility")
    check(vis in ("public", "private"), "공개 범위",
          "" if vis in ("public", "private") else f"값이 이상합니다: {vis!r}",
          '민감도 5항목을 물어보고 "public" 또는 "private" 으로 정하세요')

    check("sensitivity" in cfg, "민감도 판정 기록",
          "" if "sensitivity" in cfg else "판정 결과가 없습니다",
          "나중에 합류한 팀원이 '왜 이렇게 정했지'를 알 수 있어야 합니다")

    rt = cfg.get("realtime", "none")
    check(rt in ("supabase", "none", "degraded"), "실시간 설정",
          "" if rt in ("supabase", "none", "degraded") else f"값이 이상합니다: {rt!r}",
          'realtime 은 supabase / none / degraded 중 하나입니다')

    # ── 팀원 ──────────────────────────────────────────────
    mem, err = read_json(os.path.join(root, ".team", "members.json"))
    if check(mem is not None, "팀원 명단", err or "", ".team/members.json 을 만드세요"):
        names = list(mem.keys())
        check(names, "팀원 수", "" if names else "한 명도 없습니다",
              "최소 한 명은 있어야 합니다")

        bad = [n for n in names if not FOLDER_RE.match(n)]
        check(not bad, "폴더 이름 규칙",
              f"영문 소문자·하이픈만 쓸 수 있습니다: {', '.join(bad)}" if bad else "",
              "한글 폴더명은 OS 마다 다르게 저장돼 팀원끼리 같은 폴더가 두 개로 보입니다")

        missing = [n for n in names
                   if not os.path.isdir(os.path.join(root, "members", n))]
        check(not missing, "개인 폴더",
              f"폴더가 없습니다: {', '.join(missing)}" if missing else "",
              "members/<이름>/ 아래 planning · logs · notes · .local 을 만드세요")

        for n in names[:20]:
            base = os.path.join(root, "members", n)
            if not os.path.isdir(base):
                continue
            lack = [d for d in ("planning", "logs", "notes", ".local")
                    if not os.path.isdir(os.path.join(base, d))]
            check(not lack, f"개인 폴더 구성 ({n})",
                  f"빠진 폴더: {', '.join(lack)}" if lack else "",
                  f"members/{n}/ 아래에 만드세요")

        pend = [n for n, v in mem.items()
                if isinstance(v, dict) and v.get("invite_status") == "pending"]
        # 초대 미수락은 실패가 아니다. 팀원이 수락해야 하는 일이라 기다리면 된다.
        if pend:
            results.append((True, "초대 상태",
                            f"수락 대기 중: {', '.join(pend)}",
                            "대시보드에 표시하고, 공유가 안 될 때 이유를 안내하세요"))

    # ── 공용 폴더 ─────────────────────────────────────────
    for d in ("decisions", "report", ".team/status"):
        check(os.path.isdir(os.path.join(root, d)), f"{d}/",
              "" if os.path.isdir(os.path.join(root, d)) else "폴더가 없습니다",
              f"{d}/ 를 만드세요")

    # 대시보드는 폴더가 아니라 화면 파일이 있어야 한다.
    # 폴더 존재만 보면, 원래 쓰던 docs/ 가 대신 검사를 통과시킨다 —
    # 대시보드가 하나도 없는데 "통과" 가 뜬다. 조용한 실패의 전형이다.
    # 이미 쓰던 폴더에 세팅하면 대시보드는 dashboard/ 로 간다 (setup.md 4장).
    dash = [d for d in ("docs", "dashboard")
            if os.path.isfile(os.path.join(root, d, "index.html"))]
    check(bool(dash), "대시보드 화면",
          "" if dash else "docs/index.html · dashboard/index.html 둘 다 없습니다",
          "화면 파일을 복사하고 build_dashboard.py 로 데이터를 만드세요")

    # ── .gitignore ────────────────────────────────────────
    gi_path = os.path.join(root, ".gitignore")
    gi = ""
    if os.path.isfile(gi_path):
        try:
            gi = io.open(gi_path, encoding="utf-8", errors="replace").read()
        except OSError:
            gi = ""
    need = [".local/", "*.env", "*.key"]
    lack = [p for p in need if p not in gi]
    check(not lack, ".gitignore",
          f"빠진 항목: {', '.join(lack)}" if lack else "",
          "'.local/ 에 넣은 것은 절대 공유되지 않는다'가 팀원이 외울 유일한 규칙입니다")

    # 이미 올라간 게 있으면 gitignore 를 고쳐도 소용없다
    tracked = git(root, "ls-files", "--", "*/.local/*", ".local/*")
    check(not tracked, ".local 공유 여부",
          "이미 공유된 파일이 있습니다" if tracked else "",
          "git rm --cached 로 빼내세요. gitignore 만 고치면 이미 올라간 건 그대로입니다")

    # ── 필수 스킬 ─────────────────────────────────────────
    sk_path = os.path.join(root, ".team", "skills.yaml")
    if os.path.isfile(sk_path):
        try:
            sk = io.open(sk_path, encoding="utf-8", errors="replace").read()
        except OSError:
            sk = ""
        check("idea2planning" in sk, "필수 스킬",
              "" if "idea2planning" in sk else "idea2planning 이 명세에 없습니다",
              "Phase 1 에서 유일한 필수 스킬입니다")
    else:
        check(False, "스킬 명세", ".team/skills.yaml 이 없습니다",
              "required / optional / deferred 등급으로 나눠 작성하세요")

    # ── 원격 저장소 ───────────────────────────────────────
    # config 의 remote 가 none 이면 GitHub 를 안 쓰는 세팅이다 (혼자·로컬).
    # 이때 origin 을 요구하면 정상적인 세팅이 영영 완료되지 않는다.
    # "설정을 안 했다" 와 "안 쓰기로 했다" 는 다르다 — 그래서 추론하지 않고
    # config 에 적힌 것만 믿는다. 필드가 없으면 github 로 본다 (기존 세팅 호환).
    use_remote = cfg.get("remote", "github") != "none"

    if use_remote:
        remote = git(root, "remote", "get-url", "origin")
        check(remote, "원격 저장소", "" if remote else "origin 이 없습니다",
              "gh repo create 로 만들고 연결하세요")

        branches = git(root, "branch", "--format=%(refname:short)") or ""
        has_status = "team-status" in branches.split()
        check(has_status, "team-status 브랜치",
              "" if has_status else "없습니다",
              "기계 데이터를 여기 두어야 main 히스토리가 깨끗하게 유지됩니다")
    else:
        results.append((True, "원격 저장소",
                        "remote: none — GitHub 를 쓰지 않는 세팅입니다",
                        "나중에 팀을 붙이려면 config 의 remote 를 github 로 바꾸세요"))

    # ── 자동 기록 ─────────────────────────────────────────
    hooks = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_hooks.sh")
    if os.path.isfile(hooks):
        try:
            r = subprocess.run(["sh", hooks, "--json"], cwd=root,
                               capture_output=True, text=True, encoding="utf-8", timeout=20)
            state = json.loads(r.stdout).get("state") if r.stdout.strip() else "failed"
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
            state = "unknown"
        # 세팅 직후엔 아직 턴이 안 쌓여서 판정이 안 된다 — 실패로 치지 않는다
        results.append((state in ("active", "untrusted", "unknown"), "자동 기록",
                        "" if state == "active" else f"상태: {state}",
                        "폴더 신뢰를 수락했는지 확인하세요. 안 돌면 기록이 하나도 안 남습니다"))

    return report(as_json)


def report(as_json):
    failed = [r for r in results if not r[0]]

    if as_json:
        print(json.dumps({
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "items": [{"ok": o, "name": n, "problem": p, "fix": f}
                      for o, n, p, f in results],
        }, ensure_ascii=False))
        return 0 if not failed else 1

    print("")
    print("세팅 검사")
    print("")
    for ok, name, problem, fix in results:
        mark = "  통과 " if ok else "  실패 "
        line = f"{mark} {name}"
        if problem:
            line += f" — {problem}"
        print(line)
        if not ok and fix:
            print(f"         → {fix}")
        elif ok and problem and fix:
            print(f"         → {fix}")

    print("")
    if failed:
        print(f"통과 {len(results) - len(failed)} · 실패 {len(failed)}")
        print("")
        print("세팅을 완료로 처리하지 않습니다.")
        print("위 항목을 고친 뒤 다시 실행하세요.")
        return 1

    print(f"검사 통과 — {len(results)}/{len(results)}")
    print("")
    print("다음: config.json 의 phase 를 planning 으로 바꾸고 팀원에게 안내문을 보내세요.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)

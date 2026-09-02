#!/usr/bin/env sh
# restore_context.sh — 맥락 복원 (SessionStart hook)
#
# 이게 이 제품의 즉시 보상이다.
# 기록을 남기는 비용은 매일 드는데 발표는 48일 뒤다 — 그 간극을 이 스크립트가 메운다.
# 어제 남긴 기록 덕분에 오늘 바로 이어서 시작할 수 있으면, 기록할 이유가 생긴다.
#
# 폴더를 열면 "어디까지 했고 다음은 무엇인지"를 Claude 가 먼저 말하게 한다.

set -u

if [ -z "${LC_ALL:-}" ]; then
  L=$(locale -a 2>/dev/null | grep -iE '^(C|en_US|ko_KR)\.utf-?8$' | head -1)
  [ -n "$L" ] && { LC_ALL="$L"; export LC_ALL; }
fi

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$REPO" || exit 0
[ -f ".team/config.json" ] || exit 0        # 이 스킬이 세팅한 프로젝트가 아니다

# ── 나는 누구인가 ────────────────────────────────────────
# 세팅 때 기록해둔다. 없으면 git 설정에서 추정한다.
ME=$(cat .local/me 2>/dev/null)
if [ -z "$ME" ] && [ -f ".team/members.json" ]; then
  EMAIL=$(git config user.email 2>/dev/null)
  NAME=$(git config user.name 2>/dev/null)
  for key in $(grep -oE '"[a-z0-9-]+"[[:space:]]*:[[:space:]]*\{' .team/members.json 2>/dev/null | grep -oE '"[a-z0-9-]+"' | tr -d '"'); do
    if [ -d "members/$key" ]; then
      case "$EMAIL$NAME" in *"$key"*) ME="$key"; break ;; esac
    fi
  done
fi
[ -z "$ME" ] && ME=$(ls -1 members 2>/dev/null | head -1)
[ -z "$ME" ] && exit 0

PHASE=$(grep -oE '"phase"[[:space:]]*:[[:space:]]*"[^"]*"' .team/config.json 2>/dev/null | sed 's/.*"\([^"]*\)"$/\1/')
[ -z "$PHASE" ] && PHASE="planning"

OUT=""
add() { OUT="$OUT$1
"; }

add "[이어서 하기] 지금 단계: $PHASE · 작업자: $ME"

# ── 가장 최근 작업 노트 ──────────────────────────────────
NOTE=$(ls -1 "members/$ME/notes"/*.md 2>/dev/null | sort | tail -1)
if [ -n "$NOTE" ] && [ -f "$NOTE" ]; then
  add ""
  add "마지막 작업 기록 ($(basename "$NOTE" .md)):"
  # 최신 항목이 위에 쌓이므로 앞부분만 읽으면 된다
  sed -n '2,14p' "$NOTE" | sed '/^[[:space:]]*$/d' | head -8 | while IFS= read -r l; do
    printf '  %s\n' "$l"
  done > /tmp/vibe_note_$$ 2>/dev/null
  add "$(cat /tmp/vibe_note_$$ 2>/dev/null)"
  rm -f /tmp/vibe_note_$$
else
  add ""
  add "아직 작업 기록이 없습니다. 첫 작업입니다."
fi

# ── 아직 안 끝난 것 ──────────────────────────────────────
OPEN=$(grep -l 'status: 논의중' "members/$ME/logs"/*.md 2>/dev/null | head -3)
if [ -n "$OPEN" ]; then
  add ""
  add "결정이 안 난 것:"
  for f in $OPEN; do
    T=$(grep -m1 '^# ' "$f" 2>/dev/null | sed 's/^# //')
    [ -z "$T" ] && T=$(basename "$f" .md)
    add "  · $T ($(basename "$f" .md))"
  done
fi

# ── 답을 기다리는 질문 ───────────────────────────────────
Q=$(grep -h -A2 '^## 남은 질문' "members/$ME/logs"/*.md 2>/dev/null | grep '^- \|^· ' | head -3)
if [ -n "$Q" ]; then
  add ""
  add "답을 못 찾은 질문:"
  printf '%s\n' "$Q" | while IFS= read -r l; do printf '  %s\n' "$l"; done > /tmp/vibe_q_$$ 2>/dev/null
  add "$(cat /tmp/vibe_q_$$ 2>/dev/null)"
  rm -f /tmp/vibe_q_$$
fi

add ""
add "위 내용을 바탕으로 '어디까지 했고 다음은 무엇인지' 두세 문장으로 먼저 정리해 주세요. Git 용어는 쓰지 마세요."

MSG=$(printf '%s' "$OUT" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' '~' | sed 's/~/\\n/g')
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$MSG"
exit 0

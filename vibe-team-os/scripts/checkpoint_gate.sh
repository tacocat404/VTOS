#!/usr/bin/env sh
# checkpoint_gate.sh — 체크포인트 시점 판정 (UserPromptSubmit / PreCompact hook)
#
# 세션이 끝나기를 기다리지 않는다. GUI 로 하루 종일 한 세션을 열어두면 끝이 오지 않는다.
# 대신 작업 한 덩어리가 끝날 때마다 찍는다.
#
# 이 스크립트는 "지금이 그 시점인지"만 판정한다. 실제로 글을 쓰는 건 Claude 다 —
# 셸은 요약을 만들 수 없기 때문이다. 그래서 판정 결과를 additionalContext 로 전달한다.
#
# 사용:
#   checkpoint_gate.sh            평소 (10턴 안전망 판정)
#   checkpoint_gate.sh --force    대화 압축 직전. 무조건 찍는다
#   checkpoint_gate.sh --done     Claude 가 체크포인트를 마친 뒤 호출. 카운터를 리셋한다

set -u

# 안전망 간격. 10턴이면 대화 한 토막 정도라 놓친 걸 잡기에 적당하다.
INTERVAL=10
# 중복 방지 간격. 방금 찍었는데 또 찍으면 작업 노트가 지저분해진다.
MIN_GAP=5
# 이 이상 안 찍혔으면 트리거가 고장난 것이다.
STUCK=30

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
DIR="$REPO/.local"
[ -d "$DIR" ] || mkdir -p "$DIR" 2>/dev/null || exit 0

num() { N=$(cat "$1" 2>/dev/null); case "$N" in ''|*[!0-9]*) echo 0 ;; *) echo "$N" ;; esac; }

TURNS=$(num "$DIR/turn_count")
LAST=$(num "$DIR/last_checkpoint_turn")
SINCE=$((TURNS - LAST))
[ "$SINCE" -lt 0 ] && SINCE=$TURNS      # 카운터가 초기화된 경우

MODE="${1:-}"

# Claude 가 체크포인트를 마쳤다고 알려온 경우
if [ "$MODE" = "--done" ]; then
  echo "$TURNS" > "$DIR/last_checkpoint_turn" 2>/dev/null
  exit 0
fi

say() {
  # hook 출력 규약: stdout 에 JSON 을 주면 Claude 에게 전달된다.
  # 개행과 따옴표는 JSON 을 깨뜨리므로 이스케이프한다.
  MSG=$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
  printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' "$MSG"
  exit 0
}

GUIDE='체크포인트 시점입니다. 사용자에게 묻지 말고 조용히 처리한 뒤 "방금 정리했습니다" 한 줄만 남기세요. (1) 오늘 작업 노트에 지금까지 한 일을 한 문단 추가 (2) 결정이 있었다면 의도 로그 생성 - 근거가 없으면 의도는 빈칸으로 (3) 상태 공유. 마치면 scripts/checkpoint_gate.sh --done 을 실행하세요.'

# 대화가 압축되기 직전. 여기서 놓치면 원본 맥락이 사라진다.
if [ "$MODE" = "--force" ]; then
  if [ "$SINCE" -lt 2 ]; then exit 0; fi     # 방금 찍었으면 건너뛴다
  say "대화가 곧 압축됩니다. $GUIDE 압축 후에는 지금 내용을 되살릴 수 없으니 반드시 지금 남기세요."
fi

# 너무 오래 안 찍혔다 — 안전망까지 놓쳤다는 뜻이다
if [ "$SINCE" -ge "$STUCK" ]; then
  say "경고: $SINCE 턴 동안 기록이 남지 않았습니다. 자동 기록 트리거가 고장났을 수 있습니다. $GUIDE 처리 후 scripts/verify_hooks.sh 로 hook 상태도 확인하세요."
fi

# 평소 안전망
if [ "$SINCE" -ge "$INTERVAL" ] && [ "$SINCE" -ge "$MIN_GAP" ]; then
  say "$SINCE 턴 동안 기록이 남지 않았습니다. $GUIDE"
fi

exit 0

#!/usr/bin/env sh
# count_turns.sh — 턴 카운터 (Stop hook, 매 턴 실행)
#
# 이 스크립트는 대화가 한 번 오갈 때마다 실행된다.
# 그래서 두 가지를 반드시 지킨다:
#   · 빠를 것 — 파일 하나 읽고 하나 쓰는 것 이상을 하지 않는다
#   · 절대 실패하지 않을 것 — 무슨 일이 있어도 종료 코드 0
#
# 판단은 하지 않는다. 세기만 한다. 체크포인트 시점 판정은 checkpoint_gate.sh 가 한다.

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
DIR="$REPO/.local"
[ -d "$DIR" ] || mkdir -p "$DIR" 2>/dev/null || exit 0

F="$DIR/turn_count"
N=$(cat "$F" 2>/dev/null)

# 파일이 없거나 숫자가 아니면 0부터 시작한다. 오류로 만들지 않는다.
case "$N" in
  ''|*[!0-9]*) N=0 ;;
esac

echo $((N + 1)) > "$F" 2>/dev/null
exit 0

#!/usr/bin/env sh
# verify_hooks.sh — 자동 기록이 실제로 도는지 확인
#
# hook 은 등록만 되고 안 돌 수 있다. 폴더 신뢰를 수락하지 않으면 실행되지 않는데,
# 이때 아무 오류도 안 나고 그냥 기록이 하나도 안 남는다.
# 조용히 실패하는 것이 가장 나쁘다 — 그래서 눈에 보이게 만든다.
#
# 사용:  verify_hooks.sh              상태 확인
#        verify_hooks.sh --json       대시보드용 출력
#        verify_hooks.sh --record [이름]  판정을 .team/status/<이름>.json 에 적는다
#
# --record 가 필요한 이유 — `.local/` 은 공유되지 않아서 남의 기계가 어떤지
# 대시보드에서 직접 볼 방법이 없다. 각자 자기 기계에서 적어 둬야 모인다.
# 적는 값은 깃발이 아니라 **확인한 시각**이다. 깃발을 끄는 것도 hook 이라,
# 잘 돌다 죽으면 마지막 "active" 가 영원히 남는다.

set -u
REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "저장소가 아닙니다." >&2; exit 2; }
cd "$REPO" || exit 2

DIR=".local"
JSON=""
RECORD=""
RECORD_NAME=""
case "${1:-}" in
  --json)   JSON="--json" ;;
  --record) RECORD="1"; RECORD_NAME="${2:-}" ;;
esac
STATE="active"
REASON=""

num() { N=$(cat "$1" 2>/dev/null); case "$N" in ''|*[!0-9]*) echo 0 ;; *) echo "$N" ;; esac; }

TURNS=$(num "$DIR/turn_count")
LAST=$(num "$DIR/last_checkpoint_turn")

# ── 판정 ─────────────────────────────────────────────────
# 카운터 파일 자체가 없으면 Stop hook 이 한 번도 안 돌았다는 뜻이다.
if [ ! -f "$DIR/turn_count" ]; then
  STATE="untrusted"
  REASON="턴 카운터가 없습니다. 자동 기록이 한 번도 실행되지 않았습니다."
elif [ "$TURNS" -eq 0 ]; then
  STATE="untrusted"
  REASON="턴이 한 번도 세어지지 않았습니다."
elif [ $((TURNS - LAST)) -ge 30 ]; then
  STATE="failed"
  REASON="$((TURNS - LAST))턴 동안 기록이 남지 않았습니다. 판정은 도는데 기록이 안 되고 있습니다."
fi

# 스크립트가 제자리에 있는지 (경로가 틀리면 hook 이 조용히 실패한다)
SD="$(dirname "$0")"
MISSING=""
for f in count_turns.sh checkpoint_gate.sh restore_context.sh; do
  [ -f "$SD/$f" ] || MISSING="$MISSING $f"
done
if [ -n "$MISSING" ]; then
  STATE="failed"
  REASON="스크립트를 찾을 수 없습니다:$MISSING"
fi

# ── 기록 ─────────────────────────────────────────────────
if [ -n "$RECORD" ]; then
  # Windows 에는 python3 가 없고 python 만 있다. 둘 다 없으면 여기서 멈춘다 —
  # 못 적었는데 적은 척하면 대시보드가 낡은 값을 정상으로 읽는다.
  PY=""
  for c in python3 python py; do
    command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
  done
  [ -n "$PY" ] || { echo "python 을 찾을 수 없어 상태를 적지 못했습니다." >&2; exit 2; }
  "$PY" - "$RECORD_NAME" "$STATE" <<'PYEOF' || { echo "상태를 적지 못했습니다." >&2; exit 2; }
import io, json, os, sys
from datetime import datetime

name, state = sys.argv[1], sys.argv[2]
if not name:
    # 혼자 모드면 팀원이 하나뿐이라 이름을 물을 필요가 없다.
    try:
        m = json.load(io.open(".team/members.json", encoding="utf-8"))
    except (OSError, ValueError):
        m = {}
    if len(m) != 1:
        print("이름이 필요합니다: verify_hooks.sh --record <이름>", file=sys.stderr)
        raise SystemExit(1)
    name = next(iter(m))

path = os.path.join(".team", "status", name + ".json")
try:
    d = json.load(io.open(path, encoding="utf-8"))
except (OSError, ValueError):
    d = {"state": "idle", "task": None, "files": [], "since": None}
d["hooks"] = {"state": state,
              "checked_at": datetime.now().astimezone().isoformat(timespec="seconds")}
os.makedirs(os.path.dirname(path), exist_ok=True)
io.open(path, "w", encoding="utf-8", newline="").write(
    json.dumps(d, ensure_ascii=False, indent=2) + chr(10))
print(path)
PYEOF
  [ "$STATE" = "active" ] && exit 0 || exit 1
fi

# ── 출력 ─────────────────────────────────────────────────
if [ "$JSON" = "--json" ]; then
  printf '{"state":"%s","turns":%s,"since_checkpoint":%s,"reason":"%s"}\n' \
    "$STATE" "$TURNS" "$((TURNS - LAST))" "$REASON"
  [ "$STATE" = "active" ] && exit 0 || exit 1
fi

case "$STATE" in
  active)
    echo "자동 기록 정상"
    echo "  누적 턴 $TURNS · 마지막 정리 이후 $((TURNS - LAST))턴"
    exit 0
    ;;
  untrusted)
    {
      echo ""
      echo "자동 기록이 꺼져 있습니다"
      echo "  $REASON"
      echo ""
      echo "폴더 신뢰를 수락하지 않으면 자동 기록이 동작하지 않습니다."
      echo "이 상태로 작업하면 결정이 하나도 남지 않고, 아무 오류도 뜨지 않습니다."
      echo ""
      echo "해결"
      echo "  1. Claude Code 를 다시 시작하세요"
      echo "  2. \"이 폴더를 신뢰하시겠습니까?\" 가 뜨면 예를 누르세요"
      echo "  3. 이 검사를 다시 실행하세요"
    } >&2
    exit 1
    ;;
  failed)
    {
      echo ""
      echo "자동 기록에 문제가 있습니다"
      echo "  $REASON"
      echo ""
      echo "당장은 수동으로 정리할 수 있습니다 — 작업이 끊기지는 않습니다."
      echo "  scripts/checkpoint_gate.sh --force"
    } >&2
    exit 1
    ;;
esac

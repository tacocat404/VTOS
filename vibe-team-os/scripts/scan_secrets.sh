#!/usr/bin/env sh
# scan_secrets.sh — 공유 직전 자격증명 검사
#
# 저장소가 공개일 수 있고, 한 번 새어나간 키는 되돌릴 수 없다.
# 그래서 발견 시 종료 코드 2로 차단한다. (1은 차단되지 않고 그냥 진행된다)
#
# 검사 대상: 아직 공유되지 않은 변경분만. 이미 들어간 것은 별도 처리 대상이다.
# 사용:  scan_secrets.sh [--all]
#        --all 을 주면 추적 중인 파일 전체를 훑는다 (세팅 시 1회용)

set -u
REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "여기는 저장소가 아닙니다. 검사를 건너뜁니다." >&2
  exit 0
}
cd "$REPO" || exit 0

# 자격증명 패턴. 각 줄은 "이름|정규식" 형식.
# 오탐이 적은 것만 넣었다 — 차단하는 검사라 오탐이 잦으면 팀이 검사를 꺼버린다.
#
# 못 잡는 것 — 옛 형식 Supabase 서버 키는 JWT(eyJ...)라서 공개용 anon 키와 모양이 같다.
# JWT 를 전부 막으면 화면에 넣어야 하는 공개 키까지 막혀 배포가 안 된다.
# 그래서 새 형식(sb_secret_)만 본다. 옛 키를 쓰면 이 검사는 지나간다.
PATTERNS='
AWS 액세스 키|AKIA[0-9A-Z]{16}
GitHub 토큰|gh[pousr]_[A-Za-z0-9]{36,}
Google API 키|AIza[0-9A-Za-z_-]{35}
Slack 토큰|xox[baprs]-[0-9A-Za-z-]{10,}
개인 키 파일|-----BEGIN [A-Z ]*PRIVATE KEY-----
Supabase 비밀 키|sb_secret_[A-Za-z0-9_-]{20,}
Stripe 키|sk_(live|test)_[0-9A-Za-z]{16,}
OpenAI 키|sk-[A-Za-z0-9]{32,}
일반 비밀값|(api[_-]?key|secret[_-]?key|access[_-]?token|password)["'"'"' ]*[:=]["'"'"' ]*[A-Za-z0-9/+_-]{20,}
'

if [ "${1:-}" = "--all" ]; then
  FILES=$(git ls-files)
  MODE="추적 중인 파일 전체"
else
  # 아직 공유되지 않은 변경분 = 스테이지 + 워킹 트리
  FILES=$(git diff --name-only --diff-filter=ACM HEAD 2>/dev/null; git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
  FILES=$(printf '%s\n' "$FILES" | sort -u)
  MODE="공유 예정 변경분"
fi

[ -z "$FILES" ] && exit 0

HITS=""
for f in $FILES; do
  # .local/ 는 애초에 공유되지 않는다. 검사할 이유가 없다.
  case "$f" in */.local/*|.local/*) continue ;; esac
  # 이 스크립트 자신은 건너뛴다 — 패턴 목록을 들고 있어서 반드시 전부 걸린다.
  # 실제로 이걸 배포하려다 자기 자신에 막혔다.
  case "$f" in */scan_secrets.sh|scan_secrets.sh) continue ;; esac
  [ -f "$f" ] || continue
  # 바이너리는 건너뛴다
  grep -Iq . "$f" 2>/dev/null || continue

  printf '%s\n' "$PATTERNS" | while IFS='|' read -r name re; do
    [ -z "$name" ] && continue
    grep -nE -- "$re" "$f" 2>/dev/null | while IFS= read -r line; do
      echo "  $f:${line%%:*}  [$name]"
    done
  done
done > /tmp/vibe_secrets_$$ 2>/dev/null

HITS=$(cat /tmp/vibe_secrets_$$ 2>/dev/null)
rm -f /tmp/vibe_secrets_$$

if [ -n "$HITS" ]; then
  {
    echo ""
    echo "공유를 멈췄습니다 — 비밀정보로 보이는 것이 있습니다 ($MODE)"
    echo ""
    echo "$HITS"
    echo ""
    echo "이 저장소는 팀 밖에서도 보일 수 있습니다. 한 번 올라가면 되돌릴 수 없습니다."
    echo ""
    echo "해결 방법"
    echo "  1. 해당 값을 지우고 .local/ 안으로 옮기세요 (.local/ 은 절대 공유되지 않습니다)"
    echo "  2. 이미 다른 곳에 쓰고 있던 키라면 새로 발급받으세요"
    echo "  3. 비밀정보가 아니라면 알려주세요 — 확인 후 진행하겠습니다"
  } >&2
  exit 2
fi

exit 0

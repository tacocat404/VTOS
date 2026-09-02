#!/usr/bin/env sh
# check_sensitive.sh — 공유 직전 민감 표현 검사
#
# scan_secrets.sh 가 "키"를 막는다면, 이 검사는 "판단"을 막는다.
# 서버측 비밀정보 차단은 API 키만 잡는다. 정작 위험한 건 기록에 담기는 내용이다 —
# 경쟁사 분석, 가격, 계약 조건, 사람에 대한 평가.
#
# 기계는 이걸 확실히 판정할 수 없다. 그래서 이 검사는 "후보를 골라내는" 역할만 하고,
# 최종 판단은 사람이 한다. 확인을 받으면 승인 표시를 남기고 다시 실행한다.
#
# 승인:  touch .local/.sensitive-ack   (한 번 쓰면 소모된다)

set -u

# 한글 정규식이 바이트 단위로 쪼개지지 않게 UTF-8 로케일을 고정한다.
# C 로케일에서는 대괄호 표현이 한글을 3바이트로 흩어 매칭이 실패한다.
# 이름 표기가 환경마다 다르다 (C.UTF-8 / C.utf8 / en_US.utf8) — 느슨하게 찾는다.
if [ -z "${LC_ALL:-}" ]; then
  L=$(locale -a 2>/dev/null | grep -iE '^(C|en_US|ko_KR)\.utf-?8$' | head -1)
  [ -n "$L" ] && { LC_ALL="$L"; export LC_ALL; }
fi

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$REPO" || exit 0

ACK=".local/.sensitive-ack"
if [ -f "$ACK" ]; then
  rm -f "$ACK"          # 한 번만 유효하다. 계속 열어두면 검사가 무의미해진다
  exit 0
fi

# 후보 표현. 확정이 아니라 "사람이 봐야 할 것"이다.
PATTERNS='
사람에 대한 평가|(실력|역량|능력|퀄리티|품질)(이|가)? ?(부족|미달|떨어|별로|안 ?좋)
사람에 대한 평가|(일을? ?안|제대로 ?안|성의 ?없|대충) ?(하|함|했)
경쟁사 언급|(경쟁사|경쟁 ?업체|타사).{0,60}(베끼|따라|카피|대응|약점)
가격·매출|(단가|원가|마진|매출|영업이익|가격 ?정책)(이|가|은|는)? ?[0-9]
투자·자금|(투자|시리즈 ?[A-C]|밸류에이션|런웨이|번레이트)
계약 조건|(계약 ?조건|수수료율|독점|해지 ?조항|위약금)
미공개 계획|(아직 ?공개|비공개|대외비|내부용|유출 ?금지)
'

FILES=$(git diff --name-only --diff-filter=ACM HEAD 2>/dev/null; git diff --cached --name-only --diff-filter=ACM 2>/dev/null)
FILES=$(printf '%s\n' "$FILES" | sort -u)
[ -z "$FILES" ] && exit 0

OUT="/tmp/vibe_sensitive_$$"
: > "$OUT"

for f in $FILES; do
  case "$f" in */.local/*|.local/*) continue ;; esac
  # 이 스크립트 자신은 건너뛴다 — 찾을 표현 목록을 들고 있어서 반드시 전부 걸린다.
  # 실제로 이 스킬을 배포하려다 자기 자신에 막혔다.
  case "$f" in */check_sensitive.sh|check_sensitive.sh) continue ;; esac
  [ -f "$f" ] || continue
  grep -Iq . "$f" 2>/dev/null || continue

  printf '%s\n' "$PATTERNS" | while IFS='|' read -r name re; do
    [ -z "$name" ] && continue
    grep -nE -- "$re" "$f" 2>/dev/null | head -3 | while IFS= read -r line; do
      num="${line%%:*}"
      txt=$(printf '%s' "$line" | cut -d: -f2- | cut -c1-70)
      echo "  $f:$num  [$name]" >> "$OUT"
      echo "      $txt" >> "$OUT"
    done
  done
done

HITS=$(cat "$OUT" 2>/dev/null)
rm -f "$OUT"

if [ -n "$HITS" ]; then
  VIS=$(git config --get remote.origin.url >/dev/null 2>&1 && echo "팀 밖에서도 보일 수 있습니다" || echo "공유됩니다")
  {
    echo ""
    echo "공유하기 전에 확인이 필요합니다 — 민감할 수 있는 표현이 있습니다"
    echo ""
    echo "$HITS"
    echo ""
    echo "이 기록은 $VIS. 그리고 당사자가 읽습니다."
    echo ""
    echo "권장"
    echo "  사람이 아니라 안(案)을 평가하세요."
    echo "    \"김철수 것은 품질이 미달\"  →  \"A안이 요구사항 3.2를 충족하지 못함\""
    echo ""
    echo "  대외비 내용이라면 기록에서 빼거나, 저장소를 비공개로 바꾸세요."
    echo ""
    echo "괜찮다고 판단하시면 사용자에게 확인받은 뒤 아래를 실행하고 다시 시도하세요."
    echo "    touch .local/.sensitive-ack"
  } >&2
  exit 2
fi

exit 0

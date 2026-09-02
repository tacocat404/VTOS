#!/usr/bin/env sh
# verify_rls.sh — DB 권한 침투 검사
#
# 정적 페이지에 DB 키가 박히므로 막을 곳은 DB 쪽뿐이다.
# 설정만 하고 넘어가면 조용히 뚫려 있을 수 있다 — 그래서 실제로 뚫어본다.
#
# 이 검사는 2026-08-31 실물 검증에서 나온 것이다.
# 당시 설계대로 만든 스키마가 두 군데 뚫렸다:
#   · 권한 판정 함수를 public 에 두면 /rest/v1/rpc/ 로 직접 호출된다
#   · search_path 를 안 정하면 스키마 하이재킹이 가능하다
# 둘 다 SQL 로는 안 보이고 실제 HTTP 요청을 보내야 드러난다.
#
# 사용:  verify_rls.sh <프로젝트URL> <공개키>
# 통과하지 못하면 종료 코드 2. 세팅을 완료로 처리하지 않는다.

set -u
URL="${1:-}"
KEY="${2:-}"

if [ -z "$URL" ] || [ -z "$KEY" ]; then
  echo "사용법: verify_rls.sh <프로젝트URL> <공개키>" >&2
  exit 2
fi
URL="${URL%/}"

PASS=0
FAIL=0
REPORT=""

# 결과 기록. 기대와 다르면 실패로 센다.
note() {
  if [ "$1" = "ok" ]; then
    PASS=$((PASS+1)); REPORT="$REPORT
  통과   $2"
  else
    FAIL=$((FAIL+1)); REPORT="$REPORT
  ❌뚫림 $2
         $3"
  fi
}

hdr="-H apikey:$KEY -H Authorization:Bearer_$KEY"   # 자리표시. 아래에서 개별 지정한다.

get() {  # get <경로>  → 응답 본문
  curl -s --max-time 15 "$URL/rest/v1/$1" \
    -H "apikey: $KEY" -H "Authorization: Bearer $KEY" 2>/dev/null
}
code() { # code <메서드> <경로> [본문파일] → HTTP 상태코드
  if [ -n "${3:-}" ]; then
    curl -s -o /dev/null -w "%{http_code}" --max-time 15 -X "$1" "$URL/rest/v1/$2" \
      -H "apikey: $KEY" -H "Authorization: Bearer $KEY" \
      -H "Content-Type: application/json" --data-binary "@$3" 2>/dev/null
  else
    curl -s -o /dev/null -w "%{http_code}" --max-time 15 -X "$1" "$URL/rest/v1/$2" 2>/dev/null
  fi
}

echo "DB 권한 검사 — $URL"

# ── 읽기 차단 ────────────────────────────────────────────
R=$(get "messages?select=*")
[ "$R" = "[]" ] && note ok "로그인 없이 대화 조회" \
                || note no "로그인 없이 대화 조회" "빈 결과여야 하는데 응답이 있습니다: $(printf '%s' "$R" | cut -c1-90)"

R=$(get "members?select=*")
[ "$R" = "[]" ] && note ok "로그인 없이 팀원 명단 조회" \
                || note no "로그인 없이 팀원 명단 조회" "빈 결과여야 하는데 응답이 있습니다: $(printf '%s' "$R" | cut -c1-90)"

R=$(get "work_claims?select=*")
if [ "$R" = "[]" ] || printf '%s' "$R" | grep -q '"code"'; then
  note ok "로그인 없이 작업 상태 조회"
else
  note no "로그인 없이 작업 상태 조회" "응답: $(printf '%s' "$R" | cut -c1-90)"
fi

# ── 필터 우회 시도 ───────────────────────────────────────
R=$(get "messages?select=body&or=(project_id.not.is.null)")
[ "$R" = "[]" ] && note ok "필터를 우회한 조회" \
                || note no "필터를 우회한 조회" "응답: $(printf '%s' "$R" | cut -c1-90)"

# ── 쓰기 차단 ────────────────────────────────────────────
TMP="/tmp/vibe_rls_$$"
printf '%s' '{"project_id":"x","anchor_type":"question","anchor_id":"x","github_login":"x","body":"x"}' > "$TMP"
C=$(code POST "messages" "$TMP")
rm -f "$TMP"
[ "$C" != "201" ] && note ok "로그인 없이 쓰기 (HTTP $C)" \
                  || note no "로그인 없이 쓰기" "글이 등록됐습니다. 누구나 쓸 수 있는 상태입니다."

# ── 판정 함수 노출 ───────────────────────────────────────
C=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 -X POST "$URL/rest/v1/rpc/is_team_member" \
     -H "apikey: $KEY" -H "Authorization: Bearer $KEY" \
     -H "Content-Type: application/json" -d '{"p_project_id":"x"}' 2>/dev/null)
if [ "$C" = "404" ]; then
  note ok "권한 판정 함수 직접 호출 (없는 주소)"
else
  note no "권한 판정 함수 직접 호출" "HTTP $C — 함수가 노출돼 있습니다. private 스키마로 옮기세요."
fi

# ── 키 없이 접근 ─────────────────────────────────────────
C=$(code GET "messages?select=*")
[ "$C" = "401" ] && note ok "키 없이 접근 (HTTP 401)" \
                 || note no "키 없이 접근" "HTTP $C — 401 이어야 합니다."

# ── 결과 ─────────────────────────────────────────────────
echo "$REPORT"
echo ""
if [ "$FAIL" -gt 0 ]; then
  {
    echo "권한 검사에 실패했습니다 — 통과 $PASS · 실패 $FAIL"
    echo ""
    echo "이대로 두면 팀 대화를 누구나 읽거나 쓸 수 있습니다."
    echo "저장소를 비공개로 해도 소용없습니다. 앞문을 잠그고 뒷문을 열어둔 셈입니다."
    echo ""
    echo "검증을 통과한 설정 SQL 이 docs/06-설계-실시간계층.md 3장에 있습니다."
    echo "직접 새로 짜지 말고 그대로 쓰세요."
  } >&2
  exit 2
fi

echo "권한 검사 통과 — $PASS/$PASS"
echo ""
echo "다음: 보안 검사(get_advisors)도 함께 돌리세요. 경고가 1건이라도 있으면 세팅 실패입니다."
echo "      HTTP 요청으로는 안 드러나는 것을 잡아줍니다."
exit 0

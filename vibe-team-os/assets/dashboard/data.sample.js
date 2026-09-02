/* 대시보드 데이터 계약 (겸 시험용 표본)
 *
 * build_dashboard.py 가 이 구조 그대로 docs/data/dashboard.js 를 만든다.
 * index.html 은 window.DASHBOARD 를 읽는다.
 *
 * fetch() 를 쓰지 않고 <script> 로 싣는 이유 —
 * realtime:none 폴백에서는 로컬 파일(file://)로 열어야 하는데
 * file:// 에서는 fetch 가 CORS 로 막힌다. 이 방식은 양쪽 다 된다.
 *
 * 필드를 바꾸면 여기와 build_dashboard.py 와 index.html 을 같이 고친다.
 * scripts/verify_dashboard.py 가 셋이 어긋나면 잡는다.
 */
window.DASHBOARD = {
  generated_at: "2026-08-31T09:40:00+09:00",

  project: {
    name: "팀 할일 관리",
    phase: "planning",          // setup|planning|merging|planned|presenting|archived
    mode: "team",               // team|solo
    visibility: "public",       // public|private
    realtime: "none"            // supabase|none|degraded
  },

  // 팀원. status/<이름>.json 과 members.json 을 합친 것
  members: [
    {
      name: "hayun", display: "하윤서",
      state: "working",         // working|idle|away|left
      task: "로그인 플로우 기획",
      since: "2026-08-31T09:05:00+09:00",
      invite: "accepted",       // pending|accepted|failed
      logs: 14,
      // active|untrusted|failed|unknown — 모름을 active 로 치지 않는다.
      // 확인한 지 3일이 넘으면 빌더가 unknown 으로 내린다.
      hooks: "active",
      hooks_checked_at: "2026-08-31T09:05:00+09:00"
    },
    {
      name: "dohyun", display: "박도현",
      state: "idle", task: null, since: "2026-08-30T18:20:00+09:00",
      invite: "accepted", logs: 9,
      hooks: "unknown",         // 확인이 오래됨 → 경고가 아니라 회색 안내
      hooks_checked_at: "2026-08-26T10:00:00+09:00"
    },
    {
      name: "seojin", display: "이서진",
      state: "idle", task: null, since: null,
      invite: "pending", logs: 0,
      hooks: "unknown",         // 초대 수락 전이라 자동 기록 경고는 띄우지 않는다
      hooks_checked_at: null
    }
  ],

  // 홈 피드. 의도 로그를 최신순으로. 본문은 요약만 싣는다 (전문은 파일에)
  feed: [
    {
      id: "LOG-0012", author: "hayun", display: "하윤서",
      at: "2026-08-31T08:20:00+09:00",
      status: "결정됨",          // 논의중|결정됨|보류|폐기
      confidence: "confirmed",  // confirmed|unconfirmed
      title: "소셜 로그인 단일 단계로 통합",
      why: "가입 3단계에서 이탈이 크다고 판단. 이메일 가입은 보조 경로로 내림.",
      links: ["PRD-3.2"],
      orphan: false,
      topic: "로그인",
      open_question: null,
      path: "members/hayun/logs/LOG-0012.md"
    },
    {
      id: "LOG-0011", author: "dohyun", display: "박도현",
      at: "2026-08-30T17:40:00+09:00",
      status: "논의중", confidence: "confirmed",
      title: "온보딩 3단계 → 2단계 축소",
      why: "첫 화면 이탈이 가장 큼. 단 결제 정보를 뒤로 미루면 전환이 떨어질 수 있음.",
      links: [], orphan: false, topic: "온보딩",
      open_question: "결제 시점을 어디로 옮기나",
      path: "members/dohyun/logs/LOG-0011.md"
    },
    {
      id: "LOG-0010", author: "hayun", display: "하윤서",
      at: "2026-08-29T15:10:00+09:00",
      status: "결정됨", confidence: "unconfirmed",
      title: "비밀번호 규칙 완화",
      why: "",                  // unconfirmed 는 근거가 비어 있다 — 화면에서 확인 요청
      links: ["PRD-3.4"], orphan: false, topic: "로그인",
      open_question: null,
      path: "members/hayun/logs/LOG-0010.md"
    },
    {
      id: "LOG-0009", author: "dohyun", display: "박도현",
      at: "2026-08-28T11:25:00+09:00",
      status: "폐기", confidence: "confirmed",
      title: "진행률을 커밋 수로 측정",
      why: "AI 코딩에서는 커밋 수가 작업량과 무관해 폐기.",
      links: [], orphan: true, topic: "진행률",
      open_question: null,
      path: "members/dohyun/logs/LOG-0009.md"
    }
  ],

  // 목록·상세 화면이 쓰는 전체 기록. feed 는 이 중 최근 것의 요약이고,
  // detail 은 여기에만 있다 — 홈에 상세까지 실으면 안 쓰는 내용으로 무거워진다.
  logs: [
    {
      id: "LOG-0012", author: "hayun", display: "하윤서",
      at: "2026-08-31T08:20:00+09:00",
      status: "결정됨", confidence: "confirmed",
      title: "소셜 로그인 단일 단계로 통합",
      why: "가입 3단계에서 이탈이 크다고 판단. 이메일 가입은 보조 경로로 내림.",
      links: ["PRD-3.2"], orphan: false, topic: "로그인",
      open_question: null,
      path: "members/hayun/logs/LOG-0012.md",
      cat: "c3",             // 주제 색. 빌드가 정해 붙인다
      detail: {
        // 사용자가 한 말 그대로. 요약하면 AI 해석과 대조할 수 없다
        request: "\"로그인 화면 좀 더 간단하게 만들어줘\"",
        intent: {
          surface: "로그인 UI 단순화",
          purpose: "첫 진입 이탈률을 낮추려는 것",
          evidence: "직전 대화에서 \"가입하다 다 나가는 것 같다\"고 언급"
        },
        asked: [
          { kind: "Q", text: "단순화의 기준은? 입력 필드 수 / 단계 수 / 시각 요소?" },
          { kind: "A", text: "단계 수. 3단계를 1단계로." }
        ],
        decision: "소셜 로그인 단일 단계로 통합. 이메일 가입은 보조 경로로 내림.",
        open_questions: ["기존 이메일 가입자는 어떻게 옮기나?"],
        why_not: ""
      }
    },
    {
      id: "LOG-0010", author: "hayun", display: "하윤서",
      at: "2026-08-29T15:10:00+09:00",
      status: "결정됨", confidence: "unconfirmed",
      title: "비밀번호 규칙 완화",
      why: "",
      links: ["PRD-3.4"], orphan: false, topic: "로그인",
      open_question: null,
      path: "members/hayun/logs/LOG-0010.md",
      cat: "c3",             // 주제 색. 빌드가 정해 붙인다
      detail: {
        request: "\"비밀번호 규칙 좀 풀어줘\"",
        // unconfirmed 는 여기가 비어 있다. 채우면 화면의 확인 요청이 사라진다
        intent: { surface: "비밀번호 규칙 완화", purpose: "", evidence: "" },
        asked: [],
        decision: "특수문자 필수를 뺀다.",
        open_questions: [],
        why_not: ""
      }
    }
  ],

  // 답을 못 찾은 질문. 오래된 것이 위로 온다
  questions: [
    {
      text: "기존 이메일 가입자는 어떻게 옮기나?",
      author: "hayun", display: "하윤서",
      days: 4, from: "LOG-0012",
      impact: "PRD 3장이 확정되지 않고 있습니다"
    },
    {
      text: "태스크는 누가 정의하나?",
      author: "dohyun", display: "박도현",
      days: 2, from: "LOG-0009", impact: null
    }
  ],

  // 조용한 실패를 막는다. 문제가 없으면 빈 배열
  alerts: [
    {
      level: "info",            // warn|info
      title: "박도현 — 자동 기록 상태를 모릅니다",
      detail: "확인한 지 6일 됐습니다.",
      action: null
    },
    {
      level: "warn",
      title: "이서진 — 초대 수락 대기 (3일)",
      detail: "수락 전까지 이 사람의 작업은 팀에 보이지 않습니다.",
      action: "초대를 다시 보내세요"
    },
    {
      level: "info",
      title: "이 저장소는 공개입니다",
      detail: "기록이 팀 밖에서도 보입니다.",
      action: null
    }
  ],

  // 목차 밖 아이디어. 같은 주제로 3건 넘게 쌓이면 목차 편입을 제안한다
  orphans: [
    { topic: "진행률", count: 1 }
  ],

  // 시스템 상태 화면이 쓴다. 확인할 수 있는 것만 넣는다 —
  // 모르는 것을 초록으로 칠하면 이 화면의 존재 이유가 사라진다.
  system: {
    checks: [
      { name: "개인 폴더 제외", ok: true, detail: ".local/ 에 넣은 것은 공유되지 않습니다" },
      { name: "공유 전 비밀정보 검사", ok: true, detail: "키·토큰이 섞이면 공유가 중단됩니다" },
      { name: "공유 전 민감표현 검사", ok: true, detail: "사람 평가·대외비 표현을 걸러냅니다" }
    ],
    skills: [
      { name: "idea2planning", grade: "필수" },
      { name: "humanize-korean", grade: "선택" }
    ],
    remote: "github",          // github|none
    unknown: ["서버측 비밀정보 차단", "이번 주 차단 건수", "스킬 실제 설치 여부"]
  },

  stats: {
    logs_total: 23,
    unconfirmed: 1,             // 확인이 필요한 로그 — 방치되면 틀린 기록이 굳는다
    days: 7,
    by_member: { hayun: 14, dohyun: 9, seojin: 0 }
  }
};

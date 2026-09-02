/* make_demo.py 가 만든 더미 데이터입니다. 진짜 기록이 아닙니다. */
window.DASHBOARD = {
  "generated_at": "2026-09-02T16:31:29+09:00",
  "project": {
    "name": "팀 할일 관리",
    "phase": "planned",
    "mode": "team",
    "visibility": "public",
    "realtime": "none"
  },
  "members": [
    {
      "name": "hayun",
      "display": "하윤서",
      "state": "working",
      "task": "로그인 플로우 기획",
      "since": "2026-09-02T14:31:29+09:00",
      "invite": "accepted",
      "logs": 5,
      "hooks": "active",
      "hooks_checked_at": "2026-09-02T15:31:29+09:00",
      "joined_at": "2026-08-09T16:31:29+09:00"
    },
    {
      "name": "dohyun",
      "display": "박도현",
      "state": "idle",
      "task": null,
      "since": "2026-09-01T16:31:29+09:00",
      "invite": "accepted",
      "logs": 4,
      "hooks": "unknown",
      "hooks_checked_at": "2026-08-27T16:31:29+09:00",
      "joined_at": "2026-08-09T16:31:29+09:00"
    },
    {
      "name": "seojin",
      "display": "이서진",
      "state": "idle",
      "task": null,
      "since": null,
      "invite": "pending",
      "logs": 1,
      "hooks": "untrusted",
      "hooks_checked_at": "2026-09-02T13:31:29+09:00",
      "joined_at": "2026-08-26T16:31:29+09:00"
    }
  ],
  "feed": [
    {
      "id": "LOG-0021",
      "author": "seojin",
      "display": "이서진",
      "at": "2026-09-01T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "출시일을 2주 미룬다",
      "why": "온보딩 재설계가 예상보다 커서 2주 미룬다. 대신 범위는 안 줄인다.",
      "links": [
        "PRD-5.2"
      ],
      "orphan": false,
      "topic": "일정",
      "open_question": null,
      "path": "members/seojin/logs/LOG-0021.md",
      "supersedes": [],
      "cat": "c1"
    },
    {
      "id": "LOG-0018",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-31T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "알림은 하루 한 번으로 묶는다",
      "why": "건별로 보내면 꺼버린다. 하루치를 모아 아침에 한 번 보낸다.",
      "links": [
        "PRD-4.2"
      ],
      "orphan": false,
      "topic": "알림",
      "open_question": null,
      "path": "members/hayun/logs/LOG-0018.md",
      "supersedes": [],
      "cat": "c2"
    },
    {
      "id": "LOG-0015",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-29T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "세션은 30일 유지한다",
      "why": "매번 다시 로그인하면 이탈한다. 민감 작업만 재인증을 건다.",
      "links": [
        "PRD-3.3"
      ],
      "orphan": false,
      "topic": "세션",
      "open_question": "재인증이 필요한 작업 목록을 누가 정하나?",
      "path": "members/dohyun/logs/LOG-0015.md",
      "supersedes": [],
      "cat": "c3"
    },
    {
      "id": "LOG-0012",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-27T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "소셜 로그인 단일 단계로 통합",
      "why": "가입 3단계에서 이탈이 크다. 이메일 가입은 보조 경로로 내린다.",
      "links": [
        "PRD-3.2"
      ],
      "orphan": false,
      "topic": "로그인",
      "open_question": "기존 이메일 가입자는 어떻게 옮기나?",
      "path": "members/hayun/logs/LOG-0012.md",
      "supersedes": [],
      "cat": "c4"
    },
    {
      "id": "LOG-0011",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-25T16:31:29+09:00",
      "status": "논의중",
      "confidence": "confirmed",
      "title": "진행률을 완료 태스크 수로 잰다",
      "why": "커밋 수는 AI 코딩에서 작업량과 무관하다. 태스크 수로 바꾼다.",
      "links": [
        "PRD-4.1"
      ],
      "orphan": false,
      "topic": "진행률",
      "open_question": "태스크는 누가 정의하나?",
      "path": "members/dohyun/logs/LOG-0011.md",
      "supersedes": [],
      "cat": "c5"
    },
    {
      "id": "LOG-0009",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-23T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "이메일 가입을 보조 경로로 남긴다",
      "why": "기존 사용자 이전 문제를 확인하고 선회. 소셜 단일화는 신규에만 적용한다.",
      "links": [
        "PRD-3.2"
      ],
      "orphan": false,
      "topic": "로그인",
      "open_question": null,
      "path": "members/hayun/logs/LOG-0009.md",
      "supersedes": [
        "LOG-0012"
      ],
      "cat": "c4"
    },
    {
      "id": "LOG-0007",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-20T16:31:29+09:00",
      "status": "폐기",
      "confidence": "confirmed",
      "title": "진행률을 커밋 수로 측정",
      "why": "AI 코딩에서는 커밋 수가 작업량과 무관해 폐기.",
      "links": [],
      "orphan": true,
      "topic": "진행률",
      "open_question": null,
      "path": "members/dohyun/logs/LOG-0007.md",
      "supersedes": [],
      "cat": "c5"
    },
    {
      "id": "LOG-0004",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-17T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "unconfirmed",
      "title": "비밀번호 규칙 완화",
      "why": "",
      "links": [
        "PRD-3.1"
      ],
      "orphan": false,
      "topic": "회원가입",
      "open_question": null,
      "path": "members/hayun/logs/LOG-0004.md",
      "supersedes": [],
      "cat": "c1"
    },
    {
      "id": "LOG-0003",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-14T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "진행률을 팀원별로 나눠 보여준다",
      "why": "합계만 보면 누가 막혔는지 안 보인다. 사람별로 쪼갠다.",
      "links": [
        "PRD-4.1"
      ],
      "orphan": false,
      "topic": "진행률",
      "open_question": null,
      "path": "members/dohyun/logs/LOG-0003.md",
      "supersedes": [],
      "cat": "c5"
    },
    {
      "id": "LOG-0002",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-11T16:31:29+09:00",
      "status": "논의중",
      "confidence": "confirmed",
      "title": "작성 중 내용을 자동 저장한다",
      "why": "길게 쓰다 날리면 다시 안 쓴다. 30초마다 자동 저장한다.",
      "links": [],
      "orphan": true,
      "topic": "임시저장",
      "open_question": "저장 주기를 사용자가 바꿀 수 있어야 하나?",
      "path": "members/hayun/logs/LOG-0002.md",
      "supersedes": [],
      "cat": "c2"
    }
  ],
  "logs": [
    {
      "id": "LOG-0021",
      "author": "seojin",
      "display": "이서진",
      "at": "2026-09-01T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "출시일을 2주 미룬다",
      "why": "온보딩 재설계가 예상보다 커서 2주 미룬다. 대신 범위는 안 줄인다.",
      "detail": {
        "request": "\"출시일을 2주 미룬다 어떻게 할까요?\"",
        "intent": {
          "surface": "출시일을 2주 미룬다",
          "purpose": "온보딩 재설계가 예상보다 커서 2주 미룬다",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "온보딩 재설계가 예상보다 커서 2주 미룬다. 대신 범위는 안 줄인다.",
        "open_questions": [],
        "why_not": ""
      },
      "links": [
        "PRD-5.2"
      ],
      "orphan": false,
      "topic": "일정",
      "open_question": null,
      "path": "members/seojin/logs/LOG-0021.md",
      "supersedes": [],
      "cat": "c1"
    },
    {
      "id": "LOG-0018",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-31T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "알림은 하루 한 번으로 묶는다",
      "why": "건별로 보내면 꺼버린다. 하루치를 모아 아침에 한 번 보낸다.",
      "detail": {
        "request": "\"알림은 하루 한 번으로 묶는다 어떻게 할까요?\"",
        "intent": {
          "surface": "알림은 하루 한 번으로 묶는다",
          "purpose": "건별로 보내면 꺼버린다",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "건별로 보내면 꺼버린다. 하루치를 모아 아침에 한 번 보낸다.",
        "open_questions": [],
        "why_not": ""
      },
      "links": [
        "PRD-4.2"
      ],
      "orphan": false,
      "topic": "알림",
      "open_question": null,
      "path": "members/hayun/logs/LOG-0018.md",
      "supersedes": [],
      "cat": "c2"
    },
    {
      "id": "LOG-0015",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-29T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "세션은 30일 유지한다",
      "why": "매번 다시 로그인하면 이탈한다. 민감 작업만 재인증을 건다.",
      "detail": {
        "request": "\"세션은 30일 유지한다 어떻게 할까요?\"",
        "intent": {
          "surface": "세션은 30일 유지한다",
          "purpose": "매번 다시 로그인하면 이탈한다",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "매번 다시 로그인하면 이탈한다. 민감 작업만 재인증을 건다.",
        "open_questions": [
          "재인증이 필요한 작업 목록을 누가 정하나?"
        ],
        "why_not": ""
      },
      "links": [
        "PRD-3.3"
      ],
      "orphan": false,
      "topic": "세션",
      "open_question": "재인증이 필요한 작업 목록을 누가 정하나?",
      "path": "members/dohyun/logs/LOG-0015.md",
      "supersedes": [],
      "cat": "c3"
    },
    {
      "id": "LOG-0012",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-27T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "소셜 로그인 단일 단계로 통합",
      "why": "가입 3단계에서 이탈이 크다. 이메일 가입은 보조 경로로 내린다.",
      "detail": {
        "request": "\"소셜 로그인 단일 단계로 통합 어떻게 할까요?\"",
        "intent": {
          "surface": "소셜 로그인 단일 단계로 통합",
          "purpose": "가입 3단계에서 이탈이 크다",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "가입 3단계에서 이탈이 크다. 이메일 가입은 보조 경로로 내린다.",
        "open_questions": [
          "기존 이메일 가입자는 어떻게 옮기나?"
        ],
        "why_not": ""
      },
      "links": [
        "PRD-3.2"
      ],
      "orphan": false,
      "topic": "로그인",
      "open_question": "기존 이메일 가입자는 어떻게 옮기나?",
      "path": "members/hayun/logs/LOG-0012.md",
      "supersedes": [],
      "cat": "c4"
    },
    {
      "id": "LOG-0011",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-25T16:31:29+09:00",
      "status": "논의중",
      "confidence": "confirmed",
      "title": "진행률을 완료 태스크 수로 잰다",
      "why": "커밋 수는 AI 코딩에서 작업량과 무관하다. 태스크 수로 바꾼다.",
      "detail": {
        "request": "\"진행률을 완료 태스크 수로 잰다 어떻게 할까요?\"",
        "intent": {
          "surface": "진행률을 완료 태스크 수로 잰다",
          "purpose": "커밋 수는 AI 코딩에서 작업량과 무관하다",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "커밋 수는 AI 코딩에서 작업량과 무관하다. 태스크 수로 바꾼다.",
        "open_questions": [
          "태스크는 누가 정의하나?"
        ],
        "why_not": ""
      },
      "links": [
        "PRD-4.1"
      ],
      "orphan": false,
      "topic": "진행률",
      "open_question": "태스크는 누가 정의하나?",
      "path": "members/dohyun/logs/LOG-0011.md",
      "supersedes": [],
      "cat": "c5"
    },
    {
      "id": "LOG-0009",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-23T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "이메일 가입을 보조 경로로 남긴다",
      "why": "기존 사용자 이전 문제를 확인하고 선회. 소셜 단일화는 신규에만 적용한다.",
      "detail": {
        "request": "\"이메일 가입을 보조 경로로 남긴다 어떻게 할까요?\"",
        "intent": {
          "surface": "이메일 가입을 보조 경로로 남긴다",
          "purpose": "기존 사용자 이전 문제를 확인하고 선회",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "기존 사용자 이전 문제를 확인하고 선회. 소셜 단일화는 신규에만 적용한다.",
        "open_questions": [],
        "why_not": ""
      },
      "links": [
        "PRD-3.2"
      ],
      "orphan": false,
      "topic": "로그인",
      "open_question": null,
      "path": "members/hayun/logs/LOG-0009.md",
      "supersedes": [
        "LOG-0012"
      ],
      "cat": "c4"
    },
    {
      "id": "LOG-0007",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-20T16:31:29+09:00",
      "status": "폐기",
      "confidence": "confirmed",
      "title": "진행률을 커밋 수로 측정",
      "why": "AI 코딩에서는 커밋 수가 작업량과 무관해 폐기.",
      "detail": {
        "request": "\"진행률을 커밋 수로 측정 어떻게 할까요?\"",
        "intent": {
          "surface": "진행률을 커밋 수로 측정",
          "purpose": "AI 코딩에서는 커밋 수가 작업량과 무관해 폐기",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "AI 코딩에서는 커밋 수가 작업량과 무관해 폐기.",
        "open_questions": [],
        "why_not": ""
      },
      "links": [],
      "orphan": true,
      "topic": "진행률",
      "open_question": null,
      "path": "members/dohyun/logs/LOG-0007.md",
      "supersedes": [],
      "cat": "c5"
    },
    {
      "id": "LOG-0004",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-17T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "unconfirmed",
      "title": "비밀번호 규칙 완화",
      "why": "",
      "detail": {
        "request": "\"비밀번호 규칙 완화 어떻게 할까요?\"",
        "intent": {
          "surface": "비밀번호 규칙 완화",
          "purpose": "",
          "evidence": ""
        },
        "asked": [],
        "decision": "",
        "open_questions": [],
        "why_not": ""
      },
      "links": [
        "PRD-3.1"
      ],
      "orphan": false,
      "topic": "회원가입",
      "open_question": null,
      "path": "members/hayun/logs/LOG-0004.md",
      "supersedes": [],
      "cat": "c1"
    },
    {
      "id": "LOG-0003",
      "author": "dohyun",
      "display": "박도현",
      "at": "2026-08-14T16:31:29+09:00",
      "status": "결정됨",
      "confidence": "confirmed",
      "title": "진행률을 팀원별로 나눠 보여준다",
      "why": "합계만 보면 누가 막혔는지 안 보인다. 사람별로 쪼갠다.",
      "detail": {
        "request": "\"진행률을 팀원별로 나눠 보여준다 어떻게 할까요?\"",
        "intent": {
          "surface": "진행률을 팀원별로 나눠 보여준다",
          "purpose": "합계만 보면 누가 막혔는지 안 보인다",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "합계만 보면 누가 막혔는지 안 보인다. 사람별로 쪼갠다.",
        "open_questions": [],
        "why_not": ""
      },
      "links": [
        "PRD-4.1"
      ],
      "orphan": false,
      "topic": "진행률",
      "open_question": null,
      "path": "members/dohyun/logs/LOG-0003.md",
      "supersedes": [],
      "cat": "c5"
    },
    {
      "id": "LOG-0002",
      "author": "hayun",
      "display": "하윤서",
      "at": "2026-08-11T16:31:29+09:00",
      "status": "논의중",
      "confidence": "confirmed",
      "title": "작성 중 내용을 자동 저장한다",
      "why": "길게 쓰다 날리면 다시 안 쓴다. 30초마다 자동 저장한다.",
      "detail": {
        "request": "\"작성 중 내용을 자동 저장한다 어떻게 할까요?\"",
        "intent": {
          "surface": "작성 중 내용을 자동 저장한다",
          "purpose": "길게 쓰다 날리면 다시 안 쓴다",
          "evidence": "직전 대화에서 언급"
        },
        "asked": [],
        "decision": "길게 쓰다 날리면 다시 안 쓴다. 30초마다 자동 저장한다.",
        "open_questions": [
          "저장 주기를 사용자가 바꿀 수 있어야 하나?"
        ],
        "why_not": ""
      },
      "links": [],
      "orphan": true,
      "topic": "임시저장",
      "open_question": "저장 주기를 사용자가 바꿀 수 있어야 하나?",
      "path": "members/hayun/logs/LOG-0002.md",
      "supersedes": [],
      "cat": "c2"
    }
  ],
  "system": {
    "checks": [
      {
        "name": "개인 폴더 제외",
        "ok": true,
        "detail": ".local/ 에 넣은 것은 공유되지 않습니다"
      },
      {
        "name": "공유 전 비밀정보 검사",
        "ok": true,
        "detail": "키·토큰이 섞이면 공유가 중단됩니다"
      },
      {
        "name": "공유 전 민감표현 검사",
        "ok": false,
        "detail": "사람 평가·대외비 표현을 걸러냅니다"
      }
    ],
    "skills": [
      {
        "name": "idea2planning",
        "grade": "필수"
      },
      {
        "name": "eli5",
        "grade": "선택"
      },
      {
        "name": "humanize-korean",
        "grade": "선택"
      }
    ],
    "remote": "github",
    "unknown": [
      "서버측 비밀정보 차단",
      "이번 주 차단 건수",
      "스킬 실제 설치 여부"
    ]
  },
  "prd": {
    "version": "v1.0",
    "confirmed_at": "2026-09-01T16:31:29+09:00",
    "items": [
      {
        "no": "3.1",
        "title": "회원 가입",
        "body": "이메일과 소셜 계정으로 가입한다. 비밀번호 규칙은 8자 이상만 강제한다.",
        "proposers": [
          "hayun"
        ],
        "joint": [],
        "links": [
          "LOG-0004"
        ],
        "untracked": false
      },
      {
        "no": "3.2",
        "title": "소셜 로그인 단일 단계",
        "body": "가입 흐름을 소셜 로그인 단일 단계로 통합한다. 이메일 가입은 보조 경로로 제공하되 기본 노출에서 제외한다.",
        "proposers": [
          "hayun"
        ],
        "joint": [],
        "links": [
          "LOG-0012",
          "LOG-0009"
        ],
        "untracked": false
      },
      {
        "no": "3.3",
        "title": "세션 관리",
        "body": "세션은 30일 유지한다. 결제·개인정보 변경은 재인증을 요구한다.",
        "proposers": [
          "dohyun"
        ],
        "joint": [
          "hayun"
        ],
        "links": [
          "LOG-0015"
        ],
        "untracked": false
      },
      {
        "no": "3.5",
        "title": "자동 임시저장",
        "body": "작성 중인 내용을 30초마다 자동 저장한다.",
        "proposers": [],
        "joint": [],
        "links": [],
        "untracked": true
      },
      {
        "no": "4.1",
        "title": "팀원별 진행률 표시",
        "body": "완료한 태스크 수를 기준으로 진행률을 계산한다. 커밋 수는 AI 코딩에서 의미가 없어 제외한다.",
        "proposers": [
          "dohyun"
        ],
        "joint": [
          "seojin"
        ],
        "links": [
          "LOG-0003",
          "LOG-0011"
        ],
        "untracked": false
      },
      {
        "no": "4.2",
        "title": "알림 묶어 보내기",
        "body": "알림은 하루치를 모아 아침에 한 번 보낸다.",
        "proposers": [
          "hayun"
        ],
        "joint": [],
        "links": [
          "LOG-0018"
        ],
        "untracked": false
      },
      {
        "no": "5.2",
        "title": "출시 일정",
        "body": "온보딩 재설계 반영으로 출시를 2주 미룬다. 범위는 유지한다.",
        "proposers": [
          "seojin"
        ],
        "joint": [],
        "links": [
          "LOG-0021"
        ],
        "untracked": false
      }
    ],
    "tracked": 6,
    "total": 7
  },
  "questions": [
    {
      "text": "저장 주기를 사용자가 바꿀 수 있어야 하나?",
      "author": "hayun",
      "display": "하윤서",
      "days": 22,
      "from": "LOG-0002",
      "impact": null
    },
    {
      "text": "태스크는 누가 정의하나?",
      "author": "dohyun",
      "display": "박도현",
      "days": 8,
      "from": "LOG-0011",
      "impact": "PRD 4.1 의 계산 기준이 정해지지 않았습니다"
    },
    {
      "text": "기존 이메일 가입자는 어떻게 옮기나?",
      "author": "hayun",
      "display": "하윤서",
      "days": 6,
      "from": "LOG-0012",
      "impact": "이 질문이 막혀 PRD 3.2 가 확정되지 않고 있습니다"
    },
    {
      "text": "재인증이 필요한 작업 목록을 누가 정하나?",
      "author": "dohyun",
      "display": "박도현",
      "days": 4,
      "from": "LOG-0015",
      "impact": null
    }
  ],
  "alerts": [
    {
      "level": "warn",
      "title": "이서진 — 자동 기록이 꺼져 있습니다",
      "detail": "폴더 신뢰를 수락하지 않아서, 지금 하는 작업은 하나도 남지 않습니다.",
      "action": "Claude Code 를 다시 시작하고 \"예\"를 누르세요"
    },
    {
      "level": "warn",
      "title": "이서진 — 초대 수락 대기",
      "detail": "수락 전까지 이 사람의 작업은 팀에 보이지 않습니다.",
      "action": "초대를 다시 보내세요"
    },
    {
      "level": "info",
      "title": "이 저장소는 공개입니다",
      "detail": "기록이 팀 밖에서도 보입니다.",
      "action": null
    }
  ],
  "orphans": [
    {
      "topic": "임시저장",
      "count": 1
    }
  ],
  "stats": {
    "logs_total": 10,
    "unconfirmed": 1,
    "days": 22,
    "first": "2026-08-11T16:31:29+09:00",
    "by_member": {
      "seojin": 1,
      "hayun": 5,
      "dohyun": 4
    }
  }
};

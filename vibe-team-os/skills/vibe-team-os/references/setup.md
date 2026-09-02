# 세팅 — 새 프로젝트 시작

## 목차

- 진행 체크리스트
- 0. 시작 전 확인
- 1. 팀원 명단 받기
- 2. 민감도 판정 → 공개 범위 결정
- 3. GitHub 준비
- 4. 폴더 구조 생성
- 5. **파일 내용** — 무엇을 어떻게 채우는가
- 6. 실시간 계층(DB) 연결
- 7. 의존 스킬 확인
- 8. 자동 기록(hook) 등록
- 9. 대시보드 배포
- 10. 완료 검증 → 기획 단계로
- 팀원에게 보낼 안내문
- 자주 막히는 곳

---

## 진행 체크리스트

이 목록을 응답에 복사하고, 단계를 마칠 때마다 체크한다. 목록이 눈앞에 남아 있어야 건너뛴 게 보인다.

```
세팅 진행:
- [ ] 0. gh 설치·인증 확인
- [ ] 1. 팀원 명단 (영문 폴더명 검증)
- [ ] 2. 민감도 판정 → 공개 범위 결정
- [ ] 3. GitHub 레포·초대·Push Protection·team-status 브랜치
- [ ] 4. 폴더 구조 생성
- [ ] 5. 파일 내용 채우기 (config·members·skills·status·README)
- [ ] 6. DB 연결 + 권한 침투 검사
- [ ] 7. 의존 스킬 확인
- [ ] 8. hook 등록 + 작동 확인
- [ ] 9. 대시보드 화면 복사 + 데이터 빌드 + 배포
- [ ] 10. verify_setup.py 통과 → phase 를 planning 으로
```

---

## 0. 시작 전 확인

```bash
gh auth status
```

실패하면 여기서 멈추고 안내한다. **토큰을 직접 받지 않는다** — 사용자가 `gh auth login` 으로 처리한다.

---

## 1. 팀원 명단 받기

각 팀원에 대해 세 가지를 받는다.

| 항목 | 예시 | 규칙 |
|---|---|---|
| 표시 이름 | 홍길동 | 한글 가능 |
| 폴더 이름 | `hong` | **영문 소문자로 시작, 소문자·숫자·하이픈만** |
| GitHub 아이디 | `hong-gd` | 초대에 필요 |

**폴더 이름에 한글을 쓰면 안 된다.** macOS 와 Windows 가 한글 파일명을 다르게 저장해서, 팀원 OS 가 섞이면 같은 폴더가 두 개로 보이는 사고가 난다. 사용자가 한글을 넣으면 영문 변환을 제안한다.

1명이면 `mode` 를 `solo` 로 기록한다. 병합과 기여 귀속은 꺼지고 나머지는 그대로 동작한다.
11명 이상이면 경고하되 막지는 않는다.

---

## 2. 민감도 판정 → 공개 범위 결정

**"공개돼도 괜찮나요?" 라고 물으면 대부분 괜찮다고 답한다.** 추상적이라 실감이 안 나기 때문이다. 구체적인 항목으로 물어야 실제로 걸린다.

```
이 프로젝트에서 이런 이야기가 나올 수 있습니까?

  □ 경쟁사·시장 분석
  □ 가격·매출·투자
  □ 계약·제휴 조건
  □ 사람에 대한 평가
  □ 아직 공개하지 않은 제품 계획
```

| 응답 | 결정 |
|---|---|
| 하나도 없음 | `visibility: public` · GitHub Pages |
| **하나라도 있음** | `visibility: private` · 인증 배포 |

체크가 있으면 공개 방식을 **경고가 아니라 차단**한다. 기록에는 대화 내용이 그대로 들어가고, 한 번 새어나가면 되돌릴 수 없다.

체크한 항목을 `config.json` 에 남긴다. 나중에 합류한 팀원이 "왜 비공개죠?" 라고 물을 때 근거가 된다.

---

## 3. GitHub 준비

> **혼자 쓰거나 GitHub 를 안 쓸 거면 이 장을 통째로 건너뛴다.**
> `config.json` 에 `"remote": "none"` 을 적고 9장(대시보드 배포)도 건너뛴다.
> 기록·대시보드는 그대로 동작하고, 화면은 로컬 파일로 연다.

```bash
gh repo create <이름> --private          # 또는 --public
gh api repos/{owner}/{repo}/collaborators/{user} -X PUT   # 팀원마다
gh api repos/{owner}/{repo}/automated-security-fixes -X PUT
```

Push Protection(서버측 비밀정보 차단)을 켠다. 로컬 검사가 시간 초과로 넘어가도 서버가 막아준다.

**`team-status` 브랜치를 만든다.**

```bash
git branch team-status
git push -u origin team-status
```

작업 상태 같은 기계 데이터는 여기 둔다. 턴마다 갱신되는 것을 `main` 에 쌓으면 커밋이 폭증해 사람이 읽을 히스토리가 묻힌다.

**초대는 팀원이 수락해야 효력이 있다.** `invite_status` 를 `pending` 으로 기록하고 대시보드에 "초대 수락 대기"를 표시한다. 수락 전에는 공유가 안 되는데, 이유를 모르면 팀원이 헤맨다.

---

## 4. 폴더 구조 생성

```
<레포>/
├── README.md
├── PRD.md                  기획 완료 후 생성 (지금은 만들지 않는다)
├── .gitignore
├── .team/
│   ├── config.json
│   ├── members.json
│   ├── skills.yaml
│   └── status/<이름>.json  팀원별 분리 — 공유 파일은 겹침의 원인이 된다
├── members/<이름>/
│   ├── README.md
│   ├── planning/
│   ├── logs/               의도 로그 (영구)
│   ├── notes/              작업 노트 (30일 후 압축)
│   └── .local/             공유하지 않음
├── decisions/              팀 결정 (목차 합의 등)
├── docs/                   대시보드
└── report/                 발표물
```

`.gitignore` 는 이 내용으로 만든다.

```
members/*/.local/
**/.local/
*.env
*.key
*.pem
```

**규칙을 하나로 유지한다** — "`.local/` 에 넣은 것은 절대 공유되지 않는다". 규칙이 하나면 팀원이 외운다.

### 이미 쓰던 폴더에 세팅할 때

빈 폴더가 아닐 수 있다. **`docs/` 와 `README.md` 두 개가 부딪힌다.**

| 부딪히는 것 | 기존 뜻 | 이 스킬의 뜻 |
|---|---|---|
| `docs/` | 설계·기획 문서를 넣던 곳 | 대시보드 |
| `README.md` | 프로젝트 설명 | 팀원이 처음 보는 안내 |

**덮어쓰지 않는다.** 남의 문서를 지우고 대시보드를 깔면 세팅이 아니라 사고다.

- `docs/` 에 이미 내용이 있으면 대시보드는 `dashboard/` 로 보낸다.
  Pages 를 쓸 거면 배포 경로도 `/docs` 대신 `/dashboard` 로 맞춘다
- `README.md` 가 이미 있으면 덮지 말고 **맨 위에 「시작하기」 절만 끼워 넣는다**
- 어느 쪽이든 **무엇을 왜 옮겼는지 사용자에게 말하고 넘어간다.** 조용히 자리를 바꾸면
  나중에 "대시보드가 어디 갔지"로 돌아온다

---

## 5. 파일 내용

폴더만 만들면 검사에서 떨어진다. **아래 형식 그대로 채운다.**

### `.team/config.json`

```json
{
  "project": "프로젝트 이름",
  "phase": "setup",
  "visibility": "public",
  "sensitivity": { "checked": [], "answered_at": "2026-08-31" },
  "realtime": "supabase",
  "remote": "github",
  "mode": "team"
}
```

| 필드 | 가능한 값 | 뜻 |
|---|---|---|
| `phase` | `setup` `planning` `merging` `planned` `presenting` `archived` | 지금 어느 단계인가 |
| `visibility` | `public` `private` | 2장 판정 결과 |
| `sensitivity.checked` | 체크한 항목 배열 (예: `["경쟁사·시장 분석"]`) | 판정 근거 |
| `realtime` | `supabase` `none` `degraded` | 실시간 계층 상태 |
| `remote` | `github` `none` | GitHub 를 쓰는가. `none` 이면 3·9장을 건너뛴다 |
| `mode` | `team` `solo` | 팀원 1명이면 `solo` |

`phase` 는 세팅 중에는 `setup` 이다. **10장 검증을 통과한 뒤에 `planning` 으로 바꾼다.**

**`remote` 는 "안 했다"와 "안 쓴다"를 가른다.** 혼자 쓰거나 사내망만 쓰는 세팅은
GitHub 가 없는 것이 정상인데, 검사가 이걸 구분 못 하면 정상 세팅이 영영 완료되지 않는다.
검사는 추론하지 않고 이 필드만 본다 — 필드가 없으면 `github` 로 본다.

### `.team/members.json`

```json
{
  "hong": { "display": "홍길동", "github": "hong-gd", "invite_status": "pending" },
  "kim":  { "display": "김철수", "github": "kim-cs",  "invite_status": "pending" }
}
```

키가 폴더 이름이다. `invite_status` 는 `pending` `accepted` `failed` 중 하나.
역할이 정해졌으면 `"roles": { "기획": { "role": "기획 리드", "scope": "온보딩" } }` 를 덧붙인다.

### `.team/skills.yaml`

```yaml
required:
  - name: idea2planning
    repo: https://github.com/pentaxzs/skill-idea2planning
optional:
  - name: eli5
  - name: humanize-korean
deferred:
  - name: ponytail
  - name: karpathy-guidelines
  - name: supanova-design-engine
```

`manual_only: true` 를 붙이면 AI 가 자동으로 부르지 않고 안내만 한다. **붙이기 전에 같은 계열에 자동 호출되는 스킬이 있는지 확인한다** — `humanize` 는 막혀 있지만 `humanize-korean` 은 열려 있다.

### `.team/status/<이름>.json`

팀원 수만큼 만든다. 초기값은 전부 비어 있다.

```json
{ "state": "idle", "task": null, "files": [], "since": null }
```

`state` 는 `working` `idle` `away` `left` 중 하나.

**자동 기록이 도는지도 여기 쌓인다.** `.local/` 은 공유되지 않아서 남의 기계 상태를
대시보드가 직접 볼 방법이 없다. 각자 자기 기계에서 적어 둬야 모인다.

```bash
scripts/verify_hooks.sh --record <이름>   # 혼자 모드면 이름 생략 가능
```

```json
"hooks": { "state": "untrusted", "checked_at": "2026-09-02T09:55:57+09:00" }
```

`state` 는 `active` `untrusted` `failed`.

**깃발이 아니라 확인한 시각을 적는 이유** — 깃발을 끄는 것도 hook 이다.
잘 돌다가 죽으면 마지막에 적힌 `active` 가 영원히 남는다. 죽은 쪽에 자기가 죽었다고
적으라는 셈이다. 시각은 갱신이 멈추면 저절로 드러난다.

빌더는 3일이 지난 기록을 `unknown` 으로 내린다. **`unknown` 을 정상으로 치지 않는다** —
다만 경고도 아니다. 그냥 안 켠 사람한테 붉은 경고를 띄우면 경고가 늘 떠 있게 되고,
늘 떠 있는 경고는 아무도 안 본다. 회색으로 "확인한 지 N일"만 띄운다.

### `members/<이름>/README.md`

체크포인트가 쌓이면 자동으로 갱신된다. **세팅 시점에는 자리만 만든다.**

```markdown
# 홍길동

아직 작업 기록이 없습니다. 이 폴더에서 작업을 시작하면 여기가 채워집니다.
```

### 루트 `README.md`

팀원이 저장소를 열었을 때 처음 보는 화면이다. **Git 용어를 쓰지 않는다.**

```markdown
# 프로젝트 이름

## 시작하기
자기 이름 폴더(`members/<이름>/`)에서 작업하세요.
무엇을 왜 정했는지는 자동으로 기록되니 따로 정리하지 않으셔도 됩니다.

## 지금 상황 보기
<대시보드 주소>

## 폴더 안내
- `members/` 각자 작업 공간
- `decisions/` 팀이 함께 정한 것
- `docs/` 대시보드
```

---

## 6. 실시간 계층(DB) 연결

기본은 Supabase 다. 팀장 계정으로 프로젝트를 만들고 테이블·권한을 설정한다.

SQL 전문은 `docs/06-설계-실시간계층.md` 3장에 있다. **검증을 통과한 것이므로 그대로 쓴다.** 직접 새로 짜면 아래 세 함정에 다시 걸린다.

- 정책이 자기 테이블을 참조하면 무한 재귀에 빠진다
- 권한 판정 함수를 `public` 에 두면 REST 로 직접 호출된다
- `search_path` 를 안 정하면 스키마 하이재킹이 가능하다

### 침투 검사 — 통과 못 하면 세팅 실패

```bash
scripts/verify_rls.sh <프로젝트URL> <공개키>
# 예: scripts/verify_rls.sh https://abc.supabase.co sb_publishable_xxx
```

정적 페이지에 DB 키가 박히므로 **DB 쪽에서 막는 수밖에 없다.** 설정만 하고 넘어가면 조용히 뚫려 있을 수 있다.

7종을 시도해서 전부 막혀야 한다 — 익명 조회·명단 조회·타팀 조회·필터 우회·익명 쓰기·판정 함수 직접 호출·키 없이 접근.

그리고 **Supabase 보안 검사(`get_advisors`)도 함께 돌린다.** 경고가 1건이라도 있으면 세팅 실패다. HTTP 요청으로는 안 드러나는 것을 잡아준다.

DB 연결이 안 되면 `realtime` 을 `none` 으로 바꾸고 진행한다. 실시간 기능만 빠지고 나머지는 그대로 동작한다.

---

## 7. 의존 스킬 확인

| 등급 | 스킬 | 없으면 |
|---|---|---|
| 필수 | `idea2planning` | 세팅 실패 |
| 선택 | `eli5` · `humanize-korean` | 조용히 건너뜀 |
| 나중 | `ponytail` · `karpathy-guidelines` · `supanova-design-engine` | 개발 단계에서 설치 |

설치 경로가 환경마다 다르므로 여러 곳을 찾아본다. 설치 직후에는 인식이 안 될 수 있다 — 그때는 **Claude Code 재시작**을 안내한다. "설치했으니 됐다"고 넘어가면 팀원 환경에서 조용히 안 되는 상태가 된다.

---

## 8. 자동 기록(hook) 등록

hook 은 `hooks/hooks.json` 에 있고, 이 스킬이 플러그인으로 로드되면서 자동으로 등록된다.
등록됐다고 도는 것은 아니므로 확인한다.

**프론트매터에 두면 안 된다.** SKILL.md 프론트매터의 hook 은 **스킬을 부른 뒤에야** 등록된다 —
깔아만 두면 안 돈다. `SessionStart` 는 아예 못 뜬다. 세션이 시작된 다음에야 스킬을 부를 수 있어서다.
`.claude-plugin/plugin.json` 이 있어야 세션 시작 때 등록된다.
`hooks/` 를 고쳤으면 `/reload-plugins` 또는 재시작이 필요하다.

```bash
scripts/verify_hooks.sh            # 사람이 읽는 상태
scripts/verify_hooks.sh --record   # 판정을 status 파일에 적는다 (대시보드가 읽는다)
```

**세팅 직후에는 "자동 기록이 꺼져 있습니다"가 정상이다.** 아직 턴이 한 번도 안 쌓였기 때문이다. 이걸 세팅 실패로 처리하지 않는다.

진짜 확인은 **팀원이 처음 작업을 시작한 뒤**다. 몇 턴 지나고도 같은 메시지가 나오면 폴더 신뢰를 수락하지 않은 것이다. 이 경우 기록이 하나도 안 남는데 아무 오류도 안 난다 — 대시보드에 **"자동 기록이 꺼져 있습니다"** 를 띄우고 켜는 방법을 안내한다.

---

## 9. 대시보드 배포

```bash
gh api repos/{owner}/{repo}/pages -X POST \
  -f "source[branch]=main" -f "source[path]=/docs"
```

`visibility` 가 `private` 이면 인증 배포로 간다. 첫 배포까지 1~2분 걸린다.

실패하면 3회까지 재시도하고, 그래도 안 되면 로컬에서 여는 방식으로 물러선다. **세팅 전체를 실패로 만들지 않는다** — 대시보드가 없어도 기록은 쌓인다.

---

## 10. 완료 검증 → 기획 단계로

```bash
scripts/verify_setup.py
```

실패 항목이 있으면 무엇이 왜 안 됐는지와 다음에 할 일을 함께 보여준다. 고친 뒤 다시 실행한다.

**통과하면 `config.json` 의 `phase` 를 `planning` 으로 바꾼다.** 이걸 해야 다음 세션에서 기획 단계 지침을 읽는다.

```json
{ "phase": "planning" }
```

그리고 팀원에게 보낼 안내문을 만들어 팀장에게 준다.

---

## 팀원에게 보낼 안내문

Git 용어를 넣지 않는다.

```
[프로젝트명] 함께 만들어요

1. GitHub에서 온 초대 메일을 수락해 주세요
2. 이 링크를 열어주세요: <대시보드 주소>
3. 처음 열면 "폴더를 신뢰하시겠습니까?"가 뜹니다 — 예를 눌러주세요

이제 각자 자기 폴더에서 작업하시면 됩니다.
무엇을 왜 정했는지는 자동으로 기록되니 따로 정리하지 않으셔도 됩니다.
```

---

## 자주 막히는 곳

| 상황 | 대응 |
|---|---|
| `gh` 미설치·미인증 | 안내 후 중단. 토큰을 직접 받지 않는다 |
| **GitHub 를 안 쓴다** | `remote: none` 을 적는다. 3·9장을 건너뛰고도 검사를 통과한다 |
| 레포 이름 중복 | 대안 3개 제시 |
| 초대 미수락 | `pending` 표시. 공유 시도할 때 안내 |
| **세팅 직후 hook 미작동** | **정상이다.** 턴이 안 쌓였을 뿐. 실패로 처리하지 않는다 |
| 작업 시작 후에도 hook 미작동 | 폴더 신뢰 미수락. 대시보드에 경고 |
| 스킬 설치 후 미인식 | 재시작 안내 |
| 권한 침투 검사 실패 | **세팅 실패.** 재설정 후 재검사 |
| 보안 검사 경고 1건 이상 | **세팅 실패.** 함수를 `private` 스키마로 옮겼는지 확인 |
| DB 연결 실패 | `realtime` 을 `none` 으로 바꾸고 진행 |
| 배포 실패 | 3회 재시도 → 로컬 방식으로 물러섬 |
| 한글 폴더명 입력 | 영문 변환 제안 |
| 이름 중복 | 접미사 제안 (`kim`, `kim-2`) |
| `.local` 이 이미 공유됨 | `git rm --cached` 로 빼낸다. `.gitignore` 만 고치면 이미 올라간 건 그대로다 |

더 많은 예외는 `troubleshooting.md` 에 있다.

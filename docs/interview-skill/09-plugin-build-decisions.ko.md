---
tags: [plan, ouroboros, interview, plugin, multi-agent, decisions, korean]
created: 2026-04-23
updated: 2026-04-23
status: in-progress
language: ko
related:
  - ./09-plugin-build-decisions.md
  - ./README.md
  - ./08-customization-guide.md
---

# 플러그인 빌드 결정 — 크로스 에이전트용 interview skill 포크

> **이름 업데이트 (post-doc, 2회):**
>
> 1. 레포명 `ask-socratic` → `3b-harness` (repo = 여러 플러그인을 담는
>    harness).
> 2. 플러그인 스냅샷의 이름이 최종적으로 **`interview-claude`** (NOT
>    `ask-socratic`, NOT `interview`)로 정해짐 — 형제 격인 Codex 생성
>    스냅샷 (`plugins/interview-codex/`)과 시각적으로 대칭. 버전도 `v0.0.1`로
>    강등 — 이 플러그인은 `interview-codex`와의 cross-analysis를 위해 보관된
>    **not-for-use 스냅샷**이지, 배포 가능한 빌드가 아님.
>
> 이 문서를 읽을 때: `ask-socratic`은 `interview-claude`로, `ask-socratic-ai`
> (Phase 2 PyPI 패키지)는 `interview-ai`로 읽으면 됨. 슬래시 커맨드는
> `/interview-claude:interview`. 레포 루트의 CHANGELOG에서 전체 이름 변경
> 기록 참조. Phase 2 / Phase 3 빌드 플랜은 여전히 유효하지만 —
> `interview-claude` vs `interview-codex` cross-variant 비교에서 승자가
> 결정된 *후에만* 적용됨.

## 개정 — 2026-04-23

원래 MVP는 "agent-only / Path B 전용 / MCP 제거 / PM 제거 / brownfield
제거 / 테스트 생략"이었음. MCP 핸들러 구현을 검토한 후 뒤집음:
**Full port + 새 테스트**. 미결 질문 세 개 모두 해결:

- **R1 — Ontologist:** 예, 6번째 `InterviewPerspective`로 추가.
- **R2 — PM 변종:** 예, MVP에 포함.
- **R3 — Brownfield 탐색:** 예, MVP에 포함.
- **테스트:** 새로 작성 (상위 fixture-coupled 테스트 이식 X).

새 결정 추가: **D13 — Plugin-mode subagent dispatch** (유지 / 제거 / 추상화).
권장: **제거 (D13b)**.

구현을 **3단계**로 분할, 총 ~9–13시간. §7 참조.

## 이 문서의 목적

목표: Ouroboros의 `interview` skill을 가져와 Claude Code, Codex, Gemini
CLI에서 모두 실행되는 **당신의 플러그인**으로 출시하기. 모든 기능을 가져갈
필요는 없음 — 집중적이고, 이식성 높고, 유지보수 가능한 포크를 만드는 것이
핵심.

이 문서는 모든 유의미한 결정 사항을 옵션 + 트레이드오프와 함께 제시하므로,
빌드 시작 전에 선택할 수 있음. 승인 후 원본 영문 버전은
`ouroboros/docs/interview-skill/09-plugin-build-decisions.md`에 위치하고
이 한글 버전은 `.ko.md` 접미사로 같은 폴더에 함께 유지됨.

참고: 아래 모든 주장은 `ouroboros/docs/interview-skill/`의 분석 문서
(`01-overview.md` … `08-customization-guide.md`)에 근거함.

---

## 1. 타겟 에이전트 매트릭스

역량 비교표 — 각 플랫폼이 지원하는 기능과 포크에 미치는 영향.

| 역량 | Claude Code | Codex | Gemini CLI |
|---|---|---|---|
| Skill 형식 | `skills/{name}/SKILL.md` + `Skill` 도구 | 자동 로드; 지시사항 직접 따름 | `activate_skill` 도구로 온디맨드 로드 |
| 서브에이전트 / 병렬 디스패치 | `Task` 도구, 네임드 에이전트 | `spawn_agent` (`~/.codex/config.toml`에 `multi_agent=true` 필요), **네임드 레지스트리 없음** — 에이전트 md를 읽어 제네릭 워커로 디스패치 | **없음** — 단일 세션 전용 |
| 구조화된 사용자 입력 | `AskUserQuestion` (네이티브) | 직접적 동등 기능 없음 — 평문 프롬프트 폴백 | `ask_user` (네이티브) |
| 태스크 트래킹 | `TodoWrite` | `update_plan` | `write_todos` |
| MCP 지원 | 1급 지원 (`.mcp.json`로 서버 구성) | config.toml로 지원 | 지원 (표준 프로토콜) |
| Plan 모드 | `EnterPlanMode` / `ExitPlanMode` | 동등 기능 없음 | `enter_plan_mode` / `exit_plan_mode` |
| 메모리 / 영속성 | 프로젝트 CLAUDE.md + 파일 쓰기 | 파일 쓰기 + 선택적 MCP | `save_memory` → GEMINI.md + 파일 쓰기 |
| 웹 | `WebFetch` / `WebSearch` | 네이티브 동등 기능 | `web_fetch` / `google_web_search` |

**포크에 미치는 핵심적 영향:**

- **Gemini는 서브에이전트 없음.** Interview skill의 핫 패스는 `Task`를 쓰지
  않으므로 문제 없음 — 하지만 나중에 병렬 탐색 (예: "사용자 코드베이스 조사"
  단계)을 원하면 Gemini에선 직렬로 동작함.
- **Codex는 `AskUserQuestion` 동등 기능 없음.** Skill의 라우팅은 PATH 1b /
  2 / 3 / 4에서 `AskUserQuestion`을 많이 사용함. Codex 포크는 평문 프롬프트
  ("다음에 답해주세요: ...")로 폴백해야 함.
- **네임드 에이전트 디스패치는 Claude 전용.** 5개의 perspective 에이전트
  (researcher, simplifier, architect, breadth-keeper, seed-closer)는
  현재 Python이 서버 측에서 로드함 (interview.py:62–87). 에이전트 전용
  포크 (당신이 선택한 MVP)에서는 SKILL.md가 인라인 참조하는 프롬프트 데이터
  파일이 됨. Claude는 원하면 `Task`로 디스패치 가능; Codex는 파일 읽어서
  채운 내용으로 `spawn_agent` 호출; Gemini는 디스패치 불가능.

---

## 2. 인벤토리 — 원본 skill의 구성 요소 (Full port용 개정)

R1–R3 YES 이후: 거의 모든 것을 포트. Rename-and-adapt가 주된 작업.
테스트만 진짜 새로 작성.

| 구성 요소 | 소스 | Full-port 조치 |
|---|---|---|
| SKILL.md 듀얼 패스 플레이북 (338줄) | `skills/interview/SKILL.md` | **전체 파일 포트.** "Ouroboros" → 플러그인 브랜드 rename; MCP 도구 참조를 `{plugin}_interview`로; Path A + Path B 둘 다 유지 |
| 커맨드 엔트리 스텁 | `commands/interview.md` | **포트**, prefix 재명명 |
| Socratic interviewer (외부 역할) | `src/ouroboros/agents/socratic-interviewer.md` | **유지; 적응** — MCP 포함되므로 prefix 계약 (`[from-code]` 등) 그대로; Ouroboros 참조만 재명명 |
| 종결 감사 (canonical) | `src/ouroboros/agents/seed-closer.md` | **원본 그대로 복사** |
| 5개 perspective 에이전트 (researcher, simplifier, architect, breadth-keeper, seed-closer) | `src/ouroboros/agents/*.md` | **원본 그대로 복사** (포팅된 `agents/loader.py` 통해 로드) |
| Ontologist | `src/ouroboros/agents/ontologist.md` | **6번째 `InterviewPerspective`로 포트** — enum 값 추가 + `_load_interview_perspective_strategies()`에 매핑 + 엔진에 1줄 트리거 |
| `InterviewEngine` + `InterviewState` + `InterviewRound` + `InterviewStatus` + `InterviewPerspective` | `src/ouroboros/bigbang/interview.py` (31.6K) | **전체 파일 포트.** 패키지 참조 재명명; D13b에 따라 plugin-mode subagent dispatch 제거 |
| `AmbiguityScorer` + 임계값 + 플로어 + 마일스톤 + `qualifies_for_seed_completion` | `src/ouroboros/bigbang/ambiguity.py` (28.4K) | **전체 파일 포트** — 수치 게이트 전체 복구 |
| 이벤트 | `src/ouroboros/events/interview.py` (74줄) + `events/base.py` | **포트.** 이벤트 저장소 충돌 방지 위해 타입 이름에 플러그인 네임스페이스 (`{plugin}.interview.*`) prefix 검토 |
| MCP 핸들러 (InterviewHandler만) | `src/ouroboros/mcp/tools/authoring_handlers.py:694–1150` | **핸들러 클래스 + 헬퍼 포트.** D13b에 따라 plugin-mode 분기 제거. 도구 이름 `ouroboros_interview` → `{plugin}_interview` 재명명 |
| PM 변종 (6 파일) | `pm_interview.py` + `pm_handler.py` + `pm_seed.py` + `pm_document.py` + `pm_completion.py` + `question_classifier.py` | **전체 6개 포트** (Phase 3). ~80K Python |
| 다운스트림 `Seed` 데이터클래스 | `src/ouroboros/core/seed.py:155–229` | **포트.** Python immutable 모델로 유지 (~75줄); 핸들러의 완료 경로에서 참조 |
| Brownfield 탐색 | `src/ouroboros/bigbang/brownfield.py` (14.6K) + `explore.py` (17.4K) | **둘 다 포트** (Phase 3). `InterviewEngine.start_interview(cwd=...)`가 사용 |
| 2차 의존성 | §12 참조 | **포트** (~50K) — types, errors, file_lock, security, providers, config, event_store, MCP types, subagent 어댑터, initial_context, agent loader |
| 테스트 | `tests/unit/bigbang/test_interview.py` + `test_pm_interview.py` | **포트 X. 새로 작성** — 스코어러용 property 테스트, 엔진용 integration 테스트, 핸들러용 contract 테스트 |
| Plugin-mode subagent dispatch | `authoring_handlers.py`의 `handle()` 980–1108줄 | **D13b에 따라 제거** — subprocess 모드만. Claude 특화 코드 ~130줄 제거 |

---

## 3. MVP 최종 형상

Agent-only. Python 없음. 단일 SKILL.md + 6개의 에이전트 md 파일. 도구 이름
규약과 플랫폼별 도구 매핑 참조로 크로스 에이전트 skill 형식 구현.

```
your-plugin/
├── .claude-plugin/
│   └── plugin.json            # Claude Code manifest
├── commands/
│   └── interview.md           # Entry stub (rewrite to your plugin namespace)
├── skills/
│   └── interview/
│       ├── SKILL.md           # Path B에서 재작성; 라우팅 + 리듬 + 종결
│       └── references/        # 선택 — Codex/Gemini용 도구 매핑 참조
│           ├── codex-tools.md
│           └── gemini-tools.md
├── agents/
│   ├── socratic-interviewer.md
│   ├── seed-closer.md
│   ├── researcher.md
│   ├── simplifier.md
│   ├── architect.md
│   └── breadth-keeper.md
└── README.md                  # 세 에이전트용 설치 지침
```

최종 사용자 플로우 (세 에이전트에서 동일):

1. 사용자가 `/your-plugin:interview "주제"` 입력 (또는 각 플랫폼에서 동등한
   슬래시 / skill 호출).
2. 에이전트가 SKILL.md를 로드하고 socratic-interviewer 역할 채택.
3. 라우팅 패스 + 리듬 가드 + 종결 감사와 함께 인터뷰 진행, 전부 대화 내에서.
4. 종료 시 에이전트가 구조화된 "인터뷰 요약" 블록 (markdown) 출력 — goal /
   constraints / success criteria / non-goals / ambiguity 레저 포함.
5. 사용자는 원하는 다운스트림 단계 (seed 생성, 티켓 작성, PR 초안 등)에
   요약을 전달 가능 — 이 플러그인의 다른 skill 또는 외부 도구 사용.

---

## 4. 결정 사항

번호 매김. 각 결정에 **추천 사항** (첫 번째 옵션)이 있지만 당신이 선택.

### D1 — 플러그인 이름 + 커맨드 prefix

다운스트림 모든 것에 영향 (슬래시 커맨드, 나중에 MCP 도구를 추가할 경우
도구 이름, GitHub 레포 이름).

- **D1a. `ask-socratic`** — 서술적, 도구 우선, 에이전트 중립
- **D1b. `interview-ooo`** — Ouroboros 계보 유지
- **D1c. `socratic-spec`** — 출력물이 스펙임을 강조
- **D1d. 직접 선택**

**추천:** D1a. "socratic"은 구분되는 방법론; "ask"는 슬래시 커맨드
(`/ask-socratic:interview`)의 동사로 잘 읽힘.

### D2 — 레포 위치 + git origin

플러그인이 디스크와 GitHub 어디에 위치하는가?

- **D2a. 새로운 독립 공개 GitHub 레포** — 예: `github.com/brandonwie/ask-socratic`. Claude 마켓플레이스 통해 게시 가능. 깔끔한 경계.
- **D2b. `~/dev/personal/3b/plugins/` 하위 폴더** — 비공개 전용, 3B 스택과 긴밀한 통합. 마켓플레이스 게시 없음.
- **D2c. 새로운 `brandonwie-plugins` 모노레포 하위** — 나중에 플러그인을 더 만들 계획이면 지금 모노레포 시작.

**추천:** D2a. 독립 레포는 재사용성 + 가시성 최대화. 나중에 두 번째 플러그인
추가 비용 저렴 (또 다른 레포). 모노레포는 플러그인 3개 이상일 때 효과적.

### D3 — 영속성 모델 (agent-only MVP)

MVP는 agent-only (MCP 없음, Python 엔진 없음). 하지만 여전히 각 에이전트의
네이티브 파일 도구로 인터뷰 상태를 디스크에 기록 가능.

- **D3a. 영속성 없음** — 인터뷰가 전적으로 대화 내에 존재; 세션 종료 시 손실. 가장 단순; 진정한 이식성.
- **D3b. 파일시스템 전용** — SKILL.md가 각 라운드 후 markdown 트랜스크립트를 `~/.{plugin}/sessions/{id}.md`에 기록. 세션이 죽어도 재개 가능.
- **D3c. 파일시스템 + 구조화된 JSON** — 인간용 markdown + 프로그래밍용 라우팅 메타데이터 JSON 사이드카.

**추천:** MVP는 D3a, v0.2에서 D3b. 영속성은 복잡도를 추가하며, 사용자가
한 세션 이상 인터뷰를 실행할 때까지 효과 없음 — 그 효용은 먼저 검증 필요.

### D4 — 종결 메커니즘

Ouroboros는 수치 ambiguity 스코어링 (≤ 0.2 게이트 + 차원별 플로어 + 연속)
사용. MVP는 스코어러 제거 — 따라서 종결은 판단 호출이 됨.

- **D4a. `seed-closer.md` 통한 순수 정성적** — 에이전트가 seed-closer 기준을 읽고, 종결 질문을 하고, 사용자가 결정.
- **D4b. 대화 내 자기 스코어링** — 에이전트가 동일한 4가지 차원으로 각 라운드마다 자기 평가 점수 (0–1) 산출, 단 별도 LLM 호출이 아닌 프롬프트 수준 자기 평가. 사용자가 점수를 봄.
- **D4c. 체크리스트 기반** — 에이전트가 4가지 차원 (goal / constraints / success / context)을 명시적으로 추적하고, 각 라운드마다 어떤 차원이 "명확함" vs "흐릿함"인지 사용자에게 보여줌. 모두 명확해지면 사용자가 종결.

**추천:** D4c. 체크리스트는 구체적이고, 가시적이며, 크로스 에이전트 이식성 있음
(LLM 특화 스코어링 프롬프트 없음). 수치 게이트인 척 하지 않으면서 4차원 모델의
정신을 유지.

### D5 — 다운스트림 핸드오프 형태

인터뷰 종료 시 에이전트는 무엇을 출력하는가?

- **D5a. 평문 markdown 요약** — 헤더: Goal / Constraints / Success Criteria / Non-Goals / Open Questions. 사람이 읽기 좋음. 다운스트림 도구 계약 없음.
- **D5b. YAML frontmatter + markdown 본문** — 기계 파싱 가능 + 사람이 읽기 좋음. 다운스트림 스크립트가 로드 가능.
- **D5c. 전체 `Seed` 모양의 JSON** — 사용자가 실제 Ouroboros를 다운스트림에서 사용할 경우 호환성 위해 Ouroboros Seed 데이터클래스와 일치.

**추천:** D5b. YAML frontmatter (`goal`, `constraints`, `acceptance_criteria`,
`non_goals`, `open_questions`) + 아래 markdown 내러티브. 사람에게 좋음;
파싱 저렴; 추후 Ouroboros Seed로 매핑 쉬움. Python 모델 의존성 없음.

### D6 — Codex용 AskUserQuestion 폴백

Codex는 구조화된 입력 도구가 없음. Interview skill은 PATH 1b / 2 / 3 / 4에서
`AskUserQuestion` 사용.

- **D6a. 평문 프롬프트** — "다음에 답해주세요: <질문>. 옵션: (1) X, (2) Y, (3) 기타." 사용자가 자유 텍스트 응답. 가장 단순. 깔끔한 옵션 리스트 UX 손실.
- **D6b. 펜스드 옵션 블록** — 에이전트가 사용자가 복사할 수 있는 코드 펜스드 옵션 리스트 출력. 조금 풍부하지만 여전히 평문.
- **D6c. Codex 지원 초반 제외** — Claude + Gemini 전용; Codex CLI가 `ask_user` 동등 기능 출시하면 나중에 추가.

**추천:** D6a. 가장 깔끔한 이식성. Claude 사용자는 네이티브 `AskUserQuestion`
경험; Codex 사용자는 평문 폴백; Gemini 사용자는 `ask_user`. SKILL.md는 단일
지시 ("이 옵션으로 사용자에게 물어보세요")를 제공하고, 각 플랫폼이 자체적으로
렌더링.

### D7 — Python 로더 없는 perspective 로테이션

Ouroboros에서 `InterviewEngine`은 milestone + breadth 상태에 따라 5개
perspective를 로테이션. Python 없이는 로테이션이 SKILL.md 지시에 있어야 함.

- **D7a. SKILL.md에 서술된 마일스톤 주도 로테이션** — "라운드 1–2에서 researcher 사용, 3–4에서 simplifier 사용, …". 단순 매핑.
- **D7b. 트리거 주도 로테이션** — "최근 N 라운드가 한 스레드에 머물러 있으면 breadth-keeper 사용; 레저에서 scope/success/constraints 모두 명시적이면 seed-closer 사용; …". 원본에 더 가까움.
- **D7c. 로테이션 없음 — 에이전트가 라운드별 최적 perspective 선택** — LLM이 라운드 컨텍스트에 따라 5개 파일에서 선택하도록 신뢰.

**추천:** D7b. Python 엔진이 실제로 하는 것; 트리거는 이미 5개 에이전트 md
파일에 문서화됨; 지시를 읽을 수 있는 모든 에이전트에 이식 가능. D7a보다
프롬프트 엔지니어링 위험이 약간 높지만 원본 동작에 더 충실.

### D8 — 크로스 에이전트 skill 형식 전략

다른 도구 이름을 사용하는 세 에이전트에서 실행 가능한 하나의 skill을 어떻게
출시하는가?

- **D8a. 기준 Claude Code 도구 이름 + 플랫폼 매핑 참조** — SKILL.md는 `Read` / `Write` / `Bash` / `AskUserQuestion` (Claude 이름) 사용. Skill 내부에 `references/codex-tools.md` + `references/gemini-tools.md` 매핑 테이블 포함. 각 에이전트가 호출 시 매핑 파일 읽음. (Superpowers 패턴.)
- **D8b. 에이전트별 skill 변종** — `skills/interview/claude/SKILL.md`, `skills/interview/codex/SKILL.md`, `skills/interview/gemini/SKILL.md` 유지. 각각 네이티브 도구 이름 사용. 세 배의 유지보수.
- **D8c. 추상적 지시만** — 특정 도구를 절대 명명하지 않음 ("파일 읽기 도구 사용", "사용자에게 질문"). 대충이지만 플랫폼 중립.

**추천:** D8a. 패턴이 증명됨 (superpowers). 유지보수 O(1) 유지. 새 플랫폼은
매핑 파일만 필요, 재작성 아님.

### D9 — 배포

사용자가 플러그인을 어떻게 설치하는가?

- **D9a. Claude 플러그인 마켓플레이스 + Codex/Gemini용 수동 설치 지침** — Claude는 `claude plugin install ...`; 다른 둘은 README 문서.
- **D9b. 세 에이전트 전역 단일 git-clone 설치** — 각 플랫폼 CLI에 git에서 skill 설치 방법 있음. 통합된 설치 스토리.
- **D9c. 배포 지연 — Claude 먼저 출시, 이식성은 나중에 해결**

**추천:** D9a. Claude 마켓플레이스로 시작 (주 사용자 기반의 가장 낮은 마찰);
skill+agent 구조를 이식성 있게 유지해 Codex/Gemini 사용자가 clone + symlink
가능. 해당 생태계가 성숙하면 Codex/Gemini 마켓플레이스 게시.

### D10 — MCP는 Phase 2 핵심 (개정)

이전엔 지연. 이제 R2/R3 해결 후 **주요 목표**.

- ~~D10a. 예 — 설계 공간 예약~~ (대체됨)
- ~~D10b. 아마도 — 문 열어둠~~ (대체됨)
- ~~D10c. 아니오 — 영원히 agent-only~~ (거부됨)
- **D10 (개정).** MCP는 Phase 2 (§7 참조). 전체 `InterviewEngine` +
  `AmbiguityScorer` + `InterviewHandler`를 `ask-socratic-ai` PyPI 패키지로
  포트. SKILL.md Step 0.5가 패키지 설치 시 MCP 자동 활성화; 없으면 Path B
  폴백.

**영향:**
- 두 개의 배포 아티팩트 (Claude 마켓플레이스 플러그인 + PyPI 패키지)
- Python 패키지 없는 Gemini 사용자 → Path B만 (작동함)
- 둘 다 설치한 Claude / Codex 사용자 → Path A (전체 수치 게이트, session_id
  핸드오프, resumable 상태)

### D11 — 원본 그대로 vs 재작성할 파일

MVP가 유지하는 6개의 에이전트 md 파일 중:

- `socratic-interviewer.md` — **재작성**. 소스는 `[from-code]` / `[from-user]` / `[from-research]` prefix를 언급; MVP는 prefixed 답변을 받을 MCP가 없으므로 제거. 순수 질문으로 역할 설명 단순화.
- `seed-closer.md` — **원본 그대로 복사**. 기준이 보편적.
- `researcher.md`, `simplifier.md`, `architect.md`, `breadth-keeper.md` — **원본 그대로 복사**. 역할 프롬프트가 보편적.

**추천:** 위에 나열된 대로. MCP 가정이 드러나는 하나의 파일만 재작성.

### D12 — 테스팅 / 검증 접근법 (개정 — full port용 확장)

새 테스트 (포트 X). 3단계:

- **Property 테스트** `AmbiguityScorer`용 (stub LLM 주어지면 결정론적 수학): 임계값, 플로어, 연속, 마일스톤, brownfield weight flip. LLM 불필요.
- **Integration 테스트** `InterviewEngine`용, mock `LLMAdapter`가 고정 응답 반환: start → record → ask 플로우, 상태 영속화, save/load 왕복, perspective 로테이션 트리거.
- **Contract 테스트** `InterviewHandler` (+ `PMInterviewHandler`)용: MCP 스키마 검증, 액션 디스패치, 게이트 거부 메시지, 완료 meta 형상, 이벤트 발행.
- **Smoke 테스트** 실제 LLM (수동, CI X): 출시마다 에이전트당 (Claude Code / Codex / Gemini CLI) 한 번의 완전한 인터뷰.

목표 커버리지: unit + integration으로 `interview/` + `pm/` 모듈에 대해 ≥80%
라인 커버리지. Smoke 테스트는 출시당 pass/fail 수동 체크포인트 — CI 게이트 X.

### D13 — Plugin-mode subagent dispatch (신규)

`InterviewHandler.handle()`는 980줄에 `should_dispatch_via_plugin` 분기가
있어 실제 질문 생성을 OpenCode Task 페인 (자식 서브에이전트)에 위임. 이는
Claude Code 성능 최적화 (긴 세션에서 LLM 컨텍스트 re-prime 회피)지만
~300줄과 하나의 Claude 전용 코드 경로 추가.

- **D13a.** Plugin-mode dispatch 유지, Claude 전용 — 런타임 감지; Claude Code에선 Task 페인 dispatch, Codex/Gemini에선 subprocess.
- **D13b. Plugin-mode 완전 제거 (추천)** — 항상 subprocess 모드. 핸들러가 자체 LLM 어댑터 소유. 더 단순.
- **D13c.** "Subagent dispatcher"로 추상화 — 핸들러가 런타임 호스트에 dispatch 요청; subprocess로 폴백.

**추천:** D13b. 가장 단순; 크로스 에이전트. OpenCode 성능 보너스는 포기하지만
하나의 통일된 코드 경로 획득. 각 MCP 호출이 ~3–8초 LLM 질문 생성 지연 비용 —
Path B와 동일.

**D13b의 영향:**
- 핸들러가 항상 자체 `LLMAdapter` 생성 (`create_llm_adapter()`)
- `ask-socratic-ai` 패키지가 항상 litellm 임포트 (~50 transitive deps)
- "plugin-only 설치" flavor 없음
- 포트에서 `build_interview_subagent` + `emit_subagent_dispatched_event` 헬퍼 제거 (예외: PM 핸들러의 transcript-passing `last_question` 패턴은 유지 — dispatch뿐 아니라 연속성에도 사용)

---

## 5. 추가 미결 질문 (MVP 차단 아님)

고려해볼 가치 있지만 당장 결정할 필요 없음:

- **Q1.** 의도된 사용자는 누구? (당신 개인 / 회사 팀 / 공개 OSS 사용자.)
  문서 톤 + 설치 마찰 허용치 좌우.
- **Q2.** 다국어 지원? (MVP는 영어 전용, 나중에 에이전트 md 파일에 한국어
  프롬프트 추가?) 골격이 작동한 후 쉽게 볼트 온.
- **Q3.** 인터뷰 세션 재생 / 공유? (markdown 트랜스크립트 내보내기 + 공유
  링크 / gist 통합.) D3에 의존.
- **Q4.** 당신의 3B 지식 시스템과의 통합? (인터뷰 트랜스크립트를
  `3b/projects/{name}/` 또는 `knowledge/process/`에 자동 저장.) 자연스러운
  적합이지만 3B 의존성 추가.

---

## 6. 추천 MVP 프로필 — "Full port + 새 테스트" (개정)

R1–R3 YES + D13b 추천 후:

- **D1:** `ask-socratic`
- **D2:** 독립 레포 `github.com/brandonwie/ask-socratic` + PyPI 패키지 `ask-socratic-ai`
- **D3:** **파일시스템 영속성** MCP 상태 파일 (`~/.ask-socratic/data/interview_{id}.json`) — 상위와 일치; Path B 폴백은 대화 내 전용
- **D4:** **수치 게이트** — 전체 `AmbiguityScorer` 포트 (체크리스트 전용 D4c 대체); Path B는 `seed-closer.md` 정성적 감사를 보조로 사용
- **D5:** YAML frontmatter + markdown 본문 요약 — Path A 활성 시 `session_id` 참조 추가
- **D6:** Codex용 평문 폴백; Claude + Gemini 네이티브 위젯
- **D7:** 트리거 주도 perspective 로테이션 — 포팅된 `InterviewEngine._load_interview_perspective_strategies()`가 강제
- **D8:** 기준 Claude 도구 이름 + 매핑 참조 (변경 없음)
- **D9:** Claude 마켓플레이스 + PyPI 이중 배포
- **D10:** **MCP는 Phase 2 핵심** ("지연"에서 뒤집음)
- **D11:** 재작성 목록 확장 — §12 rename map 참조 (여러 파일, `socratic-interviewer.md`뿐 아님)
- **D12:** Property + integration + contract + smoke 테스트 (포트 X, 새로 작성)
- **D13:** Plugin-mode subagent dispatch **제거** (subprocess 모드 전용)

3단계에 걸친 총 결과물:

- 플러그인 측: `plugin.json` 1 + 커맨드 1 + SKILL.md 1 + 도구 매핑 참조 2 + 에이전트 md 7 + README + LICENSE
- 패키지 측: `pyproject.toml` + ~185–265K Python (PM 완성도에 따라) + 테스트 스위트
- 문서: 설치 가이드 (에이전트별) + 예제 트랜스크립트 + CHANGELOG

예상 총 노력: **~9–13시간, 3회 집중 세션**. §7 참조.

---

## 7. Phase 분할 — 결정 후 다음 단계 (개정)

집중 세션 3회. 각 단계 말미에 tag + push로 중단 지점 확보.

### Phase 1 — 기반 + Path B (2–3시간) → `v0.1.0-alpha`

목표: Path B (agent-only) 폴백으로 세 에이전트에서 skill이 end-to-end 작동.
Python 아직 없음.

1. `gh repo create brandonwie/ask-socratic --public` + 로컬 클론.
2. 스캐폴딩: `plugin.json`, `LICENSE`, `README.md`, `CHANGELOG.md`.
3. 7개 에이전트 md 파일 (기존 6 + ontologist.md) → `agents/`. `socratic-interviewer.md`만 적응 (Ouroboros 자기참조 제거; `[from-code]` prefix 문구 유지 — Path A에서 필요).
4. 전체 듀얼 패스 구조의 `SKILL.md` 작성, 단 Step 0.5를 "아직 MCP 없음, Path B 사용"으로 하드코드 (Phase 2 tombstone).
5. superpowers에서 복사해 `ask-socratic`으로 리브랜딩한 `skills/interview/references/codex-tools.md` + `gemini-tools.md` 추가.
6. `commands/interview.md` 엔트리 스텁 작성.
7. 스모크 테스트: Claude Code, Codex, Gemini CLI에서 각각 인터뷰 한 번씩 실행. Path B 차단 요소 수정.
8. `git tag v0.1.0-alpha && git push`.

### Phase 2 — Path A 엔진 (4–6시간) → `v0.1.0-beta`

목표: MCP 서버 존재, `ask-socratic-ai` 패키지 PyPI (또는 git) 설치 가능,
Step 0.5가 찾으면 Path A 자동 활성화.

1. `ask-socratic-ai` 패키지용 `pyproject.toml` 스캐폴딩 (플러그인 레포 하위
   `python/` 또는 별도 레포 `ask-socratic-ai` — 미결 질문).
2. 2차 의존성 포트 (§12 참조): `core/types.py`, `core/errors.py`,
   `core/file_lock.py`, `core/security.py`, `core/initial_context.py`.
3. `providers/base.py` + LLM 어댑터 하나 (litellm) 포트. 단순화된 `config.py`
   (`get_clarification_model`) 포트.
4. `agents/loader.py` 포트.
5. `interview/state.py` (`InterviewState`, `InterviewRound`,
   `InterviewStatus`, `InterviewPerspective`) 포트.
6. `interview/engine.py` (`InterviewEngine`) 포트.
7. `interview/ambiguity.py` (`AmbiguityScorer` + 모든 상수) 포트.
8. `events/base.py` + `events/interview.py` 포트.
9. `persistence/event_store.py` 포트 (moba 커플링 있으면 단순화).
10. `mcp/types.py`, `mcp/errors.py` 포트.
11. `mcp/tools/interview.py` (`InterviewHandler`, D13b에 따라 plugin-mode 분기 제거) 포트.
12. 패키지 entry point에 MCP 서버 등록; `claude mcp add ask-socratic uv tool run ask-socratic-ai` 문서화.
13. SKILL.md Step 0.5 tombstone 해제 — ToolSearch가 실제로 Path A 활성화.
14. 새 테스트: property (ambiguity.py), integration (mock LLM으로 engine.py), contract (handler.py).
15. `git tag v0.1.0-beta && git push`.

### Phase 3 — PM + brownfield + ontologist perspective (3–4시간) → `v0.1.0`

목표: 상위 interview 서브시스템과 기능 동등.

1. Brownfield 포트: `brownfield.py` + `explore.py`. 자동 감지를 위해
   `InterviewEngine.start_interview(cwd=...)`에 연결.
2. PM 핵심 포트: `pm_seed.py` (PMSeed + UserStory), `pm_document.py`,
   `pm_completion.py`, `question_classifier.py`.
3. `pm/engine.py` (`PMInterviewEngine` composition wrapper) 포트.
4. `mcp/tools/pm.py` (`PMInterviewHandler` — decide-later diff 계산 포함;
   last_question 연속성 유지) 포트.
5. 메인 도구와 함께 PM MCP 도구 `ask-socratic_pm_interview` 등록.
6. `ontologist.md`를 6번째 `InterviewPerspective`로 추가 — enum 값 + 로더
   매핑 항목 + 엔진에 트리거 로직 (예: 사용자가 명시적으로 "왜" 질문 또는
   root-cause 신호 발생 시 활성화).
7. SKILL.md를 PM 변종 훅 + brownfield 자동 감지에 맞춰 업데이트.
8. 새 테스트: brownfield 감지, PM classifier, PM seed 추출, ontologist 로테이션 트리거.
9. 세 에이전트 전부에서 완전한 end-to-end 스모크: greenfield 인터뷰, brownfield 인터뷰 (cwd=pyproject.toml 있는 repo), PM 인터뷰.
10. `git tag v0.1.0 && git push`. Claude 마켓플레이스 제출 + PyPI publish (`uv publish` 또는 `twine`).

**총 예상 노력:** 9–13시간 (3회 집중 세션). 각 단계가 실행 가능한 결과물
제공. 마감 기한 압박 시 단계 드롭 가능 — v0.1.0-alpha만으로도 세 에이전트에
Path B 제공.

---

## 8. 나중에 변경 가능한 결정 (저위험)

D3, D6, D10은 MVP 후 재방문 쉬움 — skill 구조에 영향 없음. 처음에
제대로 선택할 가치 있는 결정:

- **D1 (이름)** — 나중에 플러그인 이름 변경은 저렴하지만, 누군가 설치했다면
  성가심.
- **D2 (레포)** — 레포 이동은 stars/히스토리 손실; 제대로 선택.
- **D8 (형식 전략)** — 전략 전환은 상당한 재작성.
- **D11 (재작성 vs 복사 대상)** — `socratic-interviewer.md` 재작성에 기술
  부채 쌓이면 아픔; 시간 투자.

나머지는 모두 릴리스와 함께 진화 가능.

---

## 9. 이 계획이 결정하지 않는 것

- 재작성된 `socratic-interviewer.md`의 실제 내용 (Phase 1).
- SKILL.md 전체 복사 (Phase 1 — §11 rename map에 따라 상위에서 파생).
- `pyproject.toml` 정확한 내용 (Phase 2).
- `plugin.json` 스키마 세부 (Phase 1 — boilerplate).
- 테스트 assertion 구체 (Phase 2 — 포팅된 동작에서 파생).
- 스모크 테스트 트랜스크립트 (각 단계 중 캡처).
- 미결 하위 질문: `ask-socratic-ai`가 플러그인 레포의 subfolder (`python/`)
  인지, 별도 레포인지? Phase 2 시작 시 해결.
- 미결 하위 질문: event-store SQLite 스키마 — 상위 것 유지할지 단순화할지?
  `persistence/event_store.py` 포팅 시 해결.

---

## 10. 실행 전 검증 (개정 — phase별)

**Phase 1 종료 기준:**

- 7개 에이전트 md 파일 모두 `agents/` 아래에 존재하고 유효한 markdown.
- SKILL.md frontmatter에 `name`, `description`, 선택적 `aliases`.
- `plugin.json`이 Claude 플러그인 manifest 스키마 통과.
- 도구 매핑 참조가 superpowers 원본과 일치 (캐시:
  `~/.claude/plugins/cache/temp_git_*/skills/using-superpowers/references/`).
- Claude Code에서 `/ask-socratic:interview "build a task CLI"` 실행 시
  SKILL.md 지시 2라운드 내 첫 질문 생성.
- Codex (`multi_agent=false`) + Gemini CLI에서 비교 가능한 동작.
- `v0.1.0-alpha` 태그 push.

**Phase 2 종료 기준:**

- `ask-socratic-ai` 패키지 클린 설치: `uv tool install ask-socratic-ai`.
- MCP 도구가 `claude mcp list | grep ask-socratic`로 발견 가능.
- `AmbiguityScorer` property 테스트 통과 (점수 수학 + 플로어 + 연속 + 마일스톤 + brownfield weight switch).
- `InterviewEngine` integration 테스트가 mock LLM 어댑터로 통과 (start → record → ask → save/load 왕복).
- `InterviewHandler` contract 테스트 통과 (스키마 검증, 액션 디스패치, 게이트 거부 메시지, 완료 meta).
- SKILL.md Step 0.5 `ToolSearch`가 도구 찾아 Path A로 라우팅.
- `interview/` 모듈 커버리지 ≥80%.
- `v0.1.0-beta` 태그 push.

**Phase 3 종료 기준:**

- Brownfield 자동 감지 작동: `cwd=<pyproject.toml 있는 repo>`로 실행 시
  `state.is_brownfield=True` 세팅되고 `codebase_paths` 채워짐.
- PM 인터뷰가 `/ask-socratic:pm-interview`로 별도 호출 가능.
- PMSeed 추출이 예상 JSON 스키마 생성
  (product_name / goal / user_stories / constraints / success_criteria /
  deferred_items / decide_later_items / assumptions).
- Ontologist perspective가 root-cause 스타일 사용자 응답에 트리거.
- 세 에이전트 전부 end-to-end 스모크 (greenfield + brownfield + PM).
- `v0.1.0` 태그 push, 마켓플레이스 제출 + PyPI publish 완료.

---

## 11. Rename map — 모든 `ouroboros` 참조 (신규)

파일 포팅 전에 정확히 뭐가 바뀌는지 알기. 포팅 시 각 행에 `rg` / `sed` 사용.

| 카테고리 | 이전 | 이후 |
|---|---|---|
| Python 패키지 이름 | `ouroboros` | `ask_socratic` |
| PyPI 배포 이름 | `ouroboros-ai` | `ask-socratic-ai` |
| MCP 도구 — 메인 | `ouroboros_interview` | `ask-socratic_interview` (MCP는 `-` 선호, 단 Claude MCP 도구 명명 규칙 확인 — `ask_socratic_interview` 필요할 수도) |
| MCP 도구 — PM | `ouroboros_pm_interview` | `ask-socratic_pm_interview` |
| 데이터 디렉토리 | `~/.ouroboros/data/` | `~/.ask-socratic/data/` |
| Seed 출력 디렉토리 | `~/.ouroboros/seeds/` | `~/.ask-socratic/seeds/` |
| 상태 파일명 패턴 | `interview_{id}.json` | 변경 없음 (이미 generic) |
| 모듈 경로 | `src/ouroboros/…` | `src/ask_socratic/…` |
| 이벤트 타입 prefix | `interview.started` (flat) | **미결:** flat 유지 OR `ask-socratic.interview.started`로 네임스페이스 |
| Config 클래스 | `OuroborosConfig` | `AskSocraticConfig` (또는 모듈 레벨 함수로 단순화) |
| Command / CLI entry | `ooo interview` | `ask-socratic interview` (또는 슬래시만 `/ask-socratic:interview`) |
| README / docstring 언급 | "Ouroboros" | "ask-socratic", 상위 credit 포함 |
| Skill frontmatter | `mcp_tool: ouroboros_interview` | `mcp_tool: ask-socratic_interview` |
| SKILL.md의 에이전트 파일 교차참조 | `src/ouroboros/agents/…` | `agents/…` (플러그인 상대) |

**실행 팁:** Phase 2 포팅 완료 후 `rg -i 'ouroboros' src/ask_socratic/ docs/`
실행해서 모든 hit이 README/docstring의 credit 라인 또는 이 분석 문서 참조가
의도된 것인지 확인.

---

## 12. 2차 의존성 그래프 (신규)

주요 항목 포팅 시 끌려오는 유틸리티들. Phase 2 커밋 전에 전체 footprint 파악.

### 주요 (~185K, PM 포함 시)

| 파일 | 크기 | 역할 |
|---|---|---|
| `src/ouroboros/bigbang/interview.py` | 31.6K | 엔진 + 상태 + perspective enum + 로더 |
| `src/ouroboros/bigbang/ambiguity.py` | 28.4K | 스코어러 + 임계값 + 플로어 + 마일스톤 |
| `src/ouroboros/mcp/tools/authoring_handlers.py` (InterviewHandler 슬라이스) | ~15K | 엔진의 MCP 래핑 |
| `src/ouroboros/bigbang/brownfield.py` + `explore.py` | 14.6K + 17.4K | Brownfield 감지 + 코드베이스 스캔 |
| `src/ouroboros/bigbang/pm_interview.py` | 45.8K | PM composition wrapper |
| `src/ouroboros/mcp/tools/pm_handler.py` | ~40K | PM MCP 래퍼 |
| `src/ouroboros/bigbang/pm_seed.py` + `pm_document.py` + `pm_completion.py` + `question_classifier.py` | ~40K | PM seed + document + completion + classifier |

### 2차 drag-in (~50K)

| 파일 | 크기 | 포트 이유 |
|---|---|---|
| `src/ouroboros/core/types.py` | ~1K | `Result` 타입 (어디서나 사용) |
| `src/ouroboros/core/errors.py` | ~2K | `ProviderError`, `ValidationError` |
| `src/ouroboros/core/security.py` | ~3K | `InputValidator` (핸들러에서 사용) |
| `src/ouroboros/core/file_lock.py` | ~2K | 안전한 상태 파일 쓰기 |
| `src/ouroboros/core/initial_context.py` | ~2K | `resolve_initial_context_input` |
| `src/ouroboros/core/seed.py` | ~10K | `Seed` immutable 데이터클래스 (완료 출력) |
| `src/ouroboros/providers/base.py` + litellm 어댑터 | ~10K | `LLMAdapter`, `Message`, `CompletionConfig` |
| `src/ouroboros/config.py` (단순화) | ~5K | `get_clarification_model` |
| `src/ouroboros/events/base.py` + 기존 `events/interview.py` | ~2K | 이벤트 typing |
| `src/ouroboros/persistence/event_store.py` | ~8K | SQLite 이벤트 스토어 (moba-coupled면 단순화) |
| `src/ouroboros/mcp/types.py` + `errors.py` | ~5K | MCP 프로토콜 타입 |
| `src/ouroboros/mcp/tools/subagent.py` | ~3K | `build_interview_subagent` (D13에도 불구하고 PM last_question 연속성 위해 유지) |
| `src/ouroboros/agents/loader.py` | 7.3K | `load_persona_prompt_data` (에이전트 md → 프롬프트 데이터) |

### 3차 리스크 (포트 범위 확장할 수 있는 것들)

| 리스크 | 완화책 |
|---|---|
| `config.py`가 `get_clarification_model` 넘어 `OuroborosConfig` 계층 끌어옴 | env + 필요 시 단일 YAML에서 읽는 최소 `get_clarification_model()` 함수로 교체 |
| `providers/base.py`가 litellm 직접 참조 | 커플링 유지 — litellm 어디서나 씀; 지금 추상화 불필요 |
| `event_store.py`가 moba / 다른 프로젝트 연결된 SQLite 스키마 | 인터뷰 관련 이벤트 타입만 포트; 상위가 over-designed면 단일 테이블로 단순화 |
| `subagent.py`가 Claude 특화 OpenCode 가정 보유 | `build_*_subagent`는 PM transcript 연속성 위해 유지; emission 헬퍼 무시 (D13b가 제거) |
| `agents/loader.py`가 특정 markdown 파서 가정 | 사소함; 있는 그대로 포트 |

**R1/R2/R3 전부 YES 시 총 포트:** ~265K Python, 7 에이전트 md, SKILL.md,
plugin.json, pyproject.toml, 테스트, 문서.

---

## 13. 다음 행동

**R1–R3 해결됨: YES. D13 추천 유지 (D13b plugin-mode 제거).** Phase 1 시작 준비 완료.

시작하고 싶을 때:

1. "start Phase 1"이라고 말하면 `gh repo create` 실행, 스캐폴딩, 에이전트
   복사, SKILL.md 초안, 스모크 테스트 진행.
2. 또는 D1–D13 / R1–R3 / D13 추천 중 재정의.
3. 또는 시작 전 특정 부분 (event_store 단순화, MCP 도구 명명 규칙, SKILL.md
   Step 0.5 재작성 등) 심화 필요 시 요청.

Task 리스트가 3단계 계획 반영하도록 업데이트됨.

---

## 부록 — 이식성 관점에서의 보완 설명

영어 문서를 기반으로 한국어 독자에게 추가로 도움될 만한 설명:

- **"skill"이란?** 각 AI 에이전트 CLI (Claude Code, Codex, Gemini CLI)가
  공통적으로 지원하는 **확장 단위**. 특정 폴더 구조에 `SKILL.md`를 넣으면
  사용자가 슬래시 커맨드 (`/plugin:skill`) 또는 자연어 트리거로 호출 가능.
  플러그인의 기본 단위라고 생각하면 됨.
- **"MCP"란?** Model Context Protocol. AI 에이전트와 외부 서버 사이의
  통신 표준. MCP 서버가 도구 (tool), 리소스 (resource), 프롬프트를 제공하면
  에이전트가 그것들을 호출 가능. Ouroboros의 `ouroboros_interview`는 MCP
  도구 예시. 개정된 MVP는 `ask-socratic_interview`로 이름을 바꿔 그대로 포트.
- **"Path A / Path B"란?** Ouroboros SKILL.md가 내부적으로 구분하는 두
  실행 경로. Path A = MCP 서버가 질문 생성 + 상태 저장 + 점수 매김; Path B =
  메인 세션 (Claude)이 대화 내에서 직접 실행. **이 포크는 듀얼 패스** —
  MCP 서버 (`ask-socratic-ai` 패키지) 설치되면 Path A, 없으면 Path B 폴백.
- **"agent-only"의 의미?** Python MCP 서버 없이, 오직 markdown 파일
  (SKILL.md + 에이전트 prompt들)로만 작동하는 버전. 원래 MVP 계획이었으나
  개정 후 Path B는 **폴백**일 뿐, MCP를 함께 포함하는 듀얼 구조로 전환.
- **"perspective rotation"이란?** 인터뷰의 각 라운드마다 다른 "관점"을
  적용 — researcher (조사 모드), simplifier (축소 모드), architect (구조
  모드), breadth-keeper (폭 유지 모드), seed-closer (종결 모드). 단일
  LLM이 다섯 가지 모자를 번갈아 쓴다고 생각하면 됨.
- **"rhythm guard"란?** AI가 연속 3라운드를 사용자 판단 없이 자동으로
  대답하면, 다음 라운드는 반드시 사용자에게 직접 질문하도록 강제하는
  규칙. AI가 너무 "혼잣말"하는 것을 방지.
- **"seed-closer audit"란?** 숫자 게이트가 "통과"라고 해도, 메인 세션이
  `seed-closer.md` 기준 (범위, 비목표, 출력, 검증 등이 명확한가?)을
  자체적으로 검사해서 종결을 거부할 수 있게 하는 안전 장치. MCP의
  기계적 신호보다 맥락 있는 Claude 세션이 더 많이 봄.

각 결정에 대한 세부 설명이 필요하면 영어 원본 `09-plugin-build-decisions.md`를
참조하고, 둘 중 한 문서에서 바로 편집해도 됨.

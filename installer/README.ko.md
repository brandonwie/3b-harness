# 전역 `~/.claude` 관리

이 디렉토리는 쉬운 머신 설정과 버전 관리를 위해 이식 가능한 Claude Code 설정
파일을 3B에 중앙집중화합니다.

---

## 빠른 시작

3B 클론 후 새 머신에서:

```bash
cd ~/dev/personal/3b/.claude/global-claude-setup
chmod +x setup.sh
./setup.sh
```

그런 다음 스크립트가 출력하는 수동 단계를 완료합니다.

---

## 제공 항목

| 항목                | 위치                                          | 설명                                            |
| ------------------- | --------------------------------------------- | ----------------------------------------------- |
| 커맨드              | `commands/` → `~/.claude/commands`            | 전역 슬래시 커맨드 (commit, wrap, clean-review) |
| CLAUDE.md           | `templates/CLAUDE.md` → `~/.claude/CLAUDE.md` | Claude용 전역 지침                              |
| 설정 템플릿         | `templates/settings.example.json`             | 정제된 설정 (토큰 없음)                         |
| 플러그인 매니페스트 | `templates/plugins/`                          | 설치할 플러그인 목록                            |

---

## 디렉토리 구조

```text
global-claude-setup/
├── README.md                       # 이 파일
├── setup.sh                        # 멱등성 설정 스크립트
├── .gitignore                      # 실제 settings.json 커밋 방지
├── templates/
│   ├── CLAUDE.md                   # 전역 지침 (이식 가능)
│   ├── settings.example.json       # 정제된 설정 템플릿
│   └── plugins/
│       ├── installed_plugins.json  # 플러그인 매니페스트
│       └── known_marketplaces.json # 마켓플레이스 URL
└── commands/                       # 전역 커맨드의 SoT
    ├── commit.md                   # /commit 커맨드
    ├── wrap.md                     # /wrap 커맨드
    ├── clean-review.md             # /clean-review 커맨드
    ├── clean-review/               # 지원 파일
    │   ├── clean-code-principles.md
    │   └── refactoring-catalog.md
    └── custom/
        └── pr-review.md            # /custom:pr-review 커맨드
```

---

## 주요 설계 결정

### 커맨드는 3B에 위치 (Source of Truth)

- 이전: 커맨드가 dotfiles에 있고 `~/.claude/commands/`에 심볼릭 링크됨
- 현재: 커맨드가 3B에 있고 전체 `commands/` 디렉토리가 심볼릭 링크됨
- 이유: 단일 진실 공급원, 3B 지식 시스템과 함께 버전 관리

### CLAUDE.md는 복사됨 (심볼릭 링크 아님)

- 전역 `~/.claude/CLAUDE.md`는 3B에서 심볼릭 링크가 아닌 복사됨
- 필요한 경우 머신별 커스터마이징 가능
- 3B에서 업데이트를 가져오려면 `setup.sh`를 다시 실행

### settings.json은 절대 커밋하지 않음

- 민감한 환경 변수 포함 (실험적 기능 플래그 등)
- `settings.example.json`을 템플릿으로 사용
- `.gitignore` 안전장치가 실수로 커밋되는 것을 방지

**참고:** GitHub 인증은 `gh auth login` (키링)과 GitHub MCP 플러그인의 내부
OAuth로 처리됩니다. settings에 PAT가 필요하지 않습니다.

### 플러그인은 선언적

- `installed_plugins.json`에 설치할 항목 목록
- 실제 설치는 Claude Code CLI를 통해
- 예상되는 설정의 문서 역할

---

## 수동 설정 단계

`setup.sh` 실행 후 필요한 작업:

### 1. settings.json 구성

`~/.claude/settings.json` 편집 — 권한 패턴과 환경 변수를 필요에 맞게 조정:

또한 `$HOME` 플레이스홀더를 실제 홈 경로로 교체:

```json
"Read($HOME/dev/**)" → "Read(/Users/yourusername/dev/**)"
```

### 2. Claude Code 로그인

```bash
claude
# 로그인 프롬프트 따르기
```

### 3. 플러그인 설치

Claude Code를 열고 `installed_plugins.json`에 나열된 플러그인 설치:

```bash
# Claude Code 내에서 플러그인 설치 커맨드 사용
/install-plugin context7@claude-plugins-official
/install-plugin github@claude-plugins-official
# 등등
```

### 4. (선택사항) Claude HUD 구성

Claude HUD 플러그인은 테마 커스터마이징을 위한 수동 패치가 필요합니다. 이는
머신별로 다르며 자동화되지 않습니다.

---

## 설정 업데이트

### 커맨드 업데이트

`~/.claude/commands/`의 커맨드는 3B에 심볼릭 링크되어 있습니다. 3B 커맨드의 모든
변경 사항이 자동으로 반영됩니다.

### CLAUDE.md 업데이트

3B에서 최신 버전을 가져오려면 설정 스크립트 재실행:

```bash
./setup.sh
```

### 설정 업데이트

설정은 첫 실행 시에만 복사됩니다. 수동 편집은 보존됩니다. 템플릿으로 리셋하려면:

```bash
rm ~/.claude/settings.json
./setup.sh
```

---

## 문제 해결

### 커맨드가 작동하지 않음

심볼릭 링크가 올바른지 확인:

```bash
ls -la ~/.claude/commands
# 표시되어야 함: commands -> /path/to/3b/.claude/global-claude-setup/commands
```

### GitHub MCP가 작동하지 않음

`gh` CLI 인증 확인:

```bash
gh auth status
# ✓ Logged in to github.com 표시되어야 함
```

`settings.local.json`에 `GITHUB_PERSONAL_ACCESS_TOKEN`이 있으면 제거하세요 — MCP
플러그인의 내부 OAuth와 충돌합니다.

### 플러그인이 로드되지 않음

settings.json에서 플러그인이 활성화되었는지 확인:

```bash
jq '.enabledPlugins' ~/.claude/settings.json
```

---

## 보안 참고사항

- 실제 토큰이 포함된 `settings.json`은 **절대** 커밋하지 마세요
- 이 디렉토리의 `.gitignore`가 실수로 커밋되는 것을 방지합니다
- 루트 `3b/.gitignore`에도 안전장치 패턴이 있습니다
- `settings.example.json`은 참조용으로만 사용하고 실제 사용하지 마세요

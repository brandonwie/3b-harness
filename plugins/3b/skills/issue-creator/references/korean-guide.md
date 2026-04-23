# Korean Translation Guide (합니다체)

Use during Step 5 (Create Issue) when creating the mandatory Korean 요약
section. Every issue MUST have a Korean section at the bottom.

## 합니다체 Verb Ending Patterns

| English Action | Korean Ending    | Example                           |
| -------------- | ---------------- | --------------------------------- |
| Added          | 추가했습니다     | 새 API 엔드포인트를 추가했습니다  |
| Fixed          | 수정했습니다     | null 체크 버그를 수정했습니다     |
| Updated        | 업데이트했습니다 | 의존성을 업데이트했습니다         |
| Removed        | 제거했습니다     | 사용하지 않는 코드를 제거했습니다 |
| Improved       | 개선했습니다     | 성능을 개선했습니다               |
| Refactored     | 리팩토링했습니다 | 서비스 레이어를 리팩토링했습니다  |
| Implemented    | 구현했습니다     | 캐싱 로직을 구현했습니다          |
| Need to add    | 추가해야 합니다  | 유효성 검사를 추가해야 합니다     |
| Need to fix    | 수정해야 합니다  | 경쟁 상태를 수정해야 합니다       |
| Should support | 지원해야 합니다  | 연간 구독을 지원해야 합니다       |

## Technical Terms to Keep in English

Keep these in English (do NOT translate):

- API, DTO, endpoint, cache, queue, webhook
- Service names: Redis, PostgreSQL, S3
- Code terms: null, undefined, async, Promise
- Patterns: singleton, factory, repository

## Transformation Example

**English:**

```markdown
## Description

Add yearly subscription support to the payment module.

## Context

Monthly subscriptions are the only option. Users have requested yearly billing
with a discount.
```

**Korean (합니다체):**

```markdown
## 요약 (Korean)

### 설명

결제 모듈에 연간 구독 지원을 추가해야 합니다.

### 맥락

현재 월간 구독만 지원됩니다. 사용자들이 할인이 적용된 연간 결제를 요청했습니다.
```

## Structure Requirements

- Korean section mirrors English Description + Context sections
- Use 합니다체 endings consistently (not 해요체 or 하다체)
- Acceptance Criteria and Related sections are NOT translated (they are
  actionable checklists/links, not prose)

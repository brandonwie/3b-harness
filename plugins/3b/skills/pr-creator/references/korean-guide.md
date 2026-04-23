# Korean Translation Guide (합니다체)

Use during Step 3 (Generate PR Content) when creating the mandatory Korean 요약
section. Every PR MUST have a Korean section.

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

## Technical Terms to Keep in English

Keep these in English (do NOT translate):

- API, DTO, endpoint, cache, queue, webhook
- Service names: Redis, PostgreSQL, S3
- Code terms: null, undefined, async, Promise
- Patterns: singleton, factory, repository

## Transformation Example

**English:**

```markdown
## Summary

- Add checkout validation API endpoint
- Fix race condition in payment processing
- Update error handling for webhook failures
```

**Korean (합니다체):**

```markdown
## 요약 (Korean)

- 결제 유효성 검사 API 엔드포인트를 추가했습니다
- 결제 처리 중 경쟁 상태 버그를 수정했습니다
- webhook 실패에 대한 에러 처리를 업데이트했습니다
```

## Structure Requirements

- **MUST have same number of bullet points** as English version
- Each Korean bullet corresponds 1:1 with English bullet
- Use 합니다체 endings consistently (not 해요체 or 하다체)

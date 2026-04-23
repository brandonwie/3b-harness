# Comment Templates & Writing Guidelines

Templates for the 5 comment categories and language-specific writing guidelines.
Use during Phase 4 (Generate Comment Content) when composing inline review
comments.

## Korean Templates (합니다체)

### 1. Core Function Explanation

````markdown
### 📌 {FunctionName}() - 핵심 함수

**이 함수가 존재하는 이유:**

{Problem it solves}

**해결책:**

```typescript
{Key implementation pattern}
```

**사용처:** {Where this is called from}
````

### 2. Edge Case Handling

````markdown
### 📌 {Edge Case Name} 처리

**문제 상황:**

- {Describe the edge case}

**구현 방식:**

```typescript
{How it's handled}
```

**왜 이렇게 처리하는가:** {Reasoning}
````

### 3. Design Decision

```markdown
### 📌 설계 결정: {Decision Name}

**선택한 방식:** {What was chosen}

**대안:**

- {Alternative 1} - {Why not chosen}
- {Alternative 2} - {Why not chosen}

**이유:** {Why this approach is better}
```

### 4. Performance Optimization

````markdown
### 📌 성능 최적화: {Optimization Name}

**Before:**

```typescript
{Old code}
```

**After:**

```typescript
{New code}
```

**개선점:** {What improves and when it matters}
````

### 5. Integration Point

```markdown
### 📌 통합 포인트: {Integration Name}

**연결 대상:** {What it connects to}

**중요:** {Critical information for understanding}

**참고:** `{related_file.ts:line}` 참조
```

## English Templates

### Generic Template

````markdown
### 📌 {Title}

**Why this implementation:**

{Explanation - why this approach was chosen}

**Pattern:**

```typescript
{Key code example}
```

**See also:** {Additional context or related file links}
````

## Summary Body Templates

### Korean

```markdown
## 셀프 리뷰 (Self Review) 🔍

이 PR의 핵심 구현 포인트를 설명합니다. 새로운 개발자가 {feature_name} 처리
패턴을 이해하는 데 도움이 되길 바랍니다.

### 요약

- **{Issue 1}**: {간단한 설명}
- **{Issue 2}**: {간단한 설명}
```

### English

```markdown
## Self Review 🔍

This review explains key implementation points. Intended to help new developers
understand the {feature_name} patterns.

### Summary

- **{Issue 1}**: {Brief description}
- **{Issue 2}**: {Brief description}
```

## Writing Guidelines

### Korean (합니다체)

| Action   | Ending    | Example                         |
| -------- | --------- | ------------------------------- |
| Explains | ~합니다   | 이 함수는 EXDATE를 파싱합니다   |
| Reason   | ~했습니다 | 성능을 위해 캐싱을 추가했습니다 |
| Note     | ~입니다   | 이것은 의도적인 설계 결정입니다 |
| Warning  | ~하세요   | null 체크를 반드시 하세요       |

**Technical Terms to Keep in English:**

- API, DTO, EXDATE, RRULE, TZID, DST, UTC
- Library names: dayjs, rrule.js, Sentry
- Code terms: null, undefined, Promise, async
- Patterns: RRuleSet, cascade, webhook

### English

- Use active voice
- Be concise but complete
- Explain "why" not just "what"
- Include code snippets when helpful

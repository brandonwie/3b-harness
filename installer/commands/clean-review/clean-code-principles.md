# Clean Code Principles (Robert C. Martin)

> Source: "Clean Code: A Handbook of Agile Software Craftsmanship" (2008)

## Core Philosophy

> "Code is clean if it can be understood easily – by everyone on the team."

- Code should read like well-written prose
- Leave code cleaner than you found it (Boy Scout Rule)
- Always find root cause, don't just patch symptoms

---

## SOLID Principles

| Principle                 | Definition (per Uncle Bob)                                             |
| ------------------------- | ---------------------------------------------------------------------- |
| **S**ingle Responsibility | "A class should have one, and only one, reason to change"              |
| **O**pen/Closed           | "You should be able to extend a class's behavior without modifying it" |
| **L**iskov Substitution   | "Derived classes must be substitutable for their base classes"         |
| **I**nterface Segregation | "Make fine-grained interfaces that are client-specific"                |
| **D**ependency Inversion  | "Depend on abstractions, not on concretions"                           |

---

## Chapter 2: Meaningful Names

| Rule                          | Description                                                 |
| ----------------------------- | ----------------------------------------------------------- |
| Use Intention-Revealing Names | Name should tell why it exists, what it does, how it's used |
| Avoid Disinformation          | Don't use `accountList` if it's not actually a List         |
| Make Meaningful Distinctions  | No noise words (ProductInfo vs ProductData vs Product)      |
| Use Pronounceable Names       | `genymdhms` → `generationTimestamp`                         |
| Use Searchable Names          | Single-letter names only for small local scopes             |
| Avoid Encodings               | No Hungarian notation, no `m_` prefixes                     |
| Avoid Mental Mapping          | Reader shouldn't translate `r` → `url` mentally             |
| Class Names                   | Nouns: `Customer`, `Account`, `AddressParser`               |
| Method Names                  | Verbs: `postPayment()`, `deletePage()`, `save()`            |
| Pick One Word per Concept     | Don't mix `fetch`/`retrieve`/`get` for same concept         |
| Use Solution Domain Names     | CS terms OK: `Factory`, `Visitor`, `Queue`                  |
| Use Problem Domain Names      | When no CS term fits, use domain terminology                |
| Add Meaningful Context        | `state` → `addrState` when in address context               |

---

## Chapter 3: Functions

| Rule                     | Guidance                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------ |
| Small                    | First rule: functions should be small. Second rule: smaller than that. ~20 lines max |
| Do One Thing             | "Functions should do one thing. They should do it well. They should do it only."     |
| One Level of Abstraction | Don't mix high-level and low-level operations                                        |
| Reading Top-Down         | Code should read like a narrative, top-to-bottom                                     |
| Switch Statements        | Bury in low-level class, use polymorphism instead                                    |
| Descriptive Names        | Long descriptive name > short enigmatic name                                         |
| Few Arguments            | 0 (niladic) ideal, 1 (monadic) good, 2 (dyadic) OK, 3 (triadic) avoid, 4+ never      |
| No Flag Arguments        | `render(true)` → split into `renderForSuite()` and `renderForTest()`                 |
| No Side Effects          | Don't do hidden things (change globals, modify params)                               |
| Command Query Separation | Either DO something or ANSWER something, not both                                    |
| Prefer Exceptions        | Use exceptions over return codes for error handling                                  |
| Extract Try/Catch        | Error handling is "one thing"—extract to own function                                |
| DRY                      | Duplication is the root of all evil in software                                      |

---

## Chapter 4: Comments

### Good Comments

- Legal comments (copyright, license)
- Informative (explain regex pattern)
- Explanation of intent
- Clarification of obscure argument
- Warning of consequences
- TODO comments (but clean them up)
- Amplification of importance

### Bad Comments

- Mumbling (unclear, incomplete)
- Redundant (restates the obvious code)
- Misleading (inaccurate description)
- Mandated (forced javadocs for every function)
- Journal comments (git handles history)
- Noise comments (`/** Default constructor */`)
- Position markers (`// Actions /////`)
- Closing brace comments
- Attributions (`/* Added by Bob */`)
- Commented-out code (DELETE IT)
- Nonlocal information (describes other code)
- Too much information

---

## Chapter 6: Objects and Data Structures

| Concept                   | Description                                                                                           |
| ------------------------- | ----------------------------------------------------------------------------------------------------- |
| Data Abstraction          | Hide implementation, expose abstract interface                                                        |
| Data/Object Anti-Symmetry | Objects hide data, expose behavior. Data structures expose data, have no behavior.                    |
| Law of Demeter            | Method should only call methods on: itself, its parameters, objects it creates, its direct components |
| Train Wrecks              | `a.getB().getC().getD()` violates Demeter—hide the chain                                              |
| Hybrids                   | Worst of both worlds—half object, half data structure. Avoid.                                         |

---

## Chapter 7: Error Handling

| Rule                     | Description                                             |
| ------------------------ | ------------------------------------------------------- |
| Use Exceptions           | Not return codes                                        |
| Write Try-Catch First    | Start with exception handling, then fill in logic       |
| Use Unchecked Exceptions | Checked exceptions violate OCP                          |
| Provide Context          | Include operation attempted and failure type in message |
| Define by Caller's Needs | Wrap third-party APIs to normalize exceptions           |
| Don't Return Null        | Return empty collection or Special Case object instead  |
| Don't Pass Null          | Assert or throw on null parameters                      |

---

## Chapter 9: Unit Tests (F.I.R.S.T.)

| Letter | Principle       | Meaning                                            |
| ------ | --------------- | -------------------------------------------------- |
| **F**  | Fast            | Tests run quickly (seconds, not minutes)           |
| **I**  | Independent     | Tests don't depend on each other, run in any order |
| **R**  | Repeatable      | Same result in any environment (dev, CI, prod)     |
| **S**  | Self-Validating | Boolean output—pass or fail, no manual inspection  |
| **T**  | Timely          | Written just before or with production code (TDD)  |

### Additional Test Rules

- One assert per test (ideally)
- Single concept per test
- Tests as documentation
- Test code is as important as production code

---

## Chapter 10: Classes

| Rule                  | Description                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------- |
| Class Organization    | Public static constants → private static → private instance → public functions → private utilities |
| Small Classes         | Measured by responsibilities, not lines. Name should describe ONE responsibility                   |
| Single Responsibility | One reason to change. "If we cannot derive a concise name, class is likely too large"              |
| Cohesion              | Methods should use most instance variables. High cohesion = methods and variables co-depend        |
| Maintaining Cohesion  | When function wants only some variables → extract new class                                        |
| Organizing for Change | Classes should be open for extension, closed for modification                                      |

---

## Chapter 17: Smells and Heuristics (Design Smells)

Uncle Bob's 6 symptoms of rotting design:

| Smell                   | Symptom                                                             |
| ----------------------- | ------------------------------------------------------------------- |
| **Rigidity**            | System is hard to change—one change forces cascade of other changes |
| **Fragility**           | Changes break system in unrelated places                            |
| **Immobility**          | Hard to reuse parts in other systems—too entangled                  |
| **Viscosity**           | Doing things right is harder than doing things wrong                |
| **Needless Complexity** | Over-engineering, unused infrastructure (YAGNI violation)           |
| **Needless Repetition** | Copy-paste code, DRY violation                                      |
| **Opacity**             | Code is hard to understand, poor expression of intent               |

---

## Design Rules Summary

1. Prefer polymorphism over if/else or switch/case
2. Separate multi-threading code from business logic
3. Prevent over-configurability
4. Use dependency injection
5. Follow Law of Demeter (talk only to friends)
6. Keep configurable data at high levels

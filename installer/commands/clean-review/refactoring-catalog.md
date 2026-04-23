# Refactoring Catalog (Martin Fowler)

> Source: "Refactoring: Improving the Design of Existing Code" 2nd Edition (2018)

## Core Definition

> "Refactoring is a disciplined technique for restructuring an existing body of code, altering its internal structure without changing its external behavior."

Key insight: Small behavior-preserving transformations, each too small to be worth doing alone, but cumulative effect is significant.

---

## Code Smells by Category

> Code smells originated from Kent Beck. "A code smell is a surface indication that usually corresponds to a deeper problem in the system." — Martin Fowler

### Bloaters

_Code, methods, and classes that have grown too large to handle effectively._

| Smell                   | Signal                                             | Refactoring                                                      |
| ----------------------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| **Long Method**         | Method does too much, hard to understand           | Extract Function                                                 |
| **Large Class**         | Class has too many fields/methods/responsibilities | Extract Class, Extract Subclass                                  |
| **Long Parameter List** | > 3 parameters                                     | Introduce Parameter Object, Preserve Whole Object                |
| **Data Clumps**         | Same group of variables passed around together     | Extract Class, Introduce Parameter Object                        |
| **Primitive Obsession** | Overuse of primitives instead of small objects     | Replace Primitive with Object, Replace Type Code with Subclasses |

### Object-Orientation Abusers

_Incomplete or incorrect application of OO principles._

| Smell                                             | Signal                                                | Refactoring                                    |
| ------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------- |
| **Switch Statements**                             | Same switch on type code in multiple places           | Replace Conditional with Polymorphism          |
| **Temporary Field**                               | Field only set/used in certain circumstances          | Extract Class, Introduce Special Case          |
| **Refused Bequest**                               | Subclass doesn't use inherited methods/data           | Replace Inheritance with Delegation            |
| **Alternative Classes with Different Interfaces** | Two classes do same thing with different method names | Rename Method, Move Method, Extract Superclass |

### Change Preventers

_When one change requires changes in many other places._

| Smell                                | Signal                                                          | Refactoring                             |
| ------------------------------------ | --------------------------------------------------------------- | --------------------------------------- |
| **Divergent Change**                 | One class modified for multiple different reasons               | Extract Class (split by responsibility) |
| **Shotgun Surgery**                  | One change requires editing many classes                        | Move Method, Move Field, Inline Class   |
| **Parallel Inheritance Hierarchies** | Creating subclass in one hierarchy requires subclass in another | Move Method, Move Field                 |

### Dispensables

_Unnecessary code whose removal makes code cleaner._

| Smell                      | Signal                                                  | Refactoring                                             |
| -------------------------- | ------------------------------------------------------- | ------------------------------------------------------- |
| **Duplicated Code**        | Identical or very similar code in multiple places       | Extract Function, Extract Class, Pull Up Method         |
| **Lazy Class**             | Class that doesn't do enough to justify its existence   | Inline Class, Collapse Hierarchy                        |
| **Data Class**             | Class with only fields and getters/setters, no behavior | Move Function, Extract Function, encapsulate collection |
| **Dead Code**              | Unreachable or unused code                              | Delete it                                               |
| **Speculative Generality** | "We might need this someday" (YAGNI)                    | Collapse Hierarchy, Inline Function, Inline Class       |
| **Comments**               | Comments compensating for bad code                      | Extract Function, Rename (let code explain itself)      |

### Couplers

_Excessive coupling between classes._

| Smell                        | Signal                                                | Refactoring                                                    |
| ---------------------------- | ----------------------------------------------------- | -------------------------------------------------------------- |
| **Feature Envy**             | Method uses data from another class more than its own | Move Function, Extract Function                                |
| **Inappropriate Intimacy**   | Classes access each other's private parts excessively | Move Function, Move Field, Replace Inheritance with Delegation |
| **Message Chains**           | `a.getB().getC().getD()`                              | Hide Delegate, Extract Function, Move Function                 |
| **Middle Man**               | Class delegates most work without adding value        | Remove Middle Man, Inline Function                             |
| **Incomplete Library Class** | Library class missing needed functionality            | Introduce Foreign Method, Introduce Local Extension            |

---

## Refactoring Catalog by Category

### Composing Methods

| Refactoring                      | When to Use                                                                              |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| Extract Function                 | Code fragment that can be grouped; turn it into a function with intention-revealing name |
| Inline Function                  | Function body is as clear as its name                                                    |
| Extract Variable                 | Expression is hard to understand; put result in temp with meaningful name                |
| Inline Variable                  | Temp is no clearer than expression                                                       |
| Replace Temp with Query          | Temp holds result of expression; extract to function for reuse                           |
| Split Variable                   | Variable assigned more than once (not loop counter); use separate variable for each      |
| Remove Assignments to Parameters | Code assigns to parameter; use temp variable instead                                     |

### Moving Features

| Refactoring                            | When to Use                                               |
| -------------------------------------- | --------------------------------------------------------- |
| Move Function                          | Function uses features of another class more than its own |
| Move Field                             | Field used more by another class                          |
| Move Statements into Function          | Statements always appear with function call               |
| Move Statements to Callers             | Function behaves differently depending on caller          |
| Replace Inline Code with Function Call | Code duplicates existing function                         |
| Slide Statements                       | Related code should be near each other                    |
| Split Loop                             | Loop doing multiple things                                |
| Replace Loop with Pipeline             | Use filter, map, reduce instead of loop                   |
| Remove Dead Code                       | Code not being used                                       |

### Organizing Data

| Refactoring                         | When to Use                                  |
| ----------------------------------- | -------------------------------------------- |
| Split Variable                      | Variable used for multiple purposes          |
| Rename Field                        | Name doesn't communicate purpose             |
| Replace Derived Variable with Query | Variable can be computed from others         |
| Change Reference to Value           | Reference object should be immutable         |
| Change Value to Reference           | Need shared object for consistency           |
| Replace Primitive with Object       | Primitive needs behavior or special handling |
| Replace Type Code with Subclasses   | Type code affects behavior                   |
| Replace Subclass with Delegate      | Inheritance is limiting or inappropriate     |

### Simplifying Conditional Logic

| Refactoring                                   | When to Use                                            |
| --------------------------------------------- | ------------------------------------------------------ |
| Decompose Conditional                         | Complex conditional with complicated clauses           |
| Consolidate Conditional Expression            | Sequence of conditionals with same result              |
| Replace Nested Conditional with Guard Clauses | Special cases before main logic                        |
| Replace Conditional with Polymorphism         | Conditional chooses behavior based on type             |
| Introduce Special Case                        | Same conditional logic for special case in many places |
| Introduce Assertion                           | Code assumes something about state                     |

### Refactoring APIs

| Refactoring                               | When to Use                                         |
| ----------------------------------------- | --------------------------------------------------- |
| Separate Query from Modifier              | Function with side effects that returns value       |
| Parameterize Function                     | Functions differ only by literal values             |
| Remove Flag Argument                      | Boolean parameter selects behavior                  |
| Preserve Whole Object                     | Passing several values from one object              |
| Replace Parameter with Query              | Parameter value can be obtained from receiver       |
| Replace Query with Parameter              | Unwanted dependency in function                     |
| Remove Setting Method                     | Field should not be changed after construction      |
| Replace Constructor with Factory Function | Need more flexibility than simple constructor       |
| Replace Function with Command             | Function needs complex operations (undo, lifecycle) |
| Replace Command with Function             | Command is simple, doesn't need the overhead        |

### Dealing with Inheritance

| Refactoring                      | When to Use                                   |
| -------------------------------- | --------------------------------------------- |
| Pull Up Method                   | Duplicate methods in subclasses               |
| Pull Up Field                    | Duplicate fields in subclasses                |
| Pull Up Constructor Body         | Common code in subclass constructors          |
| Push Down Method                 | Method only relevant to one subclass          |
| Push Down Field                  | Field only used by one subclass               |
| Replace Subclass with Delegate   | Inheritance inappropriate or limiting         |
| Replace Superclass with Delegate | Subclass doesn't want all superclass behavior |
| Extract Superclass               | Classes with similar features                 |
| Collapse Hierarchy               | Superclass and subclass are too similar       |

---

## Refactoring Workflow

1. **Ensure Tests Pass** — Safety net before any change
2. **Make Smallest Possible Change** — One atomic transformation
3. **Run Tests After Each Change** — Catch issues immediately
4. **Commit Frequently** — Easy rollback points
5. **Repeat Until Smell is Gone** — Incremental improvement

### The Two Hats Metaphor

- **Adding Functionality** hat: Add new capabilities, don't change existing code
- **Refactoring** hat: Restructure code, don't add new functionality
- Never wear both hats at once

---

## When to Refactor

| Trigger                       | Action                                                                          |
| ----------------------------- | ------------------------------------------------------------------------------- |
| **Rule of Three**             | First time: just do it. Second time: wince and duplicate. Third time: refactor. |
| **Preparatory Refactoring**   | Make the change easy, then make the easy change                                 |
| **Comprehension Refactoring** | Refactor to understand unfamiliar code                                          |
| **Litter-Pickup Refactoring** | Small improvements while passing through                                        |
| **Planned Refactoring**       | Scheduled time to address tech debt                                             |
| **Long-Term Refactoring**     | Large refactoring done incrementally                                            |

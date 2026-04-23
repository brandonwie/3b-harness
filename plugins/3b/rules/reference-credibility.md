---
paths:
  - "knowledge/**"
---

# Reference Credibility

References work as crucial backups and evidence for decisions. They must
guarantee credibility.

## Reference Types

| Type            | Description                 | Validation                |
| --------------- | --------------------------- | ------------------------- |
| `official`      | Official docs, GitHub, RFCs | URL from official domain  |
| `authoritative` | Credible authors/companies  | Must be verified expert   |
| `verified`      | Third-party, tested         | Must have `verified_date` |
| `experience`    | Own implementation          | Must have `notes` context |

## Credible Source Criteria

**Official Sources (highest credibility):**

- Official documentation (docs.\*, official GitHub repos)
- RFCs and specifications (IETF, W3C, ECMA)
- Official project blogs (e.g., `https://v8.dev/` for V8 engine)

**Authoritative Sources:**

- **Inventors/Creators**: Authors of languages, frameworks, tools
  - Example: Brendan Eich for JavaScript, Guido van Rossum for Python
  - Example: Ryan Dahl for Node.js/Deno, Evan You for Vue
- **Core Contributors**: Major participants in open-source projects
- **Foundation/Company Blogs**: Official engineering blogs
  - Google: `v8.dev`, `web.dev`, `developers.google.com`
  - Mozilla: `hacks.mozilla.org`, MDN
  - Cloudflare: `blog.cloudflare.com`
  - Vercel: `vercel.com/blog`
  - AWS: `aws.amazon.com/blogs/`
- **Recognized Experts**: Authors with proven track record
  - Kent C. Dodds (React/Testing), Dan Abramov (React/Redux)
  - Martin Fowler (Architecture), Robert C. Martin (Clean Code)

**NOT Credible (avoid for blog posts):**

- Random Medium/Dev.to articles without author credentials
- Stack Overflow answers (use as hints, not references)
- AI-generated content without verification
- Outdated tutorials (> 2 years for fast-moving tech)

## Blog Publishability Decision Tree

```text
moba/ category? → publishable: false (company-specific)
Proprietary info? → publishable: false (proprietary)
Incomplete content? → publishable: "review" (incomplete)
Weak references? → publishable: "review" (needs-references)
Otherwise → publishable: true
```

## Quality Gates for Blog Publishing

- At least one `official` or `authoritative` reference required
- `experience` alone is insufficient (needs supporting reference)
- All URLs must be reachable
- `verified_date` should be within 1 year

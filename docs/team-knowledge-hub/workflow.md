# Team Workflow & Git Discipline

To maintain high code quality and satisfy academic review standards, all team members must follow this workflow.

---

## 1. Git Commit Message Standards

Every commit must follow standard semantic prefixing:

| Prefix | Usage Example |
|---|---|
| `chore:` | Project setup, configuration, dependency updates (`chore: configure tailwind css`) |
| `data:` | Dataset audit scripts, verification notes (`data: add dataset inspection script`) |
| `feat:` | New feature or functional component (`feat: implement opencv preprocessor`) |
| `fix:` | Bug fixes or stability adjustments (`fix: prevent repeated letter trigger in debounce`) |
| `docs:` | Documentation updates, team hub guides (`docs: add viva preparation notes`) |
| `test:` | Unit tests and verification scripts (`test: add preprocessor tensor shape tests`) |

---

## 2. Commit Hygiene Rules
1. **Never Commit Broken Code:** Verify that your code compiles, builds, or passes unit tests before making a commit.
2. **Review Diff Before Staging:** Run `git status` and `git diff` to ensure no unwanted temporary files or caches are staged.
3. **Strict Ignore Policy:**
   - Datasets (`dataset/raw/*`, `dataset/custom/*`) are strictly excluded.
   - Virtual environments (`.venv/`, `env/`) must never be tracked.
   - Heavy model checkpoints (only light final weights or label maps).
4. **Push Policy:** Never execute `git push` without explicit team discussion and approval.

---

## 3. Implementation Verification Checklist
Before declaring any task complete:
- [ ] Code is formatted and readable for a 3rd-year student.
- [ ] No hardcoded fake statistics or synthetic metrics are used.
- [ ] The relevant script or build command has been executed and passed.
- [ ] Documentation reflects actual, verified functionality.

# Contribution Guidelines & Git Discipline

Welcome! To maintain production-quality code and clear version history, all contributors must adhere to the following standards.

---

## 1. Git Semantic Commit Conventions

All commit messages must begin with an approved semantic prefix:

| Prefix | Type of Change | Example |
|---|---|---|
| `chore:` | Build tasks, configs, dependencies, repo organization | `chore: reorganize documentation into engineering-focused structure` |
| `data:` | Dataset audit scripts, verification notes, schema checks | `data: add dataset inspection script` |
| `feat:` | Functional code addition (backend route, model, UI) | `feat: implement opencv preprocessor` |
| `fix:` | Bug fixes or behavioral corrections | `fix: prevent duplicate letter trigger in debounce filter` |
| `docs:` | Documentation updates | `docs: update architecture with debounce algorithm` |
| `test:` | Unit tests, verification suites | `test: add preprocessor tensor shape validation` |

---

## 2. Commit Hygiene & Pull Request Rules
1. **Never Commit Broken Code:** Verify that the frontend builds cleanly (`npm run build`) and backend tests pass before committing.
2. **Review Diff Prior to Staging:** Run `git status` and `git diff` to ensure no transient files, temporary caches, or untracked models are accidentally included.
3. **Strict Ignore Exclusions:**
   - Datasets (`dataset/raw/*`, `dataset/custom/*`) are strictly excluded.
   - Virtual environments (`.venv/`, `env/`) must never be tracked.
   - Heavy HDF5/SavedModel exports (`*.h5`, `*.pb`, `saved_models/variables/`) are excluded; compact production `.keras` checkpoints (< 5 MB) are tracked for out-of-the-box inference.
4. **Push Authorization:** Never execute `git push` to a remote repository without explicit team consensus.

---

## 3. Engineering Quality Checklist
- [ ] Code is modular, readable, and free of redundant dependencies.
- [ ] No hardcoded fake statistics or synthetic metrics are used.
- [ ] Verification commands have been executed and logged.
- [ ] Documentation links and path references are validated.

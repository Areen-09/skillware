# AI-Native Contribution Workflow

This guide describes a recommended, human-in-the-loop workflow for contributing to [Skillware](https://github.com/ARPAHLS/skillware) with AI coding assistants (Cursor, Copilot, Claude Code, Gemini, or similar). The assistant does the heavy lifting; you review and approve at each stage before anything is merged.

For repository standards and contribution types, start with [CONTRIBUTING.md](../../CONTRIBUTING.md).

---

## Navigation

- [Principles](#principles)
- [Stage 1: Repository setup](#stage-1-repository-setup)
- [Stage 2: Analysis with a reasoning model](#stage-2-analysis-with-a-reasoning-model)
- [Stage 3: Human review of the plan](#stage-3-human-review-of-the-plan)
- [Stage 4: Implementation with a faster model](#stage-4-implementation-with-a-faster-model)
- [Stage 5: Verification with a reasoning model](#stage-5-verification-with-a-reasoning-model)
- [Stage 6: Branch, commit, and push](#stage-6-branch-commit-and-push)
- [Stage 7: Pull request and CI](#stage-7-pull-request-and-ci)
- [Skillware conventions for AI assistants](#skillware-conventions-for-ai-assistants)
- [Verification checklists by contribution type](#verification-checklists-by-contribution-type)
- [Starter prompts](#starter-prompts)

---

## Principles

1. **Human authority**: You own the fork, the branch, the commit message, and the decision to open or merge a PR. The model proposes; you approve.
2. **Issue-first**: Read the linked GitHub issue and its acceptance criteria before writing code. If there is no issue, open one or confirm scope with maintainers.
3. **Scope discipline**: Change only what the issue requires. Avoid drive-by refactors, unrelated formatting, or version bumps unless explicitly requested.
4. **Determinism**: Skill logic must be ordinary Python with predictable outputs. Do not rely on the model to generate executable code at runtime inside a skill.
5. **No emojis**: Do not use emojis in source code, documentation, commit messages, or PR titles.

---

## Stage 1: Repository setup

**Goal**: A local clone tied to your fork, on an up-to-date default branch.

1. Fork [ARPAHLS/skillware](https://github.com/ARPAHLS/skillware) on GitHub to your account (for example `rosspeili/skillware`).
2. Clone your fork locally:

   ```bash
   git clone https://github.com/<your-username>/skillware.git
   cd skillware
   ```

3. Add the upstream remote and fetch:

   ```bash
   git remote add upstream https://github.com/ARPAHLS/skillware.git
   git fetch upstream
   ```

4. Sync `main` before starting work:

   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

5. Install the project in editable mode with dev dependencies:

   ```bash
   pip install -e .[dev]
   ```

6. Create a feature branch (do this before implementation, or immediately after locking the plan):

   ```bash
   git checkout -b feat/issue-<number>-short-description
   ```

**Human checkpoint**: Confirm you are on the correct issue, branch name, and remote (`origin` = your fork).

---

## Stage 2: Analysis with a reasoning model

**Goal**: A written plan before any code changes. Use a capable reasoning model (for example Gemini 2.5 Pro, Claude Opus, or an equivalent tier in your editor).

Ask the assistant to:

1. Read [CONTRIBUTING.md](../../CONTRIBUTING.md) and, if the work touches skills, the [Skill Package Standard](../../CONTRIBUTING.md#skill-package-standard).
2. Read the specific GitHub issue (paste the URL or number).
3. Scan complementary paths likely affected (see table below).
4. Produce a structured analysis:

| Section | Content |
| :--- | :--- |
| **Problem statement** | What the issue actually requires, in your own words |
| **Acceptance criteria** | Bullet list mapped to verifiable outcomes |
| **Affected files** | Concrete paths (existing and new) |
| **Caveats** | Dependencies, tests, docs, CI, breaking changes, security |
| **Implementation options** | Up to three approaches with trade-offs |
| **Recommendation** | One preferred approach and why |
| **Out of scope** | What this issue does *not* ask for |

### Complementary paths to consider

| If the issue involves... | Also inspect |
| :--- | :--- |
| New or updated skill | `skills/<category>/<name>/`, `docs/skills/<name>.md`, `docs/skills/README.md`, `templates/python_skill/`, `tests/test_skill_issuer.py` |
| Core framework | `skillware/core/`, `tests/test_loader.py`, usage guides under `docs/usage/` |
| Documentation only | `docs/`, `README.md`, `CONTRIBUTING.md`, cross-links from other pages |
| Bug fix | Failing test or reproduction path, related skill or loader code |
| Good first issue | Often docs or small tests; read acceptance criteria literally |

Do not write implementation code in this stage unless the issue is trivial and you explicitly want a single-pass fix.

---

## Stage 3: Human review of the plan

**Goal**: Align on approach before tokens are spent on a large diff.

Review the analysis and adjust:

- Correct misunderstood requirements.
- Remove scope creep (extra skills, loader changes, version bumps).
- Pick one implementation option or merge ideas.
- Confirm category, naming, and issuer attribution for skill work.

Reply to the assistant with a short **approved plan** (you can paste it into Stage 4). Example:

> Proceed with option B. Touch only `docs/skills/README.md` and `CONTRIBUTING.md`. Do not modify `loader.py`. No version bump.

**Human checkpoint**: Do not start implementation until you are satisfied with the plan.

---

## Stage 4: Implementation with a faster model

**Goal**: Execute the approved plan with a faster or cheaper model tier once the approach is locked.

Instructions to the assistant:

- Follow the approved plan exactly.
- Match existing naming, types, and documentation tone.
- For skills: copy `templates/python_skill/` and replace placeholders with real values.
- Run formatters and tests locally as files are completed.

Suggested local commands (run from repository root):

```bash
python -m black .
python -m flake8 .
pytest tests/
```

For a single skill:

```bash
pytest skills/<category>/<skill_name>/test_skill.py
pytest tests/test_skill_issuer.py
```

**Human checkpoint**: Skim the diff for unrelated files, secrets, emojis, and placeholder text (`Your Name`, `you@example.com`, `YOUR ORG`) under `skills/`.

---

## Stage 5: Verification with a reasoning model

**Goal**: An independent pass that treats the change as complete only when tests, docs, and complementary files align with the issue.

Switch back to a reasoning model and ask for a **pre-PR audit** against:

1. GitHub issue acceptance criteria (every item addressed or explicitly deferred).
2. [Verification checklists by contribution type](#verification-checklists-by-contribution-type) below.
3. Local test and lint results (paste output or ask the assistant to run commands).
4. PR template sections: complete only what applies (skill checklist vs docs-only).

If anything fails, fix in a follow-up implementation pass (Stage 4) and re-run verification.

**Human checkpoint**: You run the final `pytest` / `flake8` commands yourself if you do not trust the model's report.

---

## Stage 6: Branch, commit, and push

**Goal**: Clean git history on your fork.

A lightweight model can help draft commit messages; you edit and execute git yourself.

```bash
git status
git add <paths>   # prefer scoped adds over blind git add -A when possible
git commit -m "Short imperative summary." -m "Optional body with context. Fixes #57"
git push -u origin feat/issue-<number>-short-description
```

Commit message guidelines:

- Imperative mood (`Add`, `Fix`, `Document`), not past tense.
- No emojis.
- Reference issues (`Fixes #57`, `Refs #12`) when appropriate.
- One logical change per commit when practical; squash locally before push if needed.

**Human checkpoint**: Confirm `git diff` contains no `.env`, credentials, or accidental large binaries.

---

## Stage 7: Pull request and CI

**Goal**: A reviewable PR against upstream `main`.

1. Open a pull request from your fork branch into `ARPAHLS/skillware` `main` (GitHub UI).
2. Use the PR template: check boxes that apply; complete the **New or updated skill** section only if `skills/` changed.
3. Wait for CI (lint and `pytest tests/`) to pass before requesting review.
4. Respond to review comments; push additional commits to the same branch.

Do not force-push to shared branches unless a maintainer asks you to.

**Human checkpoint**: PR description explains *why*, not only *what*. Link the issue.

---

## Skillware conventions for AI assistants

These rules must stay consistent with [CONTRIBUTING.md](../../CONTRIBUTING.md) and the rest of the repository.

### Style and communication

- No emojis in code, documentation, commit messages, or PR titles.
- Prefer clear, professional prose in docs (complete sentences, minimal jargon).
- Do not add verbose comments that restate obvious code.

### Skills (registry under `skills/`)

- A skill is a bundle: `manifest.yaml`, `skill.py`, `instructions.md`, `card.json`, `test_skill.py`, plus catalog docs.
- **`manifest.yaml` is the source of truth** for tool schema, constitution, requirements, `env_vars`, and `issuer`.
- **`issuer`**: `name` and `email` required; `github` and `org` optional. Real values only in `skills/` (not template placeholders).
- **`card.json`**: When present, `issuer` must match manifest `name` and `email`.
- **Catalog**: Add or update `docs/skills/<skill_name>.md` (ID, Issuer) and a row in `docs/skills/README.md`.
- **Categories**: Use an existing top-level folder under `skills/` (`compliance`, `data_engineering`, `finance`, `office`, `optimization`) or propose a new category in the issue before inventing one.
- **Version bumps**: Do not bump `pyproject.toml` or package version in skill-only PRs unless the issue or a maintainer requests it.
- **Logic**: Deterministic Python in `skill.py`; prompts and persona belong in `instructions.md`, not embedded as generated code paths.
- **Secrets**: Never commit API keys; document `env_vars` in the manifest.

### Core framework (`skillware/core/`)

- Changes affect all consumers; require a framework feature issue and tests in `tests/`.
- Do not change `loader.py` unless the issue requires it; issuer metadata is not passed into LLM tool schemas today.
- Keep adapters aligned with documented usage guides (`docs/usage/`).

### Documentation

- Fix broken relative links when you move or rename files.
- Skill docs live under `docs/skills/`; philosophy and architecture under `docs/introduction.md`.
- Testing commands belong in [TESTING.md](../TESTING.md); link rather than duplicate long command lists.

### Pull requests

- Use the [pull request template](../../.github/PULL_REQUEST_TEMPLATE.md).
- Skill-specific checklist items apply only when adding or changing files under `skills/`.
- Follow [Agent Code of Conduct](../../CODE_OF_CONDUCT.md) for deterministic, safe behavior.

---

## Verification checklists by contribution type

Use the checklist that matches your issue during Stage 5.

### New or updated skill

- [ ] Directory: `skills/<category>/<skill_name>/`
- [ ] `manifest.yaml`: `name`, `version`, `description`, `parameters`, `constitution`, `issuer` (real `name` + `email`)
- [ ] `skill.py`: deterministic, JSON-serializable returns, errors handled without crashing the agent
- [ ] `instructions.md`: when to use the tool, how to interpret output, limitations
- [ ] `card.json`: UI fields; `issuer` matches manifest
- [ ] `test_skill.py`: passes locally
- [ ] `docs/skills/<skill_name>.md` and row in `docs/skills/README.md`
- [ ] `pytest tests/test_skill_issuer.py` passes
- [ ] `SkillLoader.load_skill("<category>/<skill_name>")` succeeds (or missing deps documented)
- [ ] No template placeholders under `skills/`
- [ ] PR template skill section completed

### Documentation only

- [ ] All acceptance criteria in the issue addressed
- [ ] Links valid (especially `docs/skills/`, `CONTRIBUTING.md`, usage guides)
- [ ] Tone matches surrounding docs; no emojis
- [ ] No unrelated code changes unless required for accuracy
- [ ] PR marked as doc change; skill checklist skipped

### Core framework

- [ ] Issue approved for framework work
- [ ] Changes confined to `skillware/` and relevant `tests/`
- [ ] New or updated unit tests for behavior changes
- [ ] `pytest tests/` passes
- [ ] Usage docs updated if public API or adapter behavior changed
- [ ] No breaking changes without issue discussion

### Bug fix

- [ ] Reproduction understood and linked to issue
- [ ] Fix is minimal and targeted
- [ ] Regression test added when feasible
- [ ] `pytest` and `flake8` pass
- [ ] No unrelated refactors

### Good first issue

- [ ] Read issue labels and acceptance criteria literally
- [ ] Ask for clarification in the issue if scope is ambiguous
- [ ] Same verification as the underlying type (docs, test, or small code fix)

---

## Starter prompts

Copy and adapt these in your assistant. Replace placeholders.

### Analysis (Stage 2)

```text
You are helping me contribute to the Skillware repository (ARPAHLS/skillware).

Read CONTRIBUTING.md and docs/contributing/ai_native_workflow.md.
Read GitHub issue #<NUMBER>: <URL or paste body>.

Produce an analysis with:
1. Problem statement and acceptance criteria
2. Affected files (existing and new)
3. Caveats (tests, docs, CI, security)
4. Up to three implementation options with trade-offs
5. Recommended approach and explicit out-of-scope items

Do not write code yet.
```

### Implementation (Stage 4)

```text
Approved plan for issue #<NUMBER>:

<paste your approved plan>

Implement only what the plan describes. Match repository conventions.
After editing, tell me which commands to run for black, flake8, and pytest.
```

### Pre-PR audit (Stage 5)

```text
Pre-PR audit for issue #<NUMBER> on branch <branch-name>.

Compare the current diff to the issue acceptance criteria and the
verification checklist for <skill | docs | framework | bug> contributions.

List: missing items, unrelated files, placeholder text, emojis,
broken links, and suggested commit message (no emojis).

I will run pytest and flake8 locally; remind me of the exact commands.
```

---

## Related documents

- [CONTRIBUTING.md](../../CONTRIBUTING.md) — contribution hub and skill standard
- [TESTING.md](../TESTING.md) — Black, Flake8, Pytest
- [Agent Code of Conduct](../../CODE_OF_CONDUCT.md)
- [Pull request template](../../.github/PULL_REQUEST_TEMPLATE.md)
- [Skill library](../skills/README.md)

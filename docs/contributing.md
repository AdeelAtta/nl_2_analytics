# Contributing Guide

## Branch Naming

Branches must follow this convention:

```
<type>/<short-description>
```

| Type | Description | Example |
|------|-------------|---------|
| `feature` | New feature or enhancement | `feature/ke-schema-vector-search` |
| `fix` | Bug fix | `fix/null-pointer-in-retriever` |
| `chore` | Maintenance, tooling, config | `chore/upgrade-fastapi` |
| `docs` | Documentation | `docs/api-endpoint-docs` |
| `refactor` | Code restructuring | `refactor/query-pipeline-state` |
| `test` | Adding or updating tests | `test/integration-ke-api` |
| `perf` | Performance improvement | `perf/cache-schema-lookups` |
| `ci` | CI/CD changes | `ci/add-load-test-workflow` |
| `spike` | Research or investigation | `spike/vector-db-benchmark` |

### Examples

```
feature/schema-discovery-scheduler
fix/connection-pool-leak
chore/update-pre-commit-config
docs/development-guide
```

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Rules

- **Type**: One of `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `style`
- **Scope**: The component or service being changed (e.g., `ke`, `schema-intel`, `query-pipeline`, `api`, `frontend`, `infra`)
- **Description**: Imperative mood, lowercase, no period at end
- **Body**: Optional, explains *what* and *why* (not *how*)
- **Footer**: Optional, references issues (e.g., `Closes #123`)

### Examples

```
feat(ke): add vector search to schema store
fix(query-pipeline): handle empty result sets in executor
chore(deps): upgrade fastapi from 0.110.0 to 0.115.0
docs: update development guide with Redis troubleshooting
refactor(api): extract auth middleware into separate module
test(ke): add integration tests for schema store CRUD
```

## Pull Request Process

### 1. Before Creating a PR

- [ ] Code compiles and passes all checks (`make lint && make typecheck && make test`)
- [ ] New code has tests (unit and/or integration)
- [ ] Documentation is updated if needed
- [ ] Commit history is clean and follows conventional commits
- [ ] Branch is up to date with `main`

### 2. Creating a PR

1. Push your branch: `git push origin <branch-name>`
2. Open a PR against `main`
3. Use the PR template (automatically loaded)
4. Add appropriate labels (`epic/EP-XXX`, `service/XXX`, `priority/XXX`)
5. Request review from the relevant team(s)

### 3. PR Title Format

```
<type>(<scope>): <description>
```

Same format as commit messages. The PR title should be descriptive enough to understand the change at a glance.

### 4. During Review

- Address all review comments
- Keep the PR focused — split large changes into multiple PRs
- Do not force-push after reviewers have started reviewing (use regular commits)
- Update the PR description if scope changes

### 5. Merging

- PRs require at least one approval
- All CI checks must pass
- Use **Squash and Merge** to keep a clean history
- Delete the branch after merge

## Code Review Checklist

### General

- [ ] Does the code follow the project's coding standards?
- [ ] Is the code readable and maintainable?
- [ ] Are there appropriate comments for complex logic? (not for obvious code)
- [ ] No dead code, commented-out code, or debug artifacts
- [ ] No hardcoded secrets, URLs, or environment-specific values

### Architecture

- [ ] Does the change follow the frozen architecture?
- [ ] Does it respect service boundaries?
- [ ] Are new dependencies justified?
- [ ] Are the appropriate abstractions used?

### Testing

- [ ] Are there tests for new code?
- [ ] Do existing tests still pass?
- [ ] Are edge cases covered?
- [ ] Are integration/API tests included where appropriate?

### Performance

- [ ] Are database queries optimized (n+1 queries, missing indexes)?
- [ ] Are appropriate caching strategies used?
- [ ] Are async/await patterns used correctly?

### Security

- [ ] Is user input validated and sanitized?
- [ ] Are SQL injection and prompt injection risks handled?
- [ ] Are authentication/authorization checks in place?
- [ ] Are secrets managed properly (environment variables, not code)?

### Documentation

- [ ] Is the change reflected in relevant documentation?
- [ ] Are API changes documented (OpenAPI specs)?
- [ ] Are database schema changes documented?

## Workflow

```
main ← feature/xxx  (create feature branch from main)
  ↓
Develop and commit
  ↓
Push and create PR
  ↓
Code review
  ↓
Address feedback
  ↓
Squash and merge to main
  ↓
Deploy (CI/CD)
```

## Code of Conduct

Be respectful, inclusive, and professional. Focus on the code, not the person. Assume good intent.

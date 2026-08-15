# Portfolio Project Guidance

## Product baseline

- Build a multilingual personal portfolio with Home, Projects, CV, Blog, and a language selector.
- Allow authenticated administrators to manage Home content, projects, blog posts, navigation, translations, images, the current CV, and API access.
- Use Python 3.12, Flask, `app.py`, SQLite, SQLAlchemy, and vanilla HTML/CSS/JavaScript.
- Use an application factory, Blueprints, clear configuration, and migration-based schema changes.
- Never let multiple services write the same SQLite database file.

## Architecture reference

- Read `docs/architecture/Portfolio_Flask_Agent_Architecture_Blueprint.md`
  before planning or implementing application architecture.
- Keep implementation decisions consistent with the approved blueprint.
- If a requirement conflicts with the blueprint, report the conflict before changing the architecture.

## Agent routing

- Use `portfolio_developer` for requirements, architecture, implementation, migrations, and developer handoff.
- Use `portfolio_testing` for acceptance review, test planning/execution, security and accessibility verification, defects, and release recommendation.
- Use `portfolio_deployment_it_support` for environments, release runbooks, deployment, backups, monitoring, rollback, recovery, and incidents.
- During planning-only requests, do not write application code or mutate infrastructure.
- Avoid parallel write-heavy work. Developer owns product changes; Testing and Deployment remain read-only unless the user authorizes a new scoped task.

## Delivery gates

1. Developer must provide testable acceptance criteria and a change summary.
2. Testing must return evidence and a release recommendation.
3. Deployment may proceed only with a verified build, configuration inventory, backup, smoke tests, and rollback plan.
4. Any failed release smoke test returns to Developer through a recorded defect.
5. Production, DNS, credential, billing, destructive data, or restore actions require explicit user authorization.

## Quality rules

- Protect admin mutations with authentication, authorization, validation, CSRF defenses where applicable, secure sessions, audit events, and rate limits.
- Validate and safely store images and PDF CV uploads.
- Publish only approved content; public APIs must never expose drafts.
- Support Indonesian, English, and Japanese with an explicit fallback language.
- Include responsive design, keyboard access, visible focus, labels, alt text, semantic headings, and safe error messages.
- Keep secrets, SQLite files, uploads, backups, and runtime logs out of source control.

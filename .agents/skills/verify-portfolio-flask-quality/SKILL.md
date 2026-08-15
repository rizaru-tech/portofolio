---
name: verify-portfolio-flask-quality
description: Plan and execute risk-based QA for Rizal's multilingual Flask portfolio website using Python 3.12, SQLite, SQLAlchemy, and vanilla HTML/CSS/JavaScript. Use for acceptance criteria review, test strategy, API/UI/auth/upload/localization/accessibility/security/performance testing, regression analysis, defect reporting, release evidence, or QA handoff. Do not implement product fixes or deploy production unless the user separately authorizes that work.
---

# Portfolio Flask Quality Verification

Act as an independent QA owner. Verify observable behavior against accepted requirements and report evidence without silently repairing the product.

## Establish test scope

1. Read the requirement, architecture, API contract, data model, change summary, and developer self-check.
2. Convert every acceptance criterion into at least one positive test and one relevant negative or boundary test.
3. Identify the affected surfaces: public web, admin web, content API, identity/API access, shared UI, data migration, or deployment configuration.
4. State missing test data, environment constraints, assumptions, and exclusions.
5. Respect planning-only requests by producing test designs without executing or writing tests.

## Prioritize risks

Test the highest-impact paths first:

- unauthorized admin access or privilege escalation;
- destructive or inconsistent content updates;
- malicious image or CV uploads;
- stored and reflected cross-site scripting in rich content;
- CSRF, broken session handling, weak API keys, and rate-limit gaps;
- public leakage of drafts, private data, secrets, database files, or stack traces;
- broken language fallback or mixed-language content;
- inaccessible navigation, forms, dialogs, and language controls;
- schema migration, rollback, and SQLite concurrency failures;
- broken caching that shows stale content after an admin update.

## Cover product behavior

Verify at minimum:

1. Public Home, Projects, project detail, Blog, blog detail, CV download, and language switching.
2. Admin login/logout, session expiry, roles, dashboard, content CRUD, menu editing, draft/publish flow, CV replacement, media management, and API-key management.
3. API status codes, validation errors, pagination, filtering, language selection, authorization, idempotency where promised, and stable response shapes.
4. Data integrity for translated content, slugs, ordering, published timestamps, soft deletion, current CV, and audit events.
5. Responsive layouts, keyboard operation, visible focus, alt text, labels, heading order, color contrast, and reduced-motion behavior.
6. Browser compatibility for current Chrome, Firefox, Safari, and Edge targets agreed by the project.
7. Baseline page performance and caching for public content.

## Separate test layers

- Use unit tests for validators, permission rules, formatters, services, and language fallback.
- Use integration tests for SQLAlchemy repositories, migrations, Flask routes, authentication, upload storage, and API contracts.
- Use end-to-end tests for critical public journeys and admin publishing journeys.
- Use manual exploratory testing for content quality, responsive layout, accessibility, and recovery behavior.
- Keep test fixtures deterministic and isolated; never depend on production data.

## Report defects

For every defect, include:

- severity and user impact;
- affected environment and build;
- preconditions and minimal reproduction steps;
- expected and actual behavior;
- evidence such as logs, response bodies, screenshots, or test output;
- suspected boundary without presenting speculation as fact;
- regression-test recommendation.

Use severity consistently: Blocker prevents safe release, Critical exposes security or major data loss, High breaks a primary journey, Medium has a practical workaround, and Low is minor with limited impact.

## Give release evidence

Return a test summary containing scope, pass/fail counts, unresolved defects, accepted risks, coverage gaps, and a recommendation of `GO`, `GO WITH ACCEPTED RISK`, or `NO-GO`. Do not issue `GO` while any Blocker or Critical defect remains open. Hand deployment only the verified build identifier, required configuration, smoke-test checklist, known risks, and rollback triggers.

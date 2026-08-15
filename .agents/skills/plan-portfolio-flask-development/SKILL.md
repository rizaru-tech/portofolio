---
name: plan-portfolio-flask-development
description: Plan and implement the developer workstream for Rizal's multilingual portfolio website using Python 3.12, Flask with app.py, SQLite, SQLAlchemy, and vanilla HTML/CSS/JavaScript. Use for architecture, backlog refinement, database/API contracts, shared components, public/admin separation, content editing, localization, security, implementation, or developer handoff. Do not use as the final QA sign-off or as authorization to deploy production.
---

# Portfolio Flask Development

Act as the developer owner for the portfolio website. Keep decisions traceable to an accepted requirement and keep the design small enough for a personal portfolio.

## Establish the task

1. Read the current requirements, architecture decision record, acceptance criteria, and QA findings.
2. State assumptions before changing behavior. Use **Blog** as the confirmed feature and menu name.
3. Respect a planning-only request: produce designs and contracts without writing application code.
4. Identify the affected boundary: public web, admin web, content service, identity/API-access service, shared UI, or operations.
5. Refuse scope drift into testing sign-off or production deployment; prepare a handoff instead.

## Preserve the technical baseline

- Use Python 3.12 and `app.py` as the entry point.
- Use Flask application factories and Blueprints behind the entry point.
- Use SQLAlchemy with migrations; keep SQLite for the initial deployment.
- Use vanilla JavaScript, semantic HTML, and CSS.
- Separate public and admin frontends as independently deployable surfaces.
- Make one service the sole owner of each SQLite database file. Never let multiple services write the same SQLite file.
- Keep public content read APIs separate from authenticated write APIs.
- Store Home, Projects, Blog, navigation, translations, and CV metadata as managed content.
- Validate image and CV uploads by type, size, generated filename, and safe storage location.
- Protect admin mutations with authentication, authorization, CSRF defense where applicable, validation, audit logging, and rate limiting.

## Design for reuse

1. Reuse Jinja partials or macros for server-rendered fragments within one frontend.
2. Reuse CSS tokens, utility classes, API helpers, validators, and formatters through a versioned shared package.
3. Use native Web Components only for interactive components that genuinely need cross-frontend reuse.
4. Keep page-specific JavaScript beside its page module; keep shared utilities free of page state.
5. Define language behavior for Indonesian, English, and Japanese with a clear fallback language.

## Produce developer deliverables

Return only the deliverables relevant to the request:

- clarified functional and non-functional requirements;
- component and service boundaries;
- route, API, data, and authorization contracts;
- proposed folder map;
- implementation backlog with dependencies and acceptance criteria;
- architecture decisions and rejected alternatives;
- implementation changes and migration notes when coding is authorized;
- developer self-check results;
- handoff to QA with changed behavior, risk areas, fixtures, and known limitations.

## Apply architecture guardrails

- Prefer a modular monolith for the first release when independent deployment is not yet valuable.
- When microservices are required, start with `content-service` and `identity-access-service`; keep separate data ownership.
- Treat public web and admin web as two microfrontends that consume stable APIs.
- Avoid distributed transactions. Use explicit API calls and idempotent operations.
- Keep uploaded files outside the application source tree and serve them through a controlled media route or object storage later.
- Do not expose SQLite files, secrets, stack traces, admin routes, or unrestricted upload paths.

## Complete the handoff

Before handing work to QA, confirm that acceptance criteria are testable, migrations and seed expectations are documented, permissions are explicit, API errors are consistent, and rollback impact is known. Mark unresolved questions and never declare the release production-ready.

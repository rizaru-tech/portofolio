---
name: operate-portfolio-flask-deployment
description: Plan, release, operate, and support Rizal's Flask portfolio infrastructure using Python 3.12, SQLite, SQLAlchemy, public/admin frontends, and content/identity services. Use for environment design, deployment checklists, reverse proxy and WSGI planning, configuration, secrets, migrations, backups, observability, incident triage, rollback, disaster recovery, or IT support runbooks. Never change production, DNS, credentials, or external services without explicit user authorization.
---

# Portfolio Flask Deployment and IT Support

Act as the release and operations owner. Optimize for a small, reliable deployment with documented recovery steps. Treat production changes as controlled actions, not assumptions.

## Establish operational scope

1. Read the QA release recommendation, verified build identifier, architecture, data migration notes, configuration contract, smoke tests, and rollback triggers.
2. Confirm the target environment, hosting provider, domain plan, downtime tolerance, backup retention, and budget.
3. Respect planning-only requests by producing runbooks and diagrams without executing infrastructure actions.
4. Stop before any production, DNS, credential, billing, or destructive change unless the user has explicitly authorized that exact action.
5. Reject an unverified artifact or unresolved Blocker/Critical defect unless the user records a conscious risk acceptance.

## Design the runtime

- Run Flask behind a production WSGI server and a reverse proxy; never use the Flask development server in production.
- Route the public site, admin site, and APIs through explicit hostnames or path rules.
- Enforce HTTPS, secure headers, safe cookie settings, upload limits, and restricted admin access.
- Store secrets outside source control and provide separate values for development, staging, and production.
- Keep SQLite on persistent local storage with one owning service and one active writer process policy appropriate to the workload.
- Store uploaded images and CV files on a persistent volume; back them up together with matching database state.
- Plan a documented path from SQLite to PostgreSQL before traffic, concurrency, or multi-instance deployment requires it.

## Prepare a release

1. Record the immutable release identifier and dependency lock state.
2. Validate environment variables without printing secret values.
3. Take and verify a restorable database and media backup before migration.
4. Apply migrations once through a controlled release step, not concurrently from every application process.
5. Start or update services in dependency order.
6. Run health checks and QA-provided smoke tests for public pages, admin authentication, content publishing, language switching, CV download, and APIs.
7. Observe error rate, latency, resource use, and logs during the agreed stabilization window.
8. Complete the release record or execute the rollback when a trigger occurs.

## Define rollback and recovery

- Make rollback criteria measurable: health-check failure, migration error, elevated 5xx rate, inaccessible admin, corrupted content, or failed critical smoke test.
- Distinguish application rollback from database rollback.
- Never restore an old database over newer production data without explicit authorization and a data-loss assessment.
- Test backup restoration in a non-production environment on a schedule.
- Document recovery time and recovery point objectives appropriate to a personal portfolio.

## Operate and support

Monitor availability, TLS expiry, disk capacity, backup success, error rate, response latency, failed logins, suspicious API use, and service restarts. Use structured logs with request identifiers while excluding passwords, tokens, cookies, CV contents, and other sensitive data.

For an incident:

1. Classify severity and user impact.
2. Preserve evidence and timestamps.
3. Stabilize service with the least destructive reversible action.
4. Escalate application defects to Developer and reproducible regressions to QA.
5. Communicate current impact, workaround, owner, and next update.
6. Record root cause, corrective action, and prevention after recovery.

## Produce operational deliverables

Return the relevant environment matrix, deployment diagram, configuration inventory, release checklist, backup/restore runbook, rollback plan, smoke-test record, monitoring checklist, access-control matrix, incident report, and handoff notes. Never claim success without health and smoke-test evidence.

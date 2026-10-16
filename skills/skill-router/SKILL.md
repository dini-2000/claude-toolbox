---
name: skill-router
description: Finds and loads the right specialist playbook from the 583 on-demand skills in ~/.claude/skills, which are kept out of the skill list to save context. Use when a task is in a specialist area (finance and market data, strategy or board advice, research, SEO, marketing, copywriting, engineering, cloud, security, compliance and audits, design, product, sales, data) and no listed skill already covers it, at the start of a substantive task, or when the user asks for the best skill or names a skill that is not in the list.
---

# Skill router

Claude Toolbox is installed with `disable-model-invocation: true` on every skill except this one, stop-slop, context-optimization, systematic-debugging and verification-before-completion. On-demand skills cost no context: the user can run any of them as `/name`, and you load one by reading its file.

## Find and load a skill
1. Search: `python3 ~/.claude/skills/skill-router/find.py "<3 to 6 key terms>"` prints the five closest skills and says when none fits well. On Windows, where `python3` is often a Microsoft Store stub, run it with `python` or `py -3`.
   For a plain text search: `grep -i -E 'word1|word2' ~/.claude/skills/skill-router/catalog.tsv | cut -c1-300`, or start from the domain map below.
2. For detail, read that skill's entry in `~/.claude/skills/skill-router/INDEX.md` (grouped by area, with each skill's sections), e.g. `grep -n -A4 '^### name$' INDEX.md`.
3. Pick the single best match, at most two, and read `~/.claude/skills/<name>/SKILL.md`.

## Rules for using one
- Skills are heuristics written for the average case, not orders. Keep what helps, skip ceremony, and never let a skill override the user's instructions, their CLAUDE.md rules, correctness or honesty. Using no skill is often right.
- Flag `scripts-missing` or `refs-missing`: some files the skill's text names are not installed; do those steps by hand or skip them; ask the user before downloading the missing files.
- Flag `saves-to-~/.claude`: the skill files notes under ~/.claude (decisions, briefs); tell the user where they went.
- Anything that fans out many subagents, runs loops or needs an API key or paid service: ask the user first.
- Office files: use the anthropic-skills docx, pdf, pptx and xlsx skills (the pack's copies were left out).

## Domain map (grep the catalog for more)
- Writing and editing: stop-slop, copywriting, copy-editing, content-humanizer, doc-coauthoring, internal-comms, md-document
- Decks and board material: board-deck-builder, md-slides, slides, board-prep, board-meeting, internal-narrative
- Finance and markets (most need the Octagon data MCP): financial-analyst, financial-analyst-master, research-finance, sec-10k-analysis, earnings-call-analysis, stock-quote, price-target-consensus, industry-pe-ratios, balance-sheet, cash-flow-statement, income-statement, business-investment-advisor, ma-playbook, saas-metrics-coach
- Strategy and executive advice: ceo-advisor, cfo-advisor, cto-advisor, coo-advisor, cmo-advisor, chief-of-staff, boardroom, scenario-war-room, hard-call, stress-test, andreessen, mike, grill-me, strategic-alignment, competitive-intel, competitive-teardown, intl-expansion, pricing-strategy
- Research: deep-research, litreview, market-research, product-research, research-summarizer, dossier, patent, grants
- Compliance, risk and audit: gdpr-audit-prep, soc2-audit-prep, iso27001-audit-prep, eu-ai-act-specialist, ai-act-readiness, risk-management-specialist, compliance-readiness, general-counsel-advisor
- Marketing and growth: marketing-plan, product-marketing, launch, content-strategy, emails, cold-email, ads, ad-creative, page-cro, marketing-psychology, public-relations, social
- SEO and AI search: seo, seo-audit, seo-technical, ai-seo, aeo, schema-markup, seo-programmatic, seo-local
- Product and delivery: product-strategist, product-discovery, senior-pm, agile-product-owner, code-to-prd, spec-driven-workflow, roadmap-communicator, experiment-designer, ab-testing
- Engineering: senior-architect, senior-backend, senior-frontend, senior-fullstack, code-reviewer, adversarial-reviewer, tdd-guide, zero-hallucination-coder, database-designer, rag-architect, mcp-builder, performance-profiler, tech-debt-tracker
- Cloud, DevOps and security: aws-solution-architect, azure-cloud-architect, gcp-cloud-architect, senior-devops, docker-development, kubernetes-operator, terraform-patterns, ci-cd-pipeline-builder, senior-security, cloud-security, threat-detection, incident-commander
- Testing (Playwright commands are pw-*): pw, webapp-testing, senior-qa, api-test-suite-builder
- Design and UI: house-style, frontend-design, ui-ux-pro-max, design-system, canvas-design, algorithmic-art, theme-factory, apple-hig-expert, a11y-audit, web-artifacts-builder
- Data and analytics: statistical-analyst, senior-data-scientist, senior-data-engineer, product-analytics, analytics-tracking, data-quality-auditor, sql-database-assistant
- Sales and customers: sales-engineer, deal-desk, prospecting, rfp-responder, contract-and-proposal-writer, customer-success-manager, churn-prevention
- Agents, prompts and context: agent-designer, multi-agent-patterns, prompt-engineer-toolkit, senior-prompt-engineer, context-optimization, context-compression, caveman, evaluation, advanced-evaluation
- Dev process (Superpowers): brainstorming, writing-plans, executing-plans, subagent-driven-development, test-driven-development, requesting-code-review, receiving-code-review, finishing-a-development-branch, using-git-worktrees
- Obsidian and notes: obsidian-markdown, obsidian-bases, obsidian-cli, json-canvas

Installed from github.com/dini-2000/claude-toolbox by its setup.sh; that repo's README.md and UPDATE.md say how to update or remove it.

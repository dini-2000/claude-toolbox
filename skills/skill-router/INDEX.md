# Skills index

589 skills from Claude Toolbox, grouped by area. `auto` skills are in Claude's skill list; the rest load on demand: read `~/.claude/skills/<name>/SKILL.md`, or the user runs `/<name>`.

Flags: `scripts-missing` = calls a script that was not shipped (do that step by hand or skip it); `refs-missing` = points to reference docs that were not shipped; `saves-to-~/.claude` = files notes under ~/.claude.

## Contents
- Executive, board and strategy (82)
- Finance and markets (115)
- Compliance, risk, legal and quality (52)
- SEO and AI search (28)
- Sales and customers (16)
- Marketing, growth and copy (55)
- Product and project management (37)
- Research and analysis (15)
- Writing, docs and presentations (36)
- Design, UI and media (30)
- Testing and QA (28)
- Cloud, DevOps and security (26)
- AI agents, prompts and context (56)
- Engineering and code (10)

## Executive, board and strategy

### agent-decision-receipts
Mint a tamper-evident, post-quantum-signed receipt for a consequential agent action (deploy, delete, pay, grant-access, model decision) so it can be verified later from the certificate alone. Use when an autonomous agent takes a side-effecting action that may need to be proven later, or when satisfying EU AI Act Article 12 record-keeping. Three decisions: whether an action needs a receipt, minting it, verifying it. Signing is delegated to the open-source OpenAgentOntology package. Not after-the-fact log analysis; not a hosted notary; not a legal opinion.
Sections: Overview; Quick Start; Core Workflow; Decision 1: Does this action need a receipt?; Decision 2: Mint the receipt; Decision 3: Verify it; Anti-Patterns; Cross-References

### andreessen
Marc Andreessen-mode decision and productivity skill. A blunt, market-first operator that pressure-tests ideas, ventures, features, and career bets through Andreessen's actual frameworks — market dominates team and product; the only milestone that matters is product/market fit; bias to build over deliberate. Use when the user says 'andreessen', 'pmarca mode', 'should I build this', 'is there a market', 'are we at product/market fit', 'pmf check', 'pressure-test this idea', 'be brutal about this venture', 'market-first take', or wants a no-disclaimers, no-hedging, confidence-leveled verdict on whether something is worth pursuing. Also provides the 3x5-card + Anti-Todo personal productivity routine. Runs on a fixed anti-sycophancy operating prompt: leads with the strongest counterargument, never validates premises, uses explicit confidence levels, never apologizes for disagreeing. Not for polite brainstorming — this skill exists to tell you the market is dead when it is.
Sections: The Operating Prompt (non-negotiable voice); The Andreessen Lens (what the skill actually believes); Workflow; Tooling; References; Assets; Hard Rules; Anti-Patterns To Reject

### board-deck-builder
Assembles comprehensive board and investor update decks by pulling perspectives from all C-suite roles. Use when preparing board meetings, investor updates, quarterly business reviews, or fundraising narratives. Covers structure, narrative framework, bad news delivery, and common mistakes.
Sections: Keywords; Quick Start; Deck Structure (Standard Order); Narrative Framework; Delivering Bad News; Common Board Deck Mistakes; Cadence Notes; References

### board-meeting
Flags: saves-to-~/.claude
Multi-agent board meeting protocol for strategic decisions. Runs a structured 6-phase deliberation: context loading, independent C-suite contributions (isolated, no cross-pollination), critic analysis, synthesis, founder review, and decision extraction. Use when the user invokes /boardroom, calls a board meeting, or wants structured multi-perspective executive deliberation on a strategic question.
Sections: Keywords; Invoke; The 6-Phase Protocol; ROLE — DATE; Memory Structure; Failure Mode Quick Reference; References

### board-prep
Board meeting preparation for the adversarial scenario, not the friendly one. Forces numbers-cold mastery, anticipates hard questions, builds a narrative that acknowledges weakness without losing the room. Use when preparing for a board meeting, an investor update, fundraising presentation, or any high-stakes adversarial review where every number must live in your head not just on a slide.
Sections: The Reality of Board Meetings; The Preparation Framework; Pre-Meeting Checklist; During the Meeting; After the Meeting

### boardroom
Flags: saves-to-~/.claude
/boardroom <brief> — 6-phase multi-role deliberation across the C-suite with Phase 2 isolation, critic pre-screen, and synthesis. Outputs a board memo. Use when a decision spans multiple executive domains — e.g. a pricing change touching finance, positioning, and product, or a raise-vs-cut runway call.
Sections: Pipeline Position; The 6 Phases (from board-meeting skill); Output: Board Memo; Question; Recommended Option; Vote Tally; Dissent; Devil's Advocate Concerns; Success & Kill Criteria; Recommended Decision Path

### brief
Flags: saves-to-~/.claude
/brief <topic> — Generate a one-page strategy brief from an office-hours intake. First step in the strategic sprint pipeline. Use when a strategic question needs to be framed before boardroom deliberation — e.g. locking options, assumptions, and success criteria for a pricing change or a market-entry decision.
Sections: Pipeline Position; Inputs; Output; Context; Question; Options; Assumptions; Constraints; Affected Roles; Success Criteria

### c-level-agents
Founder-mode executive team. 13 cs-* C-suite agents (CFO, CMO, CRO, CPO, COO, CHRO, CISO, GC, CDO, CAIO, CCO, VPE, Chief of Staff) and 21 /cs:* slash commands for forcing-question office hours, multi-role boardroom deliberation, strategic sprint pipeline, and meta routing. Use when the founder needs a virtual executive team, when invoking /cs:* commands, or when orchestrating multi-role decisions.
Sections: Keywords; What This Plugin Provides; Quick Start; Architecture; Integration Points; Design Principles; References

### c-level-skills
Flags: saves-to-~/.claude
Index and router for the C-level advisory bundle: 33 skills covering 14 C-suite roles, orchestration, cross-cutting capabilities, and culture. Use when exploring what the c-level-advisor bundle contains, deciding which advisor skill fits a question, or finding the entry points (cs-onboard interview, chief-of-staff routing, board-meeting protocol).
Sections: Start Here; What's in the Bundle (33 skills); Routing Quick Reference; Related Layers

### caio-review
/caio-review <plan> — Eval-demanding Chief AI Officer interrogation of any plan that involves AI: model selection, risk classification, cost economics, or AI hiring. Use when shipping an AI feature without an eval set, choosing between API, fine-tune, and self-hosted, or classifying a use case under the EU AI Act.
Sections: When to Run; The Six CAIO Questions; Workflow; Output Format; The Decision Being Made; Eval Discipline; Model Selection (if applicable); Risk Classification (if applicable); Cost Economics (if applicable); Org (if applicable)

### cco-review
/cco-review <plan> — Retention-obsessed Chief Customer Officer interrogation of any plan that touches customer retention, segmentation, CS team sizing, or CS team hiring. Use when gross retention is slipping, before approving CSM headcount, or when deciding which customer segments to keep or fire.
Sections: When to Run; The Six CCO Questions; Workflow; Output Format; The Decision Being Made; Retention (if applicable); Segmentation (if applicable); Coverage (if applicable); Org (if applicable); Verdict

### cdo-review
/cdo-review <plan> — Decision-driven Chief Data Officer interrogation of any plan that touches training data, data architecture, data productization, or data team hiring. Use when validating training-data rights before model work, choosing warehouse vs lakehouse vs mesh, or valuing data assets for productization or M&A.
Sections: When to Run; The Six CDO Questions; Workflow; Output Format; The Decision Being Made; Training Audit (if applicable); Architecture (if applicable); Asset Value (if applicable); Org (if applicable); Verdict

### ceo-advisor
Executive leadership guidance for strategic decision-making, organizational development, and stakeholder management. Use when planning strategy, preparing board presentations, managing investors, developing organizational culture, making executive decisions, fundraising, or when user mentions CEO, strategic planning, board meetings, investor updates, organizational leadership, or executive strategy.
Sections: Keywords; Quick Start; Core Responsibilities; Key Questions a CEO Asks; CEO Metrics Dashboard; Red Flags; Integration with C-Suite Roles; Proactive Triggers; Output Artifacts; Reasoning Technique: Tree of Thought

### cfo-advisor
Financial leadership for startups and scaling companies. Financial modeling, unit economics, fundraising strategy, cash management, and board financial packages. Use when building financial models, analyzing unit economics, planning fundraising, managing cash runway, preparing board materials, or when user mentions CFO, burn rate, runway, fundraising, unit economics, LTV, CAC, term sheets, or financial strategy.
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; CFO Metrics Dashboard; Red Flags; Integration with Other C-Suite Roles; Resources; Proactive Triggers; Output Artifacts

### cfo-review
/cfo-review <plan> — Numerate-skeptic interrogation of any plan that touches money. Unit economics, runway, dilution, capital allocation. Use when a plan commits meaningful spend — e.g. a hiring wave, a fundraise decision, or a new channel budget.
Sections: When to Run; The Six CFO Questions; Workflow; Output Format; Numbers; Verdict; Conditions (if YELLOW); Recommendation; Routing; Related

### challenge
Pre-mortem plan analysis. Imagine the plan failed 12 months from now and work backwards to find the weaknesses. Surfaces assumptions, dependencies, and execution risks before committing resources. Use when before significant resource commitment, before presenting to a board or investors, when feedback has been one-sidedly positive, or when there is pressure to move fast and figure it out later.
Sections: The Core Idea; When to Run a Challenge; The Challenge Framework; Output Format; Challenge Patterns by Plan Type; The Hardest Questions; Deliverable

### chief-ai-officer-advisor
Chief AI Officer advisory for startups: model build-vs-buy decisions (API vs fine-tune vs in-house), AI risk classification under EU AI Act + US state patchwork, AI cost economics (API-to-self-hosted breakeven), and AI team org evolution. Use when deciding whether to call an API or fine-tune, classifying AI use cases for regulatory risk, calculating when self-hosting pays off, sequencing AI hires, or when user mentions CAIO, AI strategy, model selection, foundation model, fine-tuning, EU AI Act, NIST AI RMF, AI governance, model risk, or AI economics. Strategic only — does not duplicate engineering AI/ML skills.
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standards; Adjacent Skills; References

### chief-customer-officer-advisor
Chief Customer Officer advisory for startups: retention decomposition (gross retention vs NRR honesty, churn root-cause taxonomy), customer segmentation strategy (differential investment across tiers + ICP fit scoring), CS team coverage model (pooled vs named CSM thresholds + ratio math), and CS team org evolution (CS vs Support vs AM distinctions). Use when designing retention strategy, segmenting customers for differential investment, sizing CS team, or sequencing CS hires. Strategic only — does not duplicate engineering/business-growth tactical skills.
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standards; Adjacent Skills; References

### chief-data-officer-advisor
Chief Data Officer advisory for startups: AI training data rights and consent provenance, data product strategy (warehouse vs lakehouse vs mesh, build-vs-buy), B2B customer-data-as-asset valuation and M&A readiness, data team org evolution. Use when deciding whether to train models on customer data, choosing data architecture, valuing data for fundraising or M&A, sequencing data hires, or when user mentions CDO, chief data officer, data strategy, data mesh, lakehouse, training data, data product, data monetization, or customer data asset. NOT a tactical data engineering skill — strategic decisions only.
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standards (when invoked via cs-cdo-advisor); Adjacent Skills; References

### chief-of-staff
Flags: saves-to-~/.claude
C-suite orchestration layer. Routes founder questions to the right advisor role(s), triggers multi-role board meetings for complex decisions, synthesizes outputs, and tracks decisions. Every C-suite interaction starts here. Loads company context automatically. Use when a founder question needs routing to the right advisor — e.g. 'should we raise now or cut burn?' — or when a multi-domain decision needs a board meeting convened.
Sections: Keywords; Session Protocol (Every Interaction); Invocation Syntax; Decision Complexity Scoring; Routing Matrix (Summary); Board Meeting Protocol; Synthesis (Quick Reference); What We Agree On; The Disagreement; Recommended Actions

### chro-advisor
People leadership for scaling companies. Hiring strategy, compensation design, org structure, culture, and retention. Use when building hiring plans, designing comp frameworks, restructuring teams, managing performance, building culture, or when user mentions CHRO, HR, people strategy, talent, headcount, compensation, org design, retention, or performance management.
Sections: Keywords; Quick Start; Core Responsibilities; Key Questions a CHRO Asks; People Metrics; Red Flags; Integration with Other C-Suite Roles; Detailed References; Proactive Triggers; Output Artifacts

### chrome-mcp-troubleshooting
Diagnose and fix Claude in Chrome MCP extension connectivity issues. Use when mcp__claude-in-chrome__* tools fail, return "Browser extension is not connected", or behave erratically.
Sections: When to Use; When NOT to Use; The Claude.app vs Claude Code Conflict (Primary Issue); Quick Diagnosis; Critical Insight; Full Reset Procedure (Claude Code CLI); Other Common Causes; Diagnostic Deep Dive; File Reference; Summary

### ciso-advisor
Security leadership for growth-stage companies. Risk quantification in dollars, compliance roadmap (SOC 2/ISO 27001/HIPAA/GDPR), security architecture strategy, incident response leadership, and board-level security reporting. Use when building security programs, justifying security budget, selecting compliance frameworks, managing incidents, assessing vendor risk, or when user mentions CISO, security strategy, compliance roadmap, zero trust, or board security reporting.
Sections: Keywords; Quick Start; Core Responsibilities; Key Questions a CISO Asks; Security Metrics; Red Flags; Integration with Other C-Suite Roles; Detailed References; Proactive Triggers; Output Artifacts

### ciso-review
/ciso-review <plan> — Risk-paranoid interrogation of any plan that touches data, compliance, or production access. Use when launching features that handle customer data, before a SOC 2 / ISO audit, or after any incident or near-miss.
Sections: When to Run; The Six CISO Questions; Workflow; Output Format; Threat Model; Blast Radius; Detection; Response; Regulatory; Vendors

### cmo-advisor
Marketing leadership for scaling companies. Brand positioning, growth model design, marketing budget allocation, and marketing org design. Use when designing brand strategy, selecting growth models (PLG vs sales-led vs community-led), allocating marketing budgets, building marketing teams, or when user mentions CMO, brand strategy, growth model, CAC, LTV, channel mix, or marketing ROI.
Sections: Keywords; Quick Start; The Four CMO Questions; Core Responsibilities (Brief); Key Diagnostic Questions; CMO Metrics Dashboard; Red Flags; Integration with Other C-Suite Roles; Resources; Proactive Triggers

### cmo-review
/cmo-review <plan> — Narrative-first interrogation of positioning, ICP, message house, and channel mix. Use when launching a campaign or repositioning, or when CAC is rising and the one-sentence positioning test fails.
Sections: When to Run; The Six CMO Questions; Workflow; Output Format; Positioning; ICP; Channel Mix; Verdict; Next Steps; Routing

### commercial-forecaster
Use when building a quarterly bookings forecast, ARR projection, pipeline forecast, NRR projection, or commit/best-case/pipe-only board number — especially when the CRO needs to walk the board through funnel math + cohort ARR + per-stage conversion assumptions without the theatre of a single undefended number. Decomposes pipeline into commit, best-case, and pipe-only tiers; projects cohort-level NRR/GRR to surface leaky cohorts before they show up in the consolidated number; scores per-stage funnel confidence so soft-floor stages get treated differently from high-confidence ones. Every output explicitly names the conversion rate used, the data window, and the weighting choice. For Head of Commercial, RevOps, VP Sales, and CRO at quarterly forecast or board prep. NOT financial close (see finance/financial-analysis). NOT strategic CRO hiring/territory (see c-level-advisor/cro-advisor). NOT pricing (see sibling pricing-strategist).
Sections: Purpose; When to use; Workflow; Scripts; References; Assumptions; Anti-patterns; Distinct from; Forcing-question library (Matt Pocock grill discipline)

### commercial-policy
Use when designing or revising a company's commercial policy — the rules of engagement governing discounts off list price, approver thresholds, exception flows, and the deal framework that Deal Desk and AEs operate under. Covers discount matrix design (ARR band x term length x payment terms x strategic value), commercial policy design, exception policy, discount governance, approval thresholds, deal framework structure, and policy linting (contradictions, gaps, cliff edges, gaming surfaces). For Head of Commercial, Head of Deal Desk, VP Sales, or RevOps at the policy-design moment — NOT per-deal application (that is deal-desk) and NOT pricing model selection (that is pricing-strategist).
Sections: Purpose; When to use; Workflow; Scripts; References; Assumptions; Anti-patterns; Distinct from; Forcing-question library (Matt Pocock grill discipline); Quick examples

### company-os
The meta-framework for how a company runs — the connective tissue between all C-suite roles. Covers operating system selection (EOS, Scaling Up, OKR-native, hybrid), accountability charts, scorecards, meeting pulse, issue resolution, and 90-day rocks. Use when setting up company operations, selecting a management framework, designing meeting rhythms, building accountability systems, implementing OKRs, or when user mentions EOS, Scaling Up, operating system, L10 meetings, rocks, scorecard, accountability chart, or quarterly planning.
Sections: Keywords; Why This Matters; The Six Core Components; Operating System Selection; Implementation Roadmap; Common Failure Modes; Integration with C-Suite; Key Questions for the Operating System; Detailed References

### competitive-intel
Systematic competitor tracking that feeds CMO positioning, CRO battlecards, and CPO roadmap decisions. Use when analyzing competitors, building sales battlecards, tracking market moves, positioning against alternatives, or when user mentions competitive intelligence, competitive analysis, competitor research, battlecards, win/loss, or market positioning.
Sections: Keywords; Quick Start; Framework: 5-Layer Intelligence System; Win/Loss Analysis; The Balance: Intelligence Without Obsession; Distributing Intelligence; Red Flags in Competitive Intelligence; Integration with C-Suite Roles; References

### competitive-teardown
Analyzes competitor products and companies by synthesizing data from pricing pages, app store reviews, job postings, SEO signals, and social media into structured competitive intelligence. Produces feature comparison matrices scored across 12 dimensions, SWOT analyses, positioning maps, UX audits, pricing model breakdowns, action item roadmaps, and stakeholder presentation templates. Use when conducting competitor analysis, comparing products against competitors, researching the competitive landscape, building battle cards for sales, preparing for a product strategy or roadmap session, responding to a competitor's new feature or pricing change, or performing a quarterly competitive review.
Sections: When to Use; Teardown Workflow; Data Collection Guide; Scoring Rubric (12 Dimensions, 1-5); Templates; Related Skills

### content-strategy
When the user wants to plan a content strategy, decide what content to create, or figure out what topics to cover. Also use when the user mentions "content strategy," "what should I write about," "content ideas," "blog strategy," "topic clusters," "content planning," "editorial calendar," "content marketing," "content roadmap," "what content should I create," "blog topics," "content pillars," or "I don't know what to write." Use this whenever someone needs help deciding what content to produce, not just writing it. For writing individual pieces, see copywriting. For SEO-specific audits, see seo-audit. For social media content specifically, see social.
Sections: Before Planning; Searchable vs Shareable; Content Types; Content Pillars and Topic Clusters; Keyword Research by Buyer Stage; Content Ideation Sources; Prioritizing Content Ideas; Output Format; Task-Specific Questions; References

### coo-advisor
Operations leadership for scaling companies. Process design, OKR execution, operational cadence, and scaling playbooks. Use when designing operations, setting up OKRs, building processes, scaling teams, analyzing bottlenecks, planning operational cadence, or when user mentions COO, operations, process improvement, OKRs, scaling, operational efficiency, or execution.
Sections: Keywords; Quick Start; Core Responsibilities; Key Questions a COO Asks; Operational Metrics; Red Flags; Integration with Other C-Suite Roles; Detailed References; Proactive Triggers; Output Artifacts

### cpo-advisor
Product leadership for scaling companies. Product vision, portfolio strategy, product-market fit, and product org design. Use when setting product vision, managing a product portfolio, measuring PMF, designing product teams, prioritizing at the portfolio level, reporting to the board on product, or when user mentions CPO, product strategy, product-market fit, product organization, portfolio prioritization, or roadmap strategy.
Sections: Keywords; Quick Start; The CPO's Core Responsibilities; Diagnostic Questions; Product Metrics Hierarchy; Investment Postures; Red Flags; Integration with Other C-Suite Roles; Resources; Proactive Triggers

### cpo-review
/cpo-review <plan> — JTBD-driven interrogation of product roadmap, PMF signal, and portfolio focus. Use when committing a quarter's roadmap, deciding whether to kill a feature, or claiming PMF without a retention curve.
Sections: When to Run; The Six CPO Questions; Workflow; Output Format; JTBD; North Star Link; PMF Signal; Score; Cut List; Kill Criteria (90 days)

### cro-advisor
Revenue leadership for B2B SaaS companies. Revenue forecasting, sales model design, pricing strategy, net revenue retention, and sales team scaling. Use when designing the revenue engine, setting quotas, modeling NRR, evaluating pricing, building board forecasts, or when user mentions CRO, chief revenue officer, revenue strategy, sales model, ARR growth, NRR, expansion revenue, churn, pricing strategy, or sales capacity.
Sections: Keywords; Quick Start; Diagnostic Questions; Core Responsibilities (Overview); Revenue Metrics; Red Flags; Integration with Other C-Suite Roles; Resources; Proactive Triggers; Output Artifacts

### cro-review
/cro-review <plan> — Pipeline-paranoid interrogation of revenue, win rate, NRR, and ramp time. Use when the forecast misses pipeline coverage, win rates drop, or before scaling the sales team.
Sections: When to Run; The Six CRO Questions; Workflow; Output Format; Pipeline; Retention; Ramp; Discount; Source Mix; Verdict

### cto-advisor
Technical leadership guidance for engineering teams, architecture decisions, and technology strategy. Use when assessing technical debt, scaling engineering teams, evaluating technologies, making architecture decisions, establishing engineering metrics, or when user mentions CTO, tech debt, technical debt, team scaling, architecture decisions, technology evaluation, engineering metrics, DORA metrics, or technology strategy.
Sections: Keywords; Quick Start; Core Responsibilities; Workflows; Key Questions a CTO Asks; CTO Metrics Dashboard; Red Flags; Integration with C-Suite Roles; Proactive Triggers; Output Artifacts

### cto-review
/cto-review <plan> — Architecture and scaling interrogation. Tech debt, scaling cliffs, team scaling, build-vs-buy. Use when committing to an architecture, planning for 10x load, or weighing a rebuild against a vendor.
Sections: When to Run; The Six CTO Questions; Workflow; Output Format; Scaling Cliff; Tech Debt; Team; Build vs Buy; Reliability; Security

### culture-architect
Build, measure, and evolve company culture as operational behavior — not wall posters. Covers mission/vision/values workshops, values-to-behaviors translation, culture code creation, culture health assessment, and cultural rituals by stage. Use when building company values, assessing culture health, designing cultural rituals, creating culture codes, handling culture clashes, or when user mentions culture, values, culture debt, founder culture, or culture code.
Sections: Keywords; Core Principle; Frameworks; Culture Integration with C-Suite; Key Questions a Culture Architect Asks; Red Flags; Detailed References

### decide
Flags: saves-to-~/.claude
/decide <memo> — Log a decision to two-layer memory via decision-logger. Approved memo becomes durable; raw transcripts kept for reference. Use when the founder has approved a boardroom memo and the decision must become durable company memory — e.g. right after /boardroom concludes.
Sections: Pipeline Position; Two-Layer Memory Model; Input; Workflow; Output Record Format; Decision; Success Criteria (binding); Kill Criteria (binding); Preserved Dissent; Next Action

### decision-logger
Flags: saves-to-~/.claude
Two-layer memory architecture for board meeting decisions. Manages raw transcripts (Layer 1) and approved decisions (Layer 2). Use when logging decisions after a board meeting, reviewing past decisions with /cs:decisions, or checking overdue action items with /cs:review. Invoked automatically by the board-meeting skill after Phase 5 founder approval.
Sections: Keywords; Quick Start; Commands; Two-Layer Architecture; Decision Entry Format; YYYY-MM-DD — AGENDA ITEM TITLE; Conflict Detection; Logging Workflow (Post Phase 5); Marking Actions Complete; File Structure

### doubt-driven-development
Subjects every non-trivial decision to a fresh-context adversarial review before it stands. Use when you want every assumption cross-examined before proceeding, when stress-testing a plan for hidden failure modes, when correctness matters more than speed, when working in unfamiliar code, when stakes are high (production auth, security-sensitive logic, a high-stakes migration, irreversible operations), or any time a confident output would be cheaper to verify now than to debug later.
Sections: Overview; When to Use; Loading Constraints; The Process; Common Rationalizations; Red Flags; Interaction with Other Skills; Verification

### execute
Flags: saves-to-~/.claude
/execute <decision> — Generate a 90-day execution plan with weekly milestones, DRIs, and check-in cadence from an approved decision. Use when a logged decision needs to become an operating plan — e.g. turning an approved market-entry call into weekly milestones with DRIs.
Sections: Pipeline Position; Input; Output Plan Format; Outcome (binding); Workstreams; Weekly Milestones; Cadence; Dependencies; Risk Register; Kill Criteria Watch

### executive-mentor
Adversarial thinking partner for founders and executives. Stress-tests plans, prepares for brutal board meetings, dissects decisions with no good options, and forces honest post-mortems. Use when you need someone to find the holes before the board does, make a decision you've been avoiding, or understand what actually went wrong.
Sections: The Difference; Keywords; Commands; Quick Start; Voice; When to Use This; Commands in Detail; Agents & References; What This Isn't; Proactive Triggers

### finishing-a-development-branch
Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup
Sections: Overview; The Process; Quick Reference; Common Mistakes; Red Flags

### founder-coach
Personal leadership development for founders and first-time CEOs. Covers founder archetype identification, delegation frameworks, energy management, CEO calendar audits, leadership style evolution, blind spot identification, imposter syndrome, founder mental health, and succession planning. Use when a founder feels like the bottleneck, struggles to delegate, is burning out, transitioning from IC to executive, managing a board, or when user mentions founder mode, CEO growth, leadership development, delegation, burnout, or imposter syndrome.
Sections: Keywords; Core Truth; 1. Founder Archetype Identification; 2. Delegation Framework; 3. Energy Management; 4. CEO Calendar Audit; 5. Leadership Style Evolution; 6. Blind Spot Identification; 7. Imposter Syndrome Toolkit; 8. Founder Mental Health

### founder-mode
Flags: saves-to-~/.claude
/founder-mode <question> — Auto-routes any founder question to the right C-role advisor or to /boardroom for multi-role topics. The single-command entry point. Use when a founder asks any strategic question without knowing which advisor or command fits — e.g. 'runway pressure' routes to the CFO, 'gross retention dropped' routes to the CCO.
Sections: Routing Logic; Workflow; Output; Why This Is the Killer Command; Examples; Related

### free-tool-strategy
When the user wants to build a free tool for marketing — lead generation, SEO value, or brand awareness. Use when they mention 'engineering as marketing,' 'free tool,' 'calculator,' 'generator,' 'checker,' 'grader,' 'marketing tool,' 'lead gen tool,' 'build something for traffic,' 'interactive tool,' or 'free resource.' Covers idea evaluation, tool design, and launch strategy. For pure SEO content strategy (no tool), use seo-audit or content-strategy instead.
Sections: Before Starting; How This Skill Works; Tool Types and When to Use Each; The 6-Factor Evaluation Framework; Design Principles; Lead Capture — When, What, How; SEO Strategy for Free Tools; Measurement; Proactive Triggers; Output Artifacts

### freeze
Flags: saves-to-~/.claude
/freeze <decision> <days> — Lock a strategic decision for a cooldown period to prevent impulse reversal. Mirrors gstack's safety primitives for the business layer. Use when an irreversible decision was made under pressure — e.g. a layoff plan or multi-year contract — and deserves a cooling-off lock before execution.
Sections: When to Use; Default Freeze Periods; Workflow; Output; Override; Auto-Override; Why This Beats "Just Don't Re-Decide"; Routing; Related

### git-worktree-manager
Run parallel feature work safely with Git worktrees. Standardizes branch isolation, port allocation, environment sync, and cleanup so each worktree behaves like an independent local app. Optimized for multi-agent workflows where each agent or terminal session owns one worktree. Use when running multiple feature branches simultaneously, isolating experimental work, or coordinating multi-agent development across the same repo.
Sections: Overview; Core Capabilities; When to Use; Key Workflows; Script Interfaces; Common Pitfalls; Best Practices; Validation Checklist; References; Decision Matrix

### grill-me
Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
Sections: Rules (preserved + amplified); Workflow; Output Pattern; Tooling

### grill-with-docs
Docs-anchored grilling session — challenges a plan against the project's existing language (CONTEXT.md) and recorded decisions (docs/adr/), and updates those files inline as terminology and decisions crystallise. Use when user wants to stress-test a plan against documented domain language, or mentions "grill with docs".
Sections: Domain awareness; During the session; Wrapper Additions

### guidelines-advisor
Smart contract development advisor based on Trail of Bits' best practices. Analyzes codebase to generate documentation/specifications, review architecture, check upgradeability patterns, assess implementation quality, identify pitfalls, review dependencies, and evaluate testing. Use when asking whether a smart contract project follows development best practices, reviewing on-chain/off-chain split, upgradeability, or delegatecall proxy patterns against guidelines, or seeking recommendations on contract design, inheritance, events, documentation, dependencies, or test strategy.
Sections: Purpose; How This Works; Assessment Areas; Example Output; Deliverables; Assessment Process; Rationalizations (Do Not Skip); Notes; Ready to Begin

### hard-call
/em:hard-call — Framework for decisions with no good options. Use when every option is painful and a structured 10/10/10 + regret-minimization pass is needed — e.g. choosing between a layoff and a down round, or killing a beloved product line.
Sections: Why These Decisions Are Hard; The Framework; Decision-Specific Frameworks; The Avoiding-It Test

### hub-board
Read, write, and browse the AgentHub message board for agent coordination. Use when the user runs /hub-board or asks to post, read, or inspect coordination messages between competing AgentHub agents.
Sections: Usage; What It Does; Channels; Post Format; Result Summary; Board Rules

### idea-refine
Refines raw ideas into sharp, actionable concepts through structured divergent and convergent thinking. Use when an idea is still vague, when you need to stress-test assumptions before committing to a plan, or when you want to expand options before converging on one. Triggers on "ideate", "refine this idea", or "stress-test my plan".
Sections: Overview; When to Use; How It Works; Usage; Output; Detailed Instructions; Problem Statement; Recommended Direction; Key Assumptions to Validate; MVP Scope

### improve-codebase-architecture
Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
Sections: Process

### inbox-setup
One-time setup skill that builds a personalized inbox triage knowledge base via interactive interview. Interviews the user about their email patterns, business context, reply style, and priorities using grill-me discipline (one question at a time, forcing format where possible, dependency-ordered, each question explains why I'm asking), then generates the knowledge base files that power the companion 'inbox-triage' skill. Run this once before using inbox-triage for the first time. Re-run when business, pricing, or priorities change significantly. Triggers: 'set up my inbox', 'configure inbox triage', 'set up my email system', 'configure email triage', 'build my email knowledge base', 'initialize email management', 'set up inbox triage', 'onboard email triage', or any variation where someone wants to get the email triage system running for the first time.
Sections: Invocation Triggers; Conduct Discipline; Knowledge Base Contract — Files To Produce; Stop Condition (Full Interview); Section 1: The Big Picture; Section 2: Email Categories; Section 3: Reply Style & Voice; Section 4: Evaluation Framework (Conditional); Section 5: Blocklist & Patterns; Section 6: Current State

### inbox-triage
Runs a full inbox triage using the knowledge base created by the 'inbox-setup' skill. Light-intake by design (most invocations skip questions and run with KB-default preferences); asks at most 2 grill-me override questions when invocation is outside normal cadence or includes category-skip intent. Searches recent emails, classifies them via the user's taxonomy, researches new senders, generates recommendations, drafts replies (NEVER sends), delivers a report in the user's preferred format, and updates the knowledge base with learnings. Designed to run on a recurring schedule (1-3x daily) or on demand. Use when the user wants their inbox processed, in any variation (e.g., 'triage my inbox', 'inbox triage', 'check my email', 'run email triage', 'process my inbox', 'what's new in my email', 'handle my email', 'email triage'). Requires the inbox-setup skill to have been run first.
Sections: Invocation Triggers; Prerequisites; DRAFTS ONLY — Never Send; Step 0: Grill-Me Intake (Light — 0–2 Optional Override Questions); Step 1: Determine Search Window; Step 2: Email Search; Step 3: Classification; Step 4: Sender Research; Step 5: Recommendations; Step 6: Drafts

### intl-expansion
International market expansion strategy. Market selection, entry modes, localization, regulatory compliance, and go-to-market by region. Use when expanding to new countries, evaluating international markets, planning localization, or building regional teams.
Sections: Keywords; Quick Start; Market Selection Framework; Localization Checklist; Key Questions; Common Mistakes; Integration with C-Suite Roles; Resources

### ma-playbook
M&A strategy for acquiring companies or being acquired. Due diligence, valuation, integration, and deal structure. Use when evaluating acquisitions, preparing for acquisition, M&A due diligence, integration planning, or deal negotiation.
Sections: Keywords; Quick Start; When You're Acquiring; When You're Being Acquired; Red Flags (Both Sides); Verification Loop (before any LOI or signature); Integration with C-Suite Roles; Resources

### marketing-strategy-pmm
Product marketing skill for positioning, GTM strategy, competitive intelligence, and product launches. Use when the user asks about product positioning, go-to-market planning, competitive analysis, target audience definition, ICP definition, market research, launch plans, or sales enablement. Covers April Dunford positioning, ICP definition, competitive battlecards, launch playbooks, and international market entry. Produces deliverables including positioning statements, battlecard documents, launch plans, and go-to-market strategies.
Sections: Table of Contents; ICP Definition Workflow; Positioning Development; Competitive Intelligence; Product Launch Planning; Sales Enablement; International Expansion; Reference Documentation; PMM KPIs; Quick Reference

### mike
Use when someone asks to roast an idea, pressure-test or stress-test an idea, validate a business idea, "convene the panel", get a brutal second opinion before building something, or says "/mike", "ask Mike", "what would Mike say", "get Mike's take", "run it by Mike", or "let Mike at it". Spins up a 5-angle panel (Critic, Champion, Analyst, Investigator, Customer) that attacks the idea from every angle, then a Judge returns one GO / RESHAPE / KILL verdict with the cheapest test to de-risk it.
Sections: What this does; Step 1 — Frame the idea; Step 2 — Run the 5-angle panel (5 reviewers, in parallel); Step 3 — Call the verdict; THE VERDICT: GO / RESHAPE / KILL; Tooling; References; Assets; Rules; Anti-Patterns To Reject

### office-hours
/office-hours <topic> — YC-style 6-question founder interrogation before any advice. Forces clarity on problem, customer, distribution, defensibility, capital, and founder fit. Use when a founder question is too vague to route — e.g. 'should we grow faster?' — or before drafting a strategy brief.
Sections: When to Run; The Six Questions; Output Format; 1. Problem; 2. Customer; 3. Distribution; 4. Defensibility; 5. Capital; 6. Founder Fit; Routing

### org-health-diagnostic
Cross-functional organizational health check combining signals from all C-suite roles. Scores 8 dimensions on a traffic-light scale with drill-down recommendations. Use when assessing overall company health, preparing for board reviews, identifying at-risk functions, or when user mentions org health, health check, or health dashboard.
Sections: Keywords; Quick Start; The 8 Dimensions; Scoring & Traffic Lights; Dimension Interactions (Why One Problem Creates Another); Dashboard Output Format; Graceful Degradation; References

### pricing-strategy
Design, optimize, and communicate SaaS pricing — tier structure, value metrics, pricing pages, and price increase strategy. Use when building a pricing model from scratch, redesigning existing pricing, planning a price increase, or improving a pricing page. Trigger keywords: pricing tiers, pricing page, price increase, packaging, value metric, per seat pricing, usage-based pricing, freemium, good-better-best, pricing strategy, monetization, pricing page conversion, Van Westendorp. NOT for broader product strategy — use product-strategist for that. NOT for customer success or renewals — use customer-success-manager for expansion revenue.
Sections: Before Starting; How This Skill Works; The Three Pricing Axes; Value Metric Selection; Good-Better-Best Tier Structure; Value-Based Pricing; Pricing Research Methods; Price Increase Strategies; Pricing Page Design; Proactive Triggers

### product-strategist
Strategic product leadership toolkit for Head of Product covering OKR cascade generation, quarterly planning, competitive landscape analysis, product vision documents, and team scaling proposals. Use when creating quarterly OKR documents, defining product goals or KPIs, building product roadmaps, running competitive analysis, drafting team structure or hiring plans, aligning product strategy across engineering and design, or generating cascaded goal hierarchies from company to team level.
Sections: Core Capabilities; Quick Start; Workflow: Quarterly Strategic Planning; OKR Cascade Generator; Reference Documents; Best Practices; Related Skills

### project-development
This skill should be used for project-level decisions about LLM-powered systems: whether an LLM is the right primitive for the task at hand, the shape of a multi-stage batch or agent pipeline, token and cost estimation, choosing between single-agent and multi-agent at the project level, structured output design for downstream parsing, and structuring agent-assisted iteration. Use this when the unit of work is a whole project or a multi-stage pipeline. Route individual tool design to tool-design and individual skill-loading or context-budget tactics to context-optimization.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### reflect
Mid-conversation reflection skill that pauses execution and zooms out from detail-mode to honestly reassess direction, assumptions, and bias. Use when the user says 'reflect', 'take a step back', 'step back', 'zoom out', 'are we missing something', 'bigger picture', 'sanity check this', 'are we on track', 'are we overthinking this', 'forest for the trees', or any variation signaling intent to break out of detail-mode and reassess. Also trigger when the conversation has gone deep on implementation details without strategic check-in, or when the user shows signs of being stuck — that's often a signal the framing needs a reset, not more detail work. Intentionally low-intake: runs the 5-dimension analysis immediately when prior context is rich enough; asks one forcing clarifier only when invocation context is too thin to reassess from.
Sections: Invocation Triggers; Stop Directive (Before Reassessing); Grill-Me Optional Clarifier; The 5-Dimension Analysis Framework; Tone and Format Rules; Closing Recommendation (Mandatory); Error Handling; Tooling; References; Anti-Patterns To Reject

### scenario-war-room
Cross-functional what-if modeling for cascading multi-variable scenarios. Unlike single-assumption stress testing, this models compound adversity across all business functions simultaneously. Use when facing complex risk scenarios, strategic decisions with major downside, or when the user asks 'what if X AND Y both happen?'
Sections: Keywords; Quick Start; What This Is Not; Framework: 6-Step Cascade Model; Output Format; Rules for Good War Room Sessions; Common Scenarios by Stage; Integration with C-Suite Roles; References

### senior-architect
This skill should be used when the user asks to "design system architecture", "evaluate microservices vs monolith", "create architecture diagrams", "analyze dependencies", "choose a database", "plan for scalability", "make technical decisions", or "review system design". Use for architecture decision records (ADRs), tech stack evaluation, system design reviews, dependency analysis, and generating architecture diagrams in Mermaid, PlantUML, or ASCII format.
Sections: Table of Contents; Quick Start; Tools Overview; Decision Workflows; Reference Documentation; Tech Stack Coverage; Common Commands; Getting Help

### senior-data-scientist
World-class senior data scientist skill specialising in statistical modeling, experiment design, causal inference, and predictive analytics. Covers A/B testing (sample sizing, two-proportion z-tests, Bonferroni correction), difference-in-differences, feature engineering pipelines (Scikit-learn, XGBoost), cross-validated model evaluation (AUC-ROC, AUC-PR, SHAP), and MLflow experiment tracking — using Python (NumPy, Pandas, Scikit-learn), R, and SQL. Use when designing or analysing controlled experiments, building and evaluating classification or regression models, performing causal analysis on observational data, engineering features for structured tabular datasets, or translating statistical findings into data-driven business decisions.
Sections: Core Workflows; Reference Documentation; Common Commands

### site-architecture
When the user wants to plan, map, or restructure their website's page hierarchy, navigation, URL structure, or internal linking. Also use when the user mentions "sitemap," "site map," "visual sitemap," "site structure," "page hierarchy," "information architecture," "IA," "navigation design," "URL structure," "breadcrumbs," "internal linking strategy," "website planning," "what pages do I need," "how should I organize my site," or "site navigation." Use this whenever someone is planning what pages a website should have and how they connect. NOT for XML sitemaps (that's technical SEO — see seo-audit). For SEO audits, see seo-audit. For structured data, see schema.
Sections: Before Planning; Site Types and Starting Points; Page Hierarchy Design; Navigation Design; URL Structure; Visual Sitemap Output (Mermaid); Internal Linking Strategy; Output Format; Task-Specific Questions; Related Skills

### source-driven-development
Grounds every implementation decision in official documentation. Use when you want to verify an approach against the official docs before implementing it, or when you want authoritative, source-cited code free from outdated patterns. Use when building with any framework or library where correctness matters.
Sections: Overview; When to Use; The Process; Common Rationalizations; Red Flags; Verification

### strategic-alignment
Cascades strategy from boardroom to individual contributor. Detects and fixes misalignment between company goals and team execution. Covers strategy articulation, cascade mapping, orphan goal detection, silo identification, communication gap analysis, and realignment protocols. Use when teams are pulling in different directions, OKRs don't connect, departments optimize locally at company expense, or when user mentions alignment, strategy cascade, silo, conflicting OKRs, or strategy communication.
Sections: Keywords; Quick Start; Core Framework; Alignment Score; Key Questions for Alignment; Red Flags; Integration with Other C-Suite Roles; Detailed References

### stress-test
/em:stress-test — Business assumption stress testing. Use before betting on a plan whose core assumptions are unvalidated — e.g. stress-testing 'enterprise buyers will tolerate a 6-month pilot' or a hockey-stick revenue model.
Sections: Why Most Assumptions Are Wrong; The Stress-Test Methodology; Stress Test Patterns by Assumption Type; The Stress Test Output

### to-questionnaire
Turn a decision you can't fully answer into a questionnaire for someone else to fill in.
Sections: Document structure; Context; How to answer; <Theme heading>; Anything else?

### video-content-strategist
Use when planning video content strategy, writing video scripts, optimizing YouTube channels, building short-form video pipelines (Reels, TikTok, Shorts), or repurposing long-form content into video. Triggers: 'start a YouTube channel', 'video content strategy', 'write a video script', 'repurpose into video', 'YouTube SEO', 'short-form video'. NOT for written blog content (use content-production). NOT for social captions without video (use social-media-manager).
Sections: Before Starting; How This Skill Works; Mode 1: Strategy and Channel Setup; Mode 2: Script and Production; Mode 3: Repurpose and Distribute; Proactive Triggers; Output Artifacts; Communication; Anti-Patterns; Related Skills

### vpe-advisor
VP of Engineering advisory for startups: delivery throughput (DORA 4 metrics + bottleneck identification), engineering hiring funnel (sourcing → screen → onsite → offer conversion + time-to-fill + pipeline gap), engineering team structure (squad/tribe/chapter design + tech-lead manager-trigger thresholds), and production discipline (on-call, deployment cadence, postmortem culture). Use when sprint velocity is dropping, eng hiring is broken, team structure is unclear, or deciding when to add a tech-lead manager. NOT a CTO skill (which owns architecture) — VPE owns delivery operations and how the team ships.
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standards; Adjacent Skills; References

### vpe-review
/vpe-review <plan> — Throughput-first VP of Engineering interrogation of any plan that touches delivery, eng hiring, team structure, or production discipline. Use when cycle time balloons, DORA metrics slide, or before committing to an eng hiring wave or a reorg.
Sections: When to Run; The Six VPE Questions; Workflow; Output Format; The Decision Being Made; Delivery Throughput (if applicable); Hiring Funnel (if applicable); Team Structure (if applicable); Production Discipline (if applicable); Verdict

### vulnerability-triage-brocards
This skill should be used when the user asks to "triage a vulnerability report", "assess a CVE", "evaluate a bug bounty submission", "decide if a finding is valid", "review a security finding", "dismiss a vulnerability", "should we fix this CVE", "prioritize a vulnerability report", or needs to determine whether an incoming vulnerability report warrants investigation. Applies 7 brocards (rules of thumb) to systematically accept, dismiss, or request more information on vulnerability reports, or needs to filter raw findings from agentic vulnerability discovery pipelines before human review.
Sections: When to Use; When NOT to Use; Pipeline Position; Triage Workflow; Output Format; Triage Summary: Report ID or Title; Rationalizations to Reject; Detailed References

## Finance and markets

### aflpp
Sets up and runs AFL++ for multi-core fuzzing of C/C++ projects built with afl-clang-fast or afl-gcc-fast. Covers instrumentation modes, parallel main and secondary campaigns, persistent mode, corpus minimization, and crash triage. Use when scaling fuzzing across cores, fuzzing a mature C/C++ codebase, reading the afl-fuzz status screen, or moving on after libFuzzer has plateaued.
Sections: When to Use; Quick Start; Installation; Writing a Harness; Compilation; Corpus Management; Running Campaigns; Environment Variables That Matter; Multi-Core Fuzzing; Coverage Analysis

### ai-security
Use when assessing AI/ML systems for prompt injection, jailbreak vulnerabilities, model inversion risk, data poisoning exposure, or agent tool abuse. Covers MITRE ATLAS technique mapping, injection signature detection, and adversarial robustness scoring.
Sections: Table of Contents; Overview; AI Threat Scanner Tool; Prompt Injection Detection; Jailbreak Assessment; Model Inversion Risk; Data Poisoning Risk; Agent Tool Abuse; MITRE ATLAS Coverage; Guardrail Design Patterns

### analyst-estimates
Retrieve analyst financial estimates including Revenue and EPS projections with low/high ranges and analyst coverage. Use when analyzing forward expectations, consensus estimates, valuation inputs, or comparing projections to historical performance.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Metrics Reference; Analysis Tips; Valuation Applications; Confidence Assessment; Follow-up Queries

### arquiteto-de-empresa
Arquiteto de Empresa: constrói um negócio do zero como bundle OKF (Open Knowledge Format) — uma árvore de arquivos .md versionáveis com frontmatter type, links formando grafo, e index.md/log.md reservados, legível por humanos e por agentes. Conduz o fundador por uma entrevista de 12 fases (fundação, estratégia, mercado, financeiro, comercial, marketing, produto, operações, tech, pessoas, jurídico, governança), uma fase por vez, poucas perguntas por bloco, e gera os conceitos como markdown conformante. Acione quando o usuário quiser criar, estruturar ou documentar uma empresa inteira em pastas e arquivos .md; quando mencionar montar minha empresa do zero, empresa como código, base de conhecimento da empresa para IA ler, wiki da empresa para agentes, OKF, ou bundle de conhecimento. Em português do Brasil.
Sections: O que você produz: um bundle OKF conformante; Princípios operacionais (inquebráveis); Roteiro de 12 fases; Ferramentas (tornam o trabalho determinístico); Como começar (faça isto ao ser acionado); Referências; Assets

### balance-sheet
Retrieve detailed balance sheet statement data including Total Assets, Current Assets, Non-Current Assets, Liabilities, Equity, and Net Debt for public companies. Use when analyzing financial position, capital structure, or leverage metrics.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Metrics Reference; Analysis Tips; Follow-up Queries

### balance-sheet-growth
Retrieve year-over-year growth in balance sheet items including Total Assets, Total Liabilities, Shareholders Equity, Cash, and Inventories. Use when analyzing company financial position trends, capital structure changes, or liquidity management.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Metrics Reference; Analysis Tips; Follow-up Queries

### batch-market-cap
Retrieve market capitalization data for multiple companies at once using Octagon MCP. Use when comparing valuations across peers, screening by market cap, or analyzing a portfolio's composition by company size.
Sections: Prerequisites; Workflow; Example Queries; Market Cap Categories; Comparative Analysis Framework; Use Cases; Market Cap Calculations; Data Considerations; Analysis Tips; Integration with Other Skills

### burpsuite-project-parser
Searches and explores Burp Suite project files (.burp) from the command line. Use when searching response headers or bodies with regex patterns, extracting security audit findings, dumping proxy history or site map data, or analyzing HTTP traffic captured in a Burp project.
Sections: When to Use; Prerequisites; Quick Reference; Sub-Component Filters (USE THESE); Regex Search Operations; Other Operations; Output Limits (REQUIRED); Investigation Workflow; Understanding Results; Rationalizations to Reject

### business-investment-advisor
Business investment analysis and capital allocation advisor. Use when evaluating whether to invest in equipment, real estate, a new business, hiring, technology, or any capital expenditure. Also use for ROI calculations, IRR, NPV, payback period, build vs buy decisions, lease vs buy analysis, vendor evaluation, or deciding where to allocate limited budget for maximum return.
Sections: Before Starting; How This Skill Works; Core Analysis Framework; Decision Frameworks; Investment Scoring Rubric; Budget Allocation Framework; Proactive Triggers; Output Artifacts; Output Format; Communication

### capture
Captures and organizes chaotic brain dumps into a structured, actionable system with zero information loss. Use this skill whenever the user says 'capture this', 'brain dump', 'let me dump some ideas', 'I've got a bunch of thoughts', 'here's everything on my mind', 'idea dump', 'let me get this out of my head', 'I need to organize my thoughts', 'here's what I'm thinking', or any variation where someone is unloading a messy stream of ideas, tasks, thoughts, and plans wanting them turned into something coherent. Also trigger when the user pastes or dictates a long, unstructured block of mixed ideas — even without the exact phrase — the intent is the same. Fast-to-action by design: no upfront intake. Output is four sections (Projects/Ideas, Tasks, Connections, How I Can Help) ending with a directive question. Asks at most one mid-organization clarifying question when a single item is genuinely ambiguous between task and project.
Sections: Invocation Triggers; Operating Principles (All Five Apply Always); Grill-Me Mid-Organization Clarifier; Section 1: Projects & Ideas; Section 2: Tasks; Section 3: Connections; Section 4: How I Can Help; Compressed Output Pattern; What I heard; How I can help

### cash-flow-growth
Retrieve year-over-year growth in cash flow metrics including Operating Cash Flow, Free Cash Flow, and Net Cash Flow. Use when analyzing company cash generation trends, capital allocation efficiency, or liquidity trajectory.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Metrics Reference; Analysis Tips; Follow-up Queries

### cash-flow-statement
Retrieve real-time or historical cash flow statement data including Net Income, Operating Cash Flow, Investing Cash Flow, Financing Cash Flow, Free Cash Flow, and Cash Position for public companies. Use when analyzing cash generation, capital allocation, or liquidity trends.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Metrics Reference; Analysis Tips; Follow-up Queries

### cloud-security
Use when assessing cloud infrastructure for security misconfigurations, IAM privilege escalation paths, S3 public exposure, open security group rules, or IaC security gaps. Covers AWS, Azure, and GCP posture assessment with MITRE ATT&CK mapping.
Sections: Table of Contents; Overview; Cloud Posture Check Tool; IAM Policy Analysis; S3 Exposure Assessment; Security Group Analysis; IaC Security Review; Cloud Provider Coverage Matrix; Workflows; Anti-Patterns

### codeql
Scans a codebase for security vulnerabilities using CodeQL's interprocedural data flow and taint tracking analysis. Triggers on "run codeql", "codeql scan", "build codeql database", "SAST scan", "taint analysis", "dataflow analysis", or "find vulnerabilities in this repo". Covers Python, JavaScript/TypeScript, Go, Java/Kotlin, C/C++, C#, Ruby, and Swift. Supports "run all" (security-and-quality + security-experimental) and "important only" (high-precision) scan modes, and creates data extension models for project-specific sources and sinks. For fast single-file pattern matching, or when no build is available for a compiled language, use the semgrep skill; to parse SARIF that already exists rather than produce it, use the sarif-parsing skill.
Sections: Essential Principles; Each Bash call is a fresh shell; Output Directory; Quick Start; Rationalizations to Reject; Workflow Selection; Reference Index; Success Criteria

### commodities-list
Retrieve the full catalog of tradable commodities across energy, metals, and agriculture using Octagon MCP. Use when researching commodity markets, identifying trading firms, understanding market participants, and analyzing commodity sector coverage.
Sections: Prerequisites; Workflow; Example Queries; Commodity Categories; Market Participants; Key Market Concepts; Company Analysis; Sector Trends; Common Use Cases; Analysis Tips

### commodities-quote
Retrieve real-time commodity price quotes using Octagon MCP. Use when checking current commodity prices, analyzing day ranges, comparing to moving averages, and tracking precious metals, energy, and agricultural commodity prices.
Sections: Prerequisites; Workflow; Example Queries; Common Commodity Symbols; Understanding Quote Data; Price Analysis; Moving Average Analysis; Volume Analysis; Commodity-Specific Factors; Common Use Cases

### company-market-cap
Retrieve market capitalization data for a single company using Octagon MCP. Use when you need the current market value, valuation context, or size classification for any publicly traded stock.
Sections: Prerequisites; Workflow; Example Queries; Understanding Market Cap; Size Classifications; Market Cap Analysis; Contextual Analysis; Factors Affecting Market Cap; Common Use Cases; Analysis Tips

### constant-time-analysis
Detects timing side-channel vulnerabilities in cryptographic code. Use when implementing or reviewing crypto code, encountering division on secrets, secret-dependent branches, or constant-time programming questions in C, C++, Go, Rust, Swift, Java, Kotlin, C#, PHP, JavaScript, TypeScript, Python, or Ruby.
Sections: When to Use; When NOT to Use; Language Routing; Running the Analyzer; Interpreting Results; Triaging Findings; Limitations; Real-World Impact; References

### cosmos-vulnerability-scanner
Scans Cosmos SDK blockchain modules and CosmWasm contracts for consensus-critical vulnerabilities — chain halts, fund loss, state divergence. 25 core + 16 IBC + 10 EVM + 3 CosmWasm patterns. Use when auditing custom x/ modules, reviewing IBC integrations, or assessing pre-launch chain security. Updated for SDK v0.53.x.
Sections: Purpose; When to Use; When NOT to Use; Essential Principles; Scanning Workflow; SEVERITY Title; Success Criteria; Resources

### differential-review
Performs security-focused differential review of code changes. Adapts analysis depth to codebase size, uses git blame for context, calculates blast radius by counting callers, checks test coverage of modified code, and generates a markdown report. Use when reviewing a PR, commit, or diff for security vulnerabilities, checking whether a change re-introduces a previously fixed bug, asking what else a change could break, or finding which modified code has no test covering it.
Sections: Core Principles; Rationalizations (Do Not Skip); Quick Reference; Workflow Overview; Decision Tree; Agents; Quality Checklist; Integration; Example Usage; When NOT to Use This Skill

### dwarf-expert
Analyzes DWARF debug information in compiled binaries. Use when inspecting .debug_* sections, DIE trees, or DW_TAG_/DW_AT_ entries with dwarfdump/llvm-dwarfdump or readelf, verifying debug info with llvm-dwarfdump --verify, answering DWARF standard questions, or writing code that parses DWARF (libdwarf, pyelftools, gimli).
Sections: Searching DIEs

### earnings-analyst-master
Comprehensive earnings call analyst skill that orchestrates all Octagon earnings analysis skills. Use when analyzing earnings calls, extracting management insights, tracking guidance, and creating earnings-focused research reports.
Sections: Persona; Prerequisites; Available Skills; Workflow; Report Structure; Example: Full Analysis Query Sequence; Output Specifications; Earnings Analysis Framework; Analysis Tips; Compliance

### earnings-analyst-questions
Identify key themes and concerns raised by analysts during earnings calls, including specific analyst attribution and topic categorization.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Analyst Question Categories; Analyst Attribution; Question Intensity Analysis; Concern Classification; Tracking Questions Over Time

### earnings-call-analysis
Analyze earnings call transcripts to extract forward-looking guidance, strategic focus areas, supply chain insights, and generate follow-up questions for deeper analysis.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Key Metrics to Extract; Analysis Framework; Use Cases; Combining with Other Skills; Source Citations

### earnings-call-insights
Analyze earnings call transcripts to extract key insights about future guidance, strategic priorities, management commentary, and market signals.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Key Metrics to Extract; Analysis Framework; Use Cases; Combining with Other Skills; Analysis Tips

### earnings-capital-allocation
Extract management's commentary on capital allocation, investment priorities, shareholder returns, and strategic investments from earnings call transcripts.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Capital Allocation Framework; Capital Expenditure Analysis; Shareholder Returns Analysis; Investment Priority Analysis; M&A Commentary Analysis

### earnings-competitive-review
Analyze management's discussion of competitive landscape, market positioning, and strategic differentiation from earnings call transcripts.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Competitive Analysis Framework; Segment-Level Analysis; Competitor Mention Analysis; Differentiation Analysis; Market Share Commentary

### earnings-conf-call-sentiment
Analyze the overall sentiment and tone of management during earnings conference calls, including confidence levels, optimism indicators, and forward-looking language.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Sentiment Classification; Tone Analysis Framework; Key Sentiment Themes; Sentiment Change Tracking; Language Pattern Analysis

### earnings-cost-mgmt
Analyze cost reduction initiatives and operational efficiency measures from earnings transcripts, including headcount actions, facility consolidation, and productivity improvements.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Cost Management Categories; Cost Initiative Analysis Framework; Financial Impact Analysis; Restructuring Analysis; Tracking Cost Initiatives

### earnings-financial-guidance
Extract and analyze financial guidance and forward-looking statements from earnings transcripts, including segment guidance, risk factors, and guidance vs. actuals comparison.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Guidance Categories; Guidance Analysis Framework; Forward-Looking Statement Analysis; Segment-Level Analysis; Guidance vs. Actuals Tracking

### earnings-market-expansion
Identify market expansion and geographic growth plans discussed in earnings calls, including new market launches, international expansion, and product diversification strategies.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Expansion Categories; Expansion Strategy Framework; Growth Metrics Analysis; International Expansion Analysis; Market Density Strategy

### earnings-mgmt-comments
Extract management's commentary on specific topics from earnings call transcripts, including product development, strategy, competitive positioning, and executive quotes.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Common Topic Areas; Executive Attribution; Analysis Framework; Use Cases; Combining with Other Skills

### earnings-product-pipeline
Extract product development and pipeline updates from earnings calls, including clinical trial progress, regulatory submissions, and launch timelines.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Pipeline Stage Framework; Clinical Trial Analysis; Regulatory Progress Tracking; Portfolio Summary Analysis; Catalyst Calendar

### earnings-qa-analysis
Analyze the Q&A section of earnings call transcripts for strategic insights, analyst concerns, and management responses on key topics.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Why Q&A Matters; Common Q&A Themes; Analyst Question Analysis; Management Response Analysis; Use Cases

### earnings-revenue-guidance
Extract specific revenue guidance and growth projections from earnings call transcripts, including segment breakdown, constant currency adjustments, and M&A contributions.
Sections: Prerequisites; Workflow; Expected Output; Example Query; Example Response; Revenue Guidance Components; Currency Impact Analysis; M&A Contribution Analysis; Segment Guidance Framework; Guidance Range Analysis

### entry-point-analyzer
Analyzes smart contract codebases to identify state-changing entry points for security auditing. Detects externally callable functions that modify state, categorizes them by access level (public, admin, role-restricted, contract-only), and generates structured audit reports. Excludes view/pure/read-only functions. Use when auditing smart contracts (Solidity, Vyper, Solana/Rust, Move, TON, CosmWasm) or when asked to find entry points, audit flows, external functions, access control patterns, or privileged operations.
Sections: When to Use; When NOT to Use; Scope: State-Changing Functions Only; Workflow; Slither Integration (Solidity); Language Detection; Access Classification; Output Format; Summary; Public Entry Points (Unrestricted)

### env-secrets-manager
Manage environment-variable hygiene and secrets safety across local development and production. Practical auditing, drift awareness, rotation readiness. Use when auditing .env files for committed secrets, planning a credential rotation, debugging missing-env-var production incidents, or hardening a new project against secrets leakage.
Sections: Overview; Core Capabilities; When to Use; Quick Start; Recommended Workflow; Reference Docs; Common Pitfalls; Best Practices; Cloud Secret Store Integration; Secret Rotation Workflow

### esg-benchmark-comparison
Retrieve ESG benchmark comparison metrics by sector using Octagon MCP. Use when comparing ESG performance across industries, analyzing sector-level sustainability benchmarks, identifying ESG leaders and laggards by industry, or referencing frameworks like MSCI, S&P Global, CDP, and CSRD.
Sections: Prerequisites; Workflow; Example Queries; Key Benchmark Sources; Sector Benchmark Ranges; Analysis Tips; Use Cases

### esg-ratings
Retrieve ESG ratings and scores using Octagon MCP. Use when analyzing Environmental, Social, and Governance ratings, MSCI ESG ratings, Sustainalytics risk ratings, industry ESG rankings, and sustainability metrics for any public company.
Sections: Prerequisites; Workflow; Example Queries; Key Metrics Explained; MSCI Rating Scale; Analysis Tips; Use Cases

### finance-skills
Router/index for the 2 finance skills bundled in this plugin: financial-analyst (ratio analysis, DCF valuation, budget variance, rolling forecasts) and saas-metrics-coach (ARR/MRR, churn, CAC/LTV, NRR, quick ratio). Use when a finance request doesn't obviously match one skill and you need to pick the right one (e.g., 'analyze these financials', 'how healthy are my SaaS metrics').
Sections: Routing table; Quick start; Related (packaged separately, not in this bundle); Rules

### financial-analyst
Performs financial ratio analysis, DCF valuation, budget variance analysis, and rolling forecast construction for strategic decision-making
Sections: Overview; Use when; Clarify First; 5-Phase Workflow; Tools; Knowledge Bases; Templates; Industry Adaptations; Key Metrics & Targets; Input Data Format

### financial-analyst-master
Comprehensive equity research analyst skill that orchestrates all Octagon financial analysis skills. Use when conducting full company analysis, writing initiation of coverage reports, performing due diligence, or creating investment recommendations with quantitative support.
Sections: Persona; Prerequisites; Available Skills; Workflow; Report Structure; Example: Full Analysis Query Sequence; Output Specifications; Sourcing Hierarchy; Compliance; Analysis Tips

### financial-growth
Retrieve comprehensive year-over-year growth in key financial metrics including Revenue, Gross Profit, Operating Income, Net Income, EPS, and Free Cash Flow. Use when analyzing overall company financial performance trends across income statement and cash flow.
Sections: Prerequisites; Query Format; Output Format; Key Insights Pattern; Metrics Reference; Analysis Tips; Follow-up Queries

### financial-health-scores
Retrieve financial health scores including Altman Z-Score and Piotroski Score for public companies. Use when assessing bankruptcy risk, financial strength, value investing screening, or credit quality analysis.
Sections: Prerequisites; Query Format; Output Format; Altman Z-Score Interpretation; Piotroski Score Interpretation; Analysis Tips; Follow-up Queries

### financial-metrics-analysis
Analyze year-over-year growth in income statement items and financial metrics using Octagon MCP. Use when retrieving YoY Revenue Growth, Cost of Revenue Growth, Gross Profit Growth, Operating Income Growth, Net Income Growth, or comparing financial performance across fiscal periods for any public company.
Sections: Prerequisites; Workflow; Example Queries; Key Metrics Explained; Analysis Tips

### firebase-apk-scanner
Scans Android APKs for Firebase security misconfigurations including open databases, storage buckets, authentication issues, and exposed cloud functions. Use when analyzing APK files for Firebase vulnerabilities, performing mobile app security audits, or testing Firebase endpoint security. For authorized security research only.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Reference Documentation; How to Use This Skill; Workflow; Scan Summary; Extracted Configuration; Vulnerabilities Found; Remediation

### forex-list
Retrieve a full listing of actively traded currency pairs in the global forex market using Octagon MCP. Use when researching forex markets, understanding currency pair categories, analyzing major/minor/exotic pairs, and identifying trading opportunities.
Sections: Prerequisites; Workflow; Example Queries; Currency Pair Categories; Understanding Currency Pairs; Liquidity and Volume; Key Drivers by Pair; Trading Sessions; Volatility Characteristics; Common Use Cases

### fp-check
Systematically verifies suspected security bugs to eliminate false positives, producing a TRUE POSITIVE or FALSE POSITIVE verdict with documented evidence for each. Use when asked whether a specific finding is real, exploitable, or a false positive, or to verify or validate a suspected vulnerability — not for hunting or discovering new bugs.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Step 0: Understand the Claim and Context; Route: Standard vs Deep Verification; Batch Triage; Final Summary; References

### graph-evolution
Compares Trailmark code graphs at two source code snapshots (git commits, tags, or directories) to surface security-relevant structural changes. Detects new attack paths, complexity shifts, blast radius growth, taint propagation changes, and privilege boundary modifications that text diffs miss. Use when comparing code between commits or tags, analyzing structural evolution, detecting attack surface growth, reviewing what changed between audit snapshots, or finding security-relevant changes that text diffs miss.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Prerequisites; Quick Start; Decision Tree; Workflow; Diff Reference; Quality Checklist; Integration

### historical-financial-ratings
Retrieve historical financial ratings and key metric scores over time using Octagon MCP. Use when analyzing overall ratings, return on assets, return on equity, discounted cash flow scores, debt-to-equity scores, and letter grades (A+, A, B, etc.) for any public company.
Sections: Prerequisites; Workflow; Example Queries; Key Metrics Explained; Analysis Tips; Use Cases

### historical-market-cap
Retrieve historical market capitalization data for any stock using Octagon MCP. Use when tracking market cap changes over time, analyzing valuation trends, identifying peak and trough valuations, and comparing historical size classifications.
Sections: Prerequisites; Workflow; Example Queries; Understanding Market Cap History; Trend Analysis; Period Analysis; Volatility Assessment; Peak and Trough Analysis; Size Classification Over Time; Comparative Analysis

### income-statement
Retrieve real-time income statement data including Revenue, Net Income, and EPS Diluted for public companies. Use when analyzing absolute financial figures, historical earnings, or comparing company scale across fiscal periods.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Metrics Reference; Analysis Tips; Follow-up Queries

### income-statement-growth
Retrieve year-over-year growth in income statement items including Revenue, Gross Profit, Operating Income, Net Income, and EPS Diluted. Use when analyzing company financial growth trends, comparing fiscal year performance, or identifying profitability inflection points.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Follow-up Queries; Metrics Reference; Analysis Tips

### industry-pe-ratios
Retrieve industry-specific P/E ratios using Octagon MCP. Use when comparing company valuations to specific industry peers, analyzing sub-sector valuations, and understanding niche market valuations beyond broad sector averages.
Sections: Prerequisites; Workflow; Example Queries; Industry vs. Sector; Common Industries; Using Industry P/E for Analysis; Peer Group Analysis; Industry Characteristics; Exchange Considerations; Common Use Cases

### information-security-manager-iso27001
ISO 27001 ISMS implementation and cybersecurity governance for HealthTech and MedTech companies. Use when designing an ISMS, running security risk assessments, implementing controls, pursuing ISO 27001 certification, preparing security audits, responding to security incidents, or verifying compliance. Covers ISO 27001, ISO 27002, healthcare security, and medical device cybersecurity.
Sections: Table of Contents; Trigger Phrases; Quick Start; Tools; Workflows; Reference Guides; Validation Checkpoints; Worked Example: Healthcare Risk Assessment

### kalshi-trading-bot-cli
Operate the Kalshi Trading Bot CLI for prediction-market research, edge discovery, basket construction, backtesting, portfolio monitoring, and guarded trade execution. Use when the user mentions kalshi-trading-bot-cli, Kalshi CLI, prediction market trading workflows, market edge scans, basket sizing, or CLI-based Kalshi trading.
Sections: Persona; Prerequisites; Available CLI Workflows; Workflow; Output Specifications; Safety Framework; Example: Discovery to Research; Example: Basket Workflow; Example: Guarded Trade Flow

### market-analyst-master
Comprehensive market analyst skill that orchestrates all Octagon stock performance and market data skills. Use when conducting stock analysis, creating market reports, evaluating valuations, comparing sectors, or performing technical and sentiment analysis.
Sections: Persona; Prerequisites; Available Skills; Workflow; Report Structure; Example: Full Analysis Query Sequence; Output Specifications; Analysis Framework; Analysis Tips; Compliance

### mermaid-to-proverif
Translates Mermaid sequenceDiagrams describing cryptographic protocols into ProVerif formal verification models (.pv files). Use when generating a ProVerif model, formally verifying a protocol, converting a Mermaid diagram to ProVerif, verifying protocol security properties (secrecy, authentication, forward secrecy), checking for replay attacks, or producing a .pv file from a sequence diagram.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Workflow; Decision Tree; Example; Supporting Documentation

### modern-cpp
Guides C++ code toward modern idioms (C++20/23/26). Use when writing new C++ code, modernizing legacy patterns, or working on security-critical C++. Replaces raw pointers with smart pointers, SFINAE with concepts, printf with std::print, error codes with std::expected.
Sections: When to Use This Skill; When NOT to Use This Skill; Anti-Patterns to Avoid; Decision Tree; Feature Tiers; Compiler Hardening Quick Reference; Rationalizations to Reject; Best Practices Checklist; Read Next

### open-sourcing
This skill should be used when the user asks to "open source this project", "prepare this repository for public release", "make this repo public", "check open-source readiness", "choose a license for this project", or "set up release automation" ahead of a public launch. Provides a release-readiness workflow covering secrets hygiene, licensing, documentation, CI, and language-specific packaging.
Sections: When to Use; When NOT to Use; Workflow; Final Review; Additional Resources

### performance-profiler
Systematic performance profiling for Node.js, Python, and Go applications. Identifies CPU, memory, and I/O bottlenecks, generates flamegraphs, analyzes bundle sizes, optimizes database queries, runs load tests with k6 and Artillery. Always measures before and after. Use when investigating a slow endpoint, planning a performance budget, or hunting a memory leak in production.
Sections: Overview; Core Capabilities; When to Use; Quick Start; Golden Rule: Measure First; Node.js Profiling; References

### post-patch-validation
Validates security patches with reproducible baseline-versus-patched evidence, including original exploits, root-cause variants, behavior preservation, regressions, and newly introduced security failures. Use after a patch exists and before accepting, merging, or reporting it as fixed; also use when an AI-generated patch, remediation commit, pull request, or proposed upstream fix needs adversarial post-patch validation across any language.
Sections: When to Use; When NOT to Use; Quick Start; Evidence Contract; Coverage Rules; Reading the result; Claude Dynamic Workflow; Rationalizations to Reject

### pr-review-expert
Use when the user asks to review pull requests, analyze code changes, check for security issues in PRs, or assess code quality of diffs.
Sections: Overview; Core Capabilities; When to Use; Fetching the Diff; Workflow; Ticket Linking Verification; Complete Review Checklist (30+ Items); Code Review Checklist; Output Format; PR Review: PR Title (#NUMBER)

### prediction-markets-analysis
Generate deep research reports on prediction market events using the Octagon Prediction Markets Agent. Combines real-time Kalshi market data with AI-driven analysis to surface price drivers, compare market vs. model probabilities, and identify potential mispricings across 120+ active markets.
Sections: Prerequisites; Core Functionality; Model Variants; Example Queries; Example Response Structure; Market Overview; Price Drivers; Key Catalysts; Historical Resolution Context; Contract Details

### price-target-consensus
Retrieve consensus price targets for any stock using Octagon MCP. Use when you need the average, median, high, and low analyst price targets to evaluate upside/downside potential and analyst agreement.
Sections: Prerequisites; Workflow; Example Queries; Understanding the Metrics; Calculating Potential; Range Analysis; Consensus vs. Median; Bull vs. Bear Cases; Practical Applications; Common Use Cases

### price-target-summary
Retrieve analysts' price target summary for any stock using Octagon MCP. Use when evaluating analyst sentiment, upside/downside potential, consensus expectations, and tracking target trends over time.
Sections: Prerequisites; Workflow; Example Queries; Understanding Price Targets; Timeframe Analysis; Calculating Potential; Analyst Coverage; Consensus Strength; Target Revisions; Data Sources

### ratings-snapshot
Retrieve ratings snapshot with overall rating and key metric scores including DCF, ROE, ROA, Debt-to-Equity, P/E, and P/B for public companies. Use when screening stocks, comparing quality metrics, or quick fundamental assessment.
Sections: Prerequisites; Query Format; Output Format; Metrics Reference; Score Interpretation; Analysis Tips; Component Deep Dives; Follow-up Queries

### research-finance
Use when managing the money for an internal R&D program or portfolio — building a multi-period program budget with the F&A (indirect) split, tracking burn rate and runway against value-inflection milestones, or routing R&D cost items to a capitalize-vs-expense determination. Every budget output surfaces its assumptions block; capitalize-vs-expense is decision-support only and routes to a named finance owner — it never books an entry or decides accounting treatment. Distinct from finance/financial-analysis (corporate DCF, close, valuation) and research/grants (funding discovery — this manages money already won).
Sections: Purpose; When to use; Workflow; Scripts; Onboarding & customization; Optimize with autoresearch (opt-in); References; Assumptions; Anti-patterns; Distinct from

### revenue-geographic-segmentation
Retrieve detailed revenue breakdown by geographic segment for public companies. Use when analyzing regional exposure, geographic concentration, international expansion, or currency risk assessment.
Sections: Prerequisites; Query Format; Output Format; Key Observations Pattern; Analysis Tips; Strategic Analysis; Segment Evolution; Follow-up Queries

### revenue-product-segmentation
Retrieve detailed revenue breakdown by product segment for public companies. Use when analyzing product mix, revenue concentration, segment contribution, or business line performance.
Sections: Prerequisites; Query Format; Output Format; Key Insights Pattern; Analysis Tips; Segment Analysis Framework; Follow-up Queries

### saas-metrics-coach
SaaS financial health advisor. Use when a user shares revenue or customer numbers, or mentions ARR, MRR, churn, LTV, CAC, NRR, or asks how their SaaS business is doing.
Sections: Step 1 — Collect Inputs; Step 2 — Calculate Metrics; Step 3 — Benchmark Each Metric; Step 4 — Prioritize and Recommend; Step 5 — Output Format; Metrics at a Glance; Overall Picture; Priority Issues; What is Working; 90-Day Focus

### sec-10k-analysis
Analyze 10-K annual filings for public companies using Octagon MCP. Use when extracting key financial metrics, risk factors, business overview, management discussion, and regulatory disclosures from SEC 10-K filings.
Sections: Prerequisites; Workflow; Example Queries; 10-K Filing Structure; Key Metrics to Extract; Risk Factor Categories; Analysis Tips; Use Cases

### sec-10q-analysis
Analyze 10-Q quarterly filings for public companies using Octagon MCP. Use when extracting quarterly performance metrics, revenue breakdown, operating margins, segment performance, and interim financial updates from SEC 10-Q filings.
Sections: Prerequisites; Workflow; Example Queries; 10-Q Filing Structure; Key Quarterly Metrics; Segment Analysis; 10-Q vs 10-K Differences; Analysis Tips; Use Cases

### sec-8k-analysis
Analyze 8-K filings to extract material events and corporate changes using Octagon MCP. Use when tracking real-time corporate disclosures, M&A announcements, leadership changes, earnings releases, and other material events requiring immediate investor attention.
Sections: Prerequisites; Workflow; Example Queries; 8-K Item Categories; Event Materiality Assessment; Tracking 8-K Patterns; Analysis Tips; Use Cases

### sec-amendments-review
Review amendments to SEC filings using Octagon MCP. Use when tracking material changes, corrections, restatements, and updates to previously filed documents including 10-K/A, 10-Q/A, 8-K/A, S-1/A, and Form 144/A filings.
Sections: Prerequisites; Workflow; Example Queries; Amendment Types; Reasons for Amendments; Materiality Assessment; Amendment Analysis Framework; S-1/A Amendment Tracking; 10-K/A and 10-Q/A Analysis; 8-K/A Analysis

### sec-analyst-master
Comprehensive SEC filing analyst skill that orchestrates all Octagon SEC analysis skills. Use when conducting due diligence, regulatory compliance review, M&A analysis, or creating comprehensive company assessments based on SEC disclosures.
Sections: Persona; Prerequisites; Available Skills; Workflow; Report Structure; Example: Full Analysis Query Sequence; Output Specifications; Sourcing Hierarchy; Compliance; Analysis Tips

### sec-annual-comparison
Compare key metrics and disclosures between annual 10-K filings using Octagon MCP. Use when analyzing year-over-year changes in financials, risk factors, business descriptions, and strategic priorities across fiscal years.
Sections: Prerequisites; Workflow; Example Queries; Comparison Framework; Year-over-Year Analysis; Risk Factor Comparison; Business Description Changes; Segment Performance Comparison; Multi-Year Trend Analysis; Analysis Tips

### sec-business-desc-analysis
Extract and analyze business descriptions and competitive landscape from SEC filings using Octagon MCP. Use when researching company business models, market positioning, competitive advantages, industry dynamics, and strategic focus areas from Item 1 disclosures.
Sections: Prerequisites; Workflow; Example Queries; Item 1 Components; Competitive Analysis Framework; Business Model Analysis; Strategic Analysis; Comparing Business Descriptions; Analysis Tips; Use Cases

### sec-cash-flow-review
Extract and analyze cash flow trends and working capital changes from SEC filings using Octagon MCP. Use when researching operating cash flow, investing activities, financing activities, free cash flow, liquidity, and working capital dynamics from 10-K and 10-Q filings.
Sections: Prerequisites; Workflow; Example Queries; Cash Flow Statement Components; Key Cash Flow Metrics; Working Capital Analysis; Cash Flow Quality Assessment; Trend Analysis; Liquidity Assessment; Financing Activity Analysis

### sec-corp-governance
Review corporate governance practices and board composition from SEC filings using Octagon MCP. Use when researching board structure, director qualifications, committee composition, governance policies, shareholder rights, and related party transactions from proxy statements.
Sections: Prerequisites; Workflow; Example Queries; Board Composition Analysis; Committee Structure; Governance Policies; Leadership Structure; Related Party Transactions; Director Elections; Governance Benchmarking

### sec-debt-covenant
Analyze debt covenants and credit agreement terms from SEC filings using Octagon MCP. Use when researching financial covenants, leverage ratios, interest coverage requirements, credit facilities, debt maturity schedules, and covenant compliance from 10-K, 10-Q, and 8-K filings.
Sections: Prerequisites; Workflow; Example Queries; Debt Structure Overview; Covenant Types; Key Covenant Metrics; Covenant Cushion Analysis; Credit Agreement Terms; Maturity Schedule Analysis; Covenant Violation Analysis

### sec-footnotes-analysis
Analyze footnotes and accounting policies from SEC filings using Octagon MCP. Use when researching revenue recognition policies, critical estimates, lease obligations, pension assumptions, stock compensation, contingencies, and new accounting pronouncements.
Sections: Prerequisites; Workflow; Example Queries; Key Footnote Categories; Critical Accounting Estimates; New Accounting Standards; Comparing Footnotes; Analysis Tips; Use Cases

### sec-mda-analysis
Analyze Management Discussion and Analysis (MD&A) sections from SEC filings using Octagon MCP. Use when extracting strategic initiatives, financial performance commentary, macroeconomic challenges, and forward-looking statements from 10-K and 10-Q filings.
Sections: Prerequisites; Workflow; Example Queries; MD&A Section Components; Key Analysis Areas; Comparing MD&A Over Time; Analysis Tips; Use Cases

### sec-proxy-analysis
Analyze proxy statements (DEF 14A) to extract executive compensation, governance information, and shareholder voting matters using Octagon MCP. Use when researching CEO pay, board composition, say-on-pay votes, and corporate governance practices.
Sections: Prerequisites; Workflow; Example Queries; Proxy Statement Components; Compensation Analysis; Governance Assessment; Voting Analysis; Analysis Tips; Use Cases

### sec-risk-factors
Extract and summarize risk factors from SEC filings using Octagon MCP. Use when analyzing Item 1A risk disclosures, categorizing business risks, identifying new or material risks, and comparing risk profiles across companies or time periods.
Sections: Prerequisites; Workflow; Example Queries; Risk Factor Categories; Analyzing Risk Changes; Analysis Tips; Use Cases

### sec-s1-analysis
Analyze S-1 registration statements for IPOs using Octagon MCP. Use when researching pre-IPO companies, extracting business models, risk factors, use of proceeds, capitalization, principal shareholders, and growth opportunities from IPO filings.
Sections: Prerequisites; Workflow; Example Queries; S-1 Key Sections; IPO Analysis Framework; Risk Factor Analysis; Use of Proceeds Analysis; Valuation Context; Analysis Tips; Use Cases

### sec-segment-reporting
Analyze business segment performance and reporting from SEC filings using Octagon MCP. Use when researching segment revenue, operating income, margins, geographic breakdown, and segment restructuring from 10-K and 10-Q filings.
Sections: Prerequisites; Workflow; Example Queries; Segment Reporting Framework; Key Metrics by Segment; Segment Performance Analysis; Geographic Segment Analysis; Segment Restructuring; Tracking Segment Trends; Inter-Company Comparison

### second-opinion
Gets independent code reviews from Codex or Antigravity for uncommitted changes, branch diffs, and commits. Use when the user requests an external review, a second opinion on code, a codex review, a gemini review, an antigravity review, or /second-opinion.
Sections: Review choices; Input preparation; Provider references; Results and failures; Examples

### secrets-vault-manager
Use when the user asks to set up secret management infrastructure, integrate HashiCorp Vault, configure cloud secret stores (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager), implement secret rotation, or audit secret access patterns.
Sections: Overview; HashiCorp Vault Patterns; Cloud Secret Store Integration; Secret Rotation Workflows; Dynamic Secrets; Audit Logging; Emergency Procedures; CI/CD Integration; Anti-Patterns; Tools

### sector-pe-ratios
Retrieve sector P/E ratios using Octagon MCP. Use when comparing company valuations to sector benchmarks, analyzing sector valuations across exchanges, and understanding market-wide valuation trends.
Sections: Prerequisites; Workflow; Example Queries; Understanding P/E Ratios; Sector Categories; Major Exchanges; Using Sector P/E for Analysis; Historical Context; Cross-Sector Analysis; Data Considerations

### sector-performance-snapshot
Retrieve a snapshot of market sector performance using Octagon MCP. Use when analyzing sector-wide metrics including revenue, EBITDA, net income, market cap, and enterprise value for companies within a specific sector and exchange.
Sections: Prerequisites; Workflow; Example Queries; Key Performance Metrics; Understanding Sector Metrics; Sector Comparisons; Analysis Framework; Capital Structure Insights; Competitor Landscape; Common Use Cases

### secure-workflow-guide
Guides through Trail of Bits' 5-step secure development workflow. Runs Slither scans, checks special features (upgradeability/ERC conformance/token integration), generates visual security diagrams, helps document security properties for fuzzing/verification, and reviews manual security areas. Use when securing a smart contract end to end rather than hunting one bug, checking a project on every check-in or before deployment, triaging a Slither report, or asking where to start on smart contract security.
Sections: Purpose; The 5-Step Workflow; How I Work; Rationalizations (Do Not Skip); Example Output; What You'll Get; Getting Help; Ready to Start

### security-and-hardening
Hardens code against vulnerabilities. Use when auditing an input handler for vulnerabilities, when handling user input, authentication, data storage, or external integrations, or when checking a login flow is safe against the OWASP Top Ten. Use when building any feature that accepts untrusted data, manages user sessions, or interacts with third-party services. Use when auditing dependencies for known vulnerabilities, triaging package-manager audit findings, or assessing supply-chain risk in a new package. Use when personal data or privacy compliance (GDPR, CCPA) is involved.
Sections: Overview; When to Use; Process: Threat Model First; The Three-Tier Boundary System; Hardening Controls; Review Checklist; Common Rationalizations; Red Flags; Verification

### security-guidance
PreToolUse security-anti-pattern hook for Claude Code. Catches 12 common security risks (command injection, XSS, SQL injection, unsafe deserialization, GitHub Actions workflow injection, eval/new Function code injection) BEFORE the Edit/Write/MultiEdit operation completes. Session-state caching prevents duplicate warnings on the same file+rule combo. Stdlib only — no dependencies. Use when you want a safety net during Claude Code sessions that touch security-sensitive code (auth, payments, user input handling, IaC). Disable with ENABLE_SECURITY_REMINDER=0 if you need to perform a verified-safe operation that would otherwise trip a pattern. Triggers — "add security hook", "block unsafe code", "detect command injection before write", "prevent SQL injection patterns", "security warning hook".
Sections: What It Catches; How It Works; Installation; Configuration; Per-File Override Pattern; Why The Patterns Are Substring-Based (Not AST-Based); State Files; Debug Log; Source + Attribution; Anti-Patterns

### security-pen-testing
Use when the user asks to perform security audits, penetration testing, vulnerability scanning, OWASP Top 10 checks, or offensive security assessments. Covers static analysis, dependency scanning, secret detection, API security testing, and pen test report generation.
Sections: Table of Contents; Overview; OWASP Top 10 Systematic Audit; Static Analysis; Dependency Vulnerability Scanning; Secret Scanning; API Security Testing; Web Vulnerability Testing; Infrastructure Security; Pen Test Report Generation

### semgrep
Runs a Semgrep security scan over a codebase: detects languages, selects rulesets, presents the plan for explicit approval, then runs every approved ruleset through scripts/run-scans.sh, which batches the semgrep processes and writes scans.json, and merges the output to SARIF. Supports two scan modes, "run all" for full ruleset coverage and "important only" for security findings at medium-to-high confidence and impact. Uses Semgrep Pro for cross-file taint analysis when it is available. Use when asked to scan code for vulnerabilities, run a security audit with Semgrep, find bugs, or perform static analysis. For the same scan without the approval gate, use the /static-analysis:semgrep-scan workflow.
Sections: Essential Principles; When to Use; When NOT to Use; Output Directory; Prerequisites; Scan Modes; Orchestration Architecture; Running it as a Workflow; Workflow; Workflow and agents

### semgrep-rule-creator
Creates custom Semgrep rules for detecting security vulnerabilities, bug patterns, and code patterns. Use when writing Semgrep rules or building custom static analysis detections.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Anti-Patterns; Strictness Level; Overview; Quick Start; Quick Reference; Workflow; Documentation

### senior-backend
Designs and implements backend systems including REST APIs, microservices, database architectures, authentication flows, and security hardening. Use when the user asks to "design REST APIs", "optimize database queries", "implement authentication", "build microservices", "review backend code", "set up GraphQL", "handle database migrations", or "load test APIs". Covers Node.js/Express/Fastify development, PostgreSQL optimization, API security, and backend architecture patterns.
Sections: Quick Start; Tools Overview; Backend Development Workflows; Reference Documentation; Common Patterns Quick Reference; Common Commands; Assumptions and Verifiable Success Criteria (Karpathy discipline); Customization profiles; Composition map; Forcing-question library (Matt Pocock grill)

### senior-fullstack
Fullstack development toolkit with project scaffolding for Next.js, FastAPI, MERN, and Django stacks, code quality analysis with security and complexity scoring, and stack selection guidance. Use when the user asks to "scaffold a new project", "create a Next.js app", "set up FastAPI with React", "analyze code quality", "audit my codebase", "what stack should I use", "generate project boilerplate", or mentions fullstack development, project setup, or tech stack comparison.
Sections: Table of Contents; Trigger Phrases; Tools; Workflows; Reference Guides; Quick Reference; Assumptions and Verifiable Success Criteria (Karpathy discipline); Customization profiles; Composition map; Forcing-question library (Matt Pocock grill)

### senior-secops
Senior SecOps engineer skill for application security, vulnerability management, compliance verification, and secure development practices. Runs SAST/DAST scans, generates CVE remediation plans, checks dependency vulnerabilities, creates security policies, enforces secure coding patterns, and automates compliance checks against SOC2, PCI-DSS, HIPAA, and GDPR. Use when conducting a security review or audit, responding to a CVE or security incident, hardening infrastructure, implementing authentication or secrets management, running penetration test prep, checking OWASP Top 10 exposure, or enforcing security controls in CI/CD pipelines.
Sections: Table of Contents; Core Capabilities; Workflows; Tool Reference; Security Standards; Input Validation; Output Encoding; Authentication; Session Management; Error Handling

### senior-security
Use when the user asks for STRIDE threat modeling, DREAD risk scoring, data-flow-diagram threat analysis, or a quick secret scan — or when a security request needs routing to the right specialist skill (pen-testing, incident response, cloud posture, red team, AI security, threat hunting, secure code review). This skill owns threat modeling; everything else routes to a sibling.
Sections: Routing Table (read this first); What This Skill Owns: STRIDE Threat Modeling; References (load on demand)

### sharp-edges
Identifies error-prone APIs, dangerous configurations, and footgun designs that enable security mistakes. Use when reviewing API designs, configuration schemas, cryptographic library ergonomics, or evaluating whether code follows 'secure by default' and 'pit of success' principles. Triggers: footgun, misuse-resistant, secure defaults, API usability, dangerous configuration.
Sections: When to Use; When NOT to Use; Agent; Core Principle; Rationalizations to Reject; Sharp Edge Categories; Analysis Workflow; Severity Classification; References; Quality Checklist

### ship-gate
Pre-production audit that scans a codebase for security, database, deployment, code quality, AI/LLM, dependency, frontend, and observability issues. Intercepts deploy commands and blocks until critical items pass. Stack-agnostic. Use for "run ship gate", "am I ready to ship", "pre-launch audit", "can I deploy", "push to production", "go live checklist", "preflight check". Not for CI/CD setup or infra provisioning.
Sections: Intercept Behavior; How It Works; Categories; Scope; Integration Points

### skill-security-auditor
Security audit and vulnerability scanner for AI agent skills before installation. Use when: (1) evaluating a skill from an untrusted source, (2) auditing a skill directory or git repo URL for malicious code, (3) pre-install security gate for Claude Code plugins, OpenClaw skills, or Codex skills, (4) scanning Python scripts for dangerous patterns like os.system, eval, subprocess, network exfiltration, (5) detecting prompt injection in SKILL.md files, (6) checking dependency supply chain risks, (7) verifying file system access stays within skill boundaries. Triggers: "audit this skill", "is this skill safe", "scan skill for security", "check skill before install", "skill security check", "skill vulnerability scan".
Sections: Quick Start; What Gets Scanned; Audit Workflow; Reading the Report; Advanced Usage; Threat Model Reference; Limitations

### statistical-analyst
Run hypothesis tests, analyze A/B experiment results, calculate sample sizes, and interpret statistical significance with effect sizes. Use when you need to validate whether observed differences are real, size an experiment correctly before launch, or interpret test results with confidence.
Sections: Entry Points; Tools; Test Selection Guide; Decision Framework (Post-Experiment); Effect Size Reference; Proactive Risk Triggers; Output Artifacts; Quality Loop; Communication Standard; Related Skills

### stock-grades
Retrieve the latest stock grades and ratings from top analysts and financial institutions using Octagon MCP. Use when tracking analyst upgrades, downgrades, rating changes, and institutional sentiment over time.
Sections: Prerequisites; Workflow; Example Queries; Understanding Rating Scales; Rating Actions; Analyst Credibility; Trend Analysis; Rating Distribution; Timing Considerations; Common Use Cases

### stock-historical-index
Retrieve full historical end-of-day price data for market indices using Octagon MCP. Use when analyzing index performance over time, tracking market trends, calculating returns, and understanding market context for individual stock analysis.
Sections: Prerequisites; Workflow; Example Queries; Common Index Symbols; Understanding Index Data; Return Calculations; Volume Analysis; Trend Analysis; Volatility Analysis; Key Market Events

### stock-performance
Retrieve stock price data and performance metrics using Octagon MCP. Use when analyzing daily closing prices, trading volume, price trends, historical performance, and comparing stock movements over specific time periods.
Sections: Prerequisites; Workflow; Example Queries; Key Metrics; Price Analysis Framework; Volume Analysis; Time Period Analysis; Comparative Analysis; Analysis Tips; Use Cases

### stock-price-change
Retrieve stock price change statistics across multiple time periods using Octagon MCP. Use when analyzing short-term and long-term returns, comparing performance across timeframes, and evaluating momentum and historical growth.
Sections: Prerequisites; Workflow; Example Queries; Understanding Time Periods; Return Interpretation; Momentum Analysis; Annualized Returns; Comparison Analysis; Time Period Relationships; All-Time High Analysis

### stock-quote
Retrieve real-time stock quotes using Octagon MCP. Use when you need current price, day range, 52-week range, volume, market cap, and moving averages for any publicly traded stock.
Sections: Prerequisites; Workflow; Example Queries; Key Quote Components; Quote Analysis Framework; Market Context; Common Use Cases; Analysis Tips; Integration with Other Skills

### trailmark
Builds and queries multi-language source and binary code graphs for security analysis. Includes pre-analysis passes for blast radius, taint propagation, privilege boundaries, entry point enumeration, proxy/unresolved-call tracking, type/reference queries, structural traversal, graph diffs, audit augmentation, declared cross-language/FFI/external links via `.trailmark/links.toml`, and SQL schema graphs. Use when analyzing call paths, mapping attack surface, finding complexity hotspots, enumerating entry points, tracing taint propagation, measuring blast radius, importing SARIF/weAudit/binary findings, linking source graphs across language or RPC boundaries, or building a code graph for audit prioritization. Feature-gate version-specific Trailmark APIs before using them; prefer `trailmark.parse.detect_languages()` or `--language auto` when the target language is unknown or polyglot.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Installation; Version Gate; Quick Start; Pre-Analysis Passes; Language Selection; Repository Links (v0.5+); Graph Model

### trailmark-finding-triage
Performs graph-assisted triage of a single security finding, SARIF result, weAudit annotation, suspicious function, or report excerpt using Trailmark reachability, entrypoint paths, taint, privilege-boundary, blast-radius, caller/callee, and neighborhood evidence. Use when deciding whether one candidate issue is reachable, prioritizing a finding before PoC work, preparing evidence for exploit validation, or checking whether a static-analysis result is actionable.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Workflow; Example Prompts

### trailmark-review-gate
Runs a Trailmark structural review gate over a branch, pull request, fix commit, release diff, or git ref range to detect new entrypoints, new tainted paths, removed validation or authorization calls, privilege-boundary drift, blast-radius growth, complexity growth, and newly reachable sensitive sinks. Use when reviewing a PR, branch, remediation commit, or release diff where graph-level security regressions should be checked before merge.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Workflow; Requirements

### wizard
Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself.
Sections: Process

### wycheproof
Validates cryptographic implementations against Project Wycheproof's test vectors, which encode known attacks and edge cases across AES, RSA, ECDSA, ECDH, and more. Covers loading test vectors, mapping result flags onto pass and fail expectations, and reading a failure. Use when testing a crypto implementation against known attacks, checking a library against standard test vectors, or investigating why two implementations disagree on the same input.
Sections: Background; When to Use; Quick Reference; Testing Workflow; Repository Structure; Supported Algorithms; Test File Structure; Implementation Guide; Common Vulnerabilities Detected; Case Study: Elliptic npm Package

## Compliance, risk, legal and quality

### a11y-audit
Accessibility audit skill for scanning, fixing, and verifying WCAG 2.2 Level A and AA compliance across React, Next.js, Vue, Angular, Svelte, and plain HTML codebases. Use when auditing accessibility, fixing a11y violations, checking color contrast, generating compliance reports, or integrating accessibility checks into CI/CD pipelines.
Sections: Description; Features; Usage; Example: React Component Audit; Tools Reference; Common Pitfalls; Related Skills; Reference Documentation; Resources

### adversarial-reviewer
Adversarial code review that breaks the self-review monoculture. Use when you want a genuinely critical review of recent changes, before merging a PR, or when you suspect Claude is being too agreeable about code quality. Forces perspective shifts through hostile reviewer personas that catch blind spots the author's mental model shares with the reviewer.
Sections: Description; Features; Usage; Examples; Problem This Solves; Table of Contents; Quick Start; Review Workflow; The Three Personas; Severity Classification

### agentic-actions-auditor
Audits GitHub Actions workflows for security vulnerabilities in AI agent integrations including Claude Code Action, Gemini CLI, OpenAI Codex, and GitHub AI Inference. Detects attack vectors where attacker-controlled input reaches AI agents running in CI/CD pipelines, including env var intermediary patterns, direct expression injection, dangerous sandbox configurations, and wildcard user allowlists. Use when reviewing workflow files that invoke AI coding agents, auditing CI/CD pipeline security for prompt injection risks, or evaluating agentic action configurations.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Audit Methodology; Detailed References

### ai-act-readiness
/ai-act-readiness <system> — EU AI Act 6-question forcing interrogation. Use during AI-system intake, before EU deployment, or during annual compliance refresh as Article 113 obligations phase in (2025-02-02 / 2025-08-02 / 2026-08-02 / 2027-08-02).
Sections: When to Run; The Six EU AI Act Questions; Workflow; Output Format; The Decision Being Made; Risk Classification; Conformity Assessment (if high-risk); Obligation Matrix; Transparency (Article 50); Cross-Framework Reuse

### aims-audit
/aims-audit <scope> — ISO/IEC 42001 AIMS internal-audit 6-question forcing interrogation. Use before certification stage 1, before annual internal audit cycles, or when onboarding a new AI system into an existing AIMS.
Sections: When to Run; The Six AIMS Questions; Workflow; Output Format; The Decision Being Made; Gap Analysis (Clauses 4-10); AI Risk Register; Clause 9.2 Audit Plan; Cross-Framework Reuse; Verdict

### algorand-vulnerability-scanner
Scans Algorand smart contracts for 11 common vulnerabilities including rekeying attacks, unchecked transaction fees, missing field validations, and access control issues. Use when auditing Algorand projects (TEAL/PyTeal).
Sections: 1. Purpose; 2. When to Use This Skill; 3. Platform Detection; 4. How This Skill Works; 5. Example Output; 6. Vulnerability Patterns (11 Patterns); 7. Scanning Workflow; 8. Reporting Format; SEVERITY Vulnerability Name (e.g., Missing RekeyTo Validation); 9. Priority Guidelines

### analytics-tracking
Set up, audit, and debug analytics tracking implementation — GA4, Google Tag Manager, event taxonomy, conversion tracking, and data quality. Use when building a tracking plan from scratch, auditing existing analytics for gaps or errors, debugging missing events, or setting up GTM. Trigger keywords: GA4 setup, Google Tag Manager, GTM, event tracking, analytics implementation, conversion tracking, tracking plan, event taxonomy, custom dimensions, UTM tracking, analytics audit, missing events, tracking broken. NOT for analyzing marketing campaign data — use campaign-analytics for that. NOT for BI dashboards — use product-analytics for in-product event analysis.
Sections: Before Starting; How This Skill Works; Event Taxonomy Design; GA4 Setup; Google Tag Manager Setup; Conversion Tracking: Platform-Specific; Cross-Platform Tracking; Data Quality; Proactive Triggers; Output Artifacts

### audit-augmentation
Augments Trailmark code graphs with external audit findings from SARIF static analysis results, weAudit annotation files, and version-gated Trailmark 0.4.x binary-analysis graph exports. Maps findings to graph nodes by file and line overlap, creates severity-based subgraphs, and enables cross-referencing findings with pre-analysis data (blast radius, taint, etc.). Use when projecting SARIF results onto a code graph, overlaying weAudit annotations, importing binary graph findings, cross-referencing Semgrep, CodeQL, or binary-analysis findings with call graph data, or visualizing audit findings in the context of code structure.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Installation; Version Gate; Quick Start; Workflow; Annotation Format; Subgraphs Created; How Matching Works

### audit-prep-assistant
Prepares codebases for security review using Trail of Bits' checklist. Helps set review goals, runs static analysis tools, increases test coverage, removes dead code, ensures accessibility, and generates documentation (flowcharts, user stories, inline comments). Use when preparing your own codebase to be audited by someone else, getting a repository review-ready before an external security review, deciding what to fix before auditors start, or asking what assessors need from a project. For understanding unfamiliar code you are about to audit, use audit-context-building instead.
Sections: Purpose; The Preparation Process; How I Work; Rationalizations (Do Not Skip); Example Output; REVIEW GOALS DOCUMENT; STATIC ANALYSIS REPORT; TEST COVERAGE REPORT; CODE SCOPE; BUILD INSTRUCTIONS

### cairo-vulnerability-scanner
Scans Cairo/StarkNet smart contracts for 6 critical vulnerabilities including felt252 arithmetic overflow, L1-L2 messaging issues, address conversion problems, and signature replay. Use when auditing StarkNet projects.
Sections: 1. Purpose; 2. When to Use This Skill; 3. Platform Detection; 4. How This Skill Works; 5. Example Output; 6. Vulnerability Patterns (6 Patterns); 7. Scanning Workflow; 8. Reporting Format; CRITICAL Unchecked fromaddress in L1 Handler; 9. Priority Guidelines

### capa-officer
CAPA system management for medical device QMS. Covers root cause analysis, corrective action planning, effectiveness verification, and CAPA metrics. Use when running CAPA investigations, 5-Why analysis, fishbone diagrams, root cause determination, corrective action tracking, effectiveness verification, or CAPA program optimization.
Sections: Table of Contents; CAPA Investigation Workflow; Root Cause Analysis; Corrective Action Planning; Effectiveness Verification; CAPA Metrics and Reporting; Reference Documentation; Tools; Regulatory Requirements

### capacity-planner
Use when an ops leader (Director of CX, Head of Support, VP Ops, Head of BizOps, Head of IT ops, Head of Finance ops) is sizing ops capacity, building a headcount plan, modeling utilization risk, planning Q3 capacity or annual support capacity, or designing CS coverage — and needs Erlang-C queueing math, P90 demand sizing, shrinkage-adjusted FTE, manager-trigger thresholds, and a quarterly hiring sequence with ramp + attrition. Apply when sustained team utilization is above 80% or when the team is growing >50% in 12 months. Run before committing the headcount budget. This is NOT engineering capacity (see vpe-advisor for DORA + cycle time) and NOT strategic 3-year workforce planning (see chro-advisor).
Sections: Purpose; When to use; Workflow; Scripts; Quick example; References; Assets; Assumptions; Anti-patterns; Distinct from

### clinical-research
Use when designing a prospective clinical study before submission — selecting and classifying endpoints (primary / key-secondary / exploratory, with surrogate-endpoint flagging), estimating sample size and power for two-arm designs (means / proportions / survival), or scoring a study plan for feasibility and a GO / GO-WITH-CONDITIONS / REDESIGN / NO-GO phase-gate decision. Every output is an ESTIMATE plus a named human owner (clinician / biostatistician / regulatory owner) — never clinical fact, never a finished protocol. Distinct from ra-qm-team, which handles the regulatory/QM submission (ISO 13485, EU MDR, FDA 510(k)/PMA/QSR), not the study design.
Sections: Purpose; When to use; Workflow; Scripts; Onboarding & customization; Optimize with autoresearch (opt-in); References; Assumptions; Anti-patterns; Distinct from

### code-maturity-assessor
Systematic code maturity assessment using Trail of Bits' 9-category framework. Analyzes codebase for arithmetic safety, auditing practices, access controls, complexity, decentralization, documentation, MEV risks, low-level code, and testing, then produces a scorecard with evidence-based ratings and a priority-ordered roadmap. Use when assessing or scoring the maturity of a smart contract or blockchain codebase, producing a maturity scorecard or evaluation, or judging how mature, well-tested, or well-documented such a project is against a rubric.
Sections: Purpose; How This Works; Rating System; The 9 Categories; Example Output; Assessment Process; Rationalizations (Do Not Skip); Report Format; Ready to Begin

### code-review-and-quality
Conducts multi-axis code review. Use before merging any change. Use when reviewing code written by yourself, another agent, or a human. Use when you need to assess code quality across multiple dimensions before it enters the main branch. Use when asked to review a diff or a pull request, even when the diff is pasted inline.
Sections: Overview; When to Use; The Five-Axis Review; Structural Remedies; Change Sizing; Change Descriptions; Review Process; Multi-Model Review Pattern; Dead Code Hygiene; Review Speed

### code-reviewer
Code review automation for TypeScript, JavaScript, Python, Go, Swift, Kotlin, C#, .NET, Java, C, C++, Rust, Ruby, PHP, and Dart/Flutter. Analyzes PRs for complexity and risk, checks code quality for SOLID violations and code smells, generates review reports. Use when reviewing pull requests, analyzing code quality, identifying issues, generating review checklists.
Sections: How This Skill Is Organized; Tools; Adding a New Language; Regression Fixtures

### compliance-os
Compliance OS — meta-orchestrator that lets compliance teams CONFIGURE which frameworks apply, COMPUTE cross-framework control overlap, SIMULATE internal audits, and CONSOLIDATE evidence across multiple frameworks. Four decisions: (1) Given a company profile, which of the 12 supported frameworks apply (ISO 27001/13485/42001/14971, EU AI Act, MDR 745, GDPR, SOC 2, FDA QSR, NIST CSF 2.0, NIS2, HIPAA)? (2) Across selected frameworks, which controls overlap and how much evidence reuses? (3) For a given framework + scope, what does a realistic mock audit produce — drawing from the 205-scenario library? (4) Across selected frameworks, what's the unified evidence checklist with reuse map? Use when standing up a multi-framework program, planning the annual audit calendar, or preparing for certification stage 1. Does NOT replace per-framework skills (it orchestrates them).
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standards; Adjacent Skills; References; Phase 3 Asset: Mock Audit Scenario Library

### compliance-readiness
/compliance-readiness <program> — Multi-framework compliance officer 6-question forcing interrogation of any compliance program. Use before starting a new framework, planning the annual audit calendar, or preparing for certification stage 1.
Sections: When to Run; The Six Compliance Officer Questions; Workflow; Output Format; The Decision Being Made; Framework Set; Cross-Framework Overlap; Evidence Pool; Audit Calendar; Mock Audit Results (per framework)

### constraint-driven-development
Establishes a project's quality bar as a written contract and stops agents quietly lowering it. Interviews the user on which dimensions matter, supplies sane default thresholds when they have no number in mind, records everything in CONSTRAINTS.md, and watches the diff for a weakened bar — new @ts-ignore or eslint-disable suppressions, skipped or deleted tests, assertions stripped out, unimplemented stubs, thresholds edited down. Use when no quality bar is written down, when the user says "set up constraints" or "define our standards", when the user wants dimensions they care about — accessibility, web performance, coverage — set up as enforced constraints, when an agent keeps silencing checks or skipping tests to get to green, when you need a coverage or performance threshold and don't know what number to pick, or when an agent writes more code than anyone will read.
Sections: Overview; When to Use; Loading Constraints; The Process; Floor (always enforced, no setup required); Enforced with numbers; Measured, not yet enforced; Exceptions; Sane Defaults; Escalation Path

### data-quality-auditor
Audit datasets for completeness, consistency, accuracy, and validity. Profile data distributions, detect anomalies and outliers, surface structural issues, and produce an actionable remediation plan. Use when the user asks to check data quality, profile a dataset, hunt outliers or missing values, or validate data before analysis or model training.
Sections: Entry Points; Tools; Data Quality Score (DQS); Proactive Risk Triggers; Output Artifacts; Remediation Playbook; Quality Loop; Communication Standard; Related Skills; References

### dependency-auditor
Audit and manage dependencies across multi-language projects. Identifies vulnerabilities, license conflicts, transitive dependency risks, and safe-upgrade paths. Use when auditing third-party packages before release, investigating a CVE, planning a major version bump, or running a license-compliance review. Examples: 'audit our npm dependencies', 'do we have GPL contamination', 'plan the upgrade to React 19'.
Sections: Quick Start; Supported Ecosystems; License Classification; Upgrade Risk Matrix; Scripts (accurate capability claims); CI Integration; Best Practices

### dimensional-analysis
Audits code for unit and decimal-scaling bugs and annotates it with dimensional comments recording the units of each value. Use when someone asks to audit or review code for unit confusion, decimals or scaling mismatches, WAD/RAY scale errors, or the wrong token's decimals; to annotate units in a codebase; or to perform a dimensional analysis of a DeFi protocol, offchain code, or other arithmetic-heavy codebase. Catches formulas that combine values carrying different units or scales.
Sections: Host and dependency contract; Execution Mode; Scope and Coverage Guarantees; Annotation Format; When to Use; When NOT to Use; Reporting Scope; Red Flags; Rationalizations to Reject; Workflow Steps (Phases 1-4)

### eu-ai-act-specialist
EU AI Act (Regulation (EU) 2024/1689) operational compliance for compliance teams. Three Article-level decisions: (1) What's the risk tier of this AI system — prohibited (Art. 5), high-risk (Art. 6 + Annex III), limited-risk (Art. 50), or minimal-risk? (2) For high-risk systems, what's the Article 43 conformity assessment route (Module A internal control vs Module H full QMS + notified body) and what goes in the Annex IV technical documentation? (3) Per organizational role (provider / deployer / importer / distributor / authorized representative), what are the active obligations and deadlines? Use during AI system intake review, when planning conformity assessment, or when scoping deployer obligations. Cites Articles + Annexes for every output. NOT executive AI strategy (see chief-ai-officer-advisor). NOT a legal substitute.
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standards; Adjacent Skills; References

### fda-consultant-specialist
FDA regulatory consultant for medical device companies. Provides 510(k)/PMA/De Novo pathway guidance, QMSR (21 CFR 820, which incorporates ISO 13485:2016 by reference since 2026-02-02; formerly QSR) compliance, HIPAA assessments, and device cybersecurity. Use when user mentions FDA submission, 510(k), PMA, De Novo, QMSR, QSR, ISO 13485 for FDA, premarket, predicate device, substantial equivalence, HIPAA medical device, or FDA cybersecurity.
Sections: Table of Contents; FDA Pathway Selection; 510(k) Submission Process; QMSR Compliance (formerly QSR); HIPAA for Medical Devices; Device Cybersecurity; Resources

### fda-qsr-audit-prep
/fda-qsr-audit-prep <scope> — FDA 21 CFR 820 (QSR / QMSR) audit 6-question forcing interrogation. Post-Feb 2026 substantially harmonized with ISO 13485. Use before annual internal QSR audit, pre-FDA-inspection readiness, or Form 483 response.
Sections: When to Run; The Six QSR Questions; Workflow; Output Format; The Decision Being Made; Complaint + MDR Posture; Process Validation Status (21 CFR 820.75); DHR Completeness (21 CFR 820.180); CAPA Health (21 CFR 820.100); Labeling (21 CFR 801)

### gc-review
/gc-review <plan> — General Counsel interrogation of contracts, IP, regulatory, term sheets, and employment-law surface. Use when reviewing a term sheet before signing, redlining a customer MSA, or checking IP assignment and regulatory exposure on a new product.
Sections: When to Run; The Six GC Questions; Workflow; Output Format; Document; Issues; Regulatory Trigger; Outside Counsel Action Items; Verdict; Routing

### gdpr-audit-prep
/gdpr-audit-prep <scope> — GDPR audit 6-question Article-cited forcing interrogation. Use before annual internal GDPR review, post-breach internal audit, DPA investigation readiness, or acquisition due diligence.
Sections: When to Run; The Six DPO Questions; Workflow; Output Format; The Decision Being Made; Article 30 RoPA Status; Article 6 Lawful Basis Discipline; Article 35 DPIA Quality; Data Subject Rights (Articles 12-22); Article 28 Processor Management

### gdpr-dsgvo-expert
GDPR and German DSGVO compliance automation. Scans codebases for privacy risks, generates DPIA documentation, tracks data subject rights requests with Art. 12(3) one-month deadlines. Use when running GDPR compliance assessments, privacy audits, data protection planning, DPIA generation, or data subject rights (DSAR) management (e.g., 'check this service for GDPR risks', 'track an access request deadline'). Final compliance determinations route to the DPO or legal counsel.
Sections: Table of Contents; Tools; Reference Guides; Workflows; Key GDPR Concepts

### general-counsel-advisor
General Counsel advisory for startups: contract review (MSA, SaaS, NDA, DPA, employment), IP strategy, term sheet decoding, and regulatory landscape mapping. Use when reviewing any contract or term sheet, deciding when to engage outside counsel, defining IP strategy, evaluating regulatory exposure (HIPAA, GDPR, FDA, fintech), or when user mentions general counsel, GC, legal review, contract risk, term sheet, IP assignment, or regulatory exposure. NOT a substitute for licensed counsel — surfaces questions to bring to qualified attorneys.
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standard (when invoked via /gc-review); Adjacent Skills; References

### isms-audit-expert
Information Security Management System (ISMS) audit expert for ISO 27001 compliance verification, security control assessment, and certification support. Use when the user mentions ISO 27001, ISMS audit, Annex A controls, Statement of Applicability (SOA), gap analysis, nonconformity management, internal audit, surveillance audit, or security certification preparation. Helps review control implementation evidence, document audit findings, classify nonconformities, generate risk-based audit plans, map controls to Annex A requirements, prepare Stage 1 and Stage 2 audit documentation, and support corrective action workflows.
Sections: Table of Contents; Audit Program Management; Audit Execution; Control Assessment; Finding Management; Certification Support; Tools; References; Audit Performance Metrics

### iso13485-audit-prep
/iso13485-audit-prep <scope> — ISO 13485 QMS audit 6-question forcing interrogation. Design controls + CAPA + post-market focused. Use before Clause 8.2.4 internal audit, MDR / FDA QSR alignment review, or product-launch DHF closure audit.
Sections: When to Run; The Six QMS Questions; Workflow; Output Format; The Decision Being Made; Design Control Status (sampled DHFs); CAPA Health; Process Validation Status; Risk Management File Status; Post-Market Surveillance

### iso27001-audit-prep
/iso27001-audit-prep <scope> — ISO 27001 ISMS audit readiness 6-question forcing interrogation. Use before annual Clause 9.2 internal audit, surveillance audit prep, or stage 1 certification readiness.
Sections: When to Run; The Six ISMS Questions; Workflow; Output Format; The Decision Being Made; Audit Programme Status; Risk Register Health; High-Stakes Controls Status; Management Review Status; Cross-Framework Impact

### iso42001-specialist
ISO/IEC 42001:2023 AI Management System (AIMS) specialist for compliance teams running internal audits. Three decisions: (1) Where are the gaps against Clauses 4-10 and what do we close first? (2) What goes in the AI risk register and which Annex A controls treat each risk? (3) What's the 12-month internal audit plan that satisfies Clause 9.2? Use when preparing for certification, scoping internal audit cycles, or onboarding AI systems into an existing ISMS (27001) / QMS (13485) program. NOT an executive AI strategy skill (see chief-ai-officer-advisor). NOT EU AI Act compliance (see compliance-team-eu-ai-act).
Sections: Keywords; Quick Start; Key Questions (ask these first); Core Responsibilities; Workflows; Output Standards; Adjacent Skills; References

### knowledge-ops
Use when a Head of Ops, Knowledge Manager, or TPM-Internal needs to author, validate, or clean up company SOPs and internal runbooks (procurement intake, vendor offboarding, incident-comms cascade, employee onboarding) — including 5W2H completeness checks (Who-What-When-Where-Why-How-HowMuch), cross-link and orphan-page validation across a sprawling Notion/Confluence/Obsidian wiki, KB ingestion + hygiene reporting, and runbook step verification (named owner, expected duration, observable success signal, rollback path, escalation contact). Pairs Ishikawa's 5W2H method, Gawande's *The Checklist Manifesto*, ISO 9001, ITIL v4, and Google SRE Workbook runbook discipline with deterministic stdlib-only Python tools that score completeness, detect anti-patterns, and emit prioritized cleanup lists (e.g., "validate this runbook before it goes into rotation", "audit our Confluence wiki for stale and orphaned SOPs").
Sections: Purpose; When to use; Workflow; Scripts; Quick example; References; Assumptions; Anti-patterns; Distinct from; Forcing-question library (Matt Pocock grill discipline)

### mdr-745-specialist
EU MDR 2017/745 compliance specialist for medical device classification, technical documentation, clinical evidence, and post-market surveillance. Covers Annex VIII classification rules, Annex II/III technical files, Annex XIV clinical evaluation, Art. 86 PSUR schedules, and EUDAMED integration. Use when classifying a medical device under MDR, building or gap-checking a technical file, planning clinical evaluation or PMS/PSUR cadence, or preparing for notified body review (e.g., 'what class is my device under MDR', 'review my PSUR schedule').
Sections: Table of Contents; Device Classification Workflow; Technical Documentation; Clinical Evidence; Post-Market Surveillance; EUDAMED and UDI; Reference Documentation; Tools; Notified Body Interface

### qms-audit-expert
ISO 13485 internal audit expertise for medical device QMS. Covers audit planning, execution, nonconformity classification, and CAPA verification. Use when planning internal audits, executing audits, classifying findings, preparing for external audits, or managing an audit program.
Sections: Table of Contents; Audit Planning Workflow; Audit Execution; Nonconformity Management; External Audit Preparation; Reference Documentation; Tools; Audit Program Metrics

### quality-documentation-manager
Document control system management for medical device QMS. Covers document numbering, version control, change management, and 21 CFR Part 11 compliance. Use when working on document control procedures, change control workflows, document numbering, version management, electronic signature compliance, or regulatory documentation review.
Sections: Table of Contents; Document Control Workflow; Document Numbering System; Approval and Review Process; Change Control Process; 21 CFR Part 11 Compliance; Reference Documentation; Tools; Document Control Metrics; Regulatory Requirements

### quality-manager-qmr
Senior Quality Manager Responsible Person (QMR) for HealthTech and MedTech companies. Provides quality system governance, management review leadership, regulatory compliance oversight, and quality performance monitoring per ISO 13485 Clause 5.5.2. Use when leading management reviews, setting quality policy and objectives, monitoring quality KPIs and cost of quality, or exercising QMR governance and regulatory oversight responsibilities.
Sections: Table of Contents; QMR Responsibilities; Management Review Workflow; Quality KPI Management Workflow; Quality Objectives Workflow; Quality Culture Assessment Workflow; Regulatory Compliance Oversight; Decision Frameworks; Tools and References; Related Skills

### quality-manager-qms-iso13485
ISO 13485 Quality Management System implementation and maintenance for medical device organizations. Provides QMS design, documentation control, internal auditing, CAPA management, and certification support. Use when working with medical device quality systems, preparing for ISO 13485 audits, managing regulatory compliance documentation, setting up corrective actions, or building audit preparation programs. Useful for quality management, audit preparation, regulatory compliance, medical device documentation, and corrective action workflows.
Sections: Table of Contents; QMS Implementation Workflow; Document Control Workflow; Internal Audit Workflow; Process Validation Workflow; Supplier Qualification Workflow; QMS Process Reference; Decision Frameworks; Tools and References; Related Skills

### regulatory-affairs-head
Senior Regulatory Affairs Manager for HealthTech and MedTech companies. Prepares FDA 510(k), De Novo, and PMA submission packages; analyzes regulatory pathways for new medical devices; drafts responses to FDA deficiency letters and Notified Body queries; develops CE marking technical documentation under EU MDR 2017/745; coordinates multi-market approval strategies across FDA, EU, Health Canada, PMDA, and NMPA; and maintains regulatory intelligence on evolving standards. Use when users need to plan or execute FDA submissions, navigate 510(k) or PMA approval processes, achieve CE marking, prepare pre-submission meeting materials, write regulatory strategy documents, respond to agency queries, or manage compliance documentation for medical device market access.
Sections: Table of Contents; Regulatory Strategy Workflow; FDA Submission Workflow; EU MDR Submission Workflow; Global Market Access Workflow; Regulatory Intelligence Workflow; Decision Frameworks; Tools and References; Related Skills

### risk-management-specialist
Medical device risk management specialist implementing ISO 14971 throughout product lifecycle. Provides risk analysis, risk evaluation, risk control, and post-production information analysis. Use when user mentions risk management, ISO 14971, risk analysis, FMEA, fault tree analysis, hazard identification, risk control, risk matrix, benefit-risk analysis, residual risk, risk acceptability, or post-market risk.
Sections: Table of Contents; Risk Management Planning Workflow; Risk Analysis Workflow; Risk Evaluation Workflow; Risk Control Workflow; Post-Production Risk Management; Risk Assessment Templates; Decision Frameworks; Tools and References; Related Skills

### senior-data-engineer
Data engineering skill for building scalable data pipelines, ETL/ELT systems, and data infrastructure. Expertise in Python, SQL, Spark, Airflow, dbt, Kafka, and modern data stack. Includes data modeling, pipeline orchestration, data quality, and DataOps. Use when designing data architectures, building data pipelines, optimizing data workflows, implementing data governance, or troubleshooting data issues.
Sections: Table of Contents; Trigger Phrases; Quick Start; Workflows; Architecture Decision Framework; Tech Stack; Reference Documentation; Troubleshooting

### seo-audit
When the user wants to audit, review, or diagnose SEO issues on their site. Also use when the user mentions "SEO audit," "technical SEO," "why am I not ranking," "SEO issues," "on-page SEO," "meta tags review," "SEO health check," "my traffic dropped," "lost rankings," "not showing up in Google," "site isn't ranking," "Google update hit me," "page speed," "core web vitals," "crawl errors," or "indexing issues." Use this even if the user just says something vague like "my SEO is bad" or "help with SEO" — start with an audit. For building pages at scale to target keywords, see programmatic-seo. For adding structured data, see schema. For AI search optimization, see ai-seo.
Sections: Initial Assessment; Audit Framework; Technical SEO Audit; International SEO & Localization; On-Page SEO Audit; Content Quality Assessment; Common Issues by Site Type; Output Format; References; Tools Referenced

### soc2-audit-prep
/soc2-audit-prep <scope> — SOC 2 Type II readiness 6-question forcing interrogation. Observation-period focused. Use before Type II observation begins, mid-period checkpoint, or pre-field-test month-10 readiness.
Sections: When to Run; The Six SOC 2 Type II Questions; Workflow; Output Format; The Decision Being Made; TSC Scope; Observation Period Status; Exception Log; Sample Evidence Coverage; ISO 27001 Cross-Walk Reuse

### soc2-compliance
Use when the user asks to prepare for SOC 2 audits, map Trust Service Criteria, build control matrices, collect audit evidence, perform gap analysis, or assess SOC 2 Type I vs Type II readiness.
Sections: Table of Contents; Overview; Trust Service Criteria; Control Matrix Generation; Gap Analysis Workflow; Evidence Collection; Audit Readiness Checklist; Vendor Management; Continuous Compliance; Anti-Patterns

### solana-vulnerability-scanner
Scans Solana programs for 6 critical vulnerabilities including arbitrary CPI, improper PDA validation, missing signer/ownership checks, and sysvar spoofing. Use when auditing Solana/Anchor programs.
Sections: 1. Purpose; 2. When to Use This Skill; 3. Platform Detection; 4. How This Skill Works; 5. Example Output; 6. Vulnerability Patterns (6 Patterns); 7. Scanning Workflow; 8. Reporting Format; CRITICAL Arbitrary CPI - Unchecked Program ID; 9. Priority Guidelines

### substrate-vulnerability-scanner
Scans Substrate/Polkadot pallets for 7 critical vulnerabilities including arithmetic overflow, panic DoS, incorrect weights, and bad origin checks. Use when auditing Substrate runtimes or FRAME pallets.
Sections: 1. Purpose; 2. When to Use This Skill; 3. Platform Detection; 4. How This Skill Works; 5. Vulnerability Patterns (7 Critical Patterns); 6. Scanning Workflow; 7. Priority Guidelines; 8. Testing Recommendations; 9. Additional Resources; 10. Quick Reference Checklist

### supply-chain-risk-auditor
Audits a project's dependencies for supply-chain risk: version-matched advisories for direct dependencies and the full lockfile tree, abandoned or archived upstreams, npm publisher concentration, and install-time script execution. Use when asked to audit dependencies, assess supply-chain or third-party package risk, or review a dependency tree before an engagement.
Sections: Why the scripts do the measuring, not you; Workflow; Style for what you add; Reading the report; Rationalizations to reject; When not to use

### tech-debt-tracker
Scan codebases for technical debt, score severity, track trends, and generate prioritized remediation plans. Use when users mention tech debt, code quality, refactoring priority, debt scoring, cleanup sprints, or code health assessment. Also use for legacy code modernization planning and maintenance cost estimation.
Sections: Overview; What This Skill Provides; Quick Start — scan → prioritize → dashboard; Technical Debt Classification Framework; Common Pitfalls and How to Avoid Them

### token-integration-analyzer
Token integration and implementation analyzer based on Trail of Bits' token integration checklist. Analyzes token implementations for ERC20/ERC721 conformity, checks for 20+ weird token patterns, assesses contract composition and owner privileges, performs on-chain scarcity analysis, and evaluates how protocols handle non-standard tokens. Use when integrating or accepting arbitrary ERC20/ERC721 tokens, auditing a token implementation for standards conformity, or assessing risk from weird tokens such as fee-on-transfer, rebasing, missing return values, or blocklists.
Sections: Purpose; How This Works; Assessment Categories; Example Output; EXECUTIVE SUMMARY; 1. GENERAL CONSIDERATIONS; 2. CONTRACT COMPOSITION; 3. OWNER PRIVILEGES; 4. ERC20 CONFORMITY; 5. WEIRD TOKEN PATTERN ANALYSIS

### ton-vulnerability-scanner
Scans TON (The Open Network) smart contracts for 3 critical vulnerabilities including integer-as-boolean misuse, fake Jetton contracts, and forward TON without gas checks. Use when auditing FunC contracts.
Sections: 1. Purpose; 2. When to Use This Skill; 3. Platform Detection; 4. How This Skill Works; 5. Example Output; 6. Vulnerability Patterns (3 Patterns); 7. Scanning Workflow; 8. Reporting Format; CRITICAL Fake Jetton Contract - Missing Sender Validation; 9. Priority Guidelines

### yara-rule-authoring
Guides authoring of high-quality YARA-X detection rules for malware identification. Use when writing, reviewing, or optimizing YARA rules. Covers naming conventions, string selection, performance optimization, migration from legacy YARA, and false positive reduction. Triggers on: YARA, YARA-X, malware detection, threat hunting, IOC, signature, crx module, dex module.
Sections: Core Principles; When to Use; When NOT to Use; Platform Considerations; String Selection; Condition Design; Before Writing: Is the Sample Packed?; Debugging False Positives; Rationalizations to Reject; Toolkit

## SEO and AI search

### aeo
Answer Engine Optimization (AEO) skill — optimize content to be cited by AI language models (ChatGPT, Perplexity, Claude, Gemini, Mistral) as authoritative sources. Distinct from SEO — AEO optimizes for citation in LLM-generated responses, not search rankings. Use when planning content for AI-first search audiences, auditing existing content for E-E-A-T signals, tracking which pages get cited by which LLMs, or building a citation-friendly content strategy. Triggers — 'AEO audit', 'optimize for ChatGPT', 'get cited by Perplexity', 'LLM citation strategy', 'answer engine optimization', 'content for AI search', 'E-E-A-T audit'. Output is a markdown audit report (default) or JSON for pipeline integration. Stdlib-only Python tools.
Sections: Distinct From SEO; When To Use; When NOT To Use; Core Capabilities; References; Workflow; Configuration; Output Format; Dimension Breakdown; Top 3 Fixes

### ai-seo
When the user wants to optimize content for AI search engines, get cited by LLMs, or appear in AI-generated answers. Also use when the user mentions 'AI SEO,' 'AEO,' 'GEO,' 'LLMO,' 'answer engine optimization,' 'generative engine optimization,' 'LLM optimization,' 'AI Overviews,' 'optimize for ChatGPT,' 'optimize for Perplexity,' 'AI citations,' 'AI visibility,' 'zero-click search,' 'how do I show up in AI answers,' 'LLM mentions,' 'optimize for Claude/Gemini,' 'llms.txt,' 'OKF,' 'Open Knowledge Format,' 'knowledge bundle,' or 'agent-readable site.' Use this whenever someone wants their content to be cited or surfaced by AI assistants and AI search engines. For traditional technical and on-page SEO audits, see seo-audit. For structured data implementation, see schema.
Sections: Before Starting; How AI Search Works; AI Visibility Audit; Optimization Strategy; Free; Pro; Enterprise; Agentic Experiences; Content Types That Get Cited Most; Monitoring AI Visibility

### saas-scaffolder
Generates complete, production-ready SaaS project boilerplate including authentication, database schemas, billing integration, API routes, and a working dashboard using Next.js 14+ App Router, TypeScript, Tailwind CSS, shadcn/ui, Drizzle ORM, and Stripe. Use when the user wants to create a new SaaS app, start a subscription-based web project, scaffold a Next.js application, or mentions terms like starter template, boilerplate, new project, or wiring up auth and payments.
Sections: Input Format; File Tree Output; Key Component Patterns; Scaffold Checklist; Reference Files

### schema-markup
When the user wants to implement, audit, or validate structured data (schema markup) on their website. Use when the user mentions 'structured data,' 'schema.org,' 'JSON-LD,' 'rich results,' 'rich snippets,' 'schema markup,' 'FAQ schema,' 'Product schema,' 'HowTo schema,' or 'structured data errors in Search Console.' Also use when someone asks why their content isn't showing rich results or wants to improve AI search visibility. NOT for general SEO audits (use seo-audit) or technical SEO crawl issues (use site-architecture).
Sections: Before Starting; How This Skill Works; Schema Type Selection; Implementation Patterns; Common Mistakes; Schema and AI Search; Testing & Validation; Proactive Triggers; Output Artifacts; Communication

### seo
Comprehensive SEO analysis for any website or business type. Full site audits, single-page analysis, technical SEO (crawlability, indexability, Core Web Vitals with INP), schema markup, content quality (E-E-A-T), image optimization, sitemap analysis, and GEO for AI Overviews/ChatGPT/Perplexity. Industry detection for SaaS, e-commerce, local, publishers, agencies. Triggers on: SEO, audit, schema, Core Web Vitals, sitemap, E-E-A-T, AI Overviews, GEO, technical SEO, content quality, page speed, structured data.
Sections: Quick Reference; Orchestration Logic; Synthesis Methodology; Industry Detection; Quality Gates; Community Footer; Reference Files; Scoring Methodology; Sub-Skills; Subagents

### seo-backlinks
Backlink profile analysis: referring domains, anchor text distribution, toxic link detection, competitor gap analysis. Works with free APIs (Moz, Bing Webmaster, Common Crawl) and DataForSEO extension. Use when user says backlinks, link profile, referring domains, anchor text, toxic links, link gap, link building, disavow, or backlink audit.
Sections: Source Detection; Quick Reference; Analysis Framework; Backlink Health Score; Output Format; Error Handling; Pre-Delivery Review (MANDATORY); Post-Analysis; Reference Documentation

### seo-cluster
SERP-based semantic topic clustering for content architecture planning. Groups keywords by actual Google SERP overlap (not text similarity), designs hub-and-spoke content clusters with internal link matrices, and generates interactive visualizations. Optionally executes content creation if claude-blog is installed. Use when user says "topic cluster", "content cluster", "semantic clustering", "pillar page", "hub and spoke", "content architecture", "keyword grouping", or "cluster plan".
Sections: Quick Reference; Planning Workflow; Strategy Import; Execution Workflow; Cluster Scorecard; Map Regeneration; Output Files; Cross-Skill Integration; Error Handling; Security

### seo-competitor-pages
Generate SEO-optimized competitor comparison and alternatives pages. Covers "X vs Y" layouts, "alternatives to X" pages, feature matrices, schema markup, and conversion optimization. Use when user says "comparison page", "vs page", "alternatives page", "competitor comparison", "X vs Y", "versus", "compare competitors", or "alternative to".
Sections: Page Types; Comparison Table Generation; Schema Markup Recommendations; Keyword Targeting; Conversion-Optimized Layouts; Fairness Guidelines; Internal Linking; Output; Error Handling

### seo-content
Content quality and E-E-A-T analysis with AI citation readiness assessment. Use when user says "content quality", "E-E-A-T", "content analysis", "readability check", "thin content", or "content audit".
Sections: Google's "Who / How / Why" Test (canonical heuristic); E-E-A-T Framework (updated Sept 2025 QRG); Content Metrics; AI Content Assessment (Sept 2025 QRG addition); AI Citation Readiness (GEO signals); Content Freshness; Output; DataForSEO Integration (Optional); Error Handling; FLOW Framework Integration

### seo-content-brief
Generate competitive SEO content briefs with per-section word counts, competitor scoring, keyword density guidance, and page-type templates. Supports both new page briefs and improve-existing-page briefs. Use when user says "content brief", "write a brief", "content outline", "blog brief", "service page brief", "brief for", "writing brief", "content plan", or "outline for".
Sections: Process; Critical Rules; Keyword Density and Placement; Meta Tag Rules; Information Gain (non-negotiable); E-E-A-T Requirements; Internal Linking; Output Format; Content Brief: Primary Keyword; Outline-Only Mode

### seo-dataforseo
Live SEO data via DataForSEO MCP server. SERP analysis (Google, Bing, Yahoo, YouTube, Google Images), keyword research (volume, difficulty, intent, trends), backlink profiles, on-page analysis (Lighthouse, content parsing), competitor analysis, content analysis, business listings, AI visibility (ChatGPT scraper, LLM mention tracking), and domain analytics. Requires DataForSEO extension installed. Use when user says "dataforseo", "live SERP", "keyword volume", "backlink data", "competitor data", "AI visibility check", "LLM mentions", "image SERP", "google images", "image rankings", or "real search data".
Sections: Prerequisites; API Credit Awareness; Cost Guardrails; Quick Reference; SERP Analysis; Keyword Research; Domain & Competitor Analysis; Technical / On-Page; Content & Business Data; AI Visibility / GEO

### seo-drift
SEO drift monitoring: capture baselines of SEO-critical elements, detect changes, and track regressions over time. Git for SEO — baseline, diff, and track changes to your on-page SEO. Use when user says "SEO drift", "baseline", "track changes", "did anything break", "SEO regression", "compare SEO", "before and after", "monitor SEO changes", or "deployment check".
Sections: Commands; What It Captures; How Comparison Works; Storage; Command: baseline; Command: compare; Command: history; Cross-Skill Integration; Error Handling; Security

### seo-ecommerce
E-commerce SEO analysis: Google Shopping visibility, Amazon marketplace intelligence, product schema validation, competitor pricing analysis, and marketplace keyword gaps. Combines on-page product SEO with marketplace data from DataForSEO Merchant API. Use when user says "ecommerce SEO", "product SEO", "Google Shopping", "marketplace SEO", "product schema", "Amazon SEO", "product listings", "shopping ads", or "merchant SEO".
Sections: Commands; 1. Product Page Analysis (No DataForSEO Needed); 2. Google Shopping Intelligence (DataForSEO Merchant API); 3. Amazon Marketplace (DataForSEO); 4. Marketplace Keyword Gaps; Keyword Gap Analysis: example.com; 5. Product Schema Enhancement; Cross-Skill Integration; UCP — Universal Commerce Protocol (forward-looking); Error Handling

### seo-flow
FLOW framework integration — evidence-led SEO using the Find → Leverage → Optimize → Win loop. Surfaces stage-specific AI prompts from the FLOW knowledge base (41 prompts, CC BY 4.0). Use when user says "FLOW", "FLOW framework", "seo flow", "evidence-led SEO", "find leverage optimize win", or wants stage-specific SEO prompts.
Sections: Commands; Orchestration Logic; Context Matching (Optimize stage); Reference Files; Attribution; Error Handling

### seo-geo
Optimize content for AI Overviews (formerly SGE), ChatGPT web search, Perplexity, and other AI-powered search experiences. Generative Engine Optimization (GEO) analysis including brand mention signals, AI crawler accessibility, llms.txt compliance, passage-level citability scoring, and platform-specific optimization. Use when user says "AI Overviews", "SGE", "GEO", "AI search", "LLM optimization", "Perplexity", "AI citations", "ChatGPT search", or "AI visibility".
Sections: Primary Source: Google's AI Optimization Guide; Key Statistics; Critical Insight: Brand Mentions > Backlinks; GEO Analysis Criteria (Updated); AI Crawler Detection; llms.txt Standard; Main sections; Optional: Key facts; RSL 1.0 (Really Simple Licensing); Platform-Specific Optimization

### seo-google
Google SEO APIs: Search Console (Search Analytics, URL Inspection, Sitemaps), PageSpeed Insights v5, CrUX field data with 25-week history, Indexing API v3, and GA4 organic traffic. Provides real Google field data for Core Web Vitals, indexation status, search performance, and organic traffic trends. Use when user says "search console", "GSC", "PageSpeed", "CrUX", "field data", "indexing API", "GA4 organic", "URL inspection", "google api setup", "real CWV data", "impressions", "clicks", "CTR", "position data", "LCP", "INP", "CLS", "FCP", "TTFB", or "Lighthouse scores".
Sections: Prerequisites; Quick Reference; PageSpeed + CrUX; Search Console; Indexing API; GA4 Traffic; YouTube (Video SEO); NLP Content Analysis; Keyword Research (Google Ads); Supplementary

### seo-hreflang
Hreflang and international SEO audit, validation, and generation. Detects common mistakes, validates language/region codes, and generates correct hreflang implementations. Use when user says "hreflang", "i18n SEO", "international SEO", "multi-language", "multi-region", or "language tags".
Sections: Validation Checks; Common Mistakes; Implementation Methods; Hreflang Generation; Hreflang Sitemap Generation; Output; Cultural Adaptation Assessment; Content Parity Audit; Locale Format Validation; Reference Files

### seo-image-gen
AI image generation for SEO assets: OG/social preview images, blog hero images, schema images, product photography, infographics. Powered by Gemini via nanobanana-mcp. Requires banana extension installed. Use when user says "generate image", "OG image", "social preview", "hero image", "blog image", "product photo", "infographic", "seo image", "create visual", "image-gen", "favicon", "schema image", "pinterest pin", "generate visual", "banner", or "thumbnail".
Sections: Architecture Note; Prerequisites; Quick Reference; SEO Image Use Cases; Generation Pipeline; Post-Generation SEO Checklist; Cost Awareness; Model Routing; Error Handling; Cross-Skill Integration

### seo-images
Image optimization analysis for SEO and performance. Checks alt text, file sizes, formats, responsive images, lazy loading, CLS prevention, image SERP rankings (via DataForSEO), and image file optimization (WebP/AVIF conversion, IPTC/XMP metadata injection). Use when user says "image optimization", "alt text", "image SEO", "image size", "image audit", "optimize images", "image metadata", "image SERP", "convert to webp", or "image file optimize".
Sections: Checks; Output; Image SERP Analysis; Image File Optimization; Error Handling

### seo-local
Local SEO analysis covering Google Business Profile optimization, NAP consistency, citation health, review signals, local schema markup, location page quality, multi-location SEO, and industry-specific recommendations. Detects business type (brick-and-mortar, SAB, hybrid) and industry vertical (restaurant, healthcare, legal, home services, real estate, automotive). Use when user says "local SEO", "Google Business Profile", "GBP", "map pack", "local pack", "citations", "NAP consistency", "local rankings", "service area", "multi-location", or "local search".
Sections: Key Statistics; Business Type Detection; Industry Vertical Detection; Analysis Dimensions; AI Search Impact on Local; Reference Files; Output; Quick Wins; Medium Effort; High Impact

### seo-maps
Maps intelligence for local SEO — geo-grid rank tracking, GBP profile auditing via API, review intelligence across Google/Tripadvisor/Trustpilot, cross-platform NAP verification (Google/Bing/Apple/OSM), competitor radius mapping, and LocalBusiness schema generation from API data. Three-tier capability: free (Overpass + Geoapify), DataForSEO (full intelligence), DataForSEO + Google (maximum coverage). Use when user says "maps", "geo-grid", "rank tracking", "GBP audit", "review velocity", "competitor radius", "maps analysis", "local rank tracking", "Share of Local Voice", or "SoLV".
Sections: Quick Reference; Three-Tier Capability Detection; Geo-Grid Rank Tracking (Tier 1+); GBP Profile Audit (Tier 1 preferred, Tier 0 manual); Review Intelligence (Tier 1+); Competitor Radius Mapping (Tier 0+); Cross-Platform NAP Verification (Tier 0+); Schema Generation (Tier 0+); Reference Files; Output

### seo-page
Deep single-page SEO analysis covering on-page elements, content quality, technical meta tags, schema, images, and performance. Use when user says "analyze this page", "check page SEO", "single URL", "check this page", "page analysis", or provides a single URL for review.
Sections: What to Analyze; Output; DataForSEO Integration (Optional); Error Handling

### seo-plan
Strategic SEO planning for new or existing websites. Industry-specific templates, competitive analysis, content strategy, and implementation roadmap. Use when user says "SEO plan", "SEO strategy", "SEO planning", "content strategy", "keyword strategy", "content calendar", "site architecture", or "SEO roadmap".
Sections: Process; Industry Templates; Output; DataForSEO Integration (Optional); Error Handling

### seo-programmatic
Programmatic SEO planning and analysis for pages generated at scale from data sources. Covers template engines, URL patterns, internal linking automation, thin content safeguards, and index bloat prevention. Use when user says "programmatic SEO", "pages at scale", "dynamic pages", "template pages", "generated pages", or "data-driven SEO".
Sections: Data Source Assessment; Template Engine Planning; URL Pattern Strategy; Internal Linking Automation; Thin Content Safeguards; Canonical Strategy; Sitemap Integration; Index Bloat Prevention; Output; Error Handling

### seo-sitemap
Analyze existing XML sitemaps or generate new ones with industry templates. Validates format, URLs, and structure. Use when user says "sitemap", "generate sitemap", "sitemap issues", or "XML sitemap".
Sections: Mode 1: Analyze Existing Sitemap; Mode 2: Generate New Sitemap; Sitemap Format; Error Handling; Output

### seo-sxo
Search Experience Optimization: reads Google SERPs backwards to detect page-type mismatches, derives user stories from search intent signals, and scores pages from multiple persona perspectives. Identifies why well-optimized pages fail to rank by analyzing what Google rewards for each keyword. Use when user says "SXO", "search experience", "page type mismatch", "SERP analysis", "user story", "persona scoring", "why isn't my page ranking", "intent mismatch", or "wireframe".
Sections: Core Insight; Commands; Execution Pipeline; DataForSEO Integration; SXO Score vs SEO Health Score; Cross-Skill References; Output Format; SXO Analysis: URL; Error Handling; Quality Checklist

### seo-technical
Technical SEO audit across 9 categories: crawlability, indexability, security, URL structure, mobile, Core Web Vitals, structured data, JavaScript rendering, and IndexNow protocol. Use when user says "technical SEO", "crawl issues", "robots.txt", "Core Web Vitals", "site speed", or "security headers".
Sections: Categories; Agent-Friendly Pages (forward-looking); Output; DataForSEO Integration (Optional); Google API Integration (Optional); Error Handling

### sql-database-assistant
Use when the user asks to write SQL queries, optimize database performance, generate migrations, explore database schemas, or work with ORMs like Prisma, Drizzle, TypeORM, or SQLAlchemy.
Sections: Overview; Natural Language to SQL; Schema Exploration; Query Optimization; Migration Generation; Multi-Database Support; ORM Patterns; Data Integrity; Backup & Restore; Anti-Patterns

## Sales and customers

### channel-economics
Use when reviewing or rebalancing direct vs. partner-led channel economics — computing fully-loaded cost-to-serve per channel, channel ROI with cash / LTV / marginal lenses, and optimal channel mix subject to constraints. For Head of Commercial, RevOps, and VP Sales doing quarterly channel review when pipeline is mixed (e.g., 60% direct + 40% partner-led) and nobody actually knows which channel makes money after CAC, support load, partner discount, deal-velocity differences, retention differential, and overhead allocation are all loaded in. Outputs cost to serve, channel ROI verdicts (DOUBLE-DOWN / MAINTAIN / DEFUND / EXIT), a sensitivity-tested channel-mix recommendation, and the diminishing-returns inflection (e.g., 'which channel actually makes money — direct or partner?').
Sections: Purpose; When to use; Workflow; Scripts; Quick example; References; Assumptions; Anti-patterns; Distinct from; Forcing-question library (Matt Pocock grill discipline)

### churn-prevention
When the user wants to reduce churn, build cancellation flows, set up save offers, recover failed payments, or implement retention strategies. Also use when the user mentions 'churn,' 'cancel flow,' 'offboarding,' 'save offer,' 'dunning,' 'failed payment recovery,' 'win-back,' 'retention,' 'exit survey,' 'pause subscription,' 'involuntary churn,' 'people keep canceling,' 'churn rate is too high,' 'how do I keep users,' or 'customers are leaving.' Use this whenever someone is losing subscribers or wants to build systems to prevent it. For post-cancel win-back email sequences, see emails. For in-app upgrade paywalls, see paywalls.
Sections: Before Starting; How This Skill Works; Cancel Flow Design; Churn Prediction & Proactive Retention; Involuntary Churn: Payment Recovery; Metrics & Measurement; Common Mistakes; Tool Integrations; Related Skills

### cold-email
Write B2B cold emails and follow-up sequences that get replies. Use when the user wants to write cold outreach emails, prospecting emails, cold email campaigns, sales development emails, or SDR emails. Also use when the user mentions "cold outreach," "prospecting email," "outbound email," "email to leads," "reach out to prospects," "sales email," "follow-up email sequence," "nobody's replying to my emails," or "how do I write a cold email." Covers subject lines, opening lines, body copy, CTAs, personalization, and multi-touch follow-up sequences. For warm/lifecycle email sequences, see emails. For sales collateral beyond emails, see sales-enablement.
Sections: Before Writing; Writing Principles; Voice & Tone; Structure; Subject Lines; Follow-Up Sequences; Quality Check; What to Avoid; Data & Benchmarks; Related Skills

### contract-and-proposal-writer
Generate professional, jurisdiction-aware business documents: freelance contracts, project proposals, SOWs, NDAs, and MSAs. Structured Markdown output with docx conversion instructions. Covers US (Delaware), EU (GDPR), UK, and DACH (German law) jurisdictions. Not a substitute for legal counsel — use as strong starting points. Use when drafting a freelance contract, preparing a client proposal, writing an SOW for a new engagement, or producing an NDA before sharing sensitive material.
Sections: Overview; Core Capabilities; Key Clauses Reference; When to Use; Workflow; Jurisdiction Notes; Template A: Web Dev Fixed-Price Contract; 1. SERVICES; 2. PAYMENT; 3. INTELLECTUAL PROPERTY

### customer-research
When the user wants to conduct, analyze, or synthesize customer research. Use when the user mentions "customer research," "ICP research," "talk to customers," "analyze transcripts," "customer interviews," "survey analysis," "support ticket analysis," "voice of customer," "VOC," "build personas," "customer personas," "jobs to be done," "JTBD," "what do customers say," "what are customers struggling with," "Reddit mining," "G2 reviews," "review mining," "digital watering holes," "community research," "forum research," "competitor reviews," "customer sentiment," or "find out why customers churn/convert/buy." Use for both analyzing existing research assets AND gathering new research from online sources. For writing copy informed by research, see copywriting. For acting on research to improve pages, see cro.
Sections: Before Starting; Two Modes of Research; Mode 1: Analyzing Existing Research Assets; Mode 2: Digital Watering Hole Research; Top Themes (ranked by frequency × intensity); Persona Generation; Persona Name — Role/Title; Deliverable Formats; Questions to Ask Before Proceeding; Related Skills

### customer-success-manager
Monitors customer health, predicts churn risk, and identifies expansion opportunities using weighted scoring models for SaaS customer success. Use when analyzing customer accounts, reviewing retention metrics, scoring at-risk customers, or when the user mentions churn, customer health scores, upsell opportunities, expansion revenue, retention analysis, or customer analytics. Runs three Python CLI tools to produce deterministic health scores, churn risk tiers, and prioritized expansion recommendations across Enterprise, Mid-Market, and SMB segments.
Sections: Table of Contents; Input Requirements; Output Formats; How to Use; Scripts; Reference Guides; Templates; Best Practices; Limitations

### deal-desk
Use when reviewing a specific inbound deal before close — when sales has asked for a discount that exceeds AE authority, when the customer has redlined the MSA, when per-deal economics (margin after discount, multi-year payment shape, indemnity exposure) need to be quantified, or when discount approval needs to be routed to a named human approver (Sales Director, VP Sales, CFO, CRO, General Counsel). Covers deal review, discount approval routing, per-deal margin scoring, deal exception handling, MSA redline triage, contract landmine detection (uncapped indemnity, MFN, perpetual license-back, missing DPA), and named-approver chain assembly. NEVER auto-approves — every output is a numeric scorecard plus a routing recommendation to a named human.
Sections: Purpose; When to use; Workflow; Scripts; References; Assumptions; Anti-patterns; Distinct from; Quick examples; Forcing-question library (Matt Pocock grill discipline)

### partnerships-architect
Use when a startup is approached by a prospective partner and someone has to decide should we sign this partner, at what partner tier (referral / reseller / OEM / SI-consulting / strategic alliance), with what joint GTM commitment, and at what revshare. Classifies partner tier from independent-demand evidence vs. preferential-terms hunting, designs a 90-day joint GTM plan, models revshare against direct-sale margin, and surfaces kill criteria for unwinding under-performing partnerships. For Head of Partnerships, Head of BD, and Founder-CEOs doing reseller agreement, OEM deal, or strategic alliance review — not technical sale enablement, not channel cost economics, not M&A.
Sections: Purpose; When to use; Workflow; Scripts; Quick example; References; Assumptions; Anti-patterns; Distinct from; Forcing-question library (Matt Pocock grill discipline)

### procurement-optimizer
Use when running an annual SaaS audit, doing category-level spend review, or rationalizing the supplier base — when the user needs a spend audit, spend categorization (UNSPSC-aligned with Pareto breakdown and industry profiles), purchasing-cycle analysis (bottleneck categories per Goldratt's Theory of Constraints), or risk-balanced supplier consolidation that refuses single-source recommendations for tier-1 categories without a documented break-glass plan. Triggers on "spend audit", "SaaS audit", "spend categorization", "supplier rationalization", "supplier consolidation", "category strategy", "duplicate SaaS", "renewal cluster".
Sections: Purpose; When to use; When NOT to use; Workflow; Scripts; Quick example; References; Assumptions; Anti-patterns; Distinct from

### prospecting
When the user wants to find, qualify, and build a list of prospects to reach out to — across B2B SaaS, general B2B, or local small businesses. Also use when the user mentions "prospecting," "build a prospect list," "find prospects," "find leads," "lead gen list," "find SaaS companies that," "find B2B companies," "find local businesses," "ICP-fit accounts," "who should we go after," "outbound list," "target account list," "find clients near me," "businesses without websites," "prospect research," or "qualified leads." Use this for the list-building and qualification phase. For writing the outbound copy after the list is built, see cold-email. For deep competitive research on specific accounts, see competitor-profiling.
Sections: Before Starting; Pick the Branch; Shared Framework (all branches); Compliance Guardrails; Inputs to Collect; Tool Selection Quick Picks; Output Formats; Quality Checks (before finalizing); Common Mistakes; Task-Specific Questions

### revops
When the user wants help with revenue operations, lead lifecycle management, or marketing-to-sales handoff processes. Also use when the user mentions 'RevOps,' 'revenue operations,' 'lead scoring,' 'lead routing,' 'MQL,' 'SQL,' 'pipeline stages,' 'deal desk,' 'CRM automation,' 'marketing-to-sales handoff,' 'data hygiene,' 'leads aren't getting to sales,' 'pipeline management,' 'lead qualification,' or 'when should marketing hand off to sales.' Use this for anything involving the systems and processes that connect marketing to revenue. For cold outreach emails, see cold-email. For email drip campaigns, see emails. For pricing decisions, see pricing.
Sections: Before Starting; Core Principles; Lead Lifecycle Framework; Lead Scoring; Lead Routing; Pipeline Stage Management; CRM Automation Workflows; Deal Desk Processes; Data Hygiene & Enrichment; RevOps Metrics Dashboard

### rfp-responder
Use when an RFP, RFI, RFQ, security questionnaire, vendor questionnaire, or proposal request arrives and the team needs a structured response — parsing multi-section buyer-dictated requirements (MANDATORY vs WEIGHTED vs NICE-TO-HAVE), building a Shipley-method proof-point matrix mapping each requirement to a verifiable proof point, articulating 3-5 win-themes that ladder up across requirements, and producing a Shipley-derived winrate estimate that informs a bid / no-bid / partner-bid recommendation. For Bid Managers, Proposal Leads, Directors of Sales, and Sales Engineers at the response-strategy moment. Surfaces GAP requirements explicitly — never invents claims. NOT free-form proposal narrative authoring, NOT contract redline, NOT marketing collateral.
Sections: Purpose; When to use; Workflow; Scripts; References; Assumptions; Anti-patterns; Distinct from; Forcing-question library (Matt Pocock grill discipline)

### sales-enablement
When the user wants to create sales collateral, pitch decks, one-pagers, objection handling docs, or demo scripts. Also use when the user mentions 'sales deck,' 'pitch deck,' 'one-pager,' 'leave-behind,' 'objection handling,' 'deal-specific ROI analysis,' 'demo script,' 'talk track,' 'sales playbook,' 'proposal template,' 'buyer persona card,' 'help my sales team,' 'sales materials,' or 'what should I give my sales reps.' Use this for any document or asset that helps a sales team close deals. For competitor comparison pages and battle cards, see competitors. For marketing website copy, see copywriting. For cold outreach emails, see cold-email. For the offer being sold (bonuses, guarantees, pricing structure), see offers.
Sections: Before Starting; Core Principles; Sales Deck / Pitch Deck; One-Pagers / Leave-Behinds; Objection Handling Docs; ROI Calculators & Value Props; Demo Scripts & Talk Tracks; Case Study Briefs (Sales Format); Proposal Templates; Sales Playbooks

### sales-engineer
Analyzes RFP/RFI responses for coverage gaps, builds competitive feature comparison matrices, and plans proof-of-concept (POC) engagements for pre-sales engineering. Use when responding to RFPs, bids, or proposal requests; comparing product features against competitors; planning or scoring a customer POC or sales demo; preparing a technical proposal; or performing win/loss competitor analysis. Handles tasks described as 'RFP response', 'bid response', 'proposal response', 'competitor comparison', 'feature matrix', 'POC planning', 'sales demo prep', or 'pre-sales engineering'.
Sections: 5-Phase Workflow; Python Automation Tools; Reference Knowledge Bases; Asset Templates; Integration Points

### stripe-integration-expert
Production-grade Stripe integrations: subscriptions with trials and proration, one-time payments, usage-based billing, checkout sessions, idempotent webhook handlers, customer portal, and invoicing. Covers Next.js, Express, and Django patterns. Use when integrating Stripe for the first time, debugging webhook reliability issues, migrating from a different payment provider, or adding usage-based billing to an existing subscription product.
Sections: Overview; Core Capabilities; When to Use; Subscription Lifecycle State Machine; Stripe Client Setup; Checkout Session (Next.js App Router); Subscription Upgrade/Downgrade; Complete Webhook Handler (Idempotent); Usage-Based Billing; Customer Portal

### vendor-management
Use when reviewing, scoring, or auditing third-party SaaS / vendor relationships — running a vendor scorecard with industry tuning, tracking SLA compliance with credit-claim flags, classifying third-party risk across 4 risk vectors, preparing a tier-1 vendor review, or auditing the SaaS portfolio. Forks context so large vendor catalogs (50-500 line items) and SLA logs don't pollute the parent thread. Triggers on "vendor SLA", "vendor scorecard", "third-party risk", "TPRM", "vendor review", "supplier performance", "vendor health check", "renewal review".
Sections: Purpose; When to use; When NOT to use; Workflow; Scripts; Quick example; References; Assumptions; Anti-patterns; Distinct from

## Marketing, growth and copy

### ad-creative
When the user wants to generate, iterate, or scale ad creative — headlines, descriptions, primary text, or full ad variations — for any paid advertising platform. Also use when the user mentions 'ad copy variations,' 'ad creative,' 'generate headlines,' 'RSA headlines,' 'bulk ad copy,' 'ad iterations,' 'creative testing,' 'ad performance optimization,' 'write me some ads,' 'Facebook ad copy,' 'Google ad headlines,' 'LinkedIn ad text,' or 'I need more ad variations.' Use this whenever someone needs to produce ad copy at scale or iterate on existing ads. For campaign strategy and targeting, see ads. For landing page copy, see copywriting.
Sections: Before Starting; How This Skill Works; Platform Specs; Generating Ad Visuals; Generating Ad Copy; Iterating from Performance Data; Iteration Log; Writing Quality Standards; Output Formats; Angle: Pain Point — Manual Reporting

### ads
When the user wants help with paid advertising campaigns on Google Ads, Meta (Facebook/Instagram), LinkedIn, Twitter/X, or other ad platforms. Also use when the user mentions 'PPC,' 'paid media,' 'ROAS,' 'CPA,' 'ad campaign,' 'retargeting,' 'audience targeting,' 'Google Ads,' 'Facebook ads,' 'LinkedIn ads,' 'ad budget,' 'cost per click,' 'ad spend,' or 'should I run ads.' Use this for campaign strategy, audience targeting, bidding, and optimization. For bulk ad creative generation and iteration, see ad-creative. For landing page optimization, see cro.
Sections: Before Starting; Platform Selection Guide; Campaign Structure Best Practices; Ad Copy Frameworks; Audience Targeting Overview; Creative Best Practices; Campaign Optimization; Retargeting Strategies; Reporting & Analysis; Platform Setup

### aso
When the user wants to audit or optimize an App Store or Google Play listing. Also use when the user mentions 'ASO audit,' 'app store optimization,' 'optimize my app listing,' 'improve app visibility,' 'app store ranking,' 'audit my listing,' 'why aren't people downloading my app,' 'improve my app conversion,' 'keyword optimization for app,' or 'compare my app to competitors.' Use when the user shares an App Store or Google Play URL and wants to improve it.
Sections: When to Use; Before Auditing; Phase 1 — Identify Store & Fetch; Phase 1.5 — Assess Brand Maturity; Phase 2 — Score Each Dimension; Phase 3 — Competitor Comparison (Optional); Phase 4 — Generate Report; Platform-Specific Rules; Common Issues Checklist; Task-Specific Questions

### brand
Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Activate for branded content, tone of voice, marketing assets, brand compliance, style guides.
Sections: When to Use; Script Paths; Quick Start; Brand Sync Workflow; Subcommands; References; Scripts; Templates; Routing

### brand-guidelines
Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic's look-and-feel. Use it when brand colors or style guidelines, visual formatting, or company design standards apply.
Sections: Overview; Brand Guidelines; Features; Technical Details

### business-growth-skills
Router/index for the 4 business & growth skills bundled in this plugin: customer-success-manager (health scoring, churn risk, expansion), sales-engineer (RFP analysis, competitive matrices, PoC planning), revenue-operations (pipeline, forecast accuracy, GTM efficiency), and contract-and-proposal-writer. Use when a growth/revenue request doesn't obviously match one skill and you need to pick the right one (e.g., 'which accounts are at risk', 'should we bid on this RFP').
Sections: Routing table; Quick start; Rules

### campaign-analytics
Analyzes campaign performance with multi-touch attribution, funnel conversion analysis, and ROI calculation for marketing optimization. Use when analyzing marketing campaigns, ad performance, attribution models, conversion rates, or calculating marketing ROI, ROAS, CPA, and campaign metrics across channels.
Sections: Input Requirements; Output Formats; Typical Analysis Workflow; How to Use; Scripts; Reference Guides; Best Practices; Limitations; Related Skills

### co-marketing
When the user wants to find co-marketing partners, plan joint campaigns, or brainstorm partnership opportunities. Use when the user says 'co-marketing,' 'partner marketing,' 'joint campaign,' 'who should we partner with,' 'integration marketing,' 'cross-promotion,' 'collaborate with another company,' 'partnership ideas,' or 'co-brand.' For customer referral programs, see referrals. For launch-specific partnerships, see launch.
Sections: Before Starting; When to Use This Skill; Partner Identification Framework; Co-Marketing Campaign Types; Brainstorming Partner Campaigns; Approaching Potential Partners; Structuring the Partnership; Measuring Co-Marketing Success; Co-Marketing Checklist; Task-Specific Questions

### codebase-onboarding
Analyze a codebase and generate onboarding documentation for engineers, tech leads, and contractors. Fast fact-gathering and repeatable onboarding outputs. Use when onboarding a new engineer, writing architecture-overview docs for a new project, or producing tech-lead briefings for unfamiliar repos.
Sections: Overview; Core Capabilities; When to Use; Quick Start; Recommended Workflow; Onboarding Document Template; Common Pitfalls; Best Practices

### community-marketing
Build and leverage online communities to drive product growth and brand loyalty. Use when the user wants to create a community strategy, grow a Discord or Slack community, manage a forum or subreddit, build brand advocates, increase word-of-mouth, drive community-led growth, engage users post-signup, or turn customers into evangelists. Trigger phrases: "build a community," "community strategy," "Discord community," "Slack community," "community-led growth," "brand advocates," "user community," "forum strategy," "community engagement," "grow our community," "ambassador program," "community flywheel."
Sections: Before You Start; Community Strategy Principles; Playbooks by Goal; Platform Selection Guide; Community Health Metrics; Output Formats; Task-Specific Questions; Related Skills

### competitor-alternatives
When the user wants to create competitor comparison or alternative pages for SEO and sales enablement. Also use when the user mentions 'alternative page,' 'vs page,' 'competitor comparison,' 'comparison page,' '[Product] vs [Product],' '[Product] alternative,' 'competitive landing pages,' 'switch from competitor,' or 'comparison content.' Covers four formats: singular alternative, plural alternatives, you vs competitor, and competitor vs competitor. Emphasizes deep research, modular content architecture, and varied section types beyond feature tables.
Sections: Initial Assessment; Core Principles; Page Formats; Essential Sections; Content Architecture; Research Process; SEO Considerations; Output Format; Task-Specific Questions; Proactive Triggers

### competitor-profiling
When the user wants to research, profile, or analyze competitors from their URLs. Also use when the user mentions 'competitor profile,' 'competitor research,' 'competitor analysis,' 'profile this competitor,' 'analyze competitor,' 'competitive intelligence,' 'competitor deep dive,' 'who are my competitors,' 'competitor landscape,' 'competitor dossier,' 'competitive audit,' or 'research these competitors.' Input is a list of competitor URLs. Output is structured competitor profile markdown files. For creating comparison/alternative pages from profiles, see competitors. For sales-specific battle cards, see sales-enablement.
Sections: Initial Assessment; Core Principles; Saving Raw Data; Research Process; Output Format; At a Glance; Positioning & Messaging; Product & Features; Pricing; Customers & Social Proof

### content-creator
Deprecated redirect skill that routes legacy 'content creator' requests to the correct specialist. Use when a user invokes 'content creator', asks to write a blog post, article, guide, or brand voice analysis (routes to content-production), or asks to plan content, build a topic cluster, or create a content calendar (routes to content-strategy). Does not handle requests directly — identifies user intent and redirects to content-production for writing/SEO/brand-voice tasks or content-strategy for planning tasks.
Sections: Why the Change; Proactive Triggers; Output Artifacts; Communication; Related Skills

### content-humanizer
Makes AI-generated content sound genuinely human — not just cleaned up, but alive. Use when content feels robotic, uses too many AI clichés, lacks personality, or reads like it was written by committee. Triggers: 'this sounds like AI', 'make it more human', 'add personality', 'it feels generic', 'sounds robotic', 'fix AI writing', 'inject our voice'. NOT for initial content creation (use content-production). NOT for SEO optimization (use content-production Mode 3).
Sections: Before Starting; How This Skill Works; Mode 1: Detect — AI Pattern Analysis; Mode 2: Humanize — Pattern Removal and Rhythm Fix; Mode 3: Voice Injection — Brand Character; Proactive Triggers; Output Artifacts; Communication; Related Skills

### content-production
Full content production pipeline — takes a topic from blank page to published-ready piece. Use when you need to execute content: write a blog post, article, or guide end-to-end. Triggers: 'write a post about', 'draft an article', 'create content for', 'help me write', 'I need a blog post'. NOT for content strategy or calendar planning (use content-strategy). NOT for repurposing existing content (use content-repurposing). NOT for social captions only.
Sections: Before Starting; How This Skill Works; Mode 1: Research & Brief; Mode 2: Draft; Mode 3: Optimize & Polish; Proactive Triggers; Output Artifacts; Communication; Related Skills

### copy-editing
When the user wants to edit, review, or improve existing marketing copy, or refresh outdated content. Also use when the user mentions 'edit this copy,' 'review my copy,' 'copy feedback,' 'proofread,' 'polish this,' 'make this better,' 'copy sweep,' 'tighten this up,' 'this reads awkwardly,' 'clean up this text,' 'too wordy,' 'sharpen the messaging,' 'refresh this content,' 'update this page,' 'this content is outdated,' or 'content audit.' Use this when the user already has copy and wants it improved or refreshed rather than rewritten from scratch. For writing new copy, see copywriting.
Sections: Core Philosophy; The Seven Sweeps Framework; Expert Panel Scoring; Quick-Pass Editing Checks; Copy Editing Checklist; Common Copy Problems & Fixes; Working with Copy Sweeps; References; Content Refresh Editing; Task-Specific Questions

### copywriting
When the user wants to write, rewrite, or improve marketing copy for any page — including homepage, landing pages, pricing pages, feature pages, about pages, or product pages. Also use when the user says "write copy for," "improve this copy," "rewrite this page," "marketing copy," "headline help," "CTA copy," "value proposition," "tagline," "subheadline," "hero section copy," "above the fold," "this copy is weak," "make this more compelling," or "help me describe my product." Use this whenever someone is working on website text that needs to persuade or convert. For email copy, see emails. For popup copy, see popups. For editing existing copy, see copy-editing. For the offer underneath the copy (bonuses, guarantees, value framing), see offers.
Sections: Before Writing; Copywriting Principles; Writing Style Rules; Best Practices; Page Structure Framework; CTA Copy Guidelines; Page-Specific Guidance; Voice and Tone; Output Format; Related Skills

### defuddle
Extract clean markdown content from web pages using Defuddle CLI, removing clutter and navigation to save tokens. Use instead of WebFetch when the user provides a URL to read or analyze, for online documentation, articles, blog posts, or any standard web page. Do NOT use for URLs ending in .md — those are already markdown, use WebFetch directly.
Sections: Usage; Output formats

### directory-submissions
When the user wants to submit their product to startup, SaaS, AI, agent, MCP, no-code, or review directories for backlinks, domain rating, and discovery. Also use when the user mentions "directory submissions," "submit to directories," "backlinks from directories," "list my product," "submit to Product Hunt," "BetaList," "TAAFT," "Futurepedia," "G2 listing," "Capterra listing," "AlternativeTo," "SaaSHub," "AI directories," "MCP registry," "agent directory," "dofollow backlinks," "launch directories," or "directory tracker." Use this whenever someone is planning the directory layer of a product launch or an ongoing backlink campaign. For the broader launch moment, see launch. For programmatic SEO pages that should live behind these backlinks, see programmatic-seo. For AI citation optimization, see ai-seo.
Sections: Before Starting; Core Philosophy; The Three Hard Rules; Workflow; Product Hunt Deep Dive (The Anchor Event); Reviews Playbook (G2 / Capterra / TrustRadius); Destination Pages Strategy (What the Backlinks Point At); GEO (Generative Engine Optimization); Community & Ongoing Distribution; KPIs & Tracking

### email-template-builder
Build complete transactional email systems: React Email templates, provider integration (Resend, Postmark, SendGrid, AWS SES), preview server, i18n support, dark mode, spam optimization, analytics tracking. Use when adding transactional email to a new product, migrating between email providers, refactoring legacy email templates for accessibility, or adding internationalization to existing templates.
Sections: Overview; Core Capabilities; When to Use; Project Structure; Base Email Layout; Welcome Email; Invoice Email; Unified Send Function; Preview Server Setup; i18n Support

### emails
When the user wants to create or optimize an email sequence, drip campaign, automated email flow, or lifecycle email program. Also use when the user mentions "email sequence," "drip campaign," "nurture sequence," "onboarding emails," "welcome sequence," "re-engagement emails," "email automation," "lifecycle emails," "trigger-based emails," "email funnel," "email workflow," "what emails should I send," "welcome series," or "email cadence." Use this for any multi-email automated flow. For cold outreach emails, see cold-email. For in-app onboarding, see onboarding.
Sections: Initial Assessment; Core Principles; Email Sequence Strategy; Sequence Types Overview; Email Types by Category; Email Copy Guidelines; Output Format; Task-Specific Questions; Tool Integrations; Related Skills

### form-cro
When the user wants to optimize any form that is NOT signup/registration — including lead capture forms, contact forms, demo request forms, application forms, survey forms, or checkout forms. Also use when the user mentions "form optimization," "lead form conversions," "form friction," "form fields," "form completion rate," or "contact form." For signup/registration forms, see signup-flow-cro. For popups containing forms, see popup-cro.
Sections: Initial Assessment; Core Principles; Tools; Output Format; Experiment Ideas; Task-Specific Questions; Related Skills; Communication; Proactive Triggers; Output Artifacts

### hub-spawn
Launch N parallel subagents in isolated git worktrees to compete on the session task. Use when the user runs /hub-spawn or asks to start the competing agents for an initialized AgentHub session.
Sections: Usage; Templates; What It Does; Critical Rules; After Spawn

### landing
Generates a premium single-page HTML landing page with 3D CSS animations, GSAP scroll effects, and mouse-parallax depth. Forcing intake (product + elevator pitch, audience register, brand overrides, tone) locks down positioning before any copy or markup is written, so the page reflects the actual product rather than generic boilerplate. Use whenever the user says 'landing for X', 'create a landing page', 'build a landing page', 'make a landing page for X', 'I need a web page for Y', or provides product/service details and wants a polished website. Also triggers on 'promotional page', 'product page', 'one-pager', 'web presence', 'sales page'. Outputs a single self-contained HTML file (Claude Code) or HTML artifact (Claude.ai). Supports configurable brand colors via CSS custom property overrides.
Sections: Invocation Triggers; Delivery Mode; Phase 0: Grill-Me Intake (4 forcing questions, one at a time); Content Extraction (with Fallback Strategy); Brand System Specification; Section 1: Hero; Section 2: Features; Section 3: Closing CTA; Animation Patterns; Required CDN Dependencies

### landing-page-generator
Generates high-converting landing pages as complete Next.js/React (TSX) components with Tailwind CSS. Creates hero sections, feature grids, pricing tables, FAQ accordions, testimonial blocks, and CTA sections using proven copy frameworks (PAS, AIDA, BAB). Outputs SEO meta tags, structured data, and performance-optimised code targeting Core Web Vitals (LCP < 1s, CLS < 0.1). Use when the user asks to create a landing page, marketing page, homepage, single-page site, lead capture page, campaign page, promo page, or conversion-optimised web page — or when they want to A/B test landing page variants or replace a static page with one designed to convert.
Sections: Core Capabilities; Generation Workflow; Triggering This Skill; Design Style Reference; Copy Frameworks; Representative Component: Hero (Centered Gradient — Dark SaaS); Other Section Patterns; SEO Checklist; Performance Targets; Common Pitfalls

### launch
When the user wants to plan a product launch, feature announcement, or release strategy. Also use when the user mentions 'launch,' 'Product Hunt,' 'feature release,' 'announcement,' 'go-to-market,' 'beta launch,' 'early access,' 'waitlist,' 'product update,' 'how do I launch this,' 'launch checklist,' 'GTM plan,' or 'we're about to ship.' Use this whenever someone is preparing to release something publicly. For ongoing marketing after launch, see marketing-ideas. For the offer being launched (bonuses, guarantees, scarcity, naming), see offers.
Sections: Before Starting; Core Philosophy; The ORB Framework; Five-Phase Launch Approach; Product Hunt Launch Strategy; Post-Launch Product Marketing; Ongoing Launch Strategy; Launch Checklist; Task-Specific Questions; Related Skills

### lead-magnets
When the user wants to create, plan, or optimize a lead magnet for email capture or lead generation. Also use when the user mentions "lead magnet," "gated content," "content upgrade," "downloadable," "ebook," "cheat sheet," "checklist," "template download," "opt-in," "freebie," "PDF download," "resource library," "content offer," "email capture content," "Notion template," "spreadsheet template," or "what should I give away for emails." Use this for planning what to create and how to distribute it. For interactive tools as lead magnets, see free-tools. For writing the actual content, see copywriting. For the email sequence after capture, see emails.
Sections: Before Planning; Lead Magnet Principles; Lead Magnet Types; Matching Lead Magnets to Buyer Stage; Gating Strategy; Landing Page & Delivery; Promotion & Distribution; Measuring Success; Output Format; Task-Specific Questions

### libfuzzer
Sets up and runs libFuzzer, the coverage-guided fuzzer built into LLVM, on C/C++ code that compiles with Clang. Covers harness structure, -fsanitize=fuzzer builds, corpus and dictionary management, sanitizer integration, and campaign triage. Use when writing or debugging an LLVMFuzzerTestOneInput harness, starting fuzzing on a C/C++ library, choosing between libFuzzer and AFL++, or working out why a libFuzzer run finds nothing.
Sections: When to Use; Quick Start; Installation; Writing a Harness; Compilation; Corpus Management; Running Campaigns; Fuzzing Dictionary; Coverage Analysis; Sanitizer Integration

### marketing-context
Create and maintain the marketing context document that all marketing skills read before starting. Use when the user mentions 'marketing context,' 'brand voice,' 'set up context,' 'target audience,' 'ICP,' 'style guide,' 'who is my customer,' 'positioning,' or wants to avoid repeating foundational information across marketing tasks. Run this at the start of any new project before using other marketing skills.
Sections: How This Skill Works; Sections to Capture; Output Template; Validate the Result; Tips; Proactive Triggers; Output Artifacts; Communication; Related Skills

### marketing-demand-acquisition
Creates demand generation campaigns, optimizes paid ad spend across LinkedIn, Google, and Meta, develops SEO strategies, and structures partnership programs. Use when planning demand gen strategy, growth marketing, advertising campaigns, PPC optimization, lead generation, pipeline generation, or marketing budgets. Covers multi-channel acquisition (Google Ads, LinkedIn Ads, Meta Ads), CAC analysis, MQL/SQL workflows, attribution modeling, technical SEO, and co-marketing partnerships. Default calibration profile is a Series A+ B2B SaaS scaling internationally (EU/US/Canada, hybrid PLG/Sales-Led) — adapt benchmarks for other stages and motions rather than skipping the skill.
Sections: Table of Contents; Core KPIs; Demand Generation Framework; Paid Media Channels; SEO Strategy; Partnerships; Attribution; Tools; References; Channel Benchmarks (B2B SaaS Series A)

### marketing-ideas
When the user needs marketing ideas, inspiration, or strategies for their SaaS or software product. Also use when the user asks for 'marketing ideas,' 'growth ideas,' 'how to market,' 'marketing strategies,' 'marketing tactics,' 'ways to promote,' 'ideas to grow,' 'what else can I try,' 'I don't know how to market this,' 'brainstorm marketing,' or 'what marketing should I do.' Use this as a starting point whenever someone is stuck or looking for inspiration on how to grow. For specific channel execution, see the relevant skill (ads, social, emails, etc.).
Sections: How to Use This Skill; Ideas by Category (Quick Reference); Implementation Tips; Top Ideas by Use Case; Output Format; Task-Specific Questions; Related Skills

### marketing-ops
Central router for the marketing skill ecosystem. Use when unsure which marketing skill to use, when orchestrating a multi-skill campaign, or when coordinating across content, SEO, CRO, channels, and analytics. Also use when the user mentions 'marketing help,' 'campaign plan,' 'what should I do next,' 'marketing priorities,' or 'coordinate marketing.'
Sections: Before Starting; How This Skill Works; Routing Matrix; Tools; Campaign Orchestration; Quality Gate; Proactive Triggers; Output Artifacts; Communication; Related Skills

### marketing-plan
When the user needs a comprehensive marketing plan for a client, a company they advise, or their own product. Also use when the user mentions "marketing plan," "growth plan," "GTM plan," "go-to-market plan," "AARRR plan," "90-day marketing plan," "12-month marketing roadmap," "fractional CMO plan," or "fCMO plan." Generates an exhaustive 13-section plan structured by AARRR (Acquisition, Activation, Retention, Referral, Revenue), customized to the client's current budget, team, and stage, mapped to future funding milestones, cross-referenced with the 139-idea marketing-ideas library and an embedded 17-section current-state audit rubric, with a full marketing operations stack showing which skills and MCP/API integrations execute each part. Outputs a Notion-paste-ready markdown document. For positioning and ICP context before planning, see product-marketing. For stage-specific deep work, see onboarding, signup, emails, referrals, pricing.
Sections: When to use; How this skill is invoked; The three phases; The 13-section plan structure; The AARRR framing; The current-state rubric; Cross-references — skills this plan integrates with; The marketing operations stack; Funding-stage capability unlocks; Setting the budget scientifically

### marketing-psychology
When the user wants to apply psychological principles, mental models, or behavioral science to marketing. Also use when the user mentions 'psychology,' 'mental models,' 'cognitive bias,' 'persuasion,' 'behavioral science,' 'why people buy,' 'decision-making,' 'consumer behavior,' 'anchoring,' 'social proof,' 'scarcity,' 'loss aversion,' 'framing,' or 'nudge.' Use this whenever someone wants to understand or leverage how people think and make decisions in a marketing context. For applying psychology to specific pages, see cro; for pricing tactics, see pricing; for copy framing, see copywriting.
Sections: How to Use This Skill; Foundational Thinking Models; Understanding Buyers & Human Psychology; Influencing Behavior & Persuasion; Pricing Psychology; Design & Delivery Models; Growth & Scaling Models; Quick Reference; Task-Specific Questions; Related Skills

### marketing-skills
Directory and router for the marketing skills library. Use when you need to find the right marketing skill for a task, see what marketing capabilities exist, or get oriented in this plugin. 44 specialist skills across 8 pods (content, SEO + AEO, CRO, channels, growth, intelligence, sales enablement, ops), 59 stdlib Python tools. Routes to one skill — it does not execute marketing work itself.
Sections: Start Here; Route Table; Python Tools; Rules

### offers
When the user wants to design, construct, or improve an offer — the thing they actually sell — including value framing, bonus stacking, guarantee design, scarcity/urgency, naming, and payment structure. Also use when the user mentions 'offer,' 'offer design,' 'build an offer,' 'grand slam offer,' 'irresistible offer,' 'value stack,' 'bonus stack,' 'guarantee,' 'risk reversal,' 'money-back guarantee,' 'scarcity,' 'urgency,' 'high-ticket offer,' 'productize a service,' 'naming an offer,' 'payment plan,' 'down-sell,' 'upsell offer,' or 'why isn't my offer converting.' Best for services, agencies, courses, coaching, info products, high-ticket B2B, and direct-response. If you run pure self-serve SaaS, read pricing first — tiers and packaging do more work there. For price level itself (tiers, freemium, value metric), see pricing. For the page that presents the offer, see copywriting. For the launch moment, see launch. For sales collateral, see sales-enablement.
Sections: Before Starting; Core Philosophy; The Value Equation; The Anatomy of a Complete Offer; Reference Library; The Diagnostic Loop; When NOT to Use Offer-Design Tactics; Banned Vocabulary; Related Skills

### onboarding-cro
When the user wants to optimize post-signup onboarding, user activation, first-run experience, or time-to-value. Also use when the user mentions "onboarding flow," "activation rate," "user activation," "first-run experience," "empty states," "onboarding checklist," "aha moment," or "new user experience." For signup/registration optimization, see signup-flow-cro. For ongoing email sequences, see email-sequence.
Sections: Initial Assessment; Core Principles; Defining Activation; Onboarding Flow Design; Multi-Channel Onboarding; Handling Stalled Users; Measurement; Output Format; Common Patterns by Product Type; Experiment Ideas

### page-cro
When the user wants to optimize, improve, or increase conversions on any marketing page — including homepage, landing pages, pricing pages, feature pages, or blog posts. Also use when the user says "CRO," "conversion rate optimization," "this page isn't converting," "improve conversions," or "why isn't this page working." For signup/registration flows, see signup-flow-cro. For post-signup activation, see onboarding-cro. For forms outside of signup, see form-cro. For popups/modals, see popup-cro.
Sections: Initial Assessment; CRO Analysis Framework; Tools; Output Format; Page-Specific Frameworks; Experiment Ideas; Task-Specific Questions; Related Skills; Communication; Proactive Triggers

### paywall-upgrade-cro
When the user wants to create or optimize in-app paywalls, upgrade screens, upsell modals, or feature gates. Also use when the user mentions "paywall," "upgrade screen," "upgrade modal," "upsell," "feature gate," "convert free to paid," "freemium conversion," "trial expiration screen," "limit reached screen," "plan upgrade prompt," or "in-app pricing." Distinct from public pricing pages (see page-cro) — this skill focuses on in-product upgrade moments where the user has already experienced value.
Sections: Initial Assessment; Core Principles; Paywall Trigger Points; Paywall Screen Components; Specific Paywall Types; Timing and Frequency; Upgrade Flow Optimization; A/B Testing; Anti-Patterns to Avoid; Task-Specific Questions

### popups
When the user wants to create or optimize popups, modals, overlays, slide-ins, or banners for conversion purposes. Also use when the user mentions "exit intent," "popup conversions," "modal optimization," "lead capture popup," "email popup," "announcement banner," "overlay," "collect emails with a popup," "exit popup," "scroll trigger," "sticky bar," or "notification bar." Use this for any overlay or interrupt-style conversion element. For forms outside of popups, see cro. For general page conversion optimization, see cro.
Sections: Initial Assessment; Core Principles; Trigger Strategies; Popup Types; Design Best Practices; Copy Formulas; Frequency and Rules; Compliance and Accessibility; Measurement; Output Format

### postmortem
/em:postmortem — Honest analysis of what went wrong. Use after a failed launch, missed quarter, or bad hire to run a blameless 5-Whys retrospective with a change register — e.g. dissecting why the Q3 release slipped six weeks.
Sections: Why Most Post-Mortems Fail; The Framework; Post-Mortem Output Format; The Tone of Good Post-Mortems

### product-marketing
When the user wants to create or update their product marketing context document. Also use when the user mentions 'product context,' 'marketing context,' 'set up context,' 'positioning,' 'who is my target audience,' 'describe my product,' 'ICP,' 'ideal customer profile,' or wants to avoid repeating foundational information across marketing tasks. Use this at the start of any new project before using other marketing skills — it creates `.agents/product-marketing.md` that all other skills reference for product, audience, and positioning context.
Sections: Workflow; Sections to Capture; Step 3: Create the Document; Product Overview; Target Audience; Personas; Problems & Pain Points; Competitive Landscape; Differentiation; Objections

### public-relations
When the user wants help with public relations, earned media, press coverage, journalist outreach, or media strategy (not pull requests). Also use when the user mentions 'PR,' 'public relations,' 'press,' 'press release,' 'press coverage,' 'media outreach,' 'pitch a journalist,' 'get featured,' 'media list,' 'media kit,' 'press kit,' 'newsjacking,' 'news hijack,' 'HARO,' 'Qwoted,' 'Featured,' 'Help A Reporter,' 'reporter request,' 'tech press,' 'TechCrunch,' 'earned media,' 'thought leadership placement,' 'op-ed,' 'guest article,' 'press contacts,' or 'how do I get press.' Use this for earned media work — finding journalists, pitching stories, newsjacking, and responding to press requests. For startup/SaaS/AI directory submissions, see directory-submissions. For product launches, see launch. For social-media engagement, see social. For cold-email outreach to prospects, see cold-email.
Sections: Before Starting; Core Philosophy; The PR Mix; Owned: Press Page + Media Kit; Quick Reference: Pitch Quality Bar; Measurement; Common Workflows

### pulse
Multi-source recency research skill that takes the pulse of any topic across Reddit, Hacker News, the open web, and optionally X/Twitter within a configurable recent window (default 30 days). Forcing intake clarifies topic specificity, angle (trend/sentiment/problems/opportunities/comparison), time window, and platform scope before searching. Returns a synthesized briefing with citations, engagement metrics, and cross-platform pattern analysis. Use when the user requests multi-source recency intelligence on a topic (e.g., 'pulse on [topic]', 'what's happening with [topic]', 'what are people saying about [topic]', 'current conversation about [topic]', 'take the pulse of [topic]', 'trending: [topic]', 'find me info on [topic]'), and for competitor research, trend discovery, tool comparisons, and audience sentiment analysis.
Sections: Invocation; Agent Integrity Rules (Research-Pack Convention); Phase 0: Grill-Me Intake (2–4 forcing questions, one at a time); Pre-flight; Phase 1: Reddit (parallel with HN + Web); Phase 2: Hacker News (parallel with Reddit + Web); Phase 3: Web Search (parallel with Reddit + HN); Phase 4: X/Twitter (sequential, optional); Synthesis (Cross-Platform Patterns); Output

### referral-program
When the user wants to design, launch, or optimize a referral or affiliate program. Use when they mention 'referral program,' 'affiliate program,' 'word of mouth,' 'refer a friend,' 'incentive program,' 'customer referrals,' 'brand ambassador,' 'partner program,' 'referral link,' or 'growth through referrals.' Covers program mechanics, incentive design, and optimization — not just the idea of referrals but the actual system.
Sections: Before Starting; How This Skill Works; Referral vs. Affiliate — Choose the Right Mechanism; The Referral Loop; Incentive Design; Optimization Levers; Key Metrics; Affiliate Program Launch Checklist; Proactive Triggers; Output Artifacts

### runbook-generator
Generate operational runbooks from a service name — deployment, incident response, maintenance, and rollback workflows. Templated structure customizable per environment. Use when documenting on-call procedures for a new service, standardizing incident response across teams, or producing runbooks before launching to production.
Sections: Overview; Core Capabilities; When to Use; Quick Start; Recommended Workflow; Reference Docs; Common Pitfalls; Best Practices

### sarif-parsing
Parses and processes SARIF files from static analysis tools like CodeQL, Semgrep, or other scanners. Triggers on "parse sarif", "read scan results", "aggregate findings", "deduplicate alerts", or "process sarif output". Handles filtering, deduplication, format conversion, and CI/CD integration of SARIF data. Does NOT run scans — use the Semgrep or CodeQL skills for that.
Sections: When to Use; When NOT to Use; SARIF Structure Overview; Tool Selection Guide; Strategy 1: Quick Analysis with jq; Strategy 2: Python with pysarif; Strategy 3: Python with sarif-tools; Strategy 4: Aggregating Multiple SARIF Files; Strategy 5: Extracting Actionable Data; Common Pitfalls and Solutions

### shipping-and-launch
Prepares production launches. Use when preparing to deploy to production, or when asking what needs to be in place before shipping. Use when you need a pre-launch checklist, when setting up monitoring, when planning a staged rollout, or when you need a rollback strategy.
Sections: Overview; When to Use; The Pre-Launch Checklist; Feature Flag Strategy; Staged Rollout; Monitoring and Observability; Error Budget Release Gate; Rollback Strategy; Rollback Plan for Feature/Release; See Also

### signup
When the user wants to optimize signup, registration, account creation, or trial activation flows. Also use when the user mentions "signup conversions," "registration friction," "signup form optimization," "free trial signup," "reduce signup dropoff," "account creation flow," "people aren't signing up," "signup abandonment," "trial conversion rate," "nobody completes registration," "too many steps to sign up," or "simplify our signup." Use this whenever the user has a signup or registration flow that isn't performing. For post-signup onboarding, see onboarding. For lead capture forms (not account creation), see cro.
Sections: Initial Assessment; Core Principles; Field-by-Field Optimization; Single-Step vs. Multi-Step; Trust and Friction Reduction; Mobile Signup Optimization; Post-Submit Experience; Measurement; Output Format; Common Signup Flow Patterns

### sms
When the user wants to plan, build, or optimize SMS or MMS marketing — including welcome flows, abandoned cart texts, post-purchase, win-back, promotional sends, or transactional/auth SMS. Also use when the user mentions "SMS marketing," "text message campaigns," "SMS sequence," "SMS automation," "abandoned cart text," "post-purchase SMS," "Klaviyo SMS," "Postscript," "Attentive," "Twilio," "A2P 10DLC," "TCPA," "SMS compliance," "short code," "toll-free SMS," "MMS campaign," "should I do SMS," or "SMS vs email." For email sequences, see emails. For SMS copy framing, see copywriting. For opt-in popups that capture phone numbers, see popups.
Sections: Before Starting; When SMS Beats Email; Compliance — Read First; Phone Number Types (US); Core Principles; SMS Sequence Types; SMS Copy Guidelines; Platform Selection; Measurement; Output Format

### social
When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram, TikTok, Facebook, or other platforms, or wants to do social listening and engagement triage. Also use when the user mentions 'LinkedIn post,' 'Twitter thread,' 'social media,' 'content calendar,' 'social scheduling,' 'engagement,' 'viral content,' 'what should I post,' 'repurpose this content,' 'tweet ideas,' 'LinkedIn carousel,' 'social media strategy,' 'grow my following,' 'TikTok video,' 'Reels,' 'Shorts,' 'video script,' 'video hook,' 'short-form video,' 'create a reel,' 'social listening,' 'brand mentions,' 'competitor monitoring,' 'top posts to comment on,' or 'find people asking for.' Use this for social media content creation, repurposing, scheduling, short-form video scripting, and social listening. For broader content strategy, see content-strategy. For paid ads, see ad-creative. For earned media, see public-relations.
Sections: Before Creating Content; Platform Quick Reference; Content Pillars Framework; Hook Formulas; Content Repurposing System; Content Calendar Structure; Engagement Strategy; Analytics & Optimization; Content Ideas by Situation; Scheduling Best Practices

### social-media-analyzer
Social media campaign analysis and performance tracking. Calculates engagement rates, ROI, and benchmarks across platforms. Use when analyzing social media performance, calculating engagement rate, measuring campaign ROI, comparing platform metrics, or benchmarking against industry standards. Also use when the user mentions "social media audit," "engagement rate," or "which platform performs best."
Sections: Table of Contents; Analysis Workflow; Engagement Metrics; ROI Calculation; Platform Benchmarks; Tools; Examples; Reference Documentation; Proactive Triggers; Output Artifacts

### webinar-marketing
When the user wants to plan, promote, run, or improve a webinar or virtual event to generate and convert demand. Use when the user mentions 'webinar,' 'virtual event,' 'online event,' 'live demo,' 'virtual summit,' 'workshop,' 'masterclass,' 'fireside chat,' 'roundtable,' 'registration funnel,' 'show-up rate,' 'attendance rate,' 'webinar promotion,' 'webinar follow-up,' or 'on-demand webinar.' Also use when they have a webinar that isn't converting — low registrations, low show-up, or attendees who don't buy — and want to diagnose and fix it. Covers the full funnel: registration, promotion, show-up, live engagement, live-to-close, and post-event nurture. Distinct from launch-strategy (full product launches) and email-sequence (lifecycle nurture) — this is the end-to-end webinar/event motion. NOT for in-person field events logistics, and NOT for generic lifecycle email (use email-sequence).
Sections: Before Starting; How This Skill Works; The Funnel Math (Plan Backward); The Five Stages; What to Avoid; Proactive Triggers; Output Artifacts; Communication; Related Skills

### x-twitter-growth
X/Twitter growth engine for building audience, crafting viral content, and analyzing engagement. Use when the user wants to grow on X/Twitter, write tweets or threads, analyze their X profile, research competitors on X, plan a posting strategy, or optimize engagement. Complements social-content (generic multi-platform) with X-specific depth: algorithm mechanics, thread engineering, reply strategy, profile optimization, and competitive intelligence via web search.
Sections: When to Use This vs Other Skills; Step 1 — Profile Audit; Step 2 — Competitive Intelligence; Step 3 — Content Creation; Step 4 — Algorithm Mechanics; Step 5 — Growth Playbook; Step 6 — Content Calendar Generation; Scripts; Common Pitfalls; Related Skills

### youtube-full
Use when the user needs YouTube transcripts, video search, channel browsing, playlist extraction, or content monitoring. Trigger phrases: 'get the transcript for', 'search YouTube for', 'what are the latest videos on', 'list this playlist', 'monitor this channel', or any request involving a YouTube URL, video ID, or @handle. Do NOT use for downloading video or audio files, YouTube engagement data (likes, comments), or private/age-restricted videos.
Sections: API Setup; Operations; Credit Costs Summary; Common Workflows; Decision Rules; Error Handling; Limitations; Anti-Patterns; OSS Fallback Paths; Cross-References

## Product and project management

### ab-testing
When the user wants to plan, design, or implement an A/B test or experiment, or build a growth experimentation program. Also use when the user mentions "A/B test," "split test," "experiment," "test this change," "variant copy," "multivariate test," "hypothesis," "should I test this," "which version is better," "test two versions," "statistical significance," "how long should I run this test," "growth experiments," "experiment velocity," "experiment backlog," "ICE score," "experimentation program," or "experiment playbook." Use this whenever someone is comparing two approaches and wants to measure which performs better, or when they want to build a systematic experimentation practice. For tracking implementation, see analytics. For page-level conversion optimization, see cro.
Sections: Initial Assessment; Core Principles; Hypothesis Framework; Test Types; Sample Size; Metrics Selection; Designing Variants; Traffic Allocation; Implementation; Running the Test

### agile-product-owner
Agile product ownership for backlog management and sprint execution. Covers user story writing, acceptance criteria, sprint planning, and velocity tracking. Use when writing user stories, creating acceptance criteria, planning sprints, estimating story points, breaking down epics, or prioritizing the backlog.
Sections: Table of Contents; What Makes This Skill Different; User Story Generation Workflow; Acceptance Criteria Patterns; Epic Breakdown Workflow; Sprint Planning Workflow; Backlog Prioritization; Reference Documentation; Tools; Sprint Metrics

### ar-loop
Start an autonomous experiment loop with user-selected interval (10min, 1h, daily, weekly, monthly). Uses CronCreate for scheduling. Use when the user runs /ar-loop or asks to run an autoresearch experiment continuously on a schedule.
Sections: Usage; What It Does; Stopping a Loop; Important Limitations

### ar-resume
Resume a paused experiment. Checkout the experiment branch, read results history, continue iterating. Use when the user runs /ar-resume or asks to pick up a previously started autoresearch experiment.
Sections: Usage; What It Does

### ar-run
Run a single experiment iteration. Edit the target file, evaluate, keep or discard. Use when the user runs /ar-run or asks for one manual autoresearch iteration.
Sections: Usage; What It Does; Rules

### ar-setup
Set up a new autoresearch experiment interactively. Collects domain, target file, eval command, metric, direction, and evaluator. Use when the user runs /ar-setup or asks to start optimizing a file with the autoresearch loop.
Sections: Usage; What It Does; Built-in Evaluators; After Setup

### ar-status
Show experiment dashboard with results, active loops, and progress. Use when the user runs /ar-status or asks how an autoresearch experiment is going.
Sections: Usage; What It Does; Output Example

### atlassian-admin
Atlassian Administrator for managing and organizing Atlassian products (Jira, Confluence, Bitbucket, Trello), users, permissions, security, integrations, system configuration, and org-wide governance. Use when asked to add users to Jira, change Confluence permissions, configure access control, update admin settings, manage Atlassian groups, set up SSO, install marketplace apps, review security policies, or handle any org-wide Atlassian administration task.
Sections: Workflows; Global Configuration; Governance & Policies; Disaster Recovery; Metrics & Reporting; Decision Framework & Handoff Protocols; Atlassian MCP Integration — scope limits

### atlassian-templates
Atlassian Template and Files Creator/Modifier expert for creating, modifying, and managing Jira and Confluence templates, blueprints, custom layouts, reusable components, and standardized content structures. Use when building org-wide templates, custom blueprints, page layouts, and automated content generation.
Sections: Workflows; Confluence Templates Library; Jira Templates Library; Macro Usage Guidelines; Template scaffolder — generate storage-format markup; Atlassian MCP Integration; Best Practices & Governance; Handoff Protocols

### change-management
Framework for rolling out organizational changes without chaos. Covers the ADKAR model adapted for startups, communication templates, resistance patterns, and change fatigue management. Handles process changes, org restructures, strategy pivots, and culture changes. Use when announcing a reorg, switching tools, pivoting strategy, killing a product, changing leadership, or when user mentions change management, change rollout, managing resistance, org change, reorg, or pivot communication.
Sections: Keywords; Core Model: ADKAR Adapted for Startups; Change Types and ADKAR Application; Resistance Patterns; Change Fatigue; Key Questions for Change Management; Red Flags; Detailed References

### code-to-prd
Reverse-engineer any codebase into a complete Product Requirements Document (PRD). Analyzes routes, components, state management, API integrations, and user interactions to produce business-readable documentation detailed enough for engineers or AI agents to fully reconstruct every page and endpoint. Works with frontend frameworks (React, Vue, Angular, Svelte, Next.js, Nuxt), backend frameworks (NestJS, Django, Express, FastAPI), and fullstack applications. Use when users mention: generate PRD, reverse-engineer requirements, code to documentation, extract product specs from code, document page logic, analyze page fields and interactions, create a functional inventory, write requirements from an existing codebase, document API endpoints, or analyze backend routes.
Sections: Name; Description; Features; Usage; Examples; Role; Workflow; System Overview; Module Overview; Page Inventory

### confluence-expert
Atlassian Confluence expert for creating and managing spaces, knowledge bases, and documentation. Configures space permissions and hierarchies, creates page templates with macros, sets up documentation taxonomies, designs page layouts, and manages content governance. Use when users need to build or restructure a Confluence space, design page hierarchies with permission structures, author or standardise documentation templates, embed Jira reports in pages, run knowledge base audits, or establish documentation standards and collaborative workflows.
Sections: Atlassian MCP Integration; Workflows; Essential Macros; Page Layouts & Formatting; Templates Library; Space Permissions; Content Governance; Decision Framework; Handoff Protocols; Best Practices

### crypto-protocol-diagram
Extracts protocol message flow from source code, RFCs, academic papers, pseudocode, informal prose, ProVerif (.pv), or Tamarin (.spthy) models and generates Mermaid sequenceDiagrams with cryptographic annotations. Use when diagramming a crypto protocol, visualizing a handshake or key exchange flow, extracting message flow from a spec or RFC, diagramming a ProVerif or Tamarin model, or drawing sequence diagrams for TLS, Noise, Signal, X3DH, Double Ratchet, FROST, DH, or ECDH protocols.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Workflow; Spec Workflow (S1–S5); Protocol Summary; Decision Tree; Examples; Supporting Documentation

### experiment-designer
Use when planning product experiments, writing testable hypotheses, estimating sample size, prioritizing tests, or interpreting A/B outcomes with practical statistical rigor.
Sections: When To Use; Core Workflow; Hypothesis Quality Checklist; Common Experiment Pitfalls; Statistical Interpretation Guardrails; Tooling

### focused-fix
Use when the user asks to fix, debug, or make a specific feature/module/area work end-to-end. Triggers: 'make X work', 'fix the Y feature', 'the Z module is broken', 'focus on [area]'. Not for quick single-bug fixes — this is for systematic deep-dive repair across all files and dependencies.
Sections: When to Use; The Iron Law; Protocol — STRICTLY follow these 5 phases IN ORDER; Red Flags — STOP and Return to Current Phase; Common Rationalizations; Anti-Patterns — NEVER do these; Related Skills; Quick Reference

### fuzzing-dictionary
Builds and applies fuzzing dictionaries so a fuzzer can produce the keywords, magic bytes, and tokens a target expects. Covers extracting tokens from source, headers, binaries, and specifications, dictionary syntax, and wiring one into libFuzzer or AFL++. Use when fuzzing a parser, protocol, or file format, when coverage stalls at input validation, or when a target compares against fixed strings.
Sections: Overview; When to Apply; Quick Reference; Step-by-Step; Common Patterns; Advanced Usage; Anti-Patterns; Tool-Specific Guidance; Troubleshooting; Related Skills

### industry-performance-snapshot
Retrieve a daily overview of industry performance using Octagon MCP. Use when analyzing daily price movements, average changes, and performance trends for specific industries within an exchange.
Sections: Prerequisites; Workflow; Example Queries; Understanding Daily Performance; Industry Categories; Analyzing Performance; Catalyst Analysis; Momentum Analysis; Sector Rotation Signals; Exchange Considerations

### jira-expert
Atlassian Jira expert for creating and managing projects, planning, product discovery, JQL queries, workflows, custom fields, automation, reporting, and all Jira features. Use when setting up or configuring Jira projects, writing JQL and advanced searches, creating dashboards, designing workflows, or performing technical Jira operations.
Sections: Quick Start — Most Common Operations; Workflows; Advanced Features; JQL Functions Reference; Reporting Templates; Decision Framework; Handoff Protocols; Best Practices; Atlassian MCP Integration; Related Skills

### planning-and-task-breakdown
Breaks work into ordered tasks. Use when you have a spec or clear requirements and need to break work into implementable tasks. Use when a task feels too large to start, when you need to estimate scope, or when parallel work is possible.
Sections: Overview; When to Use; The Planning Process; Task N: Short descriptive title; Checkpoint: After Tasks 1-3; Task Sizing Guidelines; Output Files; Plan Document Template; Overview; Architecture Decisions

### pm-skills
Router/index for the 8 project-management skills bundled in this plugin (senior PM quant toolkit, scrum master, Jira/JQL, Confluence, Atlassian admin, Atlassian templates, meeting analyzer, team communications). Use when a PM request doesn't obviously match one skill and you need to pick the right one (e.g., 'our sprints feel off', 'audit our Jira permissions'). Bundles an Atlassian Remote MCP config (.mcp.json) for live Jira/Confluence access.
Sections: Routing table; Quick start; Rules

### process-mapper
Use when a BizOps lead, COO, or process-improvement owner needs to document an end-to-end business process (procurement, employee onboarding, incident handoff, customer-onboarding, claims adjudication) in BPMN-style notation, measure cycle times by stage, surface where work spends most of its time waiting vs. being worked, and quantify the gap between processing time and total elapsed time. Pairs Lean / Six Sigma / Theory-of-Constraints canon with deterministic stdlib-only Python tools to produce a process map, a ranked bottleneck list (with severity + root-cause hypothesis), and a cycle-time analysis (P50, P90, value-add ratio, Little's-Law throughput). Distinct from sales-pipeline, system-reliability (SLO), and strategic-OKR work — this is tactical process documentation for internal operations.
Sections: Purpose; When to use; Workflow; Scripts; Quick example; References; Assumptions; Anti-patterns; Distinct from; Forcing-question library (Matt Pocock grill discipline)

### product-analytics
Use when defining product KPIs, building metric dashboards, running cohort or retention analysis, or interpreting feature adoption trends across product stages.
Sections: When To Use; Workflow; KPI Guidance By Stage; Dashboard Design Principles; Cohort Analysis Method; Retention Curve Interpretation; Anti-Patterns; Tooling; Cross-References

### product-discovery
Use when validating product opportunities, mapping assumptions, planning discovery sprints, or testing problem-solution fit before committing delivery resources.
Sections: When To Use; Core Discovery Workflow; Opportunity Solution Tree (Teresa Torres); Assumption Mapping; Problem Validation Techniques; Solution Validation Techniques; Discovery Sprint Planning; Tooling

### product-manager-toolkit
Comprehensive toolkit for product managers including RICE prioritization, customer interview analysis, PRD templates, discovery frameworks, and go-to-market strategies. Use when prioritizing features, synthesizing user research, writing requirement documentation, or developing product strategy.
Sections: Table of Contents; Quick Start; Core Workflows; Tools Reference; Input/Output Examples; Integration Points; Common Pitfalls to Avoid; Best Practices; Quick Reference; Reference Documents

### product-research
Use when planning and synthesizing product/user research as a method-and-repository discipline — selecting the right method for the goal (generative interviews vs usability test vs concept test vs validation), computing method-based saturation/sample size with an explicit confidence level, or synthesizing coded observations into insights while flagging single-source anecdotes. Never fabricates user insight; an insight requires recurrence across independent participants. Distinct from product-team/ux-researcher-designer (persona/journey artifacts), product-discovery (discovery-sprint planning), and experiment-designer (live A/B) — this is the research-ops method + insight-repository layer.
Sections: Purpose; When to use; Workflow; Scripts; Onboarding & customization; Optimize with autoresearch (opt-in); References; Assumptions; Anti-patterns; Distinct from

### product-skills
Router/index for the 12 product skills bundled in this plugin (RICE prioritization, OKRs, UX research, design tokens, competitive teardown, analytics, experiments, discovery, roadmaps, spec-to-repo, landing pages, SaaS scaffolding). Use when a product request doesn't obviously match one skill and you need to pick the right one (e.g., 'help me prioritize features', 'plan a product experiment').
Sections: Routing table; Quick start; Related product-team plugins (packaged separately, not in this bundle); Rules

### roadmap-communicator
Use when preparing roadmap narratives, release notes, changelogs, or stakeholder updates tailored for executives, engineering teams, and customers.
Sections: When To Use; Roadmap Formats; Stakeholder Update Patterns; Release Notes Guidance; Changelog Generation; Feature Announcement Framework; Communication Quality Checklist

### ruzzy
Sets up and runs Ruzzy, Trail of Bits' coverage-guided Ruby fuzzer and the only production-ready one for the language. Covers harness structure, fuzzing pure Ruby and the native C extensions in gems, and sanitizer builds. Use when fuzzing a Ruby library or gem, testing a Ruby C extension for memory safety, or asking how to fuzz Ruby at all.
Sections: When to Use; Quick Start; Installation; Writing a Harness; Compilation; Running Campaigns; Sanitizer Integration; Real-World Examples; Troubleshooting; Related Skills

### scrum-master
Advanced Scrum Master skill for data-driven agile team analysis and coaching. Use when the user asks about sprint planning, velocity tracking, retrospectives, standup facilitation, backlog grooming, story points, burndown charts, blocker resolution, or agile team health. Runs Python scripts to analyse sprint JSON exports from Jira or similar tools: velocity_analyzer.py for Monte Carlo sprint forecasting, sprint_health_scorer.py for multi-dimension health scoring, and retrospective_analyzer.py for action-item and theme tracking. Produces confidence-interval forecasts, health grade reports, and improvement-velocity trends for high-performing Scrum teams.
Sections: Table of Contents; Analysis Tools & Usage; Input Requirements; Sprint Execution Workflows; Team Development Workflow; Key Metrics & Targets; Limitations; Related Skills

### senior-computer-vision
Computer vision engineering skill for object detection, image segmentation, and visual AI systems. Covers CNN and Vision Transformer architectures, YOLO/Faster R-CNN/DETR detection, Mask R-CNN/SAM segmentation, and production deployment with ONNX/TensorRT. Includes PyTorch, torchvision, Ultralytics, Detectron2, and MMDetection frameworks. Use when building detection pipelines, training custom models, optimizing inference, or deploying vision systems.
Sections: Table of Contents; Quick Start; Core Expertise; Tech Stack; Workflow 1: Object Detection Pipeline; Workflow 2: Model Optimization and Deployment; Workflow 3: Custom Dataset Preparation; Architecture Selection Guide; Reference Documentation; Performance Targets

### senior-ml-engineer
ML engineering skill for productionizing models, building MLOps pipelines, and integrating LLMs. Covers model deployment, feature stores, drift monitoring, RAG systems, and cost optimization. Use when the user asks about deploying ML models to production, setting up MLOps infrastructure (MLflow, Kubeflow, Kubernetes, Docker), monitoring model performance or drift, building RAG pipelines, or integrating LLM APIs with retry logic and cost controls. Focused on production and operational concerns rather than model research or initial training.
Sections: Table of Contents; Model Deployment Workflow; MLOps Pipeline Setup; LLM Integration Workflow; RAG System Implementation; Model Monitoring; Reference Documentation; Tools; Tech Stack

### senior-pm
Senior Project Manager for enterprise software, SaaS, and digital transformation projects. Specializes in portfolio management, quantitative risk analysis, resource optimization, stakeholder alignment, and executive reporting. Uses advanced methodologies including EMV analysis, Monte Carlo simulation, WSJF prioritization, and multi-dimensional health scoring. Use when a user needs help with project plans, project status reports, risk assessments, resource allocation, project roadmaps, milestone tracking, team capacity planning, portfolio health reviews, program management, or executive-level project reporting — especially for enterprise-scale initiatives with multiple workstreams, complex dependencies, or multi-million dollar budgets.
Sections: Overview; Methodology & Frameworks; Assets & Templates; Implementation Workflows; Integration Strategies; Handoff Protocols; Success Metrics & KPIs; Continuous Improvement Framework; Related Skills

### spec-driven-development
Creates specs before coding. Use when starting a new project, feature, or significant change and no specification exists yet. Use when drafting a PRD or requirements document with objectives and scope, or when requirements are unclear, ambiguous, or only exist as a vague idea. Use when a single requirement spans several independently testable capabilities and needs decomposing into a capability map of modules before specifying.
Sections: Overview; When to Use; The Gated Workflow; Objective; Tech Stack; Commands; Project Structure; Code Style; Testing Strategy; Boundaries

### spec-driven-workflow
Use when the user asks to write specs before code, define acceptance criteria, plan features before implementation, generate tests from specifications, or follow spec-first development practices.
Sections: Overview; The Spec Format; Bounded Autonomy Rules; Escalation: Brief Title; Workflow — 6 Phases; Self-Review Checklist; Integration with TDD Guide; Examples; Anti-Patterns; Cross-References

### spec-to-repo
Use when the user says 'build me an app', 'create a project from this spec', 'scaffold a new repo', 'generate a starter', 'turn this idea into code', 'bootstrap a project', 'I have requirements and need a codebase', or provides a natural-language project specification and expects a complete, runnable repository. Stack-agnostic: Next.js, FastAPI, Rails, Go, Rust, Flutter, and more.
Sections: When to Use; Core Workflow; Spec Interpretation; Examples; Anti-Patterns; Validation Script; Progressive Enhancement; Cross-References

### tc-tracker
Use when the user asks to track technical changes, create change records, manage TC lifecycles, or hand off work between AI sessions. Covers init/create/update/status/resume/close/export workflows for structured code change documentation.
Sections: Overview; Storage Layout; TC ID Convention; State Machine; Workflow Commands; Slash-Command Dispatcher; Session Handoff Format; Validation Rules (Always Enforced); Non-Blocking Bookkeeping Pattern; Retroactive Bulk Creation

### variant-analysis
Hunts for the other instances of a bug already found — the variants of one root cause across a codebase. Use immediately after a vulnerability, logic bug, or bad pattern turns up in a specific file and the question becomes where else it occurs, including the bare conversational form ("are there others like this?", "is this the same bug?"). Also for generalizing one known instance into a CodeQL or Semgrep query for its whole pattern family, and for triaging a set of look-alike candidates against a known root cause. Not for initial discovery with no bug in hand.
Sections: When to Use; When NOT to Use; The Five Steps; Running it as a Workflow; What Makes Hunts Fail; Resources

## Research and analysis

### deep-research
Run a disciplined, multi-source research investigation for a high-stakes question or decision — fan-out web search across many channels, parallel sub-agents, source triangulation (each claim backed by ≥3 independent sources), an adversarial review pass, and every source saved to its own file with verbatim quotes for reuse. Use when a low-quality answer is expensive: strategy work, comparing N products/methods/markets, validating a hypothesis with external data, or mapping how a field works. NOT for quick fact-checks (answer directly), structured 12-dimension competitor scoring (use competitive-teardown), or fast topic overviews where the decision risk is low (use the research router instead).
Sections: How it differs from a quick research router; The pipeline (9 phases); Core mechanisms; Output structure; When to use; Anti-Patterns; Cross-References

### dossier
Decision-grade entity research skill — produces a hypothesis-tested dossier on a specific company, person, nonprofit, or government org, not a generic profile. Forcing intake makes the user state their hypothesis upfront (what they already believe and want to verify or disprove) so the dossier tests it rather than confirms it. Output is an editable Word document (.docx) with verdict on the hypothesis, identity facts, 12-month activity timeline, network and reputation signals, red flags, conversation hooks tied to specific findings, and source-provenance audit log. Uses WebSearch + WebFetch + free APIs (SEC EDGAR, GitHub, ProPublica) as workhorses; optional BYOK MCPs enhance coverage. Use when the user asks for background research, diligence, or meeting prep on a specific entity (e.g., 'prep me for a meeting with [person/company]', 'due diligence on [company]'). Honors sensitivity exclusions for journalism + personal-vetting contexts.
Sections: Non-Generic Framing — The Differentiator; Agent Integrity Rules (Research-Pack Convention); Phase 1: Grill-Me Intake (6 forcing questions, one at a time); Phase 2: Subject Disambiguation; Phase 3: Source Matrix Selection; Phase 4: Hypothesis-Driven Search; Phase 5: 12-Month Activity Timeline; Phase 6: Network + Reputation Signals; Phase 7: Red-Flag Pass; Phase 8: Conversation Hook Generation

### grants
NIH grant research skill for clinical researchers. Grill-me intake (research idea + career stage + preliminary data + environment + submission posture + known institute targets) locks down the funding strategy before any search runs. Runs a 5-facet Consensus positioning analysis (with draft Significance/Innovation language), maps the research to the right NIH institutes and study sections via RePORTER, finds NOSIs and funded overlap, and produces an editable Word document (.docx) with budget/scope-aware mechanism recommendations, submission timelines, and a mandatory program officer recommendation. Use when the user asks about research funding or makes any grant-related request (e.g., 'grants for [topic]', 'find grants for my research idea', 'what grants match my research', 'help me find NIH funding', 'grant opportunities for my research'). NIH-only scope — non-NIH funders (PCORI, DOD CDMRP, VA, foundations) are out of scope and flagged at intake.
Sections: Agent Integrity Rules (Research-Pack Convention); Phase 1: Grill-Me Intake (6 forcing questions, one at a time); Phase 2A: Research Positioning (5 Consensus searches); Phase 2B: Institute Mapping + Grant Discovery (RePORTER POST); Mechanism Matching (Scope-Aware); Phase 3: DOCX Generation; Mandatory Program Officer Recommendation; Submission Timeline (Embedded in DOCX Section 7); Phase 4: Deliver; Tooling

### interview-me
Extracts what the user actually wants instead of what they think they should want. Achieves this through one-question-at-a-time interview until ~95% confidence about the underlying intent. Use when an ask is underspecified ("build me X" without "for whom" or "why now"), when the user explicitly invokes ("interview me", "grill me", "are we sure?", "stress-test my thinking"), or when you catch yourself silently filling in ambiguous requirements before any plan, spec, or code exists.
Sections: Overview; When to Use; Loading Constraints; The Process; Output; Example; Interaction with Other Skills; Common Rationalizations; Red Flags; Verification

### interview-system-designer
This skill should be used when the user asks to "design interview processes", "create hiring pipelines", "calibrate interview loops", "generate interview questions", "design competency matrices", "analyze interviewer bias", "create scoring rubrics", "build question banks", or "optimize hiring systems". Use for designing role-specific interview loops, competency assessments, and hiring calibration systems.
Sections: Overview; Core Capabilities; Quick Start; Recommended Workflow; References; Common Pitfalls; Best Practices

### libafl
Builds custom fuzzers with LibAFL, the modular Rust fuzzing library. Covers composing observers, feedbacks, mutators, schedulers, and executors into a fuzzer for targets the standard tools do not fit. Use when writing a bespoke fuzzer or mutator, fuzzing a non-standard target or architecture, implementing a fuzzing research idea, or when libFuzzer and AFL++ lack the control you need.
Sections: When to Use; Quick Start; Installation; Writing a Harness; Usage Modes; Writing a Custom Fuzzer; Compilation; Running Campaigns; Advanced Usage; Real-World Examples

### litreview
Academic literature orientation skill that searches papers via free keyless APIs (PubMed E-utilities + OpenAlex) by default — with the Consensus MCP as an optional enhancement lane when connected — builds a strategic search plan using PICO (default) or SPIDER / Decomposition / hybrid as fallbacks, and synthesizes findings into a formatted Word (.docx) research guide. Grill-me intake (research question specificity + framework hint + tentative depth) before the recon search; a second forcing checkpoint after Phase 2 confirms framework + sub-areas + depth before searches consume budget. Configurable depth (5/10/20 queries) controls coverage vs. speed. Output is a 'launching pad' — an orientation guide that lets a researcher dive in confidently, not a finished review. Use when the user starts literature-oriented research (e.g., 'litreview on [topic]', 'literature review on [topic]', 'I'm starting a literature review on X', 'I'm writing a paper on X', 'help me research X', 'I'm doing research on X', 'can you help me research X'). Do NOT use for single one-off paper searches wanting a quick list — that's a plain PubMed/OpenAlex (or Consensus) query.
Sections: Search Lanes; Agent Integrity Rules (Research-Pack Convention); Error Handling; Phase 0: Grill-Me Intake (3 forcing questions, one at a time); Phase 1: Initial Reconnaissance; Phase 2: Framework Selection + Sub-area Generation; Checkpoint (grill-me forcing-options moment); Phase 3: Targeted Searches; Cross-Search Intelligence; Phase 4: DOCX Research Guide

### market-research
Use when doing upstream market-research methodology — sizing a market as TAM/SAM/SOM computed BOTH top-down and bottoms-up (never a single unsourced number), planning a survey sample size with finite-population correction and per-segment minimums, or scoring candidate market segments against Kotler's measurable/substantial/accessible/differentiable/actionable criteria. Outputs always show the method and the assumptions. For market-research analysts and product-marketing at the sizing/survey/segmentation moment. Distinct from marketing-skill (campaign analytics, attribution, demand-gen) — this is the evidence-building methodology, not live-campaign optimization.
Sections: Purpose; When to use; Workflow; Scripts; Onboarding & customization; Optimize with autoresearch (opt-in); References; Assumptions; Anti-patterns; Distinct from

### meeting-analyzer
Analyzes meeting transcripts and recordings to surface behavioral patterns, communication anti-patterns, and actionable coaching feedback. Use this skill whenever the user uploads or points to meeting transcripts (.txt, .md, .vtt, .srt, .docx), asks about their communication habits, wants feedback on how they run meetings, requests speaking ratio analysis, mentions filler words or conflict avoidance, or wants to compare their communication across time periods. Also trigger when users mention tools like Granola, Otter, Fireflies, or Zoom transcripts. Even if the user just says "look at my meetings" or "how do I come across in meetings" — use this skill.
Sections: Core Workflow; Top 3 Findings; Detailed Analysis; Strengths; Growth Opportunities; Comparison to Previous Period; Edge Cases; Transcript Source Tips; Anti-Patterns; Related Skills

### patent
Patent prior-art and landscape intelligence skill — not generic patent help. Commits to one of five sub-use-cases via forcing intake (novelty search / freedom-to-operate / competitive landscape / acquisition diligence / litigation prior-art) before any search runs. Searches Google Patents, Espacenet, USPTO, and optionally Lens.org for citation-graph signals. Output is an editable Word document (.docx) with verdict, ranked closest art (claim-text extracted), CPC-class-aware landscape, family-resolved hits, geographic coverage, FTO flags where applicable, strategy recommendations, and full audit log. Use when the user asks for patent searching or analysis (e.g., 'prior art search for [invention]', 'freedom to operate analysis for [product]'). Produces search signal, not legal advice — always recommends consulting a patent attorney before filing or licensing decisions. Trademark, copyright, and trade-secret questions are out of scope.
Sections: Non-Generic Framing — The Differentiator; Agent Integrity Rules (Research-Pack Convention); Phase 1: Grill-Me Intake (6 forcing questions, one at a time); Phase 2: Search Strategy Selection; Phase 3: Multi-Source Search (Sequential); Phase 4: Claim Extraction + Relevance Scoring; Phase 5: Citation Graph + Family Resolution; CPC/IPC Classification Awareness; Phase 6: DOCX Generation (8 Sections); Date Discipline

### research
Default entry point for any research request — a hybrid router that classifies the question deterministically and either delegates to a specialist research skill (pulse for trends/sentiment, grants for NIH funding, litreview for academic literature, syllabus for course reading, patent for prior-art + IP landscape, dossier for entity research) or runs its own plan-decompose-multi-source-search-synthesize-cite fallback workflow when no specialist matches. Always surfaces the routing decision so users can override. Use when the user makes any research request that doesn't obviously match a more-specific specialist skill (e.g., "research [topic]", "look into [topic]", "what do we know about [topic]", "investigate [topic]", "find me information on [topic]", "do some research on [topic]", "I need to understand [topic]"). Output is a markdown briefing (default) or .docx document (on request) with full citations and an audit log.
Sections: Portability; Distinct From engineering/autoresearch-agent; Hybrid Architecture (C); Specialist Registry; Agent Integrity Rules; Phase 1: Grill-Me Intake (2–4 Questions); Phase 2: Deterministic Classification; Phase 3a: Specialist Delegation (≥2 signals OR one strong multi-word phrase); Phase 3b: Own Fallback Workflow; Routing Transparency Protocol (Mandatory)

### research-ops-skills
Use when planning, funding, scoping, or synthesizing enterprise research across workstreams — clinical study design, R&D program finance, market sizing/surveys, or product/user research. Triggers on "design this clinical study", "what sample size", "R&D budget", "burn rate", "capitalize or expense", "TAM SAM SOM", "market sizing", "survey design", "segment the market", "plan user interviews", "usability test", "synthesize research insights". Forks context to route to one of four Research-Operations sub-skills (clinical-research, research-finance, market-research, product-research) and returns a digest. Distinct from ra-qm-team (regulatory submission), finance (corporate close/valuation), research/grants (funding discovery), product-team (persona/journey/live experiments), and marketing-skill (campaign analytics).
Sections: When to invoke; Routing logic (deterministic); Workflow (Matt Pocock grill discipline); Forcing-question library (grill-with-docs pattern); Onboarding-first (per sub-skill); Autoresearch handoff (isolated, opt-in); Assumptions; Non-goals; Distinct from; Output artifacts

### research-summarizer
Structured research summarization agent skill for non-dev users. Handles academic papers, web articles, reports, and documentation. Extracts key findings, generates comparative analyses, and produces properly formatted citations. Use when: user wants to summarize a research paper, compare multiple sources, extract citations from documents, or create structured research briefs. Plugin for Claude Code, Codex, Gemini CLI, and OpenClaw.
Sections: Scope — Distinct From the research/ Domain; When This Skill Activates; Workflow; Tooling; Quality Assessment Framework; Summary Templates; Proactive Triggers; Installation; Verification Loop; Related Skills

### syllabus
Generates a curated supplementary reading list from any course syllabus using Consensus academic search. Grill-me intake (syllabus input format + course audience + year range) plus a grouping forcing-options checkpoint before any search runs — so the reading list matches the course's level and recency need. Parses the syllabus to extract topics and learning outcomes, searches Consensus for recent peer-reviewed papers per topic, and produces a professionally formatted .docx with clickable Consensus links, plain-language summaries calibrated to audience level, and Bloom-higher-order discussion questions tied to course learning goals. Use when the user uploads a syllabus, course outline, or curriculum document and wants supplementary readings (e.g., 'create a reading list from this syllabus', 'find recent papers for my course') — even casual mentions with a syllabus attached should trigger this skill.
Sections: Architectural Pattern: Bundled Script; Agent Integrity Rules (Research-Pack Convention); Phase 0: Grill-Me Intake (3 forcing questions); Phase 1: Parse the Syllabus; Phase 2: Group Topics + Confirm with User; Phase 3: Search Consensus per Section; Phase 4: Write Summaries + Discussion Questions; Phase 5: Generate .docx via Bundled Script; Phase 6: Deliver; Tooling

### ux-researcher-designer
UX research and design toolkit for Senior UX Designer/Researcher including data-driven persona generation, journey mapping, usability testing frameworks, and research synthesis. Use when conducting user research, creating personas, mapping user journeys, planning usability tests, or validating designs.
Sections: Table of Contents; Trigger Terms; Workflows; Tool Reference; Quick Reference Tables; Knowledge Base; Validation Checklist; Related Skills

## Writing, docs and presentations

### canvas-design
Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static piece. Create original visual designs, never copying existing artists' work to avoid copyright violations.
Sections: DESIGN PHILOSOPHY CREATION; DEDUCING THE SUBTLE REFERENCE; CANVAS CREATION; FINAL STEP; MULTI-PAGE OPTION

### cargo-fuzz
Sets up and runs cargo-fuzz, the standard fuzzing tool for Cargo-based Rust projects. Covers cargo fuzz init, the nightly toolchain requirement, fuzz_target! harnesses, Arbitrary-derived structured inputs, sanitizer options, cargo fuzz coverage, and reproducing a crash artifact. Use when fuzzing a Rust crate, writing a fuzz_target!, exercising unsafe blocks or FFI in Rust, or triaging a cargo fuzz crash.
Sections: When to Use; Quick Start; Installation; Writing a Harness; Structure-Aware Fuzzing; Running Campaigns; Sanitizer Integration; Coverage Analysis; Advanced Usage; Real-World Examples

### changelog-generator
Produce consistent, auditable release notes from Conventional Commits. Separates commit parsing, semantic-bump logic, and changelog rendering for automated releases with editorial control. Use when cutting a release, generating CHANGELOG.md from git history, computing the next semantic version from commits, automating release notes in CI, or planning a hotfix/rollback. Examples: 'generate the changelog for v1.4.0', 'what version bump do these commits require', 'we need an emergency hotfix process'.
Sections: Overview; Core Capabilities; When to Use; Key Workflows; Conventional Commit Rules; Script Interfaces; Common Pitfalls; Best Practices; Hotfix Severity & SLAs; Rollback Triggers

### code-tour
Use when the user asks to create a CodeTour .tour file — persona-targeted, step-by-step walkthroughs that link to real files and line numbers. Trigger for: create a tour, onboarding tour, architecture tour, PR review tour, explain how X works, vibe check, RCA tour, contributor guide, or any structured code walkthrough request.
Sections: Overview; When to Use This Skill; Core Workflow; Personas; Narrative Arc; Anti-Patterns; Cross-References

### doc-coauthoring
Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps users efficiently transfer context, refine content through iteration, and verify the doc works for readers. Trigger when user mentions writing docs, creating proposals, drafting specs, or similar documentation tasks.
Sections: When to Offer This Workflow; Stage 1: Context Gathering; Stage 2: Refinement & Structure; Stage 3: Reader Testing; Final Review; Tips for Effective Guidance

### docker-development
Docker and container development agent skill and plugin for Dockerfile optimization, docker-compose orchestration, multi-stage builds, and container security hardening. Use when: user wants to optimize a Dockerfile, create or improve docker-compose configurations, implement multi-stage builds, audit container security, reduce image size, or follow container best practices. Covers build performance, layer caching, secret management, and production-ready container patterns.
Sections: Slash Commands; When This Skill Activates; Workflow; Tooling; Multi-Stage Build Patterns; Base Image Decision Tree; Proactive Triggers; Installation; Related Skills

### documentation-and-adrs
Records decisions and documentation. Use when you need to document an architecture decision (ADR) or the reasoning behind a design choice, when changing public APIs, shipping features, or when you need to record context that future engineers and agents will need to understand the codebase.
Sections: Overview; When to Use; Architecture Decision Records (ADRs); Status; Date; Context; Decision; Alternatives Considered; Consequences; Inline Documentation

### domain-modeling
Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR.
Sections: File structure; During the session

### executing-plans
Use when you have a written implementation plan to execute in a separate session with review checkpoints
Sections: Overview; The Process; When to Stop and Ask for Help; When to Revisit Earlier Steps; Remember; Integration

### harness-writing
Designs and improves fuzzing harnesses for C/C++ and Rust. Covers mapping raw bytes onto a target API, generating structured inputs, avoiding non-determinism and false crashes, and deciding what to fuzz together. Use when writing a first LLVMFuzzerTestOneInput or fuzz_target! harness, when a campaign finds nothing or reports crashes that will not reproduce, or when the target API needs structured rather than raw input.
Sections: Overview; When to Apply; Quick Reference; Step-by-Step; Common Patterns; Advanced Usage; Practical Harness Rules; Anti-Patterns; Tool-Specific Guidance; Troubleshooting

### incremental-implementation
Delivers changes incrementally in thin, verifiable slices. Use when implementing any feature or change that touches more than one file, or when picking up the next task from a plan. Use when rolling a change out behind a feature flag, when you're about to write a large amount of code at once, or when a task feels too big to land in one step.
Sections: Overview; When to Use; The Increment Cycle; Slicing Strategies; Implementation Rules; Working with Agents; Increment Checklist; Common Rationalizations; Red Flags; Verification

### internal-comms
A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use. Claude should use this skill whenever asked to write some sort of internal communications (status reports, leadership updates, 3P updates, company newsletters, FAQs, incident reports, project updates, etc.).
Sections: When to use this skill; How to use this skill; Keywords

### internal-narrative
Build and maintain one coherent company story across all audiences — employees, investors, customers, candidates, and partners. Detects narrative contradictions and ensures the same truth is framed for each audience's needs. Use when preparing investor updates, all-hands presentations, board communications, recruiting narratives, crisis communications, or when user mentions company narrative, messaging consistency, storytelling, all-hands, investor update, or crisis communication.
Sections: Keywords; Core Principle; Framework; Narrative Consistency Checklist; Key Questions for Narrative; Red Flags; Integration with Other C-Suite Roles; Detailed References

### json-canvas
Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian.
Sections: File Structure; Common Workflows; Nodes; Edges; Colors; ID Generation; Layout Guidelines; Validation Checklist; Complete Examples; References

### markdown-html-orchestrator
Use when a user wants to convert any markdown file in their Claude project into a single-file, lightly-interactive HTML — long-form documents (specs, plans, RFCs, reports, explainers), code reviews with diffs and severity-tagged annotations, or slide decks. Triggers on "convert this markdown to HTML", "make this an HTML file", "turn this into an interactive document", "render this report as HTML", "PR writeup as HTML", "slides from this markdown". Forks context to route to one of three converter sub-skills (md-document, md-review, md-slides) based on a deterministic doctype classifier, after the user has run the design-system onboarding once. Refuses if input is under 100 lines (per Shihipar — markdown still wins below the threshold) or design-system isn't onboarded. Distinct from Anthropic's official Playground plugin (which is interactive prompt-tuning controls with sliders/knobs/prompt-copy-back) and from marketing/landing/ (which is a landing-page generator).
Sections: When to invoke; Pre-flight gates (hard refusals); Routing logic (deterministic); Workflow; Forcing-question library (Matt Pocock grill-with-docs pattern); Assumptions; Non-goals; Distinct from; Output artifacts; Anti-patterns (do not)

### md-document
Converts long-form markdown (specs, RFCs, reports, plans, explainers) into a single-file, lightly-interactive HTML document with sticky TOC, scrollspy, search filter, code-copy buttons, and design-system-driven brand tokens. Triggers when the markdown-html-orchestrator classifies an input as DOCUMENT, or when invoked directly via /md-document. Reads the design-system config via config_loader.py and inlines the user's 12 derived CSS custom properties; refuses to render if onboarding hasn't run. Single-file output — Google Fonts + Prism.js CDN are the only externals; no framework runtime, no build step. Use after orchestrator routing or after design-system onboarding is confirmed.
Sections: When to invoke; Pipeline; What gets rendered; Hard rules; Forcing-question library (Matt Pocock grill discipline); Distinct from; Output artifact; References

### md-review
Converts a markdown PR writeup or code review (one with ```diff fenced blocks and severity-tagged > [!BLOCKER]/[!MAJOR]/[!MINOR]/[!NIT] callouts) into a single-file 2-column HTML review — unified-diff on the left, severity-tagged annotation cards on the right, top jump-nav listing every finding, mandatory named reviewer footer. Triggers when the markdown-html-orchestrator classifies an input as REVIEW, or when invoked directly via /md-review. Refuses without explicit --reviewer (a code review must name a human), refuses if no diff hunks present (route to md-document instead), and refuses to encode severity in color only (every badge ships color + icon + aria-label per WCAG 1.4.1). Use after orchestrator routing.
Sections: When to invoke; Pipeline; What gets rendered; Hard rules; Forcing-question library (Matt Pocock grill discipline); Distinct from; Output artifact; References

### md-slides
Converts a markdown deck (slides separated by three-dash horizontal rules or by `# ` H1 headings, with optional `<!-- notes: ... -->` presenter notes blocks) into a single-file HTML presentation with arrow-key / space / PgDn / PgUp / Home / End / P / Esc keyboard navigation, presenter mode (split view with current slide + speaker notes + clock + next-slide preview), URL-hash deep linking, and `@media print` page-per-slide for PDF export. Triggers when the markdown-html-orchestrator classifies an input as SLIDES, or when invoked directly via /md-slides. Reuses md-document's markdown parser for slide-body rendering and reads design-system tokens via config_loader.py. Refuses if input has no clear slide boundaries, produces a 1-slide deck, or `--strict-notes` is on with < 50% notes coverage. Use after orchestrator routing.
Sections: When to invoke; Pipeline; What ships in the HTML; Hard rules; Forcing-question library (Matt Pocock grill discipline); Distinct from; Output artifact; References

### modern-python
Configures Python projects with modern tooling (uv, ruff, ty). Use when creating projects, writing standalone scripts, or migrating from pip/Poetry/mypy/black.
Sections: When to Use This Skill; When NOT to Use This Skill; Anti-Patterns to Avoid; Decision Tree; Tool Overview; Quick Start: Minimal Project; Full Project Setup; Migration Guide; Quick Reference: uv Commands; Quick Reference: Dependency Groups

### named-persona-adversarial-review
Code review through the lens of real engineers' documented philosophies (Torvalds, Thompson, Carmack, Kent Beck, Jobs, Cagan). Complements abstract-role adversarial review with named, sourced perspectives. Use when automated review findings feel generic, when a PR has architectural or UX impact, or when the author wants pre-submit hardening beyond standard checks.
Sections: Example Output; Problem; Attribution discipline (read this first — it is the load-bearing rule); Rules; Persona Pools; Severity Levels; The Process; Integrity Check (Feynman); Exit Condition; When to Use

### obsidian-bases
Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian.
Sections: Workflow; Schema; Filter Syntax; Properties; Formula Syntax; Key Functions; View Types; Default Summary Formulas; Complete Examples; Embedding Bases

### obsidian-cli
Interact with Obsidian vaults using the Obsidian CLI to read, create, search, and manage notes, tasks, properties, and more. Also supports plugin and theme development with commands to reload plugins, run JavaScript, capture errors, take screenshots, and inspect the DOM. Use when the user asks to interact with their Obsidian vault, manage notes, search vault content, perform vault operations from the command line, or develop and debug Obsidian plugins and themes.
Sections: Command reference; Syntax; File targeting; Vault targeting; Common patterns; Plugin development

### obsidian-markdown
Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.
Sections: Workflow: Creating an Obsidian Note; Internal Links (Wikilinks); Embeds; Callouts; Properties (Frontmatter); Tags; Comments; Obsidian-Specific Formatting; Math (LaTeX); Diagrams (Mermaid)

### onboard
Flags: saves-to-~/.claude
/onboard — Founder interview that populates ~/.claude/company-context.md using the canonical 7-dimension cs-onboard schema. The first command to run when starting with c-level-agents. Use when setting up the virtual C-suite for a new company, or when advisors lack company context — e.g. before a first /boardroom or after a fundraise changes the numbers.
Sections: What This Produces; The Interview (12 Questions); Output Format; Identity; Business; Financial; Team; Quarter; Routing Hints; Workflow

### ossfuzz
Enrolls a project in OSS-Fuzz, Google's free continuous fuzzing service for open source, and drives it locally. Covers project.yaml, Dockerfile and build.sh setup, the helper scripts, reproducing OSS-Fuzz crash reports, and the acceptance criteria. Use when setting up continuous fuzzing for an open-source project, reproducing an OSS-Fuzz bug report, or testing an OSS-Fuzz build before submitting it.
Sections: Overview; When to Apply; Quick Reference; OSS-Fuzz Project Components; Step-by-Step: Running a Single Harness; Common Patterns; Docker Images in OSS-Fuzz; Advanced Usage; Anti-Patterns; Tool-Specific Guidance

### pr
Use when writing a PR body.
Sections: Summary; Evidence; Merge Danger; Sections

### slides
Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies.
Sections: When to Use; Subcommands; References (Knowledge Base); Routing

### stop-slop
Flags: auto
Remove AI writing patterns from prose. Use when drafting, editing, or reviewing text to eliminate predictable AI tells.
Sections: Core Rules; Quick Checks; Scoring; Examples; License

### tdd-guide
Test-driven development skill for writing unit tests, generating test fixtures and mocks, analyzing coverage gaps, and guiding red-green-refactor workflows across Jest, Pytest, JUnit, Vitest, and Mocha. Use when the user asks to write tests, improve test coverage, practice TDD, generate mocks or stubs, or mentions testing frameworks like Jest, pytest, or JUnit.
Sections: Workflows; Examples; Key Tools; Input Requirements; Spec-First Workflow; Red-Green-Refactor Examples Per Language; Bounded Autonomy Rules; Property-Based Testing; Mutation Testing; Cross-References

### team-communications
Write internal company communications — 3P updates (Progress/Plans/Problems), company-wide newsletters, FAQ roundups, incident reports, leadership updates, status reports, project updates, and general internal comms. Use this skill any time the user asks to draft, edit, or format something meant for internal audiences. Trigger on keywords like "3P", "weekly update", "newsletter", "FAQ", "internal comms", "status report", "company update", "team update", "incident report", or any request to summarize work for leadership, teammates, or the broader company. Even casual requests like "write my update" or "summarize what my team did this week" should trigger this skill.
Sections: Routing; Workflow; Tone & Style (applies to all types); When tools are unavailable; Anti-Patterns; Related Skills

### universal-scraping-architect
Use for web scraping, crawling, document extraction, API parsing, or building validation-heavy data pipelines using Firecrawl or local Python scripts.
Sections: Before Starting; How This Skill Works; The Extraction Pipeline; Proactive Triggers; Output Artifacts; Anti-Patterns; Related Skills

### write-a-skill
Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, build, or author a new skill.
Sections: Process; Skill Structure; SKILL.md Template; Quick start; Workflows; Advanced features; Description Requirements; When to Add Scripts; When to Split Files; Review Checklist

### writing-for-agents
Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md.
Sections: Context pointers; The two loads; Information hierarchy; Steps and completion criteria; When to split; Leading words; Pruning

### writing-lean-proofs
Writes and reviews structured Lean 4 proofs and designs Lean libraries following Mathlib conventions. Use when proving theorems in Lean, formalizing mathematics or specifications in Lean 4, defining new types or definitions in a Lean library, reviewing Lean proofs for readability and maintainability, refactoring long tactic proofs into lemmas, filling in sorry placeholders in a Lean development, setting up CI or linters for a Lean project, diagnosing slow proofs or maxHeartbeats timeouts, or writing custom tactics, macros, or linters.
Sections: Contents; When to Use; When NOT to Use; The workflow; The extraction ladder; Quick reference; Rationalizations to reject; References

### writing-plans
Use when you have a spec or requirements for a multi-step task, before touching code
Sections: Overview; Scope Check; File Structure; Task Right-Sizing; Bite-Sized Task Granularity; Plan Document Header; Global Constraints; Task Structure; No Placeholders; Remember

### writing-skills
Use when creating new skills, editing existing skills, or verifying skills work before deployment
Sections: Overview; What is a Skill?; TDD Mapping for Skills; When to Create a Skill; Skill Types; Directory Structure; SKILL.md Structure; Overview; When to Use; Core Pattern (for techniques/patterns)

## Design, UI and media

### agent-designer
Use when the user asks to design a multi-agent system, pick an orchestration pattern (supervisor/swarm/pipeline), generate tool schemas for agents, or evaluate agent execution logs for cost, latency, and failure bottlenecks. Examples: 'design an agent architecture for research automation', 'generate Anthropic tool schemas from these tool descriptions', 'analyze these agent run logs for bottlenecks'. NOT for Claude Code workflow files (use workflow-builder) or single-agent prompt design (use agent-workflow-designer).
Sections: When to use; Pattern decision table; Workflow; References

### algorithmic-art
Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing artists' work to avoid copyright violations.
Sections: ALGORITHMIC PHILOSOPHY CREATION; DEDUCING THE CONCEPTUAL SEED; P5.JS IMPLEMENTATION; INTERACTIVE ARTIFACT CREATION; VARIATIONS & EXPLORATION; THE CREATIVE PROCESS; RESOURCES

### api-and-interface-design
Guides stable API and interface design. Use when designing APIs, module boundaries, or any public interface. Use when creating REST or GraphQL endpoints, defining type contracts between modules, or establishing boundaries between frontend and backend.
Sections: Overview; When to Use; Core Principles; REST API Patterns; TypeScript Interface Patterns; Common Rationalizations; Red Flags; Verification

### api-design-reviewer
Comprehensive REST API design review with automated linting, breaking-change detection, and design scorecards. Catches inconsistent conventions, missing versioning, and design smells before APIs ship. Use when reviewing a PR that adds or changes API endpoints, auditing an existing API for v2 migration, or establishing API standards for a team.
Sections: Overview; Quick Start — run the tools first; Core Capabilities; REST Design Principles; Versioning Strategies; Pagination Patterns; Error Response Formats; Authentication and Authorization Patterns; Rate Limiting Implementation; HATEOAS (Hypermedia as the Engine of Application State)

### apple-hig-expert
Audits and designs iOS/macOS/watchOS/visionOS interfaces against the Apple Human Interface Guidelines, including the Liquid Glass design language (announced WWDC25, shipped with iOS 26/macOS Tahoe, Sept 2025). Use when reviewing an Apple-platform mockup or app for HIG compliance, checking contrast or tap-target sizes, or designing native-feeling Apple UI (e.g., 'audit my iOS app against the HIG', 'is this text readable on Liquid Glass?').
Sections: Before Starting; Modes; The Compliance Tool; Worked example: iOS settings-screen audit; Core Design Principles; Proactive Triggers; Communication; Related Skills

### banner-design
Design banners for social media, ads, website heroes, creative assets, and print. Multiple art direction options with optional generated or supplied visuals. Actions: design, create, generate banner. Platforms: Facebook, Twitter/X, LinkedIn, YouTube, Instagram, Google Display, website hero, print. Styles: minimalist, gradient, bold typography, photo-based, illustrated, geometric, retro, glassmorphism, 3D, neon, duotone, editorial, collage.
Sections: When to Activate; Available Resources; Workflow; Banner Size Quick Reference; Art Direction Styles (Top 10); Design Rules; Security

### brainstorming
You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.
Sections: Anti-Pattern: "This Is Too Simple To Need A Design"; Checklist; Process Flow; The Process; After the Design; Key Principles; Visual Companion

### codebase-design
Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary.
Sections: Glossary; Deep vs shallow; Principles; Designing for testability; Relationships; Rejected framings; Going deeper

### database-designer
Use when the user asks to design database schemas, plan data migrations, optimize queries, choose between SQL and NoSQL, or model data relationships.
Sections: Overview; Core Competencies; Tool Workflow (run these — do not analyze schemas by hand); Database Design Principles; Best Practices; Query Generation Patterns; Migration Patterns; Performance Optimization; Multi-Database Decision Matrix; Sharding & Replication

### demo-video
Use when the user asks to create a demo video, product walkthrough, feature showcase, animated presentation, marketing video, or GIF from screenshots or scene descriptions. Orchestrates playwright, ffmpeg, and edge-tts MCPs to produce polished video content.
Sections: Overview; When to Use This Skill; Core Workflow; Output Artifacts; Scene Design System; Quality Checklist; Anti-Patterns; Cross-References

### design
Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini AI), corporate identity program (50 deliverables, CIP mockups), HTML presentations (Chart.js), banner design (22 styles, social/ads/web/print), icon design (15 styles, SVG, Gemini 3.1 Pro), social photos (HTML→screenshot, multi-platform). Actions: design logo, create CIP, generate mockups, build slides, design banner, generate icon, create social photos, social media images, brand identity, design system. Platforms: Facebook, Twitter, LinkedIn, YouTube, Instagram, Pinterest, TikTok, Threads, Google Ads.
Sections: When to Use; Sub-skill Routing; Logo Design (Built-in); CIP Design (Built-in); Slides (Built-in); Banner Design (Built-in); Icon Design (Built-in); Social Photos (Built-in); Workflows; References

### design-system
Token architecture, component specifications, and slide generation. Three-layer tokens (primitive→semantic→component), CSS variables, spacing/typography scales, component specs, strategic slide creation. Use for design tokens, systematic design, brand-compliant presentations.
Sections: When to Use; Token Architecture; Script Paths; Quick Start; References; Component Spec Pattern; Scripts; Templates; Integration; Slide System

### epic-design
Build immersive, cinematic 2.5D interactive websites using scroll storytelling, parallax depth, text animations, and premium scroll effects — no WebGL required. Use this skill for any web design task: landing pages, product sites, hero sections, scroll animations, parallax, sticky sections, section overlaps, floating products between sections, clip-path reveals, text that flies in from sides, words that light up on scroll, curtain drops, iris opens, card stacks, bleed typography, and any site that should feel cinematic or premium. Trigger on phrases like "make it feel alive", "Apple-style animation", "sections that overlap", "product rises between sections", "immersive", "scrollytelling", or any scroll-driven visual effect. Covers 45+ techniques across 8 categories. Always inspects, judges, and plans assets before coding. Use aggressively for ANY web design task.
Sections: Before Starting; Your Mindset; How This Skill Works; Step 1 — Understand the Brief + Inspect All Assets; Step 2 — Choose Your Techniques (Decision Engine); Step 3 — Layer Every Element; Step 4 — Apply Accessibility & Performance (Always); Step 5 — Code Structure (Always Use This HTML Architecture); Reference Files — Read These for Full Technique Details; Proactive Triggers

### frontend-design
Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
Sections: Ground it in the subject; Design principles; Process: brainstorm, explore, plan, critique, build, critique again; Restraint and self-critique; More on writing in design

### frontend-ui-engineering
Builds production-quality, accessible, responsive user-facing UIs. Use when building or modifying interfaces and pages, creating components, implementing layouts, meeting WCAG accessibility requirements, managing state, or when the output needs to look and feel production-quality rather than AI-generated.
Sections: Overview; When to Use; Component Architecture; State Management; Design System Adherence; Accessibility (WCAG 2.1 AA); Responsive Design; Loading and Transitions; See Also; Common Rationalizations

### full-page-screenshot
Use when the user asks to capture a full-page screenshot, long screenshot, or complete page capture of a web page. Handles SPA scroll containers, lazy-loaded images, and very tall pages via Chrome DevTools Protocol with zero external dependencies.
Sections: Prerequisites; Workflow; Core Capabilities; How It Works; Anti-Patterns; Troubleshooting; Cross-References

### image
When the user wants to create, generate, edit, or optimize images for marketing — blog heroes, social graphics, product mockups, profile banners, listing visuals, or brand assets. Also use when the user mentions 'AI image generation,' 'generate an image,' 'create a graphic,' 'product mockup,' 'hero image,' 'social media graphic,' 'banner image,' 'cover photo,' 'profile banner,' 'listing screenshot,' 'Flux,' 'Flux Kontext,' 'Midjourney,' 'DALL-E,' 'GPT Image,' 'ChatGPT Images,' 'Ideogram,' 'Gemini image,' 'Nano Banana,' 'Recraft,' 'Stable Diffusion,' 'Canva,' 'Figma,' 'image optimization,' 'compress images,' 'WebP,' or 'OG image.' Use this for general-purpose marketing image creation and optimization. For paid ad image creative and platform-specific ad specs, see ad-creative. For video production, see video.
Sections: Before Starting; Choosing Your Approach; AI Image Generation; Design Tools; Marketing Image Workflows; Image Optimization; OG & Social Preview Images; Common Mistakes; Task-Specific Questions; Related Skills

### observability-designer
Design production-ready observability strategies combining metrics, logs, and traces. Includes SLI/SLO design, golden-signals monitoring, alert optimization. Use when adding observability to a new service, refactoring alerting that is too noisy, or designing an SLO program before scaling production load.
Sections: Overview; Quick Start; Core Competencies; Scripts Overview; Integration Patterns; Advanced Patterns; Best Practices

### performance-optimization
Optimizes application performance across frontend, backend, queries, and databases. Use when performance requirements exist, when you suspect performance regressions, when Core Web Vitals or load times need improvement, when N+1 query patterns need fixing, or when profiling reveals bottlenecks.
Sections: Overview; When to Use; Core Web Vitals Targets; The Optimization Workflow; See Also; Common Rationalizations; Red Flags; Verification

### prototype
Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
Sections: Pick a branch; Rules that apply to both

### remotion
Best practices for Remotion - Video creation in React
Sections: When to use; New project setup; Designing a video; Starting preview; Optional: one-frame render check; Captions; Using FFmpeg; Silence detection; Audio visualization; Sound effects

### senior-frontend
Frontend development skill for React, Next.js, TypeScript, and Tailwind CSS applications. Use when building React components, optimizing Next.js performance, analyzing bundle sizes, scaffolding frontend projects, implementing accessibility, or reviewing frontend code quality.
Sections: Table of Contents; Project Scaffolding; Component Generation; Bundle Analysis; React Patterns; Next.js Optimization; Accessibility and Testing; Quick Reference; Resources; Assumptions and Verifiable Success Criteria (Karpathy discipline)

### slack-gif-creator
Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and animation concepts. Use when users request animated GIFs for Slack like "make me a GIF of X doing Y for Slack."
Sections: Slack Requirements; Core Workflow; Drawing Graphics; Available Utilities; Animation Concepts; Optimization Strategies; Philosophy; Dependencies

### theme-factory
Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. There are 10 pre-set themes with colors/fonts that you can apply to any artifact that has been creating, or can generate a new theme on-the-fly.
Sections: Purpose; Usage Instructions; Themes Available; Theme Details; Application Process; Create your Own Theme

### tool-design
This skill should be used for the tool-interface layer of an agent system specifically: writing tool descriptions agents can route on, designing tool schemas and response formats, naming conventions, actionable error recovery messages, MCP server design, tool-set consolidation, and deciding when to add or remove an individual tool. Use this when the unit of work is a single tool or a set of tools. Route project-shape, pipeline architecture, and task-model-fit decisions to project-development; route deciding whether to introduce sub-agents to multi-agent-patterns.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### ui-design-system
UI design system toolkit for Senior UI Designer including design token generation, component documentation, responsive design calculations, and developer handoff tools. Use when creating design systems, generating design tokens, maintaining visual consistency, or facilitating design-dev collaboration and developer handoff.
Sections: Table of Contents; Trigger Terms; Workflows; Tool Reference; Quick Reference Tables; Knowledge Base; Validation Checklist

### ui-styling
Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling, and canvas-based visual designs. Use when building user interfaces, implementing design systems, creating responsive layouts, adding accessible components (dialogs, dropdowns, forms, tables), customizing themes and colors, implementing dark mode, generating visual designs and posters, or establishing consistent styling patterns across applications.
Sections: Reference; When to Use This Skill; Core Stack; Quick Start; Component Library Guide; Theme & Customization; Accessibility Patterns; Tailwind Utilities; Responsive Design; Tailwind Customization

### ui-ux-pro-max
UI/UX design intelligence for web and mobile. Includes 50+ styles, 161 color palettes, 57 font pairings, 161 product types, 99 UX guidelines, and 25 chart types across 10 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui, and HTML/CSS). Actions: plan, build, create, design, implement, review, fix, improve, optimize, enhance, refactor, and check UI/UX code. Projects: website, landing page, dashboard, admin panel, e-commerce, SaaS, portfolio, blog, and mobile app. Elements: button, modal, navbar, sidebar, card, table, form, and chart. Styles: glassmorphism, claymorphism, minimalism, brutalism, neumorphism, bento grid, dark mode, responsive, skeuomorphism, and flat design. Topics: color systems, accessibility, animation, layout, typography, font pairing, spacing, interaction states, shadow, and gradient. Integrations: shadcn/ui MCP for component search and examples.
Sections: When to Apply; Rule Categories by Priority; Quick Reference; How to Use; Prerequisites; How to Use This Skill; Search Reference; Example Workflow; Output Formats; Tips for Better Results

### video
When the user wants to create, generate, or produce video content using AI tools or programmatic frameworks. Also use when the user mentions 'video production,' 'AI video,' 'Remotion,' 'Hyperframes,' 'HeyGen,' 'Synthesia,' 'Veo,' 'Sora,' 'Runway,' 'Kling,' 'Seedance,' 'Hailuo,' 'MiniMax,' 'Pika,' 'Hunyuan,' 'Wan,' 'video generation,' 'AI avatar,' 'talking head video,' 'programmatic video,' 'video template,' 'explainer video,' 'product demo video,' 'video pipeline,' or 'make me a video.' Use this for video creation, generation, and production workflows. For video content strategy and what to post, see social. For paid video ad creative, see ad-creative.
Sections: Before Starting; Choosing Your Approach; Programmatic Video; AI Video Generation; AI Avatars; Editing & Repurposing Tools; Video Production Workflows; Agent-Native Video Pipeline; Common Mistakes; Task-Specific Questions

### web-artifacts-builder
Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
Sections: Design & Style Guidelines; Quick Start; Reference

## Testing and QA

### address-sanitizer
Builds and runs code under AddressSanitizer to catch buffer overflows, use-after-free, and other memory errors during fuzzing or tests. Covers -fsanitize=address builds, ASAN_OPTIONS, reading the crash report, LeakSanitizer, and the overhead and platform trade-offs. Use when fuzzing C/C++ or Rust that has unsafe blocks or FFI, when debugging a memory corruption crash, or when reading an ASan stack trace.
Sections: Overview; When to Apply; Quick Reference; Step-by-Step; Common Patterns; Advanced Usage; Anti-Patterns; Tool-Specific Guidance; Troubleshooting; Related Skills

### api-test-suite-builder
Use when the user asks to generate API tests, create integration test suites, test REST endpoints, or build contract tests.
Sections: Overview; Core Capabilities; When to Use; Route Detection; Test Generation Patterns; Example Test Files; Generating Tests from Route Scan; Common Pitfalls; Best Practices

### atheris
Sets up and runs Atheris, the coverage-guided Python fuzzer built on libFuzzer. Covers TestOneInput harnesses, FuzzedDataProvider, instrumenting both pure Python and native C extensions, and running under AddressSanitizer. Use when fuzzing a Python package, hunting memory corruption in a Python C extension, or choosing between Atheris and Hypothesis for a Python target.
Sections: When to Use; Quick Start; Installation; Writing a Harness; Fuzzing Pure Python Code; Fuzzing Python C Extensions; Corpus Management; Running Campaigns; Sanitizer Integration; Advanced Usage

### browser-testing-with-devtools
Tests in real browsers via Chrome DevTools MCP. Use when building or debugging anything that runs in a browser. Use when you need to inspect the DOM, capture console errors, analyze network requests, profile performance, or verify visual output with real runtime data. Requires the chrome-devtools MCP server to be configured.
Sections: Overview; When to Use; Setting Up Chrome DevTools MCP; Security Boundaries; The DevTools Debugging Workflow; Writing Test Plans for Complex UI Bugs; Test Plan: Task completion animation bug; Screenshot-Based Verification; Console Analysis Patterns; Accessibility Verification with DevTools

### constant-time-testing
Measures timing side channels in cryptographic implementations by running them, using dudect for statistical analysis and Timecop over Valgrind for dynamic tracing. Covers the formal, symbolic, dynamic, and statistical tool categories and how to read a result. Use when testing whether a running implementation is constant-time, measuring timing variance on a compiled binary, or investigating a suspected timing attack. Not for statically inspecting compiler output — the constant-time-analysis plugin covers that.
Sections: Background; When to Use; Quick Reference; Constant-Time Tooling Categories; Testing Workflow; Tools and Approaches; Implementation Guide; Common Vulnerabilities; Case Studies; Advanced Usage

### coverage-analysis
Measures and interprets what a fuzzing campaign actually reaches, using llvm-cov, lcov, or a fuzzer's own coverage output. Covers baselining a new campaign, reading coverage reports, and turning uncovered regions into harness, seed, or dictionary work. Use when a fuzzer plateaus, when judging whether a harness is effective, after changing a harness, or when asking why some code is never reached.
Sections: Overview; When to Apply; Quick Reference; Ideal Coverage Workflow; Step-by-Step; Common Patterns; Advanced Usage; Anti-Patterns; Tool-Specific Guidance; Troubleshooting

### debugging-and-error-recovery
Guides systematic root-cause debugging. Use when tests fail, builds break, something that worked yesterday broke, behavior doesn't match expectations, or you encounter any unexpected error. Use when you need to figure out what broke and why — a systematic approach to finding and fixing the root cause rather than guessing.
Sections: Overview; When to Use; The Stop-the-Line Rule; The Triage Checklist; Error-Specific Patterns; Safe Fallback Patterns; Instrumentation Guidelines; Common Rationalizations; Treating Error Output as Untrusted Data; Red Flags

### fuzzing-obstacles
Patches past the barriers that stop a fuzzer making progress — checksum and hash verification, magic-value validation, time-based seeds, and other non-deterministic global state. Covers locating the blocking check, neutering it behind a fuzzing build flag, and avoiding the false positives a patch can introduce. Use when a fuzzer is stuck at validation, when coverage shows large regions behind a checksum, or when valid inputs are impractical to generate.
Sections: Overview; When to Apply; Quick Reference; Step-by-Step; Common Patterns; Advanced Usage; Anti-Patterns; Tool-Specific Guidance; Troubleshooting; Related Skills

### genotoxic
Graph-informed mutation testing triage. Parses codebases with Trailmark, runs mutation testing and necessist, then uses survived mutants, unnecessary test statements, and call graph data to identify false positives, missing test coverage, and fuzzing targets. Use when triaging survived mutants, analyzing mutation testing results, identifying test gaps, finding fuzzing targets from weak tests, running mutation frameworks (including circomvent and cairo-mutants), or using necessist.
Sections: When to Use; When NOT to Use; Prerequisites; Rationalizations to Reject; Quick Start; Workflow Overview; Decision Tree; Phase 1: Build Code Graph and Run Pre-Analysis; Phase 2: Run Mutation Testing; Phase 2b: Run Necessist (Optional)

### mutation-testing
Configures mewt or muton campaigns, analyzes surviving mutants, and investigates bugs exposed by testing gaps. Use when setting up mutation testing, reviewing campaign results, identifying equivalent mutants, or finding bugs from surviving mutations.
Sections: When to Use; When NOT to Use; Routing; Essential Commands; What Results Mean; Interpreting Mutation Types

### property-based-testing
Writes, reviews, and debugs property-based tests — Hypothesis, fast-check, proptest, jqwik, rapid, and Echidna or Medusa for Solidity invariants. Use whenever tests should cover a whole input domain instead of a hand-picked list of examples: encode/decode and serialize/deserialize pairs, parsers, canonicalizers and normalizers, validators, numeric and Decimal types, comparators and sort order, data structures, and smart-contract state invariants. Also use when adding cases to an existing @given, fast-check, or proptest suite, when judging whether existing property tests assert anything real, and when a generator has shrunk a counterexample and you need to tell a wrong property from a genuine bug. Not for coverage-guided binary fuzzing (libFuzzer, AFL), mutation-testing campaigns, static analysis, benchmarking, or end-to-end UI tests.
Sections: Property catalog; The two ways a property test asserts nothing; Where to look next; Introducing PBT to a project that lacks it

### pw
Production-grade Playwright testing toolkit. Use when the user mentions Playwright tests, end-to-end testing, browser automation, fixing flaky tests, test migration, CI/CD testing, or test suites. Generate tests, fix flaky failures, migrate from Cypress/Selenium, sync with TestRail, run on BrowserStack. 55 templates, 3 agents, smart reporting.
Sections: Available Commands; Quick Start Workflow; Golden Rules; Locator Priority; What's Included; Integration Setup; Quick Reference

### pw-browserstack
Run tests on BrowserStack. Use when user mentions "browserstack", "cross-browser", "cloud testing", "browser matrix", "test on safari", "test on firefox", or "browser compatibility".
Sections: Prerequisites; Capabilities; MCP Tools Used; Output

### pw-coverage
Analyze test coverage gaps. Use when user says "test coverage", "what's not tested", "coverage gaps", "missing tests", "coverage report", or "what needs testing".
Sections: Steps; Coverage Matrix; Recommended Test Plan; Output

### pw-fix
Fix failing or flaky Playwright tests. Use when user says "fix test", "flaky test", "test failing", "debug test", "test broken", "test passes sometimes", or "intermittent failure".
Sections: Input; Steps; Output

### pw-generate
Generate Playwright tests. Use when user says "write tests", "generate tests", "add tests for", "test this component", "e2e test", "create test for", "test this page", or "test this feature".
Sections: Input; Steps; Output

### pw-init
Set up Playwright in a project. Use when user says "set up playwright", "add e2e tests", "configure playwright", "testing setup", "init playwright", or "add test infrastructure".
Sections: Steps; Output

### pw-migrate
Migrate from Cypress or Selenium to Playwright. Use when user mentions "cypress", "selenium", "migrate tests", "convert tests", "switch to playwright", "move from cypress", or "replace selenium".
Sections: Input; Steps; Output

### pw-report
Generate test report. Use when user says "test report", "results summary", "test status", "show results", "test dashboard", or "how did tests go".
Sections: Steps; Summary; Failed Tests; Flaky Tests; By Project; Output

### pw-review
Review Playwright tests for quality. Use when user says "review tests", "check test quality", "audit tests", "improve tests", "test code review", or "playwright best practices check".
Sections: Input; Steps; <filename> — Score: X/10; Output

### pw-testrail
Sync tests with TestRail. Use when user mentions "testrail", "test management", "test cases", "test run", "sync test cases", "push results to testrail", or "import from testrail".
Sections: Prerequisites; Capabilities; MCP Tools Used; Test Annotation Format; Output

### senior-qa
Generates unit tests, integration tests, and E2E tests for React/Next.js applications. Scans components to create Jest + React Testing Library test stubs, analyzes Istanbul/LCOV coverage reports to surface gaps, scaffolds Playwright test files from Next.js routes, mocks API calls with MSW, creates test fixtures, and configures test runners. Use when the user asks to "generate tests", "write unit tests", "analyze test coverage", "scaffold E2E tests", "set up Playwright", "configure Jest", "implement testing patterns", or "improve test quality".
Sections: Quick Start; Tools Overview; QA Workflows; Reference Documentation; Common Patterns Quick Reference; Common Commands

### setup-pre-commit
Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing.
Sections: What This Sets Up; Steps; Notes

### skill-tester
Validate, test, and score the quality of skills within the claude-skills ecosystem. Comprehensive meta-skill: structure validation, Python script testing (syntax + imports + runtime + output format), multi-dimensional quality scoring with letter grades and tier classification (BASIC/STANDARD/POWERFUL). Use when authoring a new skill, auditing existing skills for tier promotion, setting up pre-commit hooks for skill quality, or integrating skill QA into CI.
Sections: Quick Start (exact, runnable from repo root); What Each Tool Checks; Tier Classification; CI Integration; Verification Loop; Troubleshooting

### systematic-debugging
Flags: auto
Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
Sections: Overview; The Iron Law; When to Use; The Four Phases; Red Flags - STOP and Follow Process; your human partner's Signals You're Doing It Wrong; Common Rationalizations; Quick Reference; When Process Reveals "No Root Cause"; Supporting Techniques

### test-driven-development
Use when implementing any feature or bugfix, before writing implementation code
Sections: Overview; When to Use; The Iron Law; Red-Green-Refactor; Good Tests; Why Order Matters; Common Rationalizations; Red Flags - STOP and Start Over; Example: Bug Fix; Verification Checklist

### vector-forge
Mutation-driven test vector generation. Finds implementations of a cryptographic algorithm or protocol, runs mutation testing to identify escaped mutants, then generates new test vectors that deliberately exercise the uncovered code paths. Compares before/after mutation kill rates to prove vector effectiveness. Use when generating cryptographic test vectors, measuring Wycheproof coverage gaps, finding escaped mutants via mutation testing, creating cross-implementation test suites, or improving test vector coverage for crypto primitives.
Sections: When to Use; When NOT to Use; Prerequisites; Rationalizations to Reject; Workflow Overview; Phase 1: Discovery; Phase 2: Harness; Phase 3: Baseline; Phase 4: Escape Analysis (Graph-Informed Triage); Phase 5: Vector Generation

### webapp-testing
Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
Sections: Decision Tree: Choosing Your Approach; Example: Using withserver.py; Reconnaissance-Then-Action Pattern; Common Pitfall; Best Practices; Reference Files

## Cloud, DevOps and security

### aws-solution-architect
Design AWS architectures for startups using serverless patterns and IaC templates. Use when asked to design serverless architecture, create CloudFormation templates, optimize AWS costs, set up CI/CD pipelines, or migrate to AWS. Covers Lambda, API Gateway, DynamoDB, ECS, Aurora, and cost optimization.
Sections: Workflow; Tools; Quick Start; Input Requirements; Output Formats; Reference Documentation

### azure-cloud-architect
Design Azure architectures for startups and enterprises. Use when asked to design Azure infrastructure, create Bicep/ARM templates, optimize Azure costs, set up Azure DevOps pipelines, or migrate to Azure. Covers AKS, App Service, Azure Functions, Cosmos DB, and cost optimization.
Sections: Workflow; Tools; Quick Start; Input Requirements; Anti-Patterns; Output Formats; Cross-References; Reference Documentation

### chaos-engineering
Use when planning, running, or learning from chaos engineering experiments. Triggers on "chaos experiment", "fault injection", "gameday", "resilience test", "blast radius", "steady state", "abort criteria", "Chaos Toolkit", "Chaos Mesh", "Litmus", "Gremlin", "AWS FIS", or any deliberate failure-injection question. Ships experiment designer, blast-radius calculator, and postmortem generator (all stdlib Python), 4 references on chaos principles + experiment design + attack taxonomy + tooling landscape, and a /chaos-experiment slash command. Composes with feature-flags-architect (kill switches as abort triggers) and kubernetes-operator (common chaos targets).
Sections: When to use; When NOT to use; Core principle: chaos without abort criteria is an outage; Quick start; The 3 Python tools; The 7 attack types (taxonomy); Tooling chooser; Workflows; Composition with other skills; Anti-patterns

### ci-cd-and-automation
Automates CI/CD pipeline setup. Use when setting up or modifying build and deployment pipelines. Use when you need to automate quality gates, configure test runners in CI, or establish deployment strategies.
Sections: Overview; When to Use; The Quality Gate Pipeline; GitHub Actions Configuration; Feeding CI Failures Back to Agents; Deployment Strategies; Environment Management; Automation Beyond CI; CI Optimization; Common Rationalizations

### ci-cd-pipeline-builder
Generate pragmatic CI/CD pipelines from detected project stack signals — fast baseline generation, repeatable checks, environment-aware deployment stages. Use when setting up CI for a new project, refactoring existing pipelines, or standardizing deployment workflows across multiple repos.
Sections: Overview; Core Capabilities; When to Use; Key Workflows; Script Interfaces; References

### deprecation-and-migration
Manages deprecation and migration. Use when removing old systems, APIs, or features. Use when migrating users from one implementation to another. Use when migrating a database schema in production, such as renaming or dropping a column without downtime (expand/contract). Use when deciding whether to maintain or sunset existing code.
Sections: Overview; When to Use; Core Principles; The Deprecation Decision; Compulsory vs Advisory Deprecation; The Migration Process; Deprecation Notice: OldService; Migration Patterns; Zombie Code; Common Rationalizations

### diagnosing-bugs
Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
Sections: Redact; Phase 1: Build a feedback loop; Phase 2: Reproduce + minimise; Phase 3: Hypothesise; Phase 4: Instrument; Phase 5: Fix + regression test; Phase 6: Cleanup

### diagramming-code
Generates Mermaid diagrams from Trailmark code graphs. Produces call graphs, class hierarchies, module dependency maps, containment diagrams, complexity heatmaps, and attack surface data flow visualizations. Use when visualizing code architecture, drawing call graphs, generating class diagrams, creating dependency maps, producing complexity heatmaps, or visualizing data flow and attack surface paths as Mermaid diagrams.
Sections: When to Use; When NOT to Use; Prerequisites; Version Gate; Quick Start; Diagram Types; Workflow; Script Reference; Customization; Supporting Documentation

### feature-flags-architect
Use when adding, retiring, or auditing feature flags. Triggers on "add a flag", "ship behind a flag", "rollout plan", "kill switch", "stale flags", "flag debt", "LaunchDarkly", "GrowthBook", "Statsig", "Unleash", "Flipt", or any progressive-delivery question. Ships flag debt scanner, rollout planner, and kill-switch auditor (all stdlib Python), 4 references on flag taxonomy + provider trade-offs + rollout strategies + lifecycle, plus a /flag-cleanup slash command.
Sections: When to use; Core principle: flags are a lifecycle, not an if; Quick start; The 4 flag types (taxonomy); The 3 Python tools; Provider chooser (5 + DIY); Workflows; References; Slash command; Asset templates

### gcp-cloud-architect
Design GCP architectures for startups and enterprises. Use when asked to design Google Cloud infrastructure, deploy to GKE or Cloud Run, configure BigQuery pipelines, optimize GCP costs, or migrate to GCP. Covers Cloud Run, GKE, Cloud Functions, Cloud SQL, BigQuery, and cost optimization.
Sections: Workflow; Tools; Quick Start; Input Requirements; Output Formats; Anti-Patterns; Cross-References; Reference Documentation

### google-workspace-cli
Google Workspace administration via the gws CLI (github.com/googleworkspace/cli). Install, authenticate, and automate Gmail, Drive, Sheets, Calendar, Docs, Chat, and Tasks. Run security audits and use local recipe templates and persona bundles. Use for Google Workspace admin, gws CLI setup, Gmail automation, Drive management, or Calendar scheduling.
Sections: Quick Start; Installation; Authentication; Workflow 1: Gmail Automation; Workflow 2: Drive & Sheets; Workflow 3: Calendar & Meetings; Workflow 4: Security Audit; Python Tools; Best Practices; Limitations

### helm-chart-builder
Helm chart development agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw — chart scaffolding, values design, template patterns, dependency management, security hardening, and chart testing. Use when: user wants to create or improve Helm charts, design values.yaml files, implement template helpers, audit chart security (RBAC, network policies, pod security), manage subcharts, or run helm lint/test.
Sections: Slash Commands; When This Skill Activates; Workflow; Tooling; Template Patterns; Values Design Principles; Dependency Management; Proactive Triggers; Installation; Related Skills

### incident-commander
Comprehensive incident response framework from detection through resolution and post-incident review. Battle-tested SRE/DevOps practices: severity classification, timeline reconstruction, structured post-incident analysis. Use when declaring an incident, coordinating multi-team response during an outage, leading a post-mortem, or setting up on-call practices for a new service.
Sections: Overview; Key Features; Skills Included; Incident Response Framework; Quick Reference; Detection; Initial Response (0-15 minutes); Mitigation Strategies; Recovery and Validation; Common Pitfalls

### incident-response
Use when a security incident has been detected or declared and needs classification, triage, escalation path determination, and forensic evidence collection. Covers SEV1-SEV4 classification, false positive filtering, incident taxonomy, and NIST SP 800-61 lifecycle.
Sections: Table of Contents; Overview; Incident Triage Tool; Incident Classification; Severity Framework; False Positive Filtering; Forensic Evidence Collection; Escalation Paths; Regulatory Notification Obligations; Workflows

### kubernetes-operator
Use when building a Kubernetes Operator — custom controllers that reconcile CRD state. Triggers on "build an operator", "CRD design", "reconcile loop", "controller-runtime", "kubebuilder", "operator-sdk", "metacontroller", "KOPF", "operator capability levels", or "custom resource". Ships CRD validator, reconcile-loop linter, and OperatorHub capability auditor (all stdlib Python), 4 references on the operator pattern + CRD design + reconcile patterns + tooling landscape, and a /operator-audit slash command. NOT a generic k8s skill — specifically the Operator pattern.
Sections: When to use; When NOT to use; Core principle: an operator is a reconcile loop, not a script; Quick start; The 3 Python tools; Tooling landscape; CRD design principles; Reconcile loop principles; Workflows; References

### migration-architect
Zero-downtime migration planning, compatibility validation, and rollback strategy generation. Tools for system, database, and infrastructure migrations with minimal business impact. Use when planning a database migration, infrastructure cutover, system replacement, or any high-risk transition that needs explicit rollback paths.
Sections: Overview; Core Capabilities; Quick Start — plan → check compatibility → generate rollback; Migration Patterns; Feature Flags for Migrations; Data Validation and Reconciliation; Rollback Strategies; Risk Assessment Framework; Migration Runbooks; Tools and Technologies

### monorepo-navigator
Navigate, manage, and optimize monorepos. Covers Turborepo, Nx, pnpm workspaces, and Lerna. Cross-package impact analysis, selective builds/tests on affected packages, remote caching, dependency graph visualization, and structured multi-repo to monorepo migrations. Use when setting up a new monorepo, optimizing CI for a large workspace, debugging cross-package dependency issues, or planning a multi-repo consolidation.
Sections: Overview; Core Capabilities; When to Use; Tool Selection; Turborepo; Workspace Analyzer; Common Pitfalls; Best Practices

### ms365-tenant-manager
Microsoft 365 tenant administration for Global Administrators. Automate M365 tenant setup, Office 365 admin tasks, Azure AD user management, Exchange Online configuration, Teams administration, and security policies. Generate PowerShell scripts for bulk operations, Conditional Access policies, license management, and compliance reporting. Use for M365 tenant manager, Office 365 admin, Azure AD users, Global Administrator, tenant configuration, or Microsoft 365 automation.
Sections: Quick Start; Workflows; Best Practices; Reference Guides; Limitations

### observability-and-instrumentation
Instruments code so production behavior is visible and diagnosable. Use when adding logging, metrics, tracing, or alerting. Use when shipping any feature that runs in production and you need evidence it works. Use when production issues are reported but you can't tell what happened from the available data.
Sections: Overview; When to Use; Process; Common Rationalizations; Red Flags; Verification

### red-team
Use when planning or executing authorized red team engagements, attack path analysis, or offensive security simulations. Covers MITRE ATT&CK kill-chain planning, technique scoring, choke point identification, OPSEC risk assessment, and crown jewel targeting.
Sections: Table of Contents; Overview; Engagement Planner Tool; Kill-Chain Phase Methodology; Technique Scoring and Prioritization; Choke Point Analysis; OPSEC Risk Assessment; Crown Jewel Targeting; Attack Path Methodology; Workflows

### senior-devops
Comprehensive DevOps skill for CI/CD, infrastructure automation, containerization, and cloud platforms (AWS, GCP, Azure). Includes pipeline setup, infrastructure as code, deployment automation, and monitoring. Use when setting up pipelines, deploying applications, managing infrastructure, implementing monitoring, or optimizing deployment processes.
Sections: Quick Start; Core Capabilities; Resources; Development Workflow; Multi-Cloud Cross-References; Cloud-Agnostic IaC; Troubleshooting

### slo-architect
Use when defining, reviewing, or operating SLOs/SLIs/error budgets. Triggers on "define an SLO", "what should our SLO be", "error budget", "burn rate", "SLI", "service level objective", "Google SRE workbook", "multi-window burn-rate alert", or any reliability-target question. Ships SLO designer, error-budget calculator with multi-window burn-rate thresholds, and SLO reviewer that catches the common bugs (target too aggressive, window too short, conflicting SLOs, no SLI definition). 4 references on SLO principles + SLI design + error budget math + composition with feature-flags-architect/chaos-engineering/kubernetes-operator. NOT a generic observability skill — specifically the SLO discipline.
Sections: When to use; When NOT to use; Core principle: an SLO is a promise about user experience; Quick start; The 3 Python tools; SLI selection cheatsheet; Error budget math (the basics); Composition with the rest of the portfolio; Workflows; References

### snowflake-development
Use when writing Snowflake SQL, building data pipelines with Dynamic Tables or Streams/Tasks, using Cortex AI functions, creating Cortex Agents, writing Snowpark Python, configuring dbt for Snowflake, or troubleshooting Snowflake errors.
Sections: Quick Start; SQL Best Practices; Data Pipelines; Cortex AI; Snowpark Python; dbt on Snowflake; Performance; Security; Proactive Triggers; Common Errors

### terraform-patterns
Terraform infrastructure-as-code agent skill and plugin for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. Covers module design patterns, state management strategies, provider configuration, security hardening, policy-as-code with Sentinel/OPA, and CI/CD plan/apply workflows. Use when: user wants to design Terraform modules, manage state backends, review Terraform security, implement multi-region deployments, or follow IaC best practices.
Sections: Slash Commands; When This Skill Activates; Workflow; Tooling; Module Design Patterns; Provider Configuration Patterns; State Management Decision Tree; CI/CD Integration Patterns; Proactive Triggers; Multi-Cloud Provider Configuration

### threat-detection
Use when hunting for threats in an environment, analyzing IOCs, or detecting behavioral anomalies in telemetry. Covers hypothesis-driven threat hunting, IOC sweep generation, z-score anomaly detection, and MITRE ATT&CK-mapped signal prioritization.
Sections: Table of Contents; Overview; Threat Signal Analyzer; Threat Hunting Methodology; IOC Analysis; Anomaly Detection; MITRE ATT&CK Signal Prioritization; Deception and Honeypot Integration; Workflows; Anti-Patterns

### trailmark-summary
Runs a Trailmark summary analysis on a codebase. Returns auto-detected languages, entry point count, and dependency list. Use when vivisect or galvanize needs a quick structural overview. Triggers: trailmark summary, code summary, structural overview.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Usage; Execution

## AI agents, prompts and context

### advanced-evaluation
This skill should be used for advanced LLM evaluation: LLM-as-judge systems, direct scoring, pairwise comparison, rubric calibration, evaluator bias mitigation, confidence scoring, and automated quality assessment.
Sections: When to Activate; Core Concepts; Evaluation Approaches; Task; Original Prompt; Response to Evaluate; Criteria; Instructions; Output Format; Critical Instructions

### agent-protocol
Flags: saves-to-~/.claude
Inter-agent communication protocol for C-suite agent teams. Defines invocation syntax, loop prevention, isolation rules, and response formats. Use when C-suite agents need to query each other, coordinate cross-functional analysis, or run board meetings with multiple agent roles.
Sections: Keywords; Invocation Syntax; Response Format; Loop Prevention (Hard Rules); Isolation Rules; When to Invoke vs When to Assume; Conflict Resolution; Broadcast Pattern (Crisis / CEO); Decision Memory (Canonical Layout); Quick Reference

### agenthub
Multi-agent collaboration plugin that spawns N parallel subagents competing on the same task via git worktree isolation. Agents work independently, results are evaluated by metric or LLM judge, and the best branch is merged. Use when: user wants multiple approaches tried in parallel — code optimization, content variation, research exploration, or any task that benefits from parallel competition. Requires: a git repo.
Sections: Slash Commands; Agent Templates; When This Skill Activates; Coordinator Protocol; Agent Protocol; DAG Model; Message Board; Result Summary; Evaluation Modes; Session Lifecycle

### autoresearch-agent
Autonomous experiment loop that optimizes any file by a measurable metric. Inspired by Karpathy's autoresearch. The agent edits a target file, runs a fixed evaluation, keeps improvements (git commit), discards failures (git reset), and loops indefinitely. Use when: user wants to optimize code speed, reduce bundle/image size, improve test pass rate, optimize prompts, improve content quality (headlines, copy, CTR), or run any measurable improvement loop. Requires: a target file, an evaluation command that outputs a metric, and a git repo.
Sections: Slash Commands; When This Skill Activates; Setup; Agent Protocol; Evaluators; Viewing Results; Proactive Triggers; Installation; Related Skills

### bdi-mental-states
This skill should be used when modeling agent mental states with BDI concepts: beliefs, desires, intentions, RDF-to-belief transformations, rational agency traces, cognitive agents, BDI ontologies, and neuro-symbolic AI integration.
Sections: When to Activate; Core Concepts; Practical Guidance; Detailed Topics; Guidelines; Competency Questions; Examples; Gotchas; Integration; References

### behuman
Use when the user wants more human-like AI responses — less robotic, less listy, more authentic. Triggers: 'behuman', 'be real', 'like a human', 'more human', 'less AI', 'talk like a person', 'mirror mode', 'stop being so AI', or when conversations are emotionally charged (grief, job loss, relationship advice, fear). NOT for technical questions, code generation, or factual lookups.
Sections: What This Does; When To Activate; The Process; Output Format; Examples; Token Cost; Anti-Patterns; Related Skills; Philosophy; Integration Notes

### business-operations-skills
Use when running, diagnosing, or designing internal business operations — process documentation, vendor SLAs, capacity planning, internal comms, SOP/runbook authoring, procurement spend. Triggers on "BizOps review", "where's the bottleneck", "vendor health", "internal SOP", "all-hands deck", "spend categorization", "capacity for Q3", "process mapping". Forks context to route to one of six BizOps sub-skills (process-mapper, vendor-management, capacity-planner, internal-comms, knowledge-ops, procurement-optimizer) and returns a digest. Distinct from business-growth (external sales motion) and c-level-advisor (strategic, not operational).
Sections: When to invoke; Routing logic (deterministic); Workflow (Matt Pocock grill discipline); Forcing-question library (grill-with-docs pattern); Assumptions; Non-goals; Distinct from; Output artifacts; Anti-patterns (do not); References

### caveman
Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler, articles, and pleasantries while keeping full technical accuracy. Use when user says "caveman mode", "talk like caveman", "use caveman", "less tokens", "be brief", or invokes /caveman.
Sections: Persistence; Rules; Auto-Clarity Exception; Tooling

### claude-coach
Personal coach that teaches users to become Claude power users. Use this skill the FIRST time a user asks to "learn Claude", "be a power user", "coach me", "teach me Claude tricks", "what can Claude do", "make me better at prompting", or any variation. After activation, also use it on EVERY subsequent turn to detect missed optimization opportunities (vague prompts, ignored capabilities, manual work Claude could automate) and surface a single power-user tip. Trigger generously — most users do not know what they do not know, so err on the side of coaching.
Sections: When to invoke this skill; First-activation flow; Ongoing coaching mode; Tone; References; Name; Description; Features; Usage; Examples

### collab-proof
Use when you want to understand what Claude contributed vs what you drove in a session. Triggers on: /collab-proof, session retrospective, ai contribution analysis, collaboration evidence, what did claude do.
Sections: Layer 01 — Signal detection; Layer 02 — WorkIntentClassifier; Layer 03 — Output; YYYY-MM-DD <title>; YYYY-MM-DD <bug title>; What shipped; What was figured out; Decisions made this session; Where it got hard; AI contribution summary

### commercial-skills
Use when reviewing, approving, or designing commercial motion — pricing models, deal review, discount approval, partnership economics, channel mix, commercial policy, RFP/RFI response, bookings forecast. Triggers on "review this deal", "should we discount", "pricing model", "partner economics", "RFP response", "bookings forecast", "channel mix". Forks context to route to one of seven Commercial sub-skills (pricing-strategist, deal-desk, partnerships-architect, channel-economics, commercial-policy, rfp-responder, commercial-forecaster) and returns a digest. Distinct from business-growth (sales execution) and c-level-advisor/cro-advisor (strategic CRO judgment).
Sections: When to invoke; Routing logic (deterministic); Workflow (Matt Pocock grill discipline); Forcing-question library (grill-with-docs pattern); Assumptions; Non-goals; Distinct from; Output artifacts; Anti-patterns (do not); References

### context-compression
This skill should be used when long-running agent sessions need context compression, structured summarization, compaction, token-per-task optimization, or durable handoff summaries that preserve decisions, files, risks, and next actions.
Sections: When to Activate; Core Concepts; Detailed Topics; Session Intent; Files Modified; Decisions Made; Current State; Next Steps; Practical Guidance; Examples

### context-degradation
This skill should be used for diagnosing and mitigating context degradation: lost-in-middle failures, context poisoning, context clash, context confusion, attention-pattern issues, and agent performance degradation caused by accumulated or conflicting context.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### context-engine
Flags: saves-to-~/.claude
Loads and manages company context for all C-suite advisor skills. Reads ~/.claude/company-context.md, detects stale context (>90 days), enriches context during conversations, and enforces privacy/anonymization rules before external API calls. Use when starting any C-suite advisor session, when context looks stale or missing, or before sending company data to an external service.
Sections: Keywords; Load Protocol (Run at Start of Every C-Suite Session); Context Quality Signals; Context Enrichment; Privacy Rules; Missing or Partial Context; Required Context Fields; References

### context-engineering
Optimizes agent context setup. Use when starting a new session, when agent output quality degrades, when switching between tasks, or when you need to configure rules files and context for a project.
Sections: Overview; When to Use; The Context Hierarchy; Tech Stack; Commands; Code Conventions; Boundaries; Patterns; Context Packing Strategies; Authentication (src/auth/)

### context-fundamentals
This skill should be used to explain or reason about the foundational concepts of context engineering: what context is, the anatomy of a context window, how attention mechanics work, the U-shaped attention curve, why context quality matters more than quantity, and the mental models needed to interpret every other context-engineering decision. Use this for conceptual explanation, onboarding, and background reading. Route operational work to the specialized skills: debugging attention failures goes to context-degradation, token-efficiency work goes to context-optimization, conversation summarization goes to context-compression, and project-shape decisions go to project-development.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### context-optimization
Flags: auto
This skill should be used for improving context efficiency: context budgeting, observation masking, prefix or KV-cache strategy, partitioning, token-cost reduction, retrieval scoping, and extending effective context capacity without lowering answer quality.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### cross-eval
/cross-eval <memo> — Multi-model consensus on a board memo or strategy brief. Claude + Codex + Gemini cross-review with graceful degradation. Use when a high-stakes memo needs an independent sanity check before the boardroom — e.g. a bet-the-company pivot or fundraise terms.
Sections: When to Run; Models Used (graceful degradation); Workflow; Output Format; Vote Tally; Consensus Concerns (≥2 models flagged); Divergent Concerns (1 model flagged); Consensus Supports (≥2 models endorsed); Recommendation; Open Questions for Founder

### dispatching-parallel-agents
Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies
Sections: Overview; When to Use; The Pattern; Agent Prompt Structure; Common Mistakes; When NOT to Use; Real Example from Session; Key Benefits; Verification; Real-World Impact

### engineering-advanced-skills
Index of 37 advanced engineering agent skills for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. Use when browsing or choosing among the POWERFUL-tier engineering skills: agent design, RAG, MCP servers, CI/CD, database design, observability, security auditing, changelog/release automation, reliability (SLO/chaos/flags/operators), platform ops.
Sections: Quick Start; Skills Overview; Rules

### engineering-skills
Index of the engineering-team skills bundle for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw, and 6 more tools. Architecture, frontend, backend, QA, DevOps, security, AI/ML, data engineering, Playwright, Stripe, AWS, MS365 (stdlib-only Python tools). Use when browsing or choosing among engineering-team role skills — load only the one specialist SKILL.md you need, never bulk-load the bundle.
Sections: Quick Start; Skills Overview; Python Tools; Rules

### evaluation
This skill should be used when building agent evaluation systems: deterministic checks, regression suites, multi-dimensional rubrics, quality gates, production monitoring, baseline comparison, and outcome measurement for agent pipelines.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### filesystem-context
This skill should be used when agent work needs file-backed context: durable scratchpads, tool-output offloading, just-in-time discovery, cross-agent handoff files, filesystem memory, or cleanup policies for context stored outside the prompt.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### git-guardrails-claude-code
Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
Sections: What Gets Blocked; Steps

### git-workflow-and-versioning
Structures git workflow practices. Use when making any code change. Use when committing, branching, resolving conflicts, splitting uncommitted work in a messy working tree into clean atomic commits, opening or reviewing a pull request (PR), pushing to a remote, or when you need to organize work across multiple parallel streams. Use when cutting a release, choosing a semantic version bump, tagging, or writing a changelog.
Sections: Overview; When to Use; Core Principles; Branching Strategy; Working with Worktrees; The Save Point Pattern; Change Summaries; Pre-Commit Hygiene; Handling Generated Files; Using Git for Debugging

### github-triage
Triages a repository's open GitHub issues and pull requests via the gh CLI. Optionally reviews and merges ready PRs — incrementally merging passing automated/bot PRs and maintainer-approved ones, and spawning review subagents for never-reviewed ones — then closes already-resolved issues with comments citing the resolving PR or commit, cross-links issues with their pending fix PRs, and assigns local-only priority and change-size estimates for everything outstanding. Use when triaging, grooming, or reviewing a repository's open issues and PRs.
Sections: When to Use; When NOT to Use; Core Principles; Workflow; Triage for OWNER/REPO  (N open issues); Safety Rules; Rationalizations to Reject

### goal-prompt
Drafts copy-paste-ready /goal commands for goal mode in Claude Code and Codex. Use when the user asks to create, write, rewrite, improve, compress, clean up, or prepare a goal prompt, goal condition, /goal command, goal-mode objective, or copy-ready long-running task objective.
Sections: Draft; Close the easy-outs; Security research goals; Format; Example

### harness-engineering
This skill should be used when designing autonomous agent harnesses: research loops, evaluation scaffolds, locked and editable surfaces, durable logs, novelty gates, pruning, rollback, PR preparation, and human approval boundaries.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### hosted-agents
This skill should be used when designing hosted or background agent infrastructure: sandboxed execution, remote coding environments, warm pools, session persistence, multiplayer collaboration, self-spawning agents, or Modal-style sandboxes.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### hub-eval
Evaluate and rank agent results by metric or LLM judge for an AgentHub session. Use when the user runs /hub-eval or asks to score, compare, or pick a winner among completed AgentHub agents.
Sections: Usage; What It Does; After Eval

### hub-init
Create a new AgentHub collaboration session with task, agent count, and evaluation criteria. Use when the user runs /hub-init or asks to start a multi-agent competition on a task.
Sections: Usage; What It Does; Baseline Capture; After Init

### hub-merge
Merge the winning agent's branch into base, archive losers, and clean up worktrees. Use when the user runs /hub-merge or asks to land the winning AgentHub result and tidy the session.
Sections: Usage; What It Does; Merge Summary; Safety; After Merge

### hub-run
One-shot lifecycle command that chains init → baseline → spawn → eval → merge in a single invocation. Use when the user runs /hub-run or asks to execute a full AgentHub competition end-to-end.
Sections: Usage; Parameters; What It Does; Critical Rules

### hub-status
Show DAG state, agent progress, and branch status for an AgentHub session. Use when the user runs /hub-status or asks how the AgentHub agents are doing.
Sections: Usage; What It Does; Output Format; After Status

### karpathy-coder
Use when writing, reviewing, or committing code to enforce Karpathy's 4 coding principles — surface assumptions before coding, keep it simple, make surgical changes, define verifiable goals. Triggers on "review my diff", "check complexity", "am I overcomplicating this", "karpathy check", "before I commit", or any code quality concern where the LLM might be overcoding.
Sections: The four principles; Slash command; Python tools (scripts/); Sub-agent; Pre-commit hook; References; When to relax; Cross-tool compatibility; Related skills (chains via context: fork)

### latent-briefing
This skill should be used when the user asks to "share memory between agents", "KV cache compaction for multi-agent", "orchestrator worker context", "latent briefing", "reduce worker tokens", "cross-agent memory without summarization", or discusses Attention Matching compaction, recursive language models with workers, or token explosion in hierarchical agents.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### llm-cost-optimizer
Use proactively whenever LLM API costs come up -- or should. Triggers include: 'my AI costs are too high', 'optimize token usage', 'which model should I use', 'LLM spend is out of control', 'implement prompt caching', 'we're about to launch an AI feature', 'build me an AI endpoint'. Don't wait for an explicit cost complaint -- if someone is building an AI feature, designing an LLM endpoint, or choosing between models, cost architecture belongs in the conversation. Apply immediately when any of these are true: a system prompt appears that exceeds a few hundred tokens, all requests are hitting the same model, max_tokens is not set, or no per-feature cost logging exists. NOT for RAG pipeline design (use rag-architect). NOT for improving prompt quality or effectiveness (use senior-prompt-engineer).
Sections: Step 0: Classify Before You Ask; Context You Need; Mode 1: Cost Audit; Mode 2: Optimize Existing System; Mode 3: Design Cost-Efficient Architecture; Proactive Flags; Failure Modes and Recovery; Handoff Triggers; Output Artifacts; Communication Standard

### llm-wiki
Use when building or maintaining a persistent personal knowledge base (second brain) in Obsidian where an LLM incrementally ingests sources, updates entity/concept pages, maintains cross-references, and keeps a synthesis current. Triggers include "second brain", "Obsidian wiki", "personal knowledge management", "ingest this paper/article/book", "build a research wiki", "compound knowledge", "Memex", or whenever the user wants knowledge to accumulate across sessions instead of being re-derived by RAG on every query.
Sections: Core principle; When to use; Architecture (three layers); Three core operations; Quick start; Slash commands (this plugin ships); Sub-agents (this plugin ships); Python tools (scripts/); Cross-tool compatibility; Obsidian setup (recommended)

### loop-library
Discover, find, compare, audit, repair, adapt, and design repeatable AI-agent loops with explicit triggers, actions, verification, stopping conditions, guardrails, and handoffs. Use when a user asks to analyze a codebase for potential loops, mine coding-thread history for work done more than once, turn repeated engineering work into a loop, find or recommend a published loop, create a recurring agent workflow or automation cadence, turn an outcome into a bounded copy-ready loop, or review an existing loop for weak checks, unsafe authority, unbounded repetition, stale state, or unclear stopping behavior.
Sections: Route the request; Discover loops from existing work; Find a published loop; Audit and repair a loop; Keep discovered loops, adaptations, and repairs grounded; Run the design interview; Design the feedback cycle; Validate every crafted loop; Deliver the loop; Loop name

### mcp-builder
Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
Sections: Overview; 🚀 High-Level Workflow; 📚 Documentation Library

### memory-systems
This skill should be used for persistent semantic memory in agent systems: cross-session knowledge retention, entity tracking, temporal validity, graph or vector retrieval, memory consolidation, and memory benchmark selection. Route file-backed scratchpads to filesystem-context, handoff summaries to context-compression, and token-efficiency tactics to context-optimization.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### multi-agent-patterns
This skill should be used when designing multi-agent systems that need context isolation, supervisor or swarm coordination, explicit handoffs, parallel execution, or a decision on whether multiple agents are justified.
Sections: When to Activate; Core Concepts; Detailed Topics; Practical Guidance; Examples; Guidelines; Gotchas; Integration; References; Skill Metadata

### prompt-engineer-toolkit
Turns marketing prompts into tested, versioned production assets: A/B prompt evaluation against structured test cases, immutable prompt version history with diffs, ready-to-use marketing prompt templates (ad copy, email campaigns, social posts, landing pages, SEO meta), and an LLM-governance playbook for marketing teams (claim discipline, disclosure rules, human-review gates). Use when a marketing team relies on AI-generated content and needs prompt quality to be measurable and safe — or when the user mentions 'prompt engineering,' 'improve my prompts,' 'prompt templates,' 'prompt versioning,' 'AI content workflow,' or 'AI governance for marketing.'
Sections: Overview; Core Capabilities; Key Workflows; Script Interfaces; Pitfalls, Best Practices & Review Checklist; References; Evaluation Design; Versioning Policy; Rollout Strategy

### prompt-governance
Use when managing prompts in production at scale: versioning prompts, running A/B tests on prompts, building prompt registries, preventing prompt regressions, or creating eval pipelines for production AI features. Triggers: 'manage prompts in production', 'prompt versioning', 'prompt regression', 'prompt A/B test', 'prompt registry', 'eval pipeline'. NOT for writing or improving individual prompts (use senior-prompt-engineer). NOT for RAG pipeline design (use rag-architect). NOT for LLM cost reduction (use llm-cost-optimizer).
Sections: Before Starting; How This Skill Works; Mode 1: Build Prompt Registry; Mode 2: Build Eval Pipeline; Mode 3: Governed Iteration; Proactive Triggers; Output Artifacts; Communication; Anti-Patterns; Related Skills

### ra-qm-skills
Router/index for the 15 regulatory & quality-management skills bundled in this plugin (ISO 13485 QMS, EU MDR 2017/745, FDA submissions under QMSR, ISO 14971 risk, CAPA, document control, ISO 27001/ISMS, ISO 42001 AIMS, EU AI Act, GDPR/DSGVO, SOC 2, auditing). Use when a compliance request doesn't obviously match one skill and you need to pick the right one (e.g., 'prepare us for an ISO 13485 audit', 'is my AI system high-risk under the AI Act').
Sections: Routing table; Quick start; Rules

### rag-architect
Use when the user asks to design a RAG pipeline, choose a chunking strategy or embedding model, pick a vector database, or evaluate retrieval quality (precision@k, recall@k, NDCG). Examples: 'design a RAG system for our docs', 'what chunk size should I use for this corpus', 'evaluate my retriever against ground truth'. NOT for general LLM cost tuning (use llm-cost-optimizer) or agent loops over retrieval (use agenthub).
Sections: Hard rules; Embedding model tiers (pattern, not price list); Workflow; References

### sample-skill
Sample Text Processor
Sections: Description; Features; Usage; Examples; Installation; Configuration; Architecture; Error Handling; Performance Considerations; Contributing

### self-eval
Honestly evaluate AI work quality using a two-axis scoring system. Use after completing a task, code review, or work session to get an unbiased assessment. Detects score inflation, forces devil's advocate reasoning, and persists scores across sessions.
Sections: Description; Features; Usage; Examples; Self-Evaluation; Self-Evaluation; What to Evaluate; How to Score — Two-Axis Model; Devil's Advocate (MANDATORY); Anti-Inflation Check

### senior-prompt-engineer
Use when the user asks to optimize prompts, design prompt templates, evaluate LLM outputs with an eval set, measure RAG retrieval quality, validate agent/tool configurations, analyze token usage, or design structured-output contracts. Covers eval-driven prompt iteration, RAG metrics (relevance, faithfulness, coverage), agent workflow validation, and token/cost budgeting — all model-agnostic, with three stdlib Python tools.
Sections: Operating Rules; Tools (exact CLIs, all stdlib); Workflows; References; Related Skills

### skills-handoff
Compact the current conversation into a handoff document for another agent to pick up. Save to a user-configured location (OS temp, home folder, or per-project .handoff/), redact secrets before write, suggest skills for the next session, and auto-load the latest handoff on the next SessionStart. First-run setup asks where to save so the project folder never gets cluttered. Use when the user says 'hand this off', 'handoff doc', 'summarize this for a new session', 'compact this conversation', 'I'm ending this session', 'pick this up later', or any variation signaling intent to pass work to a fresh agent. Also trigger on implicit signals: the user announcing they're switching machines, ending the day mid-task, or context is growing long without a natural stopping point.
Sections: Invocation Triggers; First-Run Setup; Output Path; Section Template; The Agent's Job; Anti-Patterns; Redaction; SessionStart Auto-Load; SessionEnd Reminder; Refreshing an Existing Handoff

### slicing-code-context
Selects bounded, graph-informed source slices with Trailmark and delegates focused code analysis or patch-proposal work to a smaller subagent. Use when offloading function-, class-, caller-, callee-, call-path-, entrypoint-, or line-focused code tasks to constrained or locally hosted models without exposing the full repository.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Workflow; Error Handling; Example Requests; Input to Output Example

### subagent-driven-development
Use when executing implementation plans with independent tasks in the current session
Sections: When to Use; The Process; Pre-Flight Plan Review; Model Selection; Handling Implementer Status; Handling Reviewer ⚠️ Items; Constructing Reviewer Prompts; File Handoffs; Durable Progress; Prompt Templates

### teach
Teach the user a new skill or concept, within this workspace.
Sections: Teaching Workspace; Philosophy; Lessons; Assets; The Mission; Zone Of Proximal Development; Knowledge; Skills; Acquiring Wisdom; Reference Documents

### tech-stack-evaluator
Technology stack evaluation and comparison with TCO analysis, security assessment, and ecosystem health scoring. Use when comparing frameworks, evaluating technology stacks, calculating total cost of ownership, assessing migration paths, or analyzing ecosystem viability.
Sections: Table of Contents; Capabilities; Quick Start; Input Formats; Analysis Types; Scripts; References; Confidence Levels; When to Use; When NOT to Use

### workflow-builder
Design and write deterministic multi-agent workflow scripts (.js files in .claude/workflows/) for Claude Code's Workflow tool. Use when a user wants to build, create, author, scaffold, or run a custom Claude Code workflow, orchestrate sub-agents (fan-out, pipeline, loop, judge-panel), or automate a repeatable multi-step task across fresh-context agents.
Sections: ALWAYS start every session with intake (non-negotiable); Decide if a workflow is even the right tool; Build → validate → run loop; Hard rules (validator enforces these); Tooling

### zero-hallucination-coder
Runs a disciplined Discuss -> Map -> Decompose -> Execute -> Verify loop that grounds code in verified structure — no invented APIs, no assumed imports, no placeholder code — with a lazy-senior-dev YAGNI ladder that deletes unnecessary code before it is written. Use when a coding task is high-stakes, complex, or spans existing code (auth, databases, migrations, multi-file features), or when the user explicitly asks to plan carefully before coding, avoid hallucinated code, or work rigorously. Not for trivial edits, typos, or throwaway one-off scripts — those do not need the full loop.
Sections: When to invoke (opt-in discipline); Credits & Inspiration; Before Starting; Modes; The Five-Phase Loop; Anti-Patterns (Rules 1-7 — always on, even when short-circuiting); Context Engineering Rules; When to Short-Circuit; Proactive Triggers; Output Artifacts

## Engineering and code

### code-simplification
Simplifies code for clarity. Use when refactoring code for clarity without changing behavior. Use when code works but is harder to read, maintain, or extend than it should be. Use when reviewing code that has accumulated unnecessary complexity.
Sections: Overview; When to Use; The Five Principles; The Simplification Process; Language-Specific Guidance; Common Rationalizations; Red Flags; Verification

### receiving-code-review
Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation
Sections: Overview; The Response Pattern; Forbidden Responses; Handling Unclear Feedback; Source-Specific Handling; YAGNI Check for "Professional" Features; Implementation Order; When To Push Back; Acknowledging Correct Feedback; Gracefully Correcting Your Pushback

### requesting-code-review
Use when completing tasks, implementing major features, or before merging to verify work meets requirements
Sections: When to Request Review; How to Request; Example; Integration with Workflows; Red Flags

### retro
Conduct a retrospective on a coding session.
Sections: Steps; Reference

### review-walkthrough
Generates an interactive HTML walkthrough for reviewing code changes. Use only when explicitly called.
Sections: Capture the branch diff; Shape the review; Render the artifact

### trailmark-structural
Runs full Trailmark structural analysis by building a graph, running `preanalysis()`, and reporting hotspots, taint, blast radius, privilege boundaries, attack surface, and version-gated Trailmark 0.4+/0.5+ data such as proxy counts, subgraph edges, type/reference summaries, and entrypoint attributes. Use when vivisect needs detailed structural data for a target. Triggers: structural analysis, blast radius, taint analysis, complexity hotspots, proxy nodes, type references.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Usage; Execution

### trailmark-variant-neighborhood
Expands one confirmed or suspected vulnerability into a Trailmark graph neighborhood of variant candidates by finding sibling functions, shared callers and callees, common sensitive sinks, common entrypoint paths, interface implementations, override relationships, type/reference neighbors, and structurally similar nodes. Use after one issue is found to seed variant-analysis, semgrep-rule-creator, static-analysis, or manual review with graph-derived candidate locations.
Sections: When to Use; When NOT to Use; Rationalizations to Reject; Workflow; Stop Conditions

### using-git-worktrees
Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback
Sections: Overview; Step 0: Detect Existing Isolation; Step 1: Create Isolated Workspace; Step 2: Project Setup; Step 3: Verify Clean Baseline; Quick Reference; Common Mistakes; Red Flags

### verification-before-completion
Flags: auto
Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
Sections: Overview; The Iron Law; The Gate Function; Common Failures; Red Flags - STOP; Rationalization Prevention; Key Patterns; Why This Matters; When To Apply; The Bottom Line

### wait-what
Stop. That last message did not land: re-pitch it.

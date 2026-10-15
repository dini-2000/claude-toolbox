#!/usr/bin/env python3
"""Curated install of Claude Toolbox (github.com/dini-2000/claude-toolbox) into ~/.claude/skills.

    python3 build_pack.py <extracted pack dir>            # stage in a temp dir and validate only
    python3 build_pack.py <extracted pack dir> --install  # stage, validate, then install
    python3 build_pack.py --sync                          # reinstall only custom/ and private/ skills after an edit

What it changes and why is in CLAUDE.md next to this script. Needs /usr/bin/ruby (Psych) for YAML checks.
"""
import collections, datetime, json, os, re, shutil, subprocess, sys, tempfile

SRC = os.path.abspath(sys.argv[1])
INSTALL = "--install" in sys.argv
REPO = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--repo=")), None)  # write the built tree into a git checkout
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.expanduser("~/.claude/skills")
CLAUDEMD = os.path.expanduser("~/.claude/CLAUDE.md")
SETTINGS = os.path.expanduser("~/.claude/settings.json")
CUSTOM = os.path.join(HERE, "custom")    # skills written for this pack: installed and published (sources also go to the repo's _build/custom)
PRIVATE = os.path.join(HERE, "private")  # local-only skills: installed, never written to the repo or its router
VENDOR = os.path.join(HERE, "vendor")    # screened upstream files that SKILL.md files reference, overlaid per skill, and the WHOLE skills; sources in vendor/MANIFEST.tsv
FIXES = os.path.join(HERE, "fixes")      # our corrections to upstream skills, laid over vendor/ (a SKILL.md here replaces the upstream text)
LOCAL_FIXES = os.path.join(HERE, "fixes-local")  # changes only this machine needs (e.g. its own download tool): laid over fixes/, never written to the repo

OMIT = {
    "claude-api": "outdated (pins claude-opus-4-8 as 'non-negotiable'); would replace Claude Code's maintained claude-api skill",
    "using-superpowers": "coercive meta-rules ('even a 1% chance a skill applies, you MUST invoke it'; ranks itself above default behaviour)",
    "docx": "stale copy of anthropic-skills:docx, scripts missing",
    "pdf": "stale copy of anthropic-skills:pdf",
    "pptx": "stale copy of anthropic-skills:pptx, scripts missing",
    "xlsx": "stale copy of anthropic-skills:xlsx, scripts missing",
    "skill-creator": "stale copy of anthropic-skills:skill-creator, assets missing",
    "self-improving-agent": "self-improving family: rewrites MEMORY.md and CLAUDE.md, competing with Claude Code's own memory",
    "status": "self-improving family: clashes with the built-in /status",
    "promote": "self-improving family: writes memory into CLAUDE.md",
    "remember": "self-improving family: appends straight to MEMORY.md at a wrongly computed path",
    "extract": "self-improving family: writes skills from memory",
    "skills-review": "self-improving family: memory pruning",
    "notebooklm": "drives Google sign-in through a 'stealth' automated browser; scripts missing",
    "browser-automation": "headline features include bot-detection evasion (fingerprint spoofing); scripts missing",
}
# skills taken whole from alirezarezvani/claude-skills at 19392f7a into vendor/<installed name>/ (SKILL.md included), since the
# pack's copies lack their scripts: installed name -> (upstream name, the family's main skill, which holds the scripts).
# Upstream ships them as plugins; installed on their own, the sub-commands get the family prefix (/hub:run -> /hub-run), so
# none replaces a built-in (/run, /loop, /resume) or another family's command.
WHOLE = {"agenthub": ("agenthub", "agenthub"), "hub-board": ("board", "agenthub"), "hub-eval": ("eval", "agenthub"),
         "hub-init": ("hub-init", "agenthub"), "hub-merge": ("merge", "agenthub"), "hub-run": ("run", "agenthub"),
         "hub-spawn": ("spawn", "agenthub"), "hub-status": ("hub-status", "agenthub"),
         "autoresearch-agent": ("autoresearch-agent", "autoresearch-agent"), "ar-loop": ("loop", "autoresearch-agent"),
         "ar-resume": ("ar-resume", "autoresearch-agent"), "ar-run": ("run", "autoresearch-agent"),
         "ar-setup": ("setup", "autoresearch-agent"), "ar-status": ("ar-status", "autoresearch-agent"),
         "security-guidance": ("security-guidance", "security-guidance")}
# collections added on 15 Oct 2026, taken whole into vendor/<name>/ at the commits MANIFEST.tsv gives (Codex's agents/openai.yaml
# left out); they install like the WHOLE skills above. LEFT_OUT gives each skill of theirs not taken, with why; omitted.tsv lists them.
ADDED = {"mattpocock/skills": [
    "codebase-design", "diagnosing-bugs", "domain-modeling", "improve-codebase-architecture", "prototype", "retro", "pr",
    "wizard", "teach", "to-questionnaire", "wait-what", "writing-for-agents", "git-guardrails-claude-code", "setup-pre-commit"],
         "addyosmani/agent-skills": [
    "api-and-interface-design", "browser-testing-with-devtools", "ci-cd-and-automation", "code-review-and-quality",
    "code-simplification", "constraint-driven-development", "context-engineering", "debugging-and-error-recovery",
    "deprecation-and-migration", "documentation-and-adrs", "doubt-driven-development", "frontend-ui-engineering",
    "git-workflow-and-versioning", "idea-refine", "incremental-implementation", "interview-me",
    "observability-and-instrumentation", "performance-optimization", "planning-and-task-breakdown", "security-and-hardening",
    "shipping-and-launch", "source-driven-development", "spec-driven-development"]}
ADDED["trailofbits/skills"] = [  # plugin-level files some need (agents, ct_analyzer, README) sit inside the skill
    "address-sanitizer", "aflpp", "agentic-actions-auditor", "algorand-vulnerability-scanner", "atheris", "audit-augmentation",
    "audit-prep-assistant", "burpsuite-project-parser", "cairo-vulnerability-scanner", "cargo-fuzz",
    "chrome-mcp-troubleshooting", "code-maturity-assessor", "codeql", "constant-time-analysis", "constant-time-testing",
    "cosmos-vulnerability-scanner", "coverage-analysis", "crypto-protocol-diagram", "diagramming-code", "differential-review",
    "dimensional-analysis", "dwarf-expert", "entry-point-analyzer", "firebase-apk-scanner", "fp-check", "fuzzing-dictionary",
    "fuzzing-obstacles", "genotoxic", "github-triage", "goal-prompt", "graph-evolution", "guidelines-advisor", "harness-writing",
    "libafl", "libfuzzer", "mermaid-to-proverif", "modern-cpp", "modern-python", "mutation-testing", "open-sourcing", "ossfuzz",
    "post-patch-validation", "property-based-testing", "review-walkthrough", "ruzzy", "sarif-parsing", "second-opinion",
    "secure-workflow-guide", "semgrep", "semgrep-rule-creator", "sharp-edges", "slicing-code-context",
    "solana-vulnerability-scanner", "substrate-vulnerability-scanner", "supply-chain-risk-auditor", "token-integration-analyzer",
    "ton-vulnerability-scanner", "trailmark", "trailmark-finding-triage", "trailmark-review-gate", "trailmark-structural",
    "trailmark-summary", "trailmark-variant-neighborhood", "variant-analysis", "vector-forge", "vulnerability-triage-brocards",
    "writing-lean-proofs", "wycheproof", "yara-rule-authoring"]
WHOLE.update({n: (n, n) for ns in ADDED.values() for n in ns})
LEFT_OUT = {
    "ask-matt (mattpocock/skills)": "a router over Matt Pocock's own collection; skill-router covers discovery",
    "audit-context-building (trailofbits/skills)": "its main mode is a plugin command that runs a workflow script",
    "c-review (trailofbits/skills)": "runs through its plugin's agents and workflow scripts, which a skills install doesn't provide",
    "chief-of-staff (mattpocock/skills)": "marked in progress upstream, and the toolbox already has a chief-of-staff",
    "claude-handoff (mattpocock/skills)": "marked in progress upstream",
    "code-improver (trailofbits/skills)": "runs through its plugin's agents and workflow scripts, which a skills install doesn't provide",
    "code-review (mattpocock/skills)": "its name would replace Claude Code's /code-review",
    "devcontainer-setup (trailofbits/skills)": "its Dockerfile pipes the Claude Code and fnm install scripts into bash",
    "gh-cli (trailofbits/skills)": "a plugin hook does its work, which a skills install doesn't provide",
    "grill-me (mattpocock/skills)": "the toolbox already has grill-me, adapted from Matt Pocock's earlier version",
    "grill-with-docs (mattpocock/skills)": "the toolbox already has grill-with-docs, adapted from Matt Pocock's earlier version",
    "grilling (mattpocock/skills)": "near-duplicate of grill-me",
    "handoff (mattpocock/skills)": "near-duplicate of skills-handoff, which is based on it",
    "implement (mattpocock/skills)": "spec-to-tickets chain (see to-spec)",
    "implement-spec (mattpocock/skills)": "spec-to-tickets chain (see to-spec)",
    "interpreting-culture-index (trailofbits/skills)": "interprets a proprietary hiring and personality survey; too narrow for a general collection",
    "let-fate-decide (trailofbits/skills)": "draws tarot cards to add randomness to planning; a novelty",
    "loop-me (mattpocock/skills)": "marked in progress upstream",
    "migrate-to-shoehorn (mattpocock/skills)": "migrates tests to the author's own library; too narrow for a general collection",
    "pr-improver (trailofbits/skills)": "runs through its plugin's agents and workflow scripts, which a skills install doesn't provide",
    "research (mattpocock/skills)": "its name is taken by the toolbox's research router",
    "rust-review (trailofbits/skills)": "runs through its plugin's agents and workflow scripts, which a skills install doesn't provide",
    "scaffold-exercises (mattpocock/skills)": "builds exercises for the author's courses",
    "semgrep-rule-variant-creator (trailofbits/skills)": "runs through its plugin's agents and workflow scripts, which a skills install doesn't provide",
    "setup-matt-pocock-skills (mattpocock/skills)": "sets up the spec-to-tickets chain, which is left out",
    "setup-ts-deep-modules (mattpocock/skills)": "marked in progress upstream",
    "skill-improver (trailofbits/skills)": "runs through its plugin's agents and workflow scripts, which a skills install doesn't provide",
    "spec-to-code-compliance (trailofbits/skills)": "its main mode is a plugin command that runs a workflow script",
    "tdd (mattpocock/skills)": "near-duplicate of test-driven-development and tdd-guide",
    "test-driven-development (addyosmani/agent-skills)": "its name is taken by superpowers' test-driven-development",
    "testing-handbook-generator (trailofbits/skills)": "maintains Trail of Bits' own testing-handbook skills",
    "to-spec (mattpocock/skills)": "spec-to-tickets chain: calls grilling, research, tdd and code-review by name, which clash here; brainstorming, writing-plans and executing-plans cover the flow",
    "to-tickets (mattpocock/skills)": "spec-to-tickets chain (see to-spec)",
    "triage (mattpocock/skills)": "spec-to-tickets chain (see to-spec)",
    "using-agent-skills (addyosmani/agent-skills)": "a router over Addy Osmani's own collection; skill-router covers discovery",
    "wayfinder (mattpocock/skills)": "spec-to-tickets chain (see to-spec)",
    "writing-beats (mattpocock/skills)": "marked in progress upstream",
    "writing-fragments (mattpocock/skills)": "marked in progress upstream",
    "writing-shape (mattpocock/skills)": "marked in progress upstream",
    "zeroize-audit (trailofbits/skills)": "runs through its plugin's agents and workflow scripts, which a skills install doesn't provide, and needs the serena MCP server",
}
# the pack's copies those replace: pack name -> installed name
REPLACED = {"agenthub": "agenthub", "board": "hub-board", "eval": "hub-eval", "merge": "hub-merge", "run": "hub-run",
            "spawn": "hub-spawn", "skills-init": "hub-init", "skills-status": "hub-status", "autoresearch-agent": "autoresearch-agent",
            "loop": "ar-loop", "resume": "ar-resume", "skills-run": "ar-run", "setup": "ar-setup", "security-guidance": "security-guidance"}
# near-duplicates (shared text or near-identical descriptions): drop -> the fuller copy that is kept
DUPES = {"competitors": "competitor-alternatives", "onboarding": "onboarding-cro", "paywalls": "paywall-upgrade-cro",
         "cro": "page-cro", "social-content": "social", "paid-ads": "ads", "popup-cro": "popups", "ab-test-setup": "ab-testing",
         "signup-flow-cro": "signup", "email-sequence": "emails", "free-tools": "free-tool-strategy", "schema": "schema-markup",
         "launch-strategy": "launch", "app-store-optimization": "aso", "referrals": "referral-program", "handoff": "skills-handoff",
         "programmatic-seo": "seo-programmatic", "local-seo-manager": "seo-local", "seo-schema": "schema-markup",
         "analytics": "analytics-tracking", "pricing": "pricing-strategy", "pricing-strategist": "pricing-strategy",
         "database-schema-designer": "database-designer", "mcp-server-builder": "mcp-builder", "cs-onboard": "onboard",
         "agent-workflow-designer": "agent-designer", "social-media-manager": "social",
         "post-mortem": "postmortem", "revenue-operations": "revops"}
PW = ["init", "review", "fix", "generate", "migrate", "coverage", "report", "testrail", "browserstack"]
RENAME = {n: "pw-" + n for n in PW}  # Playwright sub-commands: stop /init and /review clashes and generic names
TIER1 = {"skill-router", "stop-slop", "context-optimization", "systematic-debugging", "verification-before-completion"}
BUILTIN = set("""add-dir agents batch bashes bug btw claude-api clear code-review compact config context copy cost debug
desktop doctor effort exit export fast feedback fewer-permission-prompts help hooks ide init insights install-github-app
keybindings-help login logout loop mcp memory mobile model output-style permissions plan plugin pr-comments
privacy-settings release-notes remote-control resume review rewind run sandbox schedule security-review simplify skills
stats status statusline tasks teleport terminal-setup theme todos update-config upgrade usage vim dataviz
artifact-design artifact-diagramming artifact-capabilities""".split())

DOMAINS = [
    ("Writing and editing", "stop-slop copywriting copy-editing content-humanizer doc-coauthoring internal-comms md-document"),
    ("Decks and board material", "board-deck-builder md-slides slides board-prep board-meeting internal-narrative"),
    ("Finance and markets (most need the Octagon data MCP)", "financial-analyst financial-analyst-master research-finance sec-10k-analysis earnings-call-analysis stock-quote price-target-consensus industry-pe-ratios balance-sheet cash-flow-statement income-statement business-investment-advisor ma-playbook saas-metrics-coach"),
    ("Strategy and executive advice", "ceo-advisor cfo-advisor cto-advisor coo-advisor cmo-advisor chief-of-staff boardroom scenario-war-room hard-call stress-test andreessen mike grill-me strategic-alignment competitive-intel competitive-teardown intl-expansion pricing-strategy"),
    ("Research", "deep-research litreview market-research product-research research-summarizer dossier patent grants"),
    ("Compliance, risk and audit", "gdpr-audit-prep soc2-audit-prep iso27001-audit-prep eu-ai-act-specialist ai-act-readiness risk-management-specialist compliance-readiness general-counsel-advisor"),
    ("Marketing and growth", "marketing-plan product-marketing launch content-strategy emails cold-email ads ad-creative page-cro marketing-psychology public-relations social"),
    ("SEO and AI search", "seo seo-audit seo-technical ai-seo aeo schema-markup seo-programmatic seo-local"),
    ("Product and delivery", "product-strategist product-discovery senior-pm agile-product-owner code-to-prd spec-driven-workflow roadmap-communicator experiment-designer ab-testing"),
    ("Engineering", "senior-architect senior-backend senior-frontend senior-fullstack code-reviewer adversarial-reviewer tdd-guide zero-hallucination-coder database-designer rag-architect mcp-builder performance-profiler tech-debt-tracker"),
    ("Cloud, DevOps and security", "aws-solution-architect azure-cloud-architect gcp-cloud-architect senior-devops docker-development kubernetes-operator terraform-patterns ci-cd-pipeline-builder senior-security cloud-security threat-detection incident-commander"),
    ("Testing (Playwright commands are pw-*)", "pw webapp-testing senior-qa api-test-suite-builder"),
    ("Design and UI", "frontend-design ui-ux-pro-max design-system canvas-design algorithmic-art theme-factory apple-hig-expert a11y-audit web-artifacts-builder"),
    ("Data and analytics", "statistical-analyst senior-data-scientist senior-data-engineer product-analytics analytics-tracking data-quality-auditor sql-database-assistant"),
    ("Sales and customers", "sales-engineer deal-desk prospecting rfp-responder contract-and-proposal-writer customer-success-manager churn-prevention"),
    ("Agents, prompts and context", "agent-designer multi-agent-patterns prompt-engineer-toolkit senior-prompt-engineer context-optimization context-compression caveman evaluation advanced-evaluation"),
    ("Dev process (Superpowers)", "brainstorming writing-plans executing-plans subagent-driven-development test-driven-development requesting-code-review receiving-code-review finishing-a-development-branch using-git-worktrees"),
    ("Obsidian and notes", "obsidian-markdown obsidian-bases obsidian-cli json-canvas"),
]
# INDEX.md categories: first pattern matching the skill name wins, else first matching the description
CATS = [
    ("Executive, board and strategy", r"\b(ceo|cfo|cto|coo|cmo|cpo|ciso|caio|cdo|chro|vpe|cro-(advisor|review)|chief|board|founder|c-level|boardroom|executive|strateg|war-room|hard-call|stress-test|decide|decision|company-os|org-health|culture|andreessen|mike|grill|office-hours|intl-expansion|ma-playbook)"),
    ("Finance and markets", r"\b(sec|10-?k|10-?q|8-?k|s-1|earnings|stock|equit|valuation|financ|cash.flow|balance.sheet|income.statement|market.cap|price.target|analyst|pe.ratio|esg|commodit|forex|dividend|invest|trading|prediction.market|kalshi|revenue-(geographic|product))"),
    ("Compliance, risk, legal and quality", r"\b(gdpr|dsgvo|soc.?2|iso.?\d|hipaa|fda|mdr|compliance|audit|regulat|capa|qms|qmr|risk|legal|counsel|ai.act|isms|quality|clinical)"),
    ("SEO and AI search", r"\b(seo|aeo|serp|schema|sitemap|hreflang|backlink|search.console|llms\.txt)"),
    ("Sales and customers", r"\b(sales|deal|prospect|rfp|proposal|customer|churn|revops|revenue.operations|cold.email|outreach|partnership|procurement|vendor)"),
    ("Marketing, growth and copy", r"\b(marketing|copywrit|copy-edit|ads?\b|ad-|advertis|campaign|email|newsletter|social|content|brand|cro\b|conversion|landing|launch|pricing|referral|growth|paywall|popup|signup|onboarding|lead.magnet|webinar|public.relations|youtube|twitter|sms|aso\b|app.store|offer|free.tool|directory|community|competitor)"),
    ("Product and project management", r"\b(product|roadmap|backlog|user.stor|sprint|scrum|agile|prd|spec|discovery|experiment|ab.test|a/b|jira|confluence|atlassian|senior-pm|pm-|process|change.management|capacity|tc-tracker)"),
    ("Research and analysis", r"\b(research|literature|litreview|patent|grant|dossier|survey|interview|syllabus|meeting.analyzer)"),
    ("Writing, docs and presentations", r"\b(writ|prose|slop|humaniz|doc|slides|deck|presentation|markdown|md-|obsidian|canvas|narrative|comms|communication|changelog|tour|onboard)"),
    ("Design, UI and media", r"\b(design|ui|ux|tailwind|css|frontend|typograph|accessib|a11y|wcag|art\b|image|video|gif|banner|theme|remotion|screenshot|hig)"),
    ("Testing and QA", r"\b(test|playwright|pw\b|pw-|qa\b|coverage|testrail|browserstack|cypress|selenium)"),
    ("Cloud, DevOps and security", r"\b(aws|azure|gcp|cloud|devops|docker|kubernetes|helm|terraform|ci.cd|observab|slo|incident|security|secops|threat|pen.test|red.team|secret|vault|chaos|feature.flag|migration|snowflake|monorepo|ms365|google-workspace|dependency)"),
    ("AI agents, prompts and context", r"\b(agent|prompt|llm|rag|context|mcp|eval|skill|claude|subagent|memory|harness|latent|bdi|caveman|behuman|karpathy|loop-library|workflow|tool-design|hallucination)"),
    ("Engineering and code", r"."),
]
STOP = set("""a an and are as at be by can do does e.g etc for from g get has have how i if in into is it its like make may me more
must my need needs new no not of on one or our over should so such than that the their them then this those to two use used
user users uses using via want wants what when which who will with you your also any all about after before each other only
skill skills asks ask says mentions trigger triggers phrases including include includes help helps based work task tasks
without across within e whether etc covers covering provides provide guide guidance session sessions chat chats token tokens claude account accounts handover handoff""".split())
STOP |= set("""above again against ain am aren because been being below between both but couldn did didn doesn doing don down during
few further hadn hasn haven having he her here hers herself him himself his isn itself just ll mightn most mustn
myself needn nor now off once ours ourselves out own re same shan she shouldn some theirs themselves there these they
through too under until up ve very was wasn we were weren where while whom why won wouldn yours yourself yourselves um
uh umm hmm yeah yes okay alright like basically actually really literally sort kind maybe probably pretty quite lot
lots bit thing things stuff something anything everything nothing someone anyone everyone somebody anybody way ways
guess mean means meant know knows knew think thinks thought feel feels felt say says said tell tells told see sees
seen saw look looks looking looked come comes coming came goes going went gone got gets getting let lets put puts
putting take takes taking took taken give gives giving gave given keep keeps keeping kept try tries trying tried seem
seems seemed wanted wanting needed needing please thanks thank sure right well still even ever never always often
sometimes already yet much many less least several every either neither whole enough else instead rather almost around
three four five six seven eight nine ten first second third next last previous former latter half old good bad best
better great big small large little long short high low full main certain particular general real simple easy hard
able possible current currently recent recently later soon early late then today tomorrow yesterday twice time times
day days week weeks month months year years part parts point points case cases fact example examples end start step
steps level levels made makes making done does doing gets per""".split())  # plain English and speech fillers, so they carry no weight in find.py

RUBY = r'''
require "yaml"; require "json"; require "date"
Dir.glob(File.join(ARGV[0], "*/SKILL.md")).sort.each do |p|
  r = {"dir" => File.basename(File.dirname(p))}
  m = File.read(p, encoding: "UTF-8").match(/\A---\s*\n(.*?)\n---\s*\n/m)
  if m.nil? then r["error"] = "no frontmatter" else
    begin
      h = Psych.safe_load(m[1], [Date, Time], [], true)
      r["name"] = h["name"]; r["description"] = h["description"]; r["dmi"] = h["disable-model-invocation"]
    rescue => e
      r["error"] = e.message
    end
  end
  puts r.to_json
end
'''

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def split(text):
    m = FM.match(text)
    return m.group(1), text[m.end():]


def quote_description(fm):
    """Quote a plain-scalar description holding ': ' (invalid YAML, 12 skills in the pack) or ' #' (silently cut)."""
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"^description:[ \t]*(.*)$", line)
        if not m: continue
        v = m.group(1)
        if v[:1] in ("'", '"', "|", ">"): return fm
        j = i + 1
        while j < len(lines) and re.match(r"^[ \t]+\S", lines[j]): j += 1
        text = " ".join(x.strip() for x in [v] + lines[i + 1:j] if x.strip())
        if ": " not in text and " #" not in text: return fm
        lines[i:j] = ["description: '" + text.replace("'", "''") + "'"]
        return "\n".join(lines)
    return fm


DIRS = {"scripts", "references", "assets", "templates", "shared", "evaluators", "hooks", "reference", "data", "themes"}
# a file path as a whole token: never started inside a word or a URL (no letter, '/', ':' or '.' just before it); a ${VAR} prefix belongs to it
TOKEN = re.compile(r"(?<![\w{}./~:$-])\$?[\w{}./~-]+\.(py|js|ts|sh|mjs|cjs|md|json|html|yaml|yml|csv|txt|pdf|ttf|otf)\b")
NOT_SHIPPED = {"scripts/convert.sh", "scripts/audit_skills.py",  # upstream repo tooling that skill texts mention, never part of a skill
               "data/file1.json", "data/coco/train.json",  # example paths
               "assets/design-tokens.json",  # a project file: brand's and design-system's scripts write it in the user's project
               "hooks/block-dangerous-git.sh"}  # git-guardrails-claude-code has the user copy its script into .claude/hooks/
READ = re.compile(r"\b(load|loads|read|reads|located|from|use|uses|search|browse|see|check|consult|bundled|ships|includes)\b", re.I)
WRITE = re.compile(r"\b(save|saves|saved|write|writes|written|output|outputs|create|creates|generate|generates|generated|store|stores|stored|log|logs)\b", re.I)


def split_ref(tok):
    """(prefix, path) for a path token, the path starting at its first folder segment in DIRS; None for runtime paths
    (~/..., example domains) and tokens with no such segment."""
    segs = tok.split("/")
    if tok.startswith("~") or re.fullmatch(r"[\w-]+(\.[\w-]+)*\.[a-z]{2,}", segs[0]) and len(segs) > 1: return None
    for i, s in enumerate(segs[:-1]):
        if s in DIRS: return "/".join(segs[:i]), "/".join(segs[i:])
    return None


def ref_at(m):
    """split_ref for a TOKEN match; None for placeholders (<sub-skill>/scripts/x.py, {subcommand}.md), file:line sample output
    and NOT_SHIPPED paths."""
    if m.string[m.start() - 1:m.start()] == ">" or re.match(r":\d", m.string[m.end():m.end() + 2]): return None
    sp = split_ref(m.group(0))
    return None if not sp or "{" in sp[1] or "<" in sp[1] or sp[1] in NOT_SHIPPED else sp


LINK = re.compile(r"(?<![\w./~:$-])(?:\.\./)+[\w.-]+(?:/[\w.-]+)*/?")  # a relative path that climbs out of the skill folder


def inside(sd, tok):
    """tok works as written from the skill folder without climbing above the skills folder, so it works whatever that folder
    is called (../../skills/x/... works only in a folder named skills)."""
    rel = os.path.normpath(os.path.join(os.path.basename(sd), tok))
    return not rel.startswith("..") and os.path.exists(os.path.join(os.path.dirname(sd), rel))


def kept(s):
    """The installed name of a skill an upstream path names: the kept copy of a near-duplicate, or the renamed skill."""
    return DUPES.get(s, RENAME.get(s, s))


def resolves(sd, prefix, path):
    """The skill holds the file, the path works as written from the skill folder, or a sibling skill named in the prefix holds it."""
    root = os.path.dirname(sd)
    if os.path.exists(os.path.join(sd, path)) or prefix and inside(sd, prefix + "/" + path): return True
    return any(s not in (".", "..") and os.path.isfile(os.path.join(root, kept(s), "SKILL.md")) and os.path.exists(os.path.join(root, kept(s), path)) for s in prefix.split("/") if s)


def missing_files(sd, text):
    scripts = docs = False
    for m in TOKEN.finditer(text):
        sp = ref_at(m)
        if not sp or resolves(sd, *sp): continue
        if m.group(1) in ("py", "js", "ts", "sh", "mjs", "cjs"): scripts = True
        else: docs = True
    for line in text.splitlines():  # a folder named on its own (`./canvas-fonts`, the `themes/` directory) where the text reads from it
        if re.search(r"\bworkspace\b|current (?:working )?director", line, re.I): continue  # the user's folders (teach's ./lessons/), not the skill's
        for a, b in re.findall(r"`\./([\w-]+)/?`|`([\w-]+)/` director", line):
            if READ.search(line) and not WRITE.search(line) and not os.path.isdir(os.path.join(sd, a or b)): docs = True
    return "scripts-missing" if scripts else "refs-missing" if docs else ""


def skill_flags(sd):
    text = open(os.path.join(sd, "SKILL.md"), encoding="utf-8").read()
    return ",".join(f for f in [missing_files(sd, text), "saves-to-~/.claude" if SAVES.search(text) else ""] if f)


def fix_paths(root):
    """Point paths written in an upstream repo's layout at the installed files: ../<sibling>/<path> when a sibling skill named
    in the prefix holds the file, else <path> when the skill holds it (vendor/ copies bundle-level files into each skill that
    names them). A second pass does the same for links that climb out of the skill (../../../skills/cto-advisor/SKILL.md,
    ../social-content/), naming the last installed skill in the link (a dropped near-duplicate or a renamed skill counts as
    its installed name), or pointing inside the skill when it holds the path that follows the ../ segments (../../tools/x.md
    becomes tools/x.md). Paths that already work, and the rest (upstream agents/, megaprompts/), stay. Returns the
    skills rewritten, with their rewrite counts."""
    names, done = set(skill_dirs(root)), {}
    for d in sorted(names):
        sd, n = os.path.join(root, d), [0]
        def fix(m):
            tok = m.group(0); sp = ref_at(m)
            if not sp or not sp[0] or tok.startswith(("/", "$", "{")) or inside(sd, tok): return tok  # absolute, ${VAR} and {baseDir} paths stay
            prefix, path = sp
            for s in reversed(prefix.split("/")):
                k = kept(s)
                if k in names and k != d and os.path.exists(os.path.join(root, k, path)): n[0] += 1; return f"../{k}/{path}"
            if os.path.exists(os.path.join(sd, path)): n[0] += 1; return path
            return tok
        def fix_link(m):
            tok = m.group(0).rstrip("."); tail = m.group(0)[len(tok):]
            if inside(sd, tok): return m.group(0)
            own = re.sub(r"^(\.\./)+", "", tok)  # an upstream repo-level file vendor/ copied into the skill (../../tools/x.md)
            if own != tok and os.path.exists(os.path.join(sd, own)): n[0] += 1; return own + tail
            segs = [s for s in tok.split("/") if s not in ("", "..")]
            for i in range(len(segs) - 1, -1, -1):
                k = kept(segs[i])
                if k not in names: continue
                rest, slash = "/".join(segs[i + 1:]), "/" if tok.endswith("/") else ""
                new = (rest + slash if rest else "") if k == d else f"../{k}/" + (rest + slash if rest else "")
                if new and os.path.exists(os.path.join(root, k, rest)): n[0] += 1; return new + tail
                break
            return m.group(0)
        p = os.path.join(sd, "SKILL.md"); text = open(p, encoding="utf-8").read(); new = LINK.sub(fix_link, TOKEN.sub(fix, text))
        if new != text: open(p, "w", encoding="utf-8").write(new); done[d] = n[0]
    return done


def body_sans_name(d):
    return re.sub(r"^name:.*$", "", open(os.path.join(SRC, d, "SKILL.md"), encoding="utf-8").read(), count=1, flags=re.M)


def category(name, desc):
    for field in (name, desc.lower()):
        for title, pat in CATS[:-1]:
            if re.search(pat, field): return title
    return CATS[-1][0]


def skill_dirs(root):
    return sorted(d for d in os.listdir(root) if os.path.isfile(os.path.join(root, d, "SKILL.md"))) if os.path.isdir(root) else []


def write_router(stage, desc, flags, sections, final):
    """skill-router/: SKILL.md, catalog.tsv (one line per skill), INDEX.md (detailed, by category), find.py (ranked search)"""
    rd = os.path.join(stage, "skill-router"); os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, "catalog.tsv"), "w", encoding="utf-8") as f:
        f.write("name\tflags\tdescription\n")
        for n in sorted(desc): f.write(f"{n}\t{('auto,' if n in TIER1 else '') + flags.get(n, '')}\t{desc[n]}\n")
    groups = collections.defaultdict(list)
    for n in sorted(desc): groups[category(n, desc[n])].append(n)
    order = [t for t, _ in CATS if groups.get(t)]
    idx = [f"# Skills index\n\n{len(desc)} skills from Claude Toolbox, grouped by area. `auto` skills are in Claude's skill list; the rest load on demand: read `~/.claude/skills/<name>/SKILL.md`, or the user runs `/<name>`.\n",
           "Flags: `scripts-missing` = calls a script that was not shipped (do that step by hand or skip it); `refs-missing` = points to reference docs that were not shipped; `saves-to-~/.claude` = files notes under ~/.claude.\n",
           "## Contents\n" + "\n".join(f"- {t} ({len(groups[t])})" for t in order) + "\n"]
    for t in order:
        idx.append(f"## {t}\n")
        for n in groups[t]:
            fl = ", ".join(x for x in [("auto" if n in TIER1 else ""), flags.get(n, "")] if x)
            idx.append(f"### {n}\n" + (f"Flags: {fl}\n" if fl else "") + f"{desc[n]}\n" + (f"Sections: {'; '.join(sections[n])}\n" if sections.get(n) else ""))
    open(os.path.join(rd, "INDEX.md"), "w", encoding="utf-8").write("\n".join(idx))
    open(os.path.join(rd, "find.py"), "w", encoding="utf-8").write(FIND.replace("__STOP__", " ".join(sorted(STOP))))
    missing_map, lines = [], []
    for title, names in DOMAINS:
        missing_map += [n for n in names.split() if n not in final]
        lines.append(f"- {title}: {', '.join(n for n in names.split() if n in final)}")
    open(os.path.join(rd, "SKILL.md"), "w", encoding="utf-8").write(ROUTER.format(n=len(final) - len(TIER1), domains="\n".join(lines), note=LOCAL_NOTE))
    return groups, order, missing_map


SAVES = re.compile(r"~/\.claude/(decisions|company-context|briefs|postmortems|freezes|execution)")


def section_titles(body):
    return [re.sub(r"[*`_\[\]]", "", h).strip() for h in re.findall(r"^## +(.+)$", body, re.M)][:10]


def lay_local_fixes(root):
    """fixes-local/<skill>/<path> over the skills in root. No SKILL.md, so the texts and the router match the repo's."""
    ds = [d for d in sorted(os.listdir(LOCAL_FIXES)) if os.path.isdir(os.path.join(LOCAL_FIXES, d))] if os.path.isdir(LOCAL_FIXES) else []
    for d in ds:
        assert os.path.isdir(os.path.join(root, d)), f"fixes-local/{d}: no skill of that name"
        assert not any("SKILL.md" in fs for _, _, fs in os.walk(os.path.join(LOCAL_FIXES, d))), f"fixes-local/{d}: no SKILL.md here"
        shutil.copytree(os.path.join(LOCAL_FIXES, d), os.path.join(root, d), dirs_exist_ok=True)
    return ds


def stage_skill(sd, d, new, stage, final):
    """Copy one skill into the stage and fix it up for Claude Code; returns its flags and its first ten section titles."""
    shutil.copytree(sd, os.path.join(stage, new))
    for o in (VENDOR, FIXES):  # vendor/ holds a SKILL.md only for WHOLE skills; fixes/ may replace one
        v = os.path.join(o, new)
        if os.path.isdir(v): shutil.copytree(v, os.path.join(stage, new), dirs_exist_ok=True)
    if new in WHOLE: whole_text(os.path.join(stage, new), new, final)
    p = os.path.join(stage, new, "SKILL.md")
    text = open(p, encoding="utf-8").read()
    flag = [missing_files(os.path.join(stage, new), text)]
    if SAVES.search(text): flag.append("saves-to-~/.claude")
    text, body = finish_text(text, d, new, final)
    open(p, "w", encoding="utf-8").write(text)
    return ",".join(f for f in flag if f), section_titles(body)


def whole_text(sd, new, final):
    """A WHOLE skill's texts and scripts: plugin commands (/hub:spawn, /ar:ar-status) become the installed names (/hub-spawn,
    /ar-status), and {skill_path}/, which upstream leaves undefined, becomes the family's main skill, where the scripts live."""
    main = WHOLE[new][1]
    for dp, _, fs in os.walk(sd):
        for f in fs:
            if not f.endswith((".md", ".py")): continue
            p = os.path.join(dp, f); t = open(p, encoding="utf-8").read()
            n = re.sub(r"/(hub|ar):(?:(?:hub|ar)-)?([a-z][a-z-]*)", lambda m: f"/{m.group(1)}-{m.group(2)}" if f"{m.group(1)}-{m.group(2)}" in final else m.group(0), t)
            n = n.replace("{skill_path}/", "" if main == new else f"../{main}/")
            if n != t: open(p, "w", encoding="utf-8").write(n)


def finish_text(text, d, new, final):
    """A SKILL.md made ready for Claude Code: installed command names, the installed name, a quoted description, and
    disable-model-invocation outside TIER1. Returns the new text and its body."""
    text = re.sub(r"/pw:([a-z0-9][a-z0-9-]*)", lambda m: f"/pw-{m.group(1)}" if f"pw-{m.group(1)}" in final else m.group(0), text)
    text = re.sub(r"/pw:(?![a-z0-9])", "/pw", text)
    text = re.sub(r"/cs:([a-z0-9][a-z0-9-]*)", lambda m: f"/{m.group(1)}" if m.group(1) in final else m.group(0), text)
    fm, body = split(text)
    if new != d: fm = re.sub(r"^name:.*$", f"name: {new}", fm, count=1, flags=re.M)
    if d == "claude-coach": fm = re.sub(r"^(Name|Version):.*\n", "", fm, flags=re.M)  # duplicate capitalised keys
    fm = quote_description(fm)
    fm = fm.replace("`---` HR boundaries", "three-dash horizontal rules")  # md-slides
    assert "---" not in fm, f"{new}: Claude Code ends the frontmatter at the first '---', even mid-line, and drops the keys after it"
    fm = re.sub(r"^allowed-tools:.*(\n[ \t]+.*)*(\n|$)", "", fm, flags=re.M)  # no skill pre-approves tools: permissions stay the user's
    fm = re.sub(r"^disable-model-invocation:.*(\n|$)", "", fm, flags=re.M).rstrip("\n")  # some upstreams set it; a second key breaks YAML
    if new not in TIER1: fm += "\ndisable-model-invocation: true"
    return f"---\n{fm}\n---\n{body}", body


def validate(root):
    """Parse every SKILL.md under root with a real YAML parser; returns the descriptions by name and the skills that fail."""
    res = [json.loads(l) for l in subprocess.run(["/usr/bin/ruby", "-e", RUBY, root], capture_output=True, text=True, check=True).stdout.splitlines()]
    bad = [r for r in res if r.get("error") or r.get("name") != r["dir"] or not isinstance(r.get("description"), str) or not r["description"].strip()
           or (r["dmi"] is not True) != (r["dir"] in TIER1)]
    return {r["dir"]: re.sub(r"\s+", " ", r.get("description") or "").strip() for r in res}, bad


def sync():
    """--sync: reinstall only the custom/, private/ and WHOLE skills, then rewrite the router from the whole install, so a fact
    update needs neither the pack nor a full build. The repo is untouched: a custom/ change still needs --repo and a commit."""
    custom, private, whole = skill_dirs(CUSTOM), skill_dirs(PRIVATE), sorted(WHOLE)
    assert os.path.isfile(os.path.join(DEST, "skill-router", "catalog.tsv")), f"no install in {DEST}: run a full build with --install first"
    final = set(skill_dirs(DEST)) | set(custom) | set(private) | set(whole)
    stage = tempfile.mkdtemp(prefix="skills-sync-")
    for d in custom + private: stage_skill(os.path.join(CUSTOM if d in custom else PRIVATE, d), d, d, stage, final)
    for d in whole: stage_skill(os.path.join(VENDOR, d), WHOLE[d][0], d, stage, final)
    bad = validate(stage)[1]
    if bad: sys.exit(f"not syncing: {bad}")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for d in custom + private + whole:
        live = os.path.join(DEST, d)
        if os.path.exists(live): shutil.move(live, os.path.join(os.path.expanduser("~/.Trash"), f"{d}-{stamp}"))
        shutil.copytree(os.path.join(stage, d), live)
    vendored = [d for d in sorted(os.listdir(VENDOR)) if os.path.isdir(os.path.join(VENDOR, d)) and d not in custom + private + whole] if os.path.isdir(VENDOR) else []
    for d in vendored:  # files only added or replaced; a file dropped from vendor/ stays installed until a full build
        assert os.path.isdir(os.path.join(DEST, d)), f"vendor/{d}: no installed skill of that name"
        shutil.copytree(os.path.join(VENDOR, d), os.path.join(DEST, d), dirs_exist_ok=True)
    fixes = [d for d in sorted(os.listdir(FIXES)) if os.path.isdir(os.path.join(FIXES, d))] if os.path.isdir(FIXES) else []
    for d in fixes:  # our corrections go over vendor/; a SKILL.md here is finished as a full build would
        if d in WHOLE: continue  # staged with its fixes above
        assert os.path.isdir(os.path.join(DEST, d)) and d not in custom + private, f"fixes/{d}: no installed upstream skill of that name"
        shutil.copytree(os.path.join(FIXES, d), os.path.join(DEST, d), dirs_exist_ok=True)
        p = os.path.join(FIXES, d, "SKILL.md")
        if os.path.isfile(p): open(os.path.join(DEST, d, "SKILL.md"), "w", encoding="utf-8").write(finish_text(open(p, encoding="utf-8").read(), d, d, final)[0])
    lay_local_fixes(DEST)
    fixed = fix_paths(DEST)
    desc = validate(DEST)[0]; desc.pop("skill-router", None)  # the full build writes the router after validating, so it is not in desc
    flags, sections = {}, {}
    for n in desc:
        flags[n] = skill_flags(os.path.join(DEST, n))
        sections[n] = section_titles(split(open(os.path.join(DEST, n, "SKILL.md"), encoding="utf-8").read())[1])
    tmp = tempfile.mkdtemp(prefix="skills-router-")
    missing_map = write_router(tmp, desc, flags, sections, final)[2]
    for f in os.listdir(os.path.join(tmp, "skill-router")): shutil.copy2(os.path.join(tmp, "skill-router", f), os.path.join(DEST, "skill-router", f))
    print(f"synced {len(custom)} custom, {len(private)} private and {len(whole)} whole upstream skills and vendor files for {len(vendored)} more into {DEST} (old copies in the Trash); router rewritten for {len(desc)} skills")
    if fixed: print(f"paths rewritten to the installed layout: {sum(fixed.values())} in {len(fixed)} skills: {', '.join(sorted(fixed))}")
    print("flags:", {k: sum(1 for v in flags.values() if k in v) for k in ("scripts-missing", "refs-missing", "saves-to-~/.claude")})
    if missing_map: print("domain-map names not installed:", missing_map)
    if custom: print("custom/ skills are public: the repo changes only through a full build with --repo=repo, committed with the user's word")


def main():
    src = skill_dirs(SRC)
    dups = {d: f"identical copy of {d[7:]}" for d in src if d.startswith("skills-") and d[7:] in src and body_sans_name(d) == body_sans_name(d[7:])}
    near = {d: f"near-duplicate of {k} (kept the fuller copy)" for d, k in DUPES.items()}
    repl = {d: f"lacks its scripts; replaced by {n}, taken whole from upstream" for d, n in REPLACED.items()}
    dropped = {**OMIT, **repl, **dups, **near}
    unknown = (set(OMIT) | set(REPLACED) | set(DUPES) | set(DUPES.values())) - set(src)
    assert not unknown, f"names not in pack: {unknown}"
    keep = [d for d in src if d not in dropped and d != "skill-router"]
    custom, private = skill_dirs(CUSTOM), skill_dirs(PRIVATE)
    home = {**{d: CUSTOM for d in custom}, **{d: PRIVATE for d in private}}
    taken = (set(custom) & set(private)) | (set(home) & (set(src) | set(RENAME.values()) | {"skill-router"}))
    assert not taken, f"custom or private names already used: {taken}"
    taken = set(WHOLE) & (set(keep) | set(home) | set(RENAME.values()))
    assert not taken, f"whole upstream skill names already used: {taken}"
    assert all(os.path.isfile(os.path.join(VENDOR, d, "SKILL.md")) for d in WHOLE), "vendor/ lacks a WHOLE skill's SKILL.md"
    home.update({d: VENDOR for d in WHOLE})
    keep += custom + private + sorted(WHOLE)
    final = {RENAME.get(d, d) for d in keep} | {"skill-router"}
    clash = final & BUILTIN
    assert not clash, f"names that would replace Claude Code built-ins: {clash}"

    stage = tempfile.mkdtemp(prefix="skills-stage-")
    flags, sections = {}, {}
    for d in keep:
        new = RENAME.get(d, d)
        flags[new], sections[new] = stage_skill(os.path.join(home.get(d, SRC), d), WHOLE[d][0] if d in WHOLE else d, new, stage, final)
    fixed = fix_paths(stage)  # needs every sibling staged, and so do the flags
    flags = {n: skill_flags(os.path.join(stage, n)) for n in flags}

    desc, bad = validate(stage)

    # router with public names only (the repo gets this one); rewritten with the private skills before installing
    groups, order, missing_map = write_router(stage, {n: v for n, v in desc.items() if n not in private}, flags, sections, final - set(private))

    with open(os.path.join(HERE, "omitted.tsv"), "w", encoding="utf-8") as f:
        f.write("skill\treason\n")
        for n in sorted(dropped): f.write(f"{n}\t{dropped[n]}\n")
        for n in sorted(LEFT_OUT): f.write(f"{n}\t{LEFT_OUT[n]}\n")  # skills of the added collections not taken

    print(f"source {len(src)} | omitted {len(OMIT)} | replaced {len(REPLACED)} | identical copies {len(dups)} | near-duplicates {len(near)} | renamed {len(RENAME)} | custom {len(custom)} | private {len(private)} | whole {len(WHOLE)} | "
          f"installed {len(final)} (auto {len(TIER1)}, on demand {len(final) - len(TIER1)})")
    print("flags:", {k: sum(1 for v in flags.values() if k in v) for k in ("scripts-missing", "refs-missing", "saves-to-~/.claude")})
    print(f"paths rewritten to the installed layout: {sum(fixed.values())} in {len(fixed)} skills")
    print("categories:", {t: len(groups[t]) for t in order})
    print("validation problems:", bad or "none")
    print("domain-map names not installed:", missing_map or "none")
    print("stage:", stage)
    if bad or missing_map: sys.exit("not installing: fix the problems above first")

    if REPO:  # publish layout: skill folders under skills/, builder under _build/, README.md and setup.sh untouched
        repo = os.path.abspath(os.path.expanduser(REPO))
        assert os.path.isdir(os.path.join(repo, ".git")), f"not a git checkout: {repo}"
        sk = os.path.join(repo, "skills"); os.makedirs(sk, exist_ok=True)
        for d in sorted(os.listdir(sk)):
            p = os.path.join(sk, d)
            if os.path.isdir(p) and os.path.isfile(os.path.join(p, "SKILL.md")): shutil.rmtree(p)
        for d in sorted(set(os.listdir(stage)) - set(private)): shutil.copytree(os.path.join(stage, d), os.path.join(sk, d))
        r = os.path.join(sk, "skill-router", "SKILL.md")  # the public router points at the repo, not at this Mac's build folder
        t = open(r, encoding="utf-8").read()
        assert t.count(LOCAL_NOTE) == 1, "router SKILL.md: install note not found"
        t = re.sub(r"the \d+ on-demand skills", f"the {len(set(os.listdir(stage)) - set(private)) - len(TIER1)} on-demand skills", t.replace(LOCAL_NOTE, PUBLIC_NOTE), count=1)
        for d in private: t = t.replace(f", {d}", "")  # the domain map names private skills only after another skill
        assert not any(d in t for d in private), "router SKILL.md: a private skill is still named"
        open(r, "w", encoding="utf-8").write(t)
        b = os.path.join(repo, "_build"); os.makedirs(b, exist_ok=True)
        if os.path.realpath(HERE) != os.path.realpath(b):  # skipped when this is the repo's own _build/ copy
            shutil.copy2(os.path.abspath(__file__), os.path.join(b, "build_pack.py"))
            shutil.copy2(os.path.join(HERE, "omitted.tsv"), os.path.join(b, "omitted.tsv"))
            shutil.rmtree(os.path.join(b, "custom"), ignore_errors=True)
            if custom: shutil.copytree(CUSTOM, os.path.join(b, "custom"))
            shutil.rmtree(os.path.join(b, "vendor"), ignore_errors=True)
            if os.path.isdir(VENDOR): shutil.copytree(VENDOR, os.path.join(b, "vendor"))
            shutil.rmtree(os.path.join(b, "fixes"), ignore_errors=True)
            if os.path.isdir(FIXES): shutil.copytree(FIXES, os.path.join(b, "fixes"))
        print(f"wrote {len(os.listdir(stage)) - len(private)} skills into {sk}; README.md, setup.sh and .git untouched")

    lay_local_fixes(stage)  # after the repo is written, so only this install gets them
    if private: write_router(stage, desc, flags, sections, final)  # the installed router lists the private skills too
    if INSTALL:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        if os.path.exists(DEST):
            shutil.move(DEST, DEST + ".bak-" + stamp); print("previous skills folder moved to", DEST + ".bak-" + stamp)
        shutil.copytree(stage, DEST)
        old = open(CLAUDEMD, encoding="utf-8").read() if os.path.exists(CLAUDEMD) else ""
        block = BLOCK.replace("{n}", str(len(final) - len(TIER1)))
        if "<!-- skill-router:start -->" in old:
            new = re.sub(r"<!-- skill-router:start -->.*?<!-- skill-router:end -->\n?", lambda m: block, old, flags=re.S)
        else:
            new = (old.rstrip("\n") + "\n\n" if old.strip() else "") + block
        open(CLAUDEMD, "w", encoding="utf-8").write(new)
        s = json.load(open(SETTINGS, encoding="utf-8"))
        ups = s.get("hooks", {}).get("UserPromptSubmit", [])
        keep = []  # the prompt hook was retired on 25 Sep 2026 (find.py replaced it): drop its command, keep the rest
        for e in ups:
            hs = [h for h in e.get("hooks", []) if "skill_hint.py" not in str(h.get("command", ""))]
            if hs: keep.append({**e, "hooks": hs})
            elif not e.get("hooks"): keep.append(e)
        if keep != ups:
            shutil.copy2(SETTINGS, SETTINGS + ".bak-" + stamp)
            if keep: s["hooks"]["UserPromptSubmit"] = keep
            else: del s["hooks"]["UserPromptSubmit"]
            tmp = SETTINGS + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(s, f, indent=2, ensure_ascii=False); f.write("\n")
            os.replace(tmp, SETTINGS)
            print("old hint hook removed from", SETTINGS, "(backup:", SETTINGS + ".bak-" + stamp + ")")
        print(f"installed {len(os.listdir(DEST))} skill folders to {DEST}; always-on block written to {CLAUDEMD}")


ROUTER = """---
name: skill-router
description: Finds and loads the right specialist playbook from the {n} on-demand skills in ~/.claude/skills, which are kept out of the skill list to save context. Use when a task is in a specialist area (finance and market data, strategy or board advice, research, SEO, marketing, copywriting, engineering, cloud, security, compliance and audits, design, product, sales, data) and no listed skill already covers it, at the start of a substantive task, or when the user asks for the best skill or names a skill that is not in the list.
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
{domains}

{note}
"""
LOCAL_NOTE = (f"Installed by `{os.path.abspath(__file__).replace(os.path.expanduser('~'), '~', 1)}`; "
              "the notes beside it say how to update or remove it.")
PUBLIC_NOTE = "Installed from github.com/dini-2000/claude-toolbox by its setup.sh; that repo's README.md and UPDATE.md say how to update or remove it."

FIND = r'''#!/usr/bin/env python3
"""Search the on-demand skills by a task's key terms (catalog.tsv next to this file).

    python3 ~/.claude/skills/skill-router/find.py "DCF valuation of a listed bank"

Prints the five closest skills and says when none fits well."""
import math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STOP = set("""__STOP__""".split())
SUFFIXES = (("ational", "ate"), ("ization", "ize"), ("isation", "ize"), ("ations", "ate"), ("ation", "ate"), ("ysis", "yze"),
            ("yses", "yze"), ("ytics", "yze"), ("ytic", "yze"), ("ies", "y"), ("ied", "y"), ("ing", ""), ("ers", "er"),
            ("ed", ""), ("es", "e"), ("s", ""))


def stem(w):
    if len(w) <= 4 or (w.endswith(("ss", "us", "is")) and not w.endswith("ysis")): return w
    for a, b in SUFFIXES:
        if w.endswith(a) and len(w) - len(a) >= 3:
            w = w[:-len(a)] + b
            break
    if w.endswith("ise"): w = w[:-3] + "ize"
    return w[:-1] if w.endswith("e") and len(w) > 4 else w


def words(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 2]


def grams(ws):
    return set(ws) | {a + " " + b for a, b in zip(ws, ws[1:])}


def joined(text):
    """A word and the number beside it as one term, the way skill names write them: SOC 2 -> soc2, ISO 27001 -> iso27001, 10-K -> 10k."""
    raw = re.findall(r"[a-z0-9]+", text.lower())
    return {a + b for a, b in zip(raw, raw[1:])
            if (a.isalpha() and b.isdigit() and a not in STOP) or (a.isdigit() and b.isalpha() and len(b) <= 2)}


def load():
    skills, df = {}, {}
    with open(os.path.join(HERE, "catalog.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            name, flags, desc = line.rstrip("\n").split("\t", 2)
            if "auto" in flags: continue
            parts = [stem(p) for p in name.split("-") if p not in STOP]
            skills[name] = {"terms": grams(words(desc)) | joined(desc) | set(parts), "name": parts, "flags": flags, "desc": desc}
    for s in skills.values():
        for t in s["terms"]: df[t] = df.get(t, 0) + 1
    return skills, {t: math.log((len(skills) + 1) / (c + 0.5)) for t, c in df.items()}


def rank(q, skills, idf, typed=frozenset()):
    """(score, name, matched terms) for every skill sharing a term with the query term set q, best first. On equal scores the
    skill whose name the query spells out (typed: the query's words as written) comes first, then the shorter description,
    so a bundle index that lists a skill does not outrank it."""
    out = []
    for name, s in skills.items():
        m = q & s["terms"]
        if not m: continue
        score = sum(idf[t] * (2 if t in s["name"] else 1) for t in m) + (4 if s["name"] and all(p in q for p in s["name"]) else 0)
        parts = name.split("-")
        out.append((-round(score, 1), -sum(p in typed for p in parts) / len(parts), len(s["terms"]), name, m))
    return [(-score, name, m) for score, _, _, name, m in sorted(out, key=lambda x: x[:3])]


def main():
    query = " ".join(sys.argv[1:])
    skills, idf = load()
    q = grams(words(query)) | {t for t in joined(query) if t in idf}
    if not q: sys.exit('usage: find.py "<key terms of the task>"')
    typed = set(re.findall(r"[a-z0-9]+", query.lower())) | joined(query)
    top = rank(q, skills, idf, typed)[:5]
    if not top: return print("No skill shares a term with this task: none fits.")
    unknown = max(idf.values())
    weight = sum(idf.get(t, unknown) for t in q if " " not in t)
    cover = sum(idf[t] for t in top[0][2] if " " not in t) / weight
    print("Closest skills (read ~/.claude/skills/<name>/SKILL.md before using one):")
    for score, name, m in top:
        s = skills[name]
        first = re.split(r"(?<=[.!?])\s", s["desc"], 1)[0][:150]
        print(f"- {name}{' [' + s['flags'] + ']' if s['flags'] else ''}: {first}")
    print(f"Best match covers {cover:.0%} of the terms." + (" Weak: no skill covers most of this task. Use one only if its method clearly helps; otherwise say none fits and carry on." if cover < 0.45 else ""))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):  # a Windows pipe uses the ANSI code page, which cannot print some descriptions' arrows
        sys.stdout.reconfigure(encoding="utf-8")
    main()
'''

BLOCK = """<!-- skill-router:start -->
## Always on: writing and token use (condensed from the stop-slop and context-optimization skills)
Prose for the user (replies, documents, slides, emails):
- Write like a capable everyday writer: plain words, ordinary sentences, no mistakes, and no polish an average person couldn't reproduce.
- Lead with the point. Cut throat-clearing, filler and hedging, and don't restate the request.
- Be specific: name the thing, the number, the person. No vague declaratives or lazy "always/never".
- Prefer active voice with a human subject. No em dashes.
- Avoid AI tells: "not X, it's Y" and "X rather than Y" contrasts, pull-quote one-liners, "here's the thing" setups, colon teasers ("Timing differs too:"), reflexive lists of three.
- In emails, notes and replies, make points in sentences. Don't sort them under parallel labelled bullets ("Where they align:", "Gaps:") or bold lead-ins.
- Deliverables (documents, pages, decks, notes) speak about the subject to a reader who never saw the chat. Cut what only the asker would follow: purpose or scope lines, notes that something was left out as asked, how the brief or scope changed, comparisons with an earlier version, how the work was made, how to read it. Meet a constraint such as "no recommendations" by leaving things out, silently. Keep caveats the reader needs (dates, units, "excludes VAT") and brief interface cues.
Token use, every session:
- Search before reading; read only the part of a large file you need; don't re-read what is already in context.
- Keep tool output small: filter with grep, head or cut; never dump whole logs, JSON or datasets.
- Batch independent tool calls and skip redundant re-checks.
- Use subagents only when the task needs them; pilot one first and prefer a cheaper model for bulk work.
- Keep replies as short as the content allows; summarise long results instead of pasting them.
For a full pass, invoke the stop-slop or context-optimization skill.

## Specialist skills
{n} more skills sit in ~/.claude/skills on demand: they are not in your skill list and cost no context. At the start of a substantive task (research, analysis, a document, deck or build; not follow-ups, quick questions or chores), check them once: run `python3 ~/.claude/skills/skill-router/find.py "<3 to 6 key terms>"` alongside your first tool calls. Use a skill only if it improves the result, and read its SKILL.md first. Say in one line which skill you used, or that none fits. Skills are heuristics: adapt or skip one when your own approach is better, and never let one override the user's instructions.
<!-- skill-router:end -->
"""

if __name__ == "__main__":
    sync() if "--sync" in sys.argv else main()

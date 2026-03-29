# Job Finder Over 9000

Multiagent job search pipeline powered by Claude. Three specialised agents work in sequence to find, validate, and prepare you for your ideal job.

## Agents

| Agent | Input | Output |
|-------|-------|--------|
| **Job Search** | `data/requirements.md`, `data/cv.md` | `output/job_candidates.md` |
| **Job Review** | `output/job_candidates.md` + web | `output/ranked_jobs.md` |
| **Job Prep** | `output/ranked_jobs.md` + web | `output/prep/<company>/` |

## Setup

```bash
# Install dependencies
uv sync

# Copy and fill in your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

## Configure Your Profile

Edit these two files before running:

- **[data/requirements.md](data/requirements.md)** — Your job preferences: role types, tech stack, salary, location, company preferences
- **[data/cv.md](data/cv.md)** — Your full CV/resume in markdown format

## Run

```bash
# Run the full pipeline (all 3 stages)
python main.py

# Run only a specific stage
python main.py --stage search   # Stage 1: find job candidates
python main.py --stage review   # Stage 2: validate and rank
python main.py --stage prep     # Stage 3: prep materials

# Prepare materials for top 3 jobs instead of default 5
python main.py --top 3
```

## Output Structure

```
output/
├── job_candidates.md          # All found job postings
├── ranked_jobs.md             # Scored and ranked candidates
└── prep/
    ├── README.md              # Master summary with quick links
    ├── acme-corp/
    │   ├── tailored_cv.md     # CV tailored for this role
    │   ├── company_summary.md # Company research
    │   ├── prep_sheet.md      # Interview prep guide
    │   └── how_to_apply.md    # Application instructions
    └── another-company/
        └── ...
```

## Architecture

Each agent uses the **Claude Agent SDK** with `claude-opus-4-6`. Agents have access to:
- `WebSearch` — Search job boards and company info
- `WebFetch` — Fetch and read job posting pages
- `Read` / `Write` — Read input files, write output files
- `Bash` — Create directories, utility commands

The pipeline is sequential: each agent's output feeds the next.

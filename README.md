# JobHunt

JobHunt is a personal job search assistant that finds software engineering openings, filters them against your preferences, scores promising roles against your profile, and prepares an email digest with application drafts. It helps you organize your search; you review each draft and submit every application yourself.

## Features

- Fetches public job listings from Greenhouse, Lever, and Ashby boards.
- Filters listings by job title, location, and posting age before using an AI model.
- Scores matching roles against your profile and drafts application materials for the strongest matches.
- Builds an HTML digest and can send it by email.
- Tracks previously seen jobs and application status to help avoid duplicates.
- Includes a mock mode so you can try the workflow without making network requests or configuring an AI provider.

JobHunt does not submit applications automatically and does not scrape LinkedIn or Naukri.

## Requirements

- Python 3.10 or newer
- `pip` and a virtual environment
- An API key for the AI provider you choose when using AI scoring and drafting
- SMTP credentials only if you want JobHunt to email the digest

## Getting started

Open a terminal in the project folder:

```bash
cd JobHunt
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Copy the example environment file and add the settings you plan to use:

```bash
cp .env.example .env
```

Keep your `.env` file and personal profile out of version control. The example file is a template; replace its placeholder values only in your local `.env` file.

## Configure your search

Edit `companies.yaml` to choose the public job boards JobHunt should check. Each entry identifies the board provider, its board slug, and the company name. The available filters, score threshold, and digest settings are in `config.yaml`.

Start with a small list of companies and review the filters before running a full search. The next section will cover profile setup and running JobHunt.

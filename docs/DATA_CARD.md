# GigBid Dataset Card

## 1. Summary & Provenance
The GigBid system leverages a hybrid data architecture combining empirical freelance marketplace distributions derived from public Kaggle datasets with carefully controlled synthetic persona and evaluation corpora.

### Real-World Reference Datasets & Attribution
1. **Upwork Job Postings Dataset 2024 (50k records)** — `asaniczka/upwork-job-postings-dataset-2024-50k-records`
   - *Attribution:* asaniczka (Kaggle), 2024. Open Database License (ODbL).
   - *Usage:* Informed real-world budget distributions ($/hr and fixed price), required skill co-occurrences, screening question patterns, and client spend tiers.
2. **All Jobs on Upwork (200k+ records)** — `asaniczka/all-jobs-on-upwork-200k-plus`
   - *Attribution:* asaniczka (Kaggle). Database Contents License (DbCL).
   - *Usage:* Category hierarchies, job title syntax, and duration distributions.
3. **Upwork Freelance Jobs (60k)** — `ahmedmyalo/upwork-freelance-jobs-60k`
   - *Attribution:* Ahmed Myalo. CC BY 4.0.
   - *Usage:* Screening questions, client feedback patterns, and connects requirements.
4. **Freelance Contracts Dataset (1.3M entries)** — `asaniczka/freelance-contracts-dataset-1-3-million-entries`
   - *Attribution:* asaniczka (Kaggle).
   - *Usage:* Historical win and reply rates, contract milestones, and pricing elasticity.
5. **Freelancer Success, Earnings, and Churn Prediction** — `sarveshchhetri/freelancer-success-earnings-and-churn-prediction`
   - *Attribution:* Sarvesh Chhetri.
   - *Usage:* Calibrated freelancer hourly rate floors and profile rating distributions.
6. **Trial-1 Dataset** — `adityammantri/trial-1`
   - *Attribution:* Aditya Mantri.
   - *Usage:* Realistic client review sentiment and communication threads.

---

## 2. Synthetic Corpora Generation & Structure
Where proprietary or privacy-sensitive data could not be collected directly, realistic synthetic data was synthesized using deterministic generators (`data/generate_dataset.py`) seeded for full reproducibility.

### A. Three Freelancer Personas (`data/personas/`)
1. **Alex Chen (`alex_chen_aiml`)**: Senior AI/ML Engineer ($85/hr, $500 min project).
   - 1 Markdown CV (`cv.md`)
   - 20 Detailed Case Studies with measurable results (e.g. inference latency, Recall@5)
   - 5 GitHub Repositories (`README.md` and typed code)
   - 15 Client Reviews with numerical ratings (4.8 - 5.0)
   - 150 Past Proposals labelled with outcomes (35 won, 45 replied, 70 ignored)
2. **Sarah Jenkins (`sarah_jenkins_fullstack`)**: Principal Full-Stack Web Architect ($75/hr, $450 min project).
   - 1 Markdown CV, 20 Case Studies (React, Next.js, FastAPI, PostgreSQL), 5 Repos, 15 Reviews, 150 Proposals.
3. **Marcus Vance (`marcus_vance_analyst`)**: Lead Data Analyst & BI Specialist ($65/hr, $350 min project).
   - 1 Markdown CV, 20 Case Studies (Snowflake, dbt, PowerBI, Tableau), 5 Repos, 15 Reviews, 150 Proposals.

### B. Marketplace Seed Data (`gigsim/data/`)
- **1,500 Historical Jobs (`jobs_stream.json`)**: Spanning AI/ML, Full-Stack Web, and Data Analytics. Includes realistic scam signals (unpaid trials, off-platform contact), prompt-injection payloads, and duplicates.
- **120 Clients (`clients.json`)**: Enterprise, Mid-Market, Startup, and Unverified tiers with spend histories and hidden preference vectors.

### C. Development Evaluation Set (`evals/datasets/dev_eval_jobs.json`)
- **600 Annotated Dev Jobs** (200 per persona):
  - Gold decisions: `BID` (110 jobs) vs `SKIP` (90 jobs)
  - Ground-truth scam flags and injection indicators
  - Gold evidence IDs mapping directly to verified persona case studies
  - Fair price bands `[min, max]`

---

## 3. Data Preprocessing & Sanitization
1. **PII Masking**: All personal phone numbers, emails, and physical addresses in the public datasets were scrubbed or mapped to RFC 2606 reserved domains (`@example.com`).
2. **Adversarial Labeling**: Planted injection jobs were explicitly tagged with `<system_instruction>` delimiters to test boundary defenses.
3. **Deduplication**: Exact hash-based deduplication removed duplicate job posts across runs.

## 4. Licensing & Ethical Considerations
- All Kaggle datasets are utilized under their respective non-commercial research and educational licenses (ODbL, CC BY 4.0, DbCL).
- Synthetic data generated herein is dedicated to the public domain under CC0 1.0 Universal.
- In compliance with Upwork Terms of Service, live Upwork data is accessed exclusively via official OAuth 2.1 MCP endpoints, with zero website scraping or unapproved automation.

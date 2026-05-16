"""
Run this script to populate the database with dummy actors for demo purposes.
Usage: python seed.py [base_url]
Default base_url: http://localhost:8000
"""

import sys
import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

ACTORS = [
    # ── Mentors ────────────────────────────────────────────────────────────────
    {
        "name": "Sarah Mitchell",
        "actor_type": "mentor",
        "sector": "SaaS / B2B Software",
        "stage": "Partner",
        "tags": ["SaaS", "B2B", "go-to-market", "sales", "scaling"],
        "needs": ["Interesting early-stage startups to mentor", "Equity or advisory arrangements"],
        "expertise": ["B2B SaaS sales strategy", "Pricing models", "Expansion into EU markets", "Building SDR teams"],
        "location": "London, UK",
        "bio": "Former VP Sales at Salesforce EMEA, scaled revenue from $2M to $40M ARR in 4 years. Now advises SaaS startups on go-to-market strategy and enterprise sales. Particular focus on EU market entry.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "David Okonkwo",
        "actor_type": "mentor",
        "sector": "FinTech / Payments",
        "stage": "Senior",
        "tags": ["fintech", "payments", "regulation", "banking", "APIs"],
        "needs": ["Startups disrupting traditional finance", "Speaking opportunities"],
        "expertise": ["Payments infrastructure", "PSD2 / open banking compliance", "Fundraising from fintech VCs", "Product-market fit in regulated markets"],
        "location": "Amsterdam, Netherlands",
        "bio": "Co-founder of PayRoute (acquired by Adyen 2021). 15 years in payments across Mastercard and two successful startups. Deep expertise in navigating financial regulation while shipping fast.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Amara Diallo",
        "actor_type": "mentor",
        "sector": "HealthTech / Digital Health",
        "stage": "Principal",
        "tags": ["healthtech", "clinical", "GDPR", "patient data", "NHS"],
        "needs": ["HealthTech founders tackling real clinical problems", "Co-investment opportunities"],
        "expertise": ["Clinical validation", "NHS procurement pathway", "Health data regulation (GDPR, HIPAA)", "Investor relations for HealthTech"],
        "location": "Manchester, UK",
        "bio": "Medical doctor turned entrepreneur. Founded CareLoop, a remote patient monitoring platform used by 12 NHS trusts. Passionate about helping founders navigate the complex healthcare system without losing their product vision.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Jonas Weber",
        "actor_type": "mentor",
        "sector": "Deep Tech / AI",
        "stage": "Partner",
        "tags": ["AI", "machine learning", "deep tech", "MLOps", "enterprise AI"],
        "needs": ["AI startups with real technical differentiation", "Research commercialisation projects"],
        "expertise": ["AI product strategy", "Building ML teams", "Enterprise AI adoption", "Moving from research to production"],
        "location": "Berlin, Germany",
        "bio": "Ex-Google Brain researcher, built and led ML platform teams at two unicorns. Now an active angel in AI startups. Specialises in helping technical founders translate research into scalable commercial products.",
        "source_file": "seed",
        "programme_history": [],
    },

    # ── Companies / Startups ───────────────────────────────────────────────────
    {
        "name": "Novastack",
        "actor_type": "company",
        "sector": "SaaS / Developer Tools",
        "stage": "seed",
        "tags": ["developer tools", "SaaS", "CI/CD", "devops", "B2B"],
        "needs": ["Go-to-market mentor", "Cloud infrastructure credits", "Enterprise sales guidance", "Series A fundraising advice"],
        "expertise": ["Automated code review", "CI/CD pipeline optimisation", "Developer productivity analytics"],
        "location": "Warsaw, Poland",
        "bio": "Novastack builds AI-powered code review tools that cut PR review time by 60%. Currently at $80K MRR with 40 paying teams. Looking to expand into enterprise contracts and Western European markets.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "MediSync",
        "actor_type": "company",
        "sector": "HealthTech",
        "stage": "pre-seed",
        "tags": ["healthtech", "patient data", "clinical", "interoperability", "FHIR"],
        "needs": ["Clinical validation support", "NHS pilot access", "Regulatory guidance", "Technical co-founder"],
        "expertise": ["Patient record interoperability", "FHIR API integration", "Hospital workflow automation"],
        "location": "Birmingham, UK",
        "bio": "MediSync eliminates the manual transfer of patient records between hospitals using a FHIR-based integration layer. Founded by two ex-NHS IT consultants who lived the problem first hand. Pre-revenue, seeking first NHS pilot.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "GreenLedger",
        "actor_type": "company",
        "sector": "CleanTech / FinTech",
        "stage": "seed",
        "tags": ["sustainability", "carbon tracking", "ESG", "fintech", "B2B SaaS"],
        "needs": ["Fintech mentor", "Partnerships with accounting software", "EU regulatory expertise", "Series A prep"],
        "expertise": ["Automated carbon footprint tracking", "ESG reporting for SMEs", "Scope 1-2-3 emissions calculation"],
        "location": "Stockholm, Sweden",
        "bio": "GreenLedger automates ESG reporting for SMEs, pulling data directly from accounting and ERP systems. $120K ARR, growing 15% MoM. EU taxonomy regulation is driving inbound demand faster than they can handle.",
        "source_file": "seed",
        "programme_history": [],
    },

    # ── Service Providers ──────────────────────────────────────────────────────
    {
        "name": "CloudNest",
        "actor_type": "service_provider",
        "sector": "Cloud Infrastructure",
        "stage": "growth",
        "tags": ["cloud", "AWS", "infrastructure", "DevOps", "startup credits"],
        "needs": ["Early-stage startups to onboard", "Technical partnerships"],
        "expertise": ["Cloud architecture", "Kubernetes", "Cost optimisation", "Startup credit programmes up to $100K", "24/7 technical support"],
        "location": "Dublin, Ireland",
        "bio": "CloudNest is an AWS Advanced Partner specialising in helping startups architect scalable, cost-efficient infrastructure. Offers a startup accelerator programme with up to $100K in cloud credits and dedicated solutions architects.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "LegalBridge",
        "actor_type": "service_provider",
        "sector": "Legal Services",
        "stage": "growth",
        "tags": ["legal", "startup law", "GDPR", "IP", "term sheets", "equity"],
        "needs": ["Startups needing legal support", "VC introductions"],
        "expertise": ["Startup incorporation", "GDPR compliance", "IP protection", "Term sheet negotiation", "Employment contracts for fast-growing teams"],
        "location": "Amsterdam, Netherlands",
        "bio": "LegalBridge provides fixed-fee legal services designed for startups. From incorporation to Series A, their team of startup-specialist lawyers has supported over 200 companies across the EU. No billable hour surprises.",
        "source_file": "seed",
        "programme_history": [],
    },

    # ── Partners ───────────────────────────────────────────────────────────────
    {
        "name": "EIT Digital",
        "actor_type": "partner",
        "sector": "Innovation / Education",
        "stage": "growth",
        "tags": ["EU funding", "deep tech", "accelerator", "pan-European", "grants"],
        "needs": ["High-potential deep tech startups", "University spin-outs"],
        "expertise": ["EU grant access (Horizon Europe)", "Pan-European market expansion", "Corporate partnership facilitation", "Talent network across 20+ countries"],
        "location": "Brussels, Belgium",
        "bio": "EIT Digital is a pan-European innovation organisation that accelerates deep tech startups through EU funding, corporate partnerships, and a network spanning 20 countries. Focus areas: AI, cybersecurity, digital infrastructure.",
        "source_file": "seed",
        "programme_history": [],
    },
]


def seed():
    print(f"Seeding {len(ACTORS)} actors to {BASE_URL}...\n")
    client = httpx.Client(base_url=BASE_URL, timeout=30)
    success, failed = 0, 0

    for actor in ACTORS:
        try:
            res = client.post("/api/actors", json=actor)
            res.raise_for_status()
            data = res.json()
            print(f"  ✓  {data['actor_type']:16s}  {data['name']}  ({data['id'][:8]}…)")
            success += 1
        except Exception as e:
            print(f"  ✗  {actor['name']}: {e}")
            failed += 1

    print(f"\nDone — {success} created, {failed} failed.")


if __name__ == "__main__":
    seed()

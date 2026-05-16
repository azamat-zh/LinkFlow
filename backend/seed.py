"""
Seed all demo data: actors + relationships (pending, active, stale).
Usage: python seed.py [base_url]
"""
import sys
from datetime import datetime, timedelta, timezone
import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

ACTORS = [
    {
        "name": "Sarah Mitchell",
        "actor_type": "mentor",
        "sector": "SaaS / B2B Software",
        "stage": "Partner",
        "tags": ["SaaS", "B2B", "go-to-market", "sales", "scaling"],
        "needs": ["Interesting early-stage startups to mentor", "Equity or advisory arrangements"],
        "expertise": ["B2B SaaS sales strategy", "Pricing models", "Expansion into EU markets", "Building SDR teams"],
        "location": "London, UK",
        "bio": "Former VP Sales at Salesforce EMEA, scaled revenue from $2M to $40M ARR in 4 years. Now advises SaaS startups on go-to-market strategy and enterprise sales.",
        "source_file": "seed",
        "programme_history": [],
        "email": "sarah.mitchell@demo.linkflow.io",
    },
    {
        "name": "David Okonkwo",
        "actor_type": "mentor",
        "sector": "FinTech / Payments",
        "stage": "Senior",
        "tags": ["fintech", "payments", "regulation", "banking", "APIs"],
        "needs": ["Startups disrupting traditional finance", "Speaking opportunities"],
        "expertise": ["Payments infrastructure", "PSD2 / open banking compliance", "Fundraising from fintech VCs"],
        "location": "Amsterdam, Netherlands",
        "bio": "Co-founder of PayRoute (acquired by Adyen 2021). 15 years in payments across Mastercard and two successful startups.",
        "source_file": "seed",
        "programme_history": [],
        "email": "david.okonkwo@demo.linkflow.io",
    },
    {
        "name": "Amara Diallo",
        "actor_type": "mentor",
        "sector": "HealthTech / Digital Health",
        "stage": "Principal",
        "tags": ["healthtech", "clinical", "GDPR", "patient data", "NHS"],
        "needs": ["HealthTech founders tackling real clinical problems"],
        "expertise": ["Clinical validation", "NHS procurement pathway", "Health data regulation (GDPR, HIPAA)"],
        "location": "Manchester, UK",
        "bio": "Medical doctor turned entrepreneur. Founded CareLoop, a remote patient monitoring platform used by 12 NHS trusts.",
        "source_file": "seed",
        "programme_history": [],
        "email": "amara.diallo@demo.linkflow.io",
    },
    {
        "name": "Jonas Weber",
        "actor_type": "mentor",
        "sector": "Deep Tech / AI",
        "stage": "Partner",
        "tags": ["AI", "machine learning", "deep tech", "MLOps", "enterprise AI"],
        "needs": ["AI startups with real technical differentiation"],
        "expertise": ["AI product strategy", "Building ML teams", "Enterprise AI adoption"],
        "location": "Berlin, Germany",
        "bio": "Ex-Google Brain researcher, built and led ML platform teams at two unicorns. Now an active angel in AI startups.",
        "source_file": "seed",
        "programme_history": [],
        "email": "jonas.weber@demo.linkflow.io",
    },
    {
        "name": "Novastack",
        "actor_type": "company",
        "sector": "SaaS / Developer Tools",
        "stage": "seed",
        "tags": ["developer tools", "SaaS", "CI/CD", "devops", "B2B"],
        "needs": ["Go-to-market mentor", "Cloud infrastructure credits", "Enterprise sales guidance", "Series A fundraising advice"],
        "expertise": ["Automated code review", "CI/CD pipeline optimisation"],
        "location": "Warsaw, Poland",
        "bio": "Novastack builds AI-powered code review tools that cut PR review time by 60%. Currently at $80K MRR with 40 paying teams.",
        "source_file": "seed",
        "programme_history": [],
        "email": "hello@novastack.demo.io",
    },
    {
        "name": "MediSync",
        "actor_type": "company",
        "sector": "HealthTech",
        "stage": "pre-seed",
        "tags": ["healthtech", "patient data", "clinical", "interoperability", "FHIR"],
        "needs": ["Clinical validation support", "NHS pilot access", "Regulatory guidance"],
        "expertise": ["Patient record interoperability", "FHIR API integration"],
        "location": "Birmingham, UK",
        "bio": "MediSync eliminates manual transfer of patient records between hospitals using a FHIR-based integration layer.",
        "source_file": "seed",
        "programme_history": [],
        "email": "team@medisync.demo.io",
    },
    {
        "name": "GreenLedger",
        "actor_type": "company",
        "sector": "CleanTech / FinTech",
        "stage": "seed",
        "tags": ["sustainability", "carbon tracking", "ESG", "fintech", "B2B SaaS"],
        "needs": ["Fintech mentor", "Partnerships with accounting software", "EU regulatory expertise"],
        "expertise": ["Automated carbon footprint tracking", "ESG reporting for SMEs"],
        "location": "Stockholm, Sweden",
        "bio": "GreenLedger automates ESG reporting for SMEs. $120K ARR, growing 15% MoM.",
        "source_file": "seed",
        "programme_history": [],
        "email": "founders@greenledger.demo.io",
    },
    {
        "name": "CloudNest",
        "actor_type": "service_provider",
        "sector": "Cloud Infrastructure",
        "stage": "growth",
        "tags": ["cloud", "AWS", "infrastructure", "DevOps", "startup credits"],
        "needs": ["Early-stage startups to onboard"],
        "expertise": ["Cloud architecture", "Kubernetes", "Startup credit programmes up to $100K"],
        "location": "Dublin, Ireland",
        "bio": "CloudNest is an AWS Advanced Partner offering up to $100K in cloud credits and dedicated solutions architects.",
        "source_file": "seed",
        "programme_history": [],
        "email": "partners@cloudnest.demo.io",
    },
    {
        "name": "LegalBridge",
        "actor_type": "service_provider",
        "sector": "Legal Services",
        "stage": "growth",
        "tags": ["legal", "startup law", "GDPR", "IP", "term sheets"],
        "needs": ["Startups needing legal support"],
        "expertise": ["Startup incorporation", "GDPR compliance", "IP protection", "Term sheet negotiation"],
        "location": "Amsterdam, Netherlands",
        "bio": "Fixed-fee legal services for startups. Supported 200+ companies across the EU.",
        "source_file": "seed",
        "programme_history": [],
        "email": "hello@legalbridge.demo.io",
    },
    {
        "name": "EIT Digital",
        "actor_type": "partner",
        "sector": "Innovation / Education",
        "stage": "growth",
        "tags": ["EU funding", "deep tech", "accelerator", "pan-European", "grants"],
        "needs": ["High-potential deep tech startups"],
        "expertise": ["EU grant access (Horizon Europe)", "Pan-European market expansion"],
        "location": "Brussels, Belgium",
        "bio": "Pan-European innovation organisation accelerating deep tech startups through EU funding and a 20-country network.",
        "source_file": "seed",
        "programme_history": [],
        "email": "programmes@eitdigital.demo.io",
    },
]


def seed_actors(client: httpx.Client) -> dict[str, str]:
    """Seed actors, return name->id map."""
    print(f"\nSeeding {len(ACTORS)} actors...")
    name_to_id = {}
    for actor in ACTORS:
        try:
            res = client.post("/api/actors", json=actor)
            res.raise_for_status()
            data = res.json()
            name_to_id[data["name"]] = data["id"]
            print(f"  ✓  {data['actor_type']:16s}  {data['name']}")
        except Exception as e:
            print(f"  ✗  {actor['name']}: {e}")
    return name_to_id


def seed_relationships(client: httpx.Client, name_to_id: dict[str, str]):
    """Seed three demo relationships: pending, active, stale."""
    now = datetime.now(timezone.utc)
    stale_date = (now - timedelta(days=16)).isoformat()
    active_date = (now - timedelta(days=3)).isoformat()
    now_iso = now.isoformat()

    relationships = [
        # 1. PENDING — just approved, awaiting confirmation
        {
            "id": "demo-rel-pending-001",
            "relationship_type": "mentor_company",
            "actor_a_id": name_to_id.get("David Okonkwo", ""),
            "actor_b_id": name_to_id.get("GreenLedger", ""),
            "state": "pending",
            "match_score": 91.0,
            "match_reasoning": "David's fintech and payments expertise directly addresses GreenLedger's need for financial regulatory guidance in the EU.",
            "session_log": [
                {"date": now_iso, "notes": "Match approved by coordinator. Score: 91. Strong fintech alignment.", "logged_by": "coordinator"},
                {"date": now_iso, "notes": "Intro email simulated to David Okonkwo (david.okonkwo@demo.linkflow.io) and GreenLedger (founders@greenledger.demo.io).", "logged_by": "system"},
            ],
            "created_at": now_iso,
            "last_updated": now_iso,
            "programme_id": "default",
            "mentor_confirmed": False,
            "startup_confirmed": False,
        },
        # 2. ACTIVE — both confirmed, sessions happening
        {
            "id": "demo-rel-active-001",
            "relationship_type": "mentor_company",
            "actor_a_id": name_to_id.get("Amara Diallo", ""),
            "actor_b_id": name_to_id.get("MediSync", ""),
            "state": "active",
            "match_score": 97.0,
            "match_reasoning": "Amara's NHS procurement and clinical validation expertise is exactly what MediSync needs for their first NHS pilot.",
            "session_log": [
                {"date": (now - timedelta(days=14)).isoformat(), "notes": "Match approved by coordinator. Score: 97.", "logged_by": "coordinator"},
                {"date": (now - timedelta(days=14)).isoformat(), "notes": "Intro email simulated to both parties.", "logged_by": "system"},
                {"date": (now - timedelta(days=13)).isoformat(), "notes": "Mentor confirmed participation.", "logged_by": "coordinator"},
                {"date": (now - timedelta(days=13)).isoformat(), "notes": "Startup confirmed participation.", "logged_by": "coordinator"},
                {"date": (now - timedelta(days=13)).isoformat(), "notes": "Both parties confirmed — relationship marked active.", "logged_by": "system"},
                {"date": active_date, "notes": "First session: reviewed NHS procurement checklist, identified 3 key blockers. Next session in 2 weeks.", "logged_by": "coordinator"},
            ],
            "created_at": (now - timedelta(days=14)).isoformat(),
            "last_updated": active_date,
            "programme_id": "default",
            "mentor_confirmed": True,
            "startup_confirmed": True,
        },
        # 3. STALE — active but no session logged for 16 days
        {
            "id": "demo-rel-stale-001",
            "relationship_type": "mentor_company",
            "actor_a_id": name_to_id.get("Sarah Mitchell", ""),
            "actor_b_id": name_to_id.get("Novastack", ""),
            "state": "active",
            "match_score": 88.0,
            "match_reasoning": "Sarah's B2B SaaS go-to-market experience is a strong match for Novastack's enterprise expansion needs.",
            "session_log": [
                {"date": (now - timedelta(days=20)).isoformat(), "notes": "Match approved by coordinator. Score: 88.", "logged_by": "coordinator"},
                {"date": (now - timedelta(days=19)).isoformat(), "notes": "Both parties confirmed — relationship marked active.", "logged_by": "system"},
                {"date": stale_date, "notes": "Intro call completed. Sarah shared EU expansion playbook. No follow-up scheduled yet.", "logged_by": "coordinator"},
            ],
            "created_at": (now - timedelta(days=20)).isoformat(),
            "last_updated": stale_date,
            "programme_id": "default",
            "mentor_confirmed": True,
            "startup_confirmed": True,
        },
    ]

    print(f"\nSeeding {len(relationships)} demo relationships...")
    for rel in relationships:
        if not rel["actor_a_id"] or not rel["actor_b_id"]:
            print(f"  ✗  Skipping {rel['id']} — actor IDs not found (actors may not have seeded)")
            continue
        try:
            res = client.post("/api/relationships/seed-demo", json=rel)
            res.raise_for_status()
            data = res.json()
            print(f"  ✓  [{data['state']:9s}]  {rel['id']}")
        except Exception as e:
            print(f"  ✗  {rel['id']}: {e}")


def seed():
    print(f"Seeding demo data to {BASE_URL}...")
    client = httpx.Client(base_url=BASE_URL, timeout=30)
    name_to_id = seed_actors(client)
    seed_relationships(client, name_to_id)
    print("\nDone.")


if __name__ == "__main__":
    seed()

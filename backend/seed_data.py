from datetime import datetime, timezone, timedelta

from services.firebase_client import get_db


def seed_actors(db):
    now = datetime.now(timezone.utc)

    actors = {
        "company_greentech": {
            "id": "company_greentech",
            "name": "GreenTech Solar",
            "actor_type": "company",
            "sector": "Renewable Energy",
            "stage": "Early-stage",
            "tags": ["climate-tech", "solar", "sustainability"],
            "needs": ["fundraising", "market expansion", "pitch preparation"],
            "expertise": [],
            "location": "Malaysia",
            "bio": "Early-stage renewable energy startup building solar solutions for Southeast Asia.",
            "source_file": "seed_data.py",
            "created_at": now,
            "programme_history": ["Climate Accelerator 2026"],
        },
        "mentor_amina": {
            "id": "mentor_amina",
            "name": "Amina Rahman",
            "actor_type": "mentor",
            "sector": "Climate Tech",
            "stage": "Growth advisory",
            "tags": ["fundraising", "investor readiness", "climate-tech"],
            "needs": [],
            "expertise": ["fundraising", "pitch preparation", "investor strategy"],
            "location": "Malaysia",
            "bio": "Mentor specialized in fundraising and investor readiness for climate-tech startups.",
            "source_file": "seed_data.py",
            "created_at": now,
            "programme_history": [],
        },
        "partner_green_capital": {
            "id": "partner_green_capital",
            "name": "Green Capital Network",
            "actor_type": "partner",
            "sector": "Investment",
            "stage": "Partner organization",
            "tags": ["investment", "climate finance", "funding"],
            "needs": [],
            "expertise": ["climate finance", "investor network", "funding access"],
            "location": "Southeast Asia",
            "bio": "Partner network connecting climate startups with investors and funding opportunities.",
            "source_file": "seed_data.py",
            "created_at": now,
            "programme_history": [],
        },
        "service_legalhub": {
            "id": "service_legalhub",
            "name": "LegalHub Startup Support",
            "actor_type": "service_provider",
            "sector": "Legal and Compliance",
            "stage": "Service provider",
            "tags": ["legal", "compliance", "contracts"],
            "needs": [],
            "expertise": ["startup legal support", "compliance", "contracts"],
            "location": "Malaysia",
            "bio": "Service provider offering legal and compliance support for startups.",
            "source_file": "seed_data.py",
            "created_at": now,
            "programme_history": [],
        },
    }

    for actor_id, actor_data in actors.items():
        db.collection("actors").document(actor_id).set(actor_data)

    print(f"Seeded {len(actors)} actors.")


def seed_relationships(db):
    now = datetime.now(timezone.utc)

    relationships = {
        "rel_greentech_amina": {
            "id": "rel_greentech_amina",
            "relationship_type": "mentor_company",
            "actor_a_id": "company_greentech",
            "actor_b_id": "mentor_amina",
            "state": "active",
            "match_score": 92.0,
            "match_reasoning": (
                "The mentor has strong fundraising and investor-readiness expertise, "
                "which matches GreenTech Solar's current needs."
            ),
            "session_log": [
                {
                    "date": now - timedelta(days=3),
                    "notes": "Introductory mentoring session completed.",
                    "logged_by": "system",
                }
            ],
            "created_at": now - timedelta(days=5),
            "last_updated": now - timedelta(days=3),
            "programme_id": "climate_accelerator_2026",
        },
        "rel_greentech_green_capital": {
            "id": "rel_greentech_green_capital",
            "relationship_type": "partner_initiative",
            "actor_a_id": "company_greentech",
            "actor_b_id": "partner_green_capital",
            "state": "pending",
            "match_score": 84.0,
            "match_reasoning": (
                "The partner network is relevant because the company needs climate-focused "
                "funding and investor access."
            ),
            "session_log": [],
            "created_at": now,
            "last_updated": now,
            "programme_id": "climate_accelerator_2026",
        },
    }

    for rel_id, rel_data in relationships.items():
        db.collection("relationships").document(rel_id).set(rel_data)

    print(f"Seeded {len(relationships)} relationships.")


def main():
    db = get_db()
    seed_actors(db)
    seed_relationships(db)
    print("Firestore seed completed successfully.")


if __name__ == "__main__":
    main()
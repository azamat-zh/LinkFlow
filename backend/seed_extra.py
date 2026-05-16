"""
Additional dummy actors for demo purposes.
Usage: python seed_extra.py [base_url]
"""

import sys
import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

ACTORS = [
    # ── Mentors ────────────────────────────────────────────────────────────────
    {
        "name": "Elena Vasquez",
        "actor_type": "mentor",
        "sector": "E-commerce / Marketplaces",
        "stage": "Partner",
        "tags": ["e-commerce", "marketplace", "growth", "D2C", "retention"],
        "needs": ["Marketplace startups with traction", "Advisory board seats"],
        "expertise": ["Marketplace liquidity strategies", "D2C brand building", "Customer retention", "Paid acquisition at scale", "Internationalisation"],
        "location": "Barcelona, Spain",
        "bio": "Built and exited two e-commerce companies — one marketplace (€30M exit) and one D2C brand (€12M exit). Now mentors founders on avoiding the growth traps she fell into. Fluent in Spanish, English, and French.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Marcus Chen",
        "actor_type": "mentor",
        "sector": "Cybersecurity",
        "stage": "Partner",
        "tags": ["cybersecurity", "enterprise", "CISO", "zero-trust", "compliance"],
        "needs": ["Cybersecurity startups with enterprise focus", "Technical advisory roles"],
        "expertise": ["Enterprise security architecture", "Zero-trust implementation", "SOC 2 / ISO 27001 compliance", "Selling to CISOs", "Security product-market fit"],
        "location": "Zurich, Switzerland",
        "bio": "Former CISO at two Fortune 500 companies, now a cybersecurity angel investor and mentor. Has evaluated hundreds of security products from the buyer side. Helps startups position correctly and avoid common enterprise sales mistakes.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Fatima Al-Rashid",
        "actor_type": "mentor",
        "sector": "Growth / Marketing",
        "stage": "Principal",
        "tags": ["growth", "PLG", "product-led growth", "SEO", "content", "virality"],
        "needs": ["B2B SaaS startups under $1M ARR", "Fractional CMO opportunities"],
        "expertise": ["Product-led growth strategy", "Content marketing at scale", "SEO for SaaS", "Community building", "Viral loop design"],
        "location": "Dubai, UAE",
        "bio": "Led growth at three SaaS companies from zero to Series B. Grew Taskly from 0 to 200K users in 18 months purely through PLG. Specialist in building organic growth engines that don't rely on paid ads.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Thomas Bergmann",
        "actor_type": "mentor",
        "sector": "Hardware / IoT",
        "stage": "Senior",
        "tags": ["hardware", "IoT", "manufacturing", "supply chain", "embedded systems"],
        "needs": ["Hardware startups at prototype stage", "Manufacturing partnerships"],
        "expertise": ["Hardware prototyping to production", "Asia manufacturing sourcing", "Supply chain resilience", "FCC/CE certification", "IoT platform architecture"],
        "location": "Munich, Germany",
        "bio": "Built IoT products at Siemens for 10 years then co-founded two hardware startups. Knows every pitfall between a working prototype and a shipped product. Has production relationships in Shenzhen and Vietnam.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Priya Sharma",
        "actor_type": "mentor",
        "sector": "EdTech / Future of Work",
        "stage": "Principal",
        "tags": ["edtech", "future of work", "HR tech", "learning", "B2B"],
        "needs": ["EdTech and HR tech founders", "University partnerships"],
        "expertise": ["Edtech monetisation models", "Corporate L&D sales", "Curriculum design", "University and government partnerships", "Impact measurement"],
        "location": "Bangalore, India",
        "bio": "Former Head of Learning at Coursera APAC, then founded SkillBridge (acquired by LinkedIn Learning 2022). Deep expertise in both consumer and enterprise learning products. Particularly passionate about upskilling in emerging markets.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Aleksei Petrov",
        "actor_type": "mentor",
        "sector": "Supply Chain / Logistics",
        "stage": "Senior",
        "tags": ["logistics", "supply chain", "last-mile", "automation", "warehousing"],
        "needs": ["Logistics tech startups", "Corporate innovation projects"],
        "expertise": ["Last-mile delivery optimisation", "Warehouse automation", "Supply chain visibility", "3PL partnerships", "Logistics unit economics"],
        "location": "Warsaw, Poland",
        "bio": "15 years in logistics at DHL and two venture-backed startups. Built a last-mile routing platform used by 50+ courier companies across CEE. Expert in the unglamorous but critical details of physical logistics tech.",
        "source_file": "seed",
        "programme_history": [],
    },

    # ── Companies / Startups ───────────────────────────────────────────────────
    {
        "name": "CyberShield",
        "actor_type": "company",
        "sector": "Cybersecurity",
        "stage": "seed",
        "tags": ["cybersecurity", "SME", "threat detection", "SaaS", "zero-trust"],
        "needs": ["Cybersecurity mentor", "Enterprise sales guidance", "SOC 2 compliance help", "Seed funding"],
        "expertise": ["Automated threat detection for SMEs", "Zero-trust network access", "Security awareness training"],
        "location": "Tallinn, Estonia",
        "bio": "CyberShield makes enterprise-grade cybersecurity accessible to SMEs through an automated SaaS platform. $45K MRR, 80 paying customers. Currently navigating the jump from SME to mid-market and need help positioning against bigger players.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "HarvestAI",
        "actor_type": "company",
        "sector": "AgriTech / AI",
        "stage": "pre-seed",
        "tags": ["agritech", "AI", "crop monitoring", "IoT", "sustainability"],
        "needs": ["AI mentor", "IoT hardware guidance", "EU agricultural grants", "Pilot farm partnerships"],
        "expertise": ["AI-powered crop disease detection", "Drone-based field monitoring", "Yield prediction models"],
        "location": "Poznan, Poland",
        "bio": "HarvestAI uses drone imagery and machine learning to detect crop diseases 3 weeks earlier than traditional methods, reducing pesticide use by up to 40%. Two PhD founders, strong IP, seeking first commercial pilot with a large farm cooperative.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "Learnly",
        "actor_type": "company",
        "sector": "EdTech",
        "stage": "seed",
        "tags": ["edtech", "B2B", "corporate training", "microlearning", "engagement"],
        "needs": ["EdTech mentor", "Corporate L&D sales strategy", "LMS integrations", "Series A prep"],
        "expertise": ["Microlearning platform", "AI-personalised learning paths", "Engagement analytics for L&D teams"],
        "location": "Amsterdam, Netherlands",
        "bio": "Learnly is a microlearning platform that increases corporate training completion rates from 12% (industry average) to 74%. $200K ARR, 15 enterprise customers. Struggling to scale enterprise sales beyond warm intros.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "FreightPath",
        "actor_type": "company",
        "sector": "Logistics Tech",
        "stage": "series-a",
        "tags": ["logistics", "freight", "marketplace", "cross-border", "automation"],
        "needs": ["Series A fundraising support", "Enterprise partnerships", "Logistics mentor", "Expansion into DACH market"],
        "expertise": ["Cross-border freight marketplace", "Real-time shipment tracking", "Automated customs documentation"],
        "location": "Prague, Czech Republic",
        "bio": "FreightPath is a B2B freight marketplace connecting 2,000+ SME shippers with 500+ carriers across CEE and DACH. €1.8M ARR, profitable unit economics. Raised €3M seed, now preparing Series A to fund DACH expansion.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "NutriTrack",
        "actor_type": "company",
        "sector": "HealthTech / Consumer",
        "stage": "pre-seed",
        "tags": ["healthtech", "nutrition", "consumer", "AI", "personalisation"],
        "needs": ["HealthTech mentor", "Consumer growth strategy", "Dietitian partnerships", "Pre-seed funding"],
        "expertise": ["AI nutrition planning", "Food logging via photo", "Integration with wearables"],
        "location": "Lisbon, Portugal",
        "bio": "NutriTrack uses computer vision to log meals from a photo and generates personalised nutrition plans reviewed by registered dietitians. 8,000 active users, strong retention (68% D30). Looking to move from consumer freemium to a sustainable B2B2C model through gyms and corporate wellness.",
        "source_file": "seed",
        "programme_history": [],
    },

    # ── Service Providers ──────────────────────────────────────────────────────
    {
        "name": "PixelForge Studio",
        "actor_type": "service_provider",
        "sector": "Design / Branding",
        "stage": "growth",
        "tags": ["design", "UX", "branding", "product design", "startup"],
        "needs": ["Seed to Series A startups", "Long-term design partnerships"],
        "expertise": ["Product UX/UI design", "Brand identity for startups", "Design system creation", "Pitch deck design", "User research"],
        "location": "Krakow, Poland",
        "bio": "PixelForge is a design studio that works exclusively with tech startups. Has designed products for 60+ startups, 12 of which went on to raise Series A+. Offers a startup package: brand identity + core product screens in 4 weeks.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "TalentBridge EU",
        "actor_type": "service_provider",
        "sector": "Recruitment / HR Tech",
        "stage": "growth",
        "tags": ["recruitment", "tech hiring", "HR", "remote", "employer branding"],
        "needs": ["Fast-growing startups hiring engineers", "Equity-for-recruitment arrangements"],
        "expertise": ["Technical recruitment across EU", "Remote-first hiring", "Employer branding for startups", "Engineering leadership search", "Equity compensation structuring"],
        "location": "Berlin, Germany",
        "bio": "TalentBridge specialises in recruiting senior engineers and tech leads for VC-backed startups across Europe. Average time-to-hire is 3 weeks vs industry average of 10. Works on success-fee basis, startup-friendly pricing.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "ScaleFinance",
        "actor_type": "service_provider",
        "sector": "Finance / CFO Services",
        "stage": "growth",
        "tags": ["finance", "CFO", "fundraising", "financial modelling", "SaaS metrics"],
        "needs": ["Startups preparing for seed or Series A", "Ongoing fractional CFO clients"],
        "expertise": ["Fractional CFO services", "Investor-ready financial models", "SaaS metrics and KPI dashboards", "Grant applications", "Term sheet review"],
        "location": "Dublin, Ireland",
        "bio": "ScaleFinance provides fractional CFO services to startups from pre-seed to Series B. Has helped 40+ startups raise a combined €120M. Specialises in building the financial infrastructure investors want to see before writing a cheque.",
        "source_file": "seed",
        "programme_history": [],
    },

    # ── Partners ───────────────────────────────────────────────────────────────
    {
        "name": "TechWars Accelerator",
        "actor_type": "partner",
        "sector": "Acceleration / Investment",
        "stage": "growth",
        "tags": ["accelerator", "pre-seed", "investment", "CEE", "cohort"],
        "needs": ["Pre-seed startups with strong founders", "Corporate sponsors"],
        "expertise": ["€50K pre-seed investment", "12-week intensive programme", "100+ mentor network", "Demo day with 80+ VCs", "CEE market access"],
        "location": "Warsaw, Poland",
        "bio": "TechWars is Central Europe's leading early-stage accelerator, running 3 cohorts per year with 10 startups each. Portfolio of 120+ companies, 18 exits. Invests €50K for 7% equity and provides intensive mentoring, office space, and a structured path to Series A.",
        "source_file": "seed",
        "programme_history": [],
    },
    {
        "name": "University of Warsaw Tech Transfer",
        "actor_type": "partner",
        "sector": "Research / Academia",
        "stage": "growth",
        "tags": ["research", "university", "deep tech", "IP licensing", "spin-out"],
        "needs": ["Industry partners for research projects", "Startups to license university IP"],
        "expertise": ["University IP licensing", "Research grant co-applications", "Access to PhD researchers", "Lab facilities", "Spin-out formation support"],
        "location": "Warsaw, Poland",
        "bio": "The University of Warsaw Tech Transfer Office connects industry with 3,500 researchers across computer science, biotech, and engineering. Supports IP licensing, joint research projects, and spin-out formation. Gateway to Horizon Europe collaborative grants.",
        "source_file": "seed",
        "programme_history": [],
    },
]


def seed():
    print(f"Seeding {len(ACTORS)} additional actors to {BASE_URL}...\n")
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

import os
import sys
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.core.config import settings
from app.core.database import SessionLocal, Base, engine
from app.models import (
    VehicleBrand,
    VehicleModel,
    Color,
    ColorType,
    Formula,
    FormulaStatus,
    FormulaSourceType,
    FormulaComponent,
    ComponentLibrary,
    User,
    AuditLog,
)
from app.auth.security import get_password_hash


def run_seed():
    print(f"Connecting to database and creating tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Admin User
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name=settings.ADMIN_FULL_NAME,
                is_active=True,
                is_superuser=True,
            )
            db.add(admin)
            db.commit()
            print(f"Created default admin user: {settings.ADMIN_EMAIL}")

        # 2. Component Library (Standard paint toners used in Azerbaijan body shops)
        library_data = [
            ("B001", "White Base", "Standard Base", "Toner", "g", "High-opacity mixing white"),
            ("B014", "Deep Black", "Standard Base", "Toner", "g", "Deep jet black without undertone"),
            ("B020", "Jet Black", "Standard Base", "Toner", "g", "High strength black"),
            ("M001", "Extra Coarse Metallic Silver", "Effect", "Metallic", "g", "Sparkle aluminum flakes"),
            ("M003", "Fine Metallic Silver", "Effect", "Metallic", "g", "Smooth fine aluminum flake"),
            ("M007", "Medium Metallic Silver", "Effect", "Metallic", "g", "Standard medium aluminum flake"),
            ("P001", "Fine White Pearl", "Effect", "Pearl", "g", "Micro-fine white mica pearl"),
            ("P005", "Blue Pearl", "Effect", "Pearl", "g", "Interference blue pearl"),
            ("P009", "Red Pearl", "Effect", "Pearl", "g", "Interference red pearl"),
            ("K002", "Deep Blue Toner", "Color", "Toner", "g", "Phthalo blue concentrated toner"),
            ("K008", "Yellow Oxide", "Color", "Toner", "g", "Inorganic iron oxide yellow"),
            ("K015", "Fast Red Toner", "Color", "Toner", "g", "Organic magenta red tint"),
            ("K022", "Green Shade Blue", "Color", "Toner", "g", "Cyan blue tint"),
            ("X001", "Transparent Binder", "Additive", "Binder", "g", "Clear acrylic resin base binder"),
            ("X002", "Basecoat Controller", "Additive", "Additive", "g", "Aluminum flop orientation agent"),
        ]

        comp_dict = {}
        for code, name, brand, category, unit, desc in library_data:
            c = db.query(ComponentLibrary).filter(ComponentLibrary.code == code).first()
            if not c:
                c = ComponentLibrary(code=code, name=name, brand=brand, category=category, unit=unit, description=desc)
                db.add(c)
                db.flush()
            comp_dict[code] = c
        db.commit()
        print(f"Component Library seeded with {len(library_data)} components.")

        # 3. Vehicle Brands & Models (Azerbaijan Car Market)
        brands_data = [
            {
                "name": "Toyota",
                "country": "Japan",
                "models": [
                    ("Camry", 2010, 2025),
                    ("Corolla", 2008, 2025),
                    ("Prius", 2004, 2024),
                    ("Land Cruiser Prado", 2003, 2024),
                    ("RAV4", 2006, 2025),
                ],
            },
            {
                "name": "Mercedes-Benz",
                "country": "Germany",
                "models": [
                    ("E-Class", 1995, 2025),
                    ("C-Class", 1998, 2025),
                    ("S-Class", 2000, 2025),
                    ("G-Class", 1999, 2025),
                    ("GLE", 2015, 2025),
                ],
            },
            {
                "name": "BMW",
                "country": "Germany",
                "models": [
                    ("3 Series", 2000, 2025),
                    ("5 Series", 2000, 2025),
                    ("7 Series", 2002, 2025),
                    ("X5", 2000, 2025),
                    ("X6", 2008, 2025),
                ],
            },
            {
                "name": "Hyundai",
                "country": "South Korea",
                "models": [
                    ("Elantra", 2006, 2025),
                    ("Sonata", 2005, 2025),
                    ("Tucson", 2004, 2025),
                    ("Santa Fe", 2006, 2025),
                    ("Accent", 2006, 2024),
                ],
            },
            {
                "name": "Kia",
                "country": "South Korea",
                "models": [
                    ("Optima", 2010, 2020),
                    ("K5", 2021, 2025),
                    ("Cerato", 2008, 2024),
                    ("Sportage", 2005, 2025),
                    ("Sorento", 2003, 2025),
                ],
            },
            {
                "name": "LADA (VAZ)",
                "country": "Russia",
                "models": [
                    ("2107", 1982, 2012),
                    ("Niva 4x4", 1977, 2024),
                    ("Priora", 2007, 2018),
                    ("Granta", 2011, 2025),
                    ("Vesta", 2015, 2025),
                ],
            },
            {
                "name": "BYD",
                "country": "China",
                "models": [
                    ("Song Plus", 2021, 2025),
                    ("Han", 2020, 2025),
                    ("Seal", 2022, 2025),
                ],
            },
        ]

        brand_dict = {}
        model_dict = {}

        for b_info in brands_data:
            b_name = b_info["name"]
            b = db.query(VehicleBrand).filter(VehicleBrand.name == b_name).first()
            if not b:
                b = VehicleBrand(
                    name=b_name,
                    slug=b_name.lower().replace(" ", "-").replace("(", "").replace(")", ""),
                    country=b_info["country"],
                )
                db.add(b)
                db.flush()
            brand_dict[b_name] = b

            for m_name, y_from, y_to in b_info["models"]:
                m = db.query(VehicleModel).filter(VehicleModel.brand_id == b.id, VehicleModel.name == m_name).first()
                if not m:
                    m = VehicleModel(
                        brand_id=b.id,
                        name=m_name,
                        slug=f"{b.slug}-{m_name.lower().replace(' ', '-')}",
                        year_from=y_from,
                        year_to=y_to,
                    )
                    db.add(m)
                    db.flush()
                model_dict[(b_name, m_name)] = m
        db.commit()
        print(f"Vehicle Brands and Models seeded.")

        # 4. Color & Formula Data
        # Format: (Brand, Model, ColorCode, ColorName, ColorType, PaintSystem, [Formulas])
        color_records = [
            (
                "Toyota",
                "Camry",
                "1G3",
                "Magnetic Gray",
                ColorType.METALLIC,
                "Basecoat",
                "Popular charcoal gray metallic across Toyota Camry and RAV4",
                [
                    {
                        "variant": "Standard Variant",
                        "version": 2,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "Verified against 2021 Toyota OEM spray-out card. Excellent match.",
                        "prep": "Mix components thoroughly. Apply 2-3 coats at 1.8-2.0 bar with 10 min flash-off. Follow with 2K clearcoat.",
                        "components": [
                            ("B001", "White Base", "350.0000"),
                            ("B014", "Deep Black", "220.0000"),
                            ("M003", "Fine Metallic Silver", "180.0000"),
                            ("K002", "Deep Blue Toner", "100.0000"),
                            ("X001", "Transparent Binder", "150.0000"),
                        ],
                    },
                    {
                        "variant": "Variant A - Darker",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.CORRECTED,
                        "notes": "Slightly darker flop for vehicles exposed to prolonged sun or US imports.",
                        "prep": "Apply 2 coats. Check match in direct sunlight.",
                        "components": [
                            ("B001", "White Base", "300.0000"),
                            ("B014", "Deep Black", "260.0000"),
                            ("M003", "Fine Metallic Silver", "180.0000"),
                            ("K002", "Deep Blue Toner", "110.0000"),
                            ("X001", "Transparent Binder", "150.0000"),
                        ],
                    },
                    {
                        "variant": "Variant B - Bluer",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.CORRECTED,
                        "notes": "More bluish face angle.",
                        "prep": "Standard basecoat application.",
                        "components": [
                            ("B001", "White Base", "340.0000"),
                            ("B014", "Deep Black", "210.0000"),
                            ("M003", "Fine Metallic Silver", "170.0000"),
                            ("K002", "Deep Blue Toner", "130.0000"),
                            ("X001", "Transparent Binder", "150.0000"),
                        ],
                    },
                ],
            ),
            (
                "Mercedes-Benz",
                "E-Class",
                "197",
                "Obsidian Black",
                ColorType.METALLIC,
                "Basecoat",
                "Signature Mercedes metallic black with subtle blue pearl sheen",
                [
                    {
                        "variant": "Standard Variant",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "OEM formulation tested on Baku workshop test panels.",
                        "prep": "Stir pearl thoroughly before adding. 2 wet coats with 15 min flash.",
                        "components": [
                            ("B014", "Deep Black", "740.0000"),
                            ("M003", "Fine Metallic Silver", "120.0000"),
                            ("P005", "Blue Pearl", "40.0000"),
                            ("X001", "Transparent Binder", "100.0000"),
                        ],
                    },
                    {
                        "variant": "Variant A - Finer Flake",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.CORRECTED,
                        "notes": "Alternative batch without blue pearl sheen.",
                        "prep": "2 coats basecoat + 2 coats high solids clearcoat.",
                        "components": [
                            ("B014", "Deep Black", "760.0000"),
                            ("M003", "Fine Metallic Silver", "140.0000"),
                            ("X001", "Transparent Binder", "100.0000"),
                        ],
                    },
                ],
            ),
            (
                "BMW",
                "5 Series",
                "300",
                "Alpine White III",
                ColorType.SOLID,
                "Basecoat",
                "Classic BMW pure solid white",
                [
                    {
                        "variant": "Standard Variant",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "Solid white formula with precise toner balance to prevent greening.",
                        "prep": "Solid white requires 2 full cross-coats for 100% opacity.",
                        "components": [
                            ("B001", "White Base", "920.0000"),
                            ("B014", "Deep Black", "25.0000"),
                            ("K008", "Yellow Oxide", "35.0000"),
                            ("X001", "Transparent Binder", "20.0000"),
                        ],
                    }
                ],
            ),
            (
                "Hyundai",
                "Elantra",
                "WAW",
                "Polar White",
                ColorType.SOLID,
                "Basecoat",
                "High-volume Hyundai/Kia solid white in Azerbaijan",
                [
                    {
                        "variant": "Standard Variant",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "High coverage solid white formulation.",
                        "prep": "2 wet coats with 10 min flash-off.",
                        "components": [
                            ("B001", "White Base", "950.0000"),
                            ("B014", "Deep Black", "15.0000"),
                            ("K008", "Yellow Oxide", "15.0000"),
                            ("X001", "Transparent Binder", "20.0000"),
                        ],
                    }
                ],
            ),
            (
                "Hyundai",
                "Sonata",
                "T2G",
                "Nocturne Gray",
                ColorType.METALLIC,
                "Basecoat",
                "Modern dark metallic gray",
                [
                    {
                        "variant": "Standard Variant",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "Even metallic distribution formulation.",
                        "prep": "Drop coat recommended for uniform flake orientation.",
                        "components": [
                            ("B001", "White Base", "280.0000"),
                            ("B014", "Deep Black", "380.0000"),
                            ("M003", "Fine Metallic Silver", "190.0000"),
                            ("K002", "Deep Blue Toner", "50.0000"),
                            ("X001", "Transparent Binder", "100.0000"),
                        ],
                    }
                ],
            ),
            (
                "LADA (VAZ)",
                "Niva 4x4",
                "690",
                "Snow Queen (Snezhnaya Koroleva)",
                ColorType.METALLIC,
                "Basecoat",
                "Widely requested classic silver metallic across Azerbaijan regions",
                [
                    {
                        "variant": "Standard Variant",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "High sparkle coarse metallic formula.",
                        "prep": "Apply 1 mist coat at 2.2 bar after 2 wet coats.",
                        "components": [
                            ("B001", "White Base", "200.0000"),
                            ("M001", "Extra Coarse Metallic Silver", "400.0000"),
                            ("M003", "Fine Metallic Silver", "250.0000"),
                            ("B014", "Deep Black", "30.0000"),
                            ("X001", "Transparent Binder", "120.0000"),
                        ],
                    }
                ],
            ),
            (
                "LADA (VAZ)",
                "2107",
                "202",
                "Bright White",
                ColorType.SOLID,
                "Basecoat",
                "Legendary VAZ classic solid white",
                [
                    {
                        "variant": "Standard Variant",
                        "version": 1,
                        "status": FormulaStatus.PUBLISHED,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "Classic VAZ shade.",
                        "prep": "2 full coats.",
                        "components": [
                            ("B001", "White Base", "980.0000"),
                            ("K008", "Yellow Oxide", "10.0000"),
                            ("X001", "Transparent Binder", "10.0000"),
                        ],
                    }
                ],
            ),
            # Sample Draft / Under Review formulas for expert workflow demonstration
            (
                "BYD",
                "Song Plus",
                "B10",
                "Time Gray",
                ColorType.METALLIC,
                "Basecoat",
                "New Chinese EV gray shade under workshop verification",
                [
                    {
                        "variant": "Laboratory Trial 1",
                        "version": 1,
                        "status": FormulaStatus.UNDER_REVIEW,
                        "source": FormulaSourceType.MEASURED,
                        "notes": "Measured with 3-angle spectrophotometer. Awaiting test panel confirmation.",
                        "prep": "Trial batch.",
                        "components": [
                            ("B001", "White Base", "410.0000"),
                            ("B014", "Deep Black", "290.0000"),
                            ("M003", "Fine Metallic Silver", "200.0000"),
                            ("X001", "Transparent Binder", "100.0000"),
                        ],
                    },
                    {
                        "variant": "Draft Correction",
                        "version": 1,
                        "status": FormulaStatus.DRAFT,
                        "source": FormulaSourceType.EXPERT_CREATED,
                        "notes": "Work in progress draft formula by technician.",
                        "prep": "Do not spray on vehicle yet.",
                        "components": [
                            ("B001", "White Base", "420.0000"),
                            ("B014", "Deep Black", "280.0000"),
                            ("M003", "Fine Metallic Silver", "200.0000"),
                            ("X001", "Transparent Binder", "100.0000"),
                        ],
                    },
                ],
            ),
        ]

        total_formulas = 0
        for b_name, m_name, c_code, c_name, c_type, p_sys, notes, formulas in color_records:
            b = brand_dict[b_name]
            m = model_dict.get((b_name, m_name))

            color = (
                db.query(Color)
                .filter(Color.brand_id == b.id, Color.color_code == c_code, Color.paint_system == p_sys)
                .first()
            )
            if not color:
                color = Color(
                    brand_id=b.id,
                    model_id=m.id if m else None,
                    color_code=c_code,
                    color_name=c_name,
                    color_type=c_type,
                    paint_system=p_sys,
                    notes=notes,
                    is_active=True,
                )
                db.add(color)
                db.flush()

            for f_data in formulas:
                variant_name = f_data["variant"]
                version = f_data["version"]

                formula = (
                    db.query(Formula)
                    .filter(
                        Formula.color_id == color.id,
                        Formula.variant_name == variant_name,
                        Formula.version == version,
                    )
                    .first()
                )

                comps = f_data["components"]
                total_amount = sum(Decimal(amt) for _, _, amt in comps)

                if not formula:
                    formula = Formula(
                        color_id=color.id,
                        formula_name=f"{b_name} {c_code} {c_name} - {variant_name}",
                        variant_name=variant_name,
                        paint_system=p_sys,
                        base_total_amount=total_amount,
                        unit="g",
                        status=f_data["status"],
                        version=version,
                        source_type=f_data["source"],
                        expert_notes=f_data["notes"],
                        preparation_notes=f_data["prep"],
                        created_by=settings.ADMIN_EMAIL,
                        verified_by=settings.ADMIN_EMAIL if f_data["status"] == FormulaStatus.PUBLISHED else None,
                        verified_at=datetime.now(timezone.utc) if f_data["status"] == FormulaStatus.PUBLISHED else None,
                    )
                    db.add(formula)
                    db.flush()

                    for idx, (comp_code, comp_name, amt) in enumerate(comps):
                        fc = FormulaComponent(
                            formula_id=formula.id,
                            component_code=comp_code,
                            component_name=comp_name,
                            amount=Decimal(amt),
                            unit="g",
                            sort_order=idx,
                        )
                        db.add(fc)
                    total_formulas += 1

        db.commit()
        print(f"Seed completed: {len(color_records)} colors and {total_formulas} formulas populated.")

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()

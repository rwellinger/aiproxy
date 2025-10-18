#!/usr/bin/env python3
"""
Seeding script for lyric parsing rules.
Exported from Dev-DB on 2025-10-17.
This script seeds the database with regex-based lyric cleanup and section detection rules.

Usage:
    python scripts/seed_lyric_parsing_rules.py
"""

import base64
import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.orm import Session

from db.database import get_db
from db.models import LyricParsingRule


def encode_replacement(text: str) -> str:
    """Encode replacement string to Base64 for safe storage"""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


# Current production lyric parsing rules from Dev-DB (2025-10-17)
# NOTE: All replacement values are Base64-encoded for safe storage
RULES = [
    {
        "name": "Comma Line Breaks",
        "description": "Add line break after comma if followed by 5+ words",
        "pattern": r",\s+(?=(?:[^\s,]+\s*){5,})",
        "replacement": encode_replacement(",\n"),
        "rule_type": "cleanup",
        "active": True,
        "order": 0,
    },
    {
        "name": "Line Break After Comma + Capital",
        "description": "Add line break after comma when followed by capital letter",
        "pattern": r",\s+(?=[A-Z])",
        "replacement": encode_replacement(",\n"),
        "rule_type": "cleanup",
        "active": True,
        "order": 1,
    },
    {
        "name": "Remove Trailing Spaces",
        "description": "Remove whitespace at the end of each line",
        "pattern": r"\s+$",
        "replacement": encode_replacement(""),
        "rule_type": "cleanup",
        "active": True,
        "order": 3,
    },
    {
        "name": "Normalize Smart Quotes (Double)",
        "description": "Convert curly double quotes to straight quotes",
        "pattern": r"[\u201C\u201D]",
        "replacement": encode_replacement('"'),
        "rule_type": "cleanup",
        "active": True,
        "order": 4,
    },
    {
        "name": "Normalize Smart Quotes (Single)",
        "description": "Convert curly single quotes to straight quotes",
        "pattern": r"[\u2018\u2019]",
        "replacement": encode_replacement("'"),
        "rule_type": "cleanup",
        "active": True,
        "order": 5,
    },
    {
        "name": "Line Break After Period + Capital",
        "description": "Add line break after period when followed by capital letter",
        "pattern": r"\.\s+(?=[A-Z])",
        "replacement": encode_replacement(".\n"),
        "rule_type": "cleanup",
        "active": True,
        "order": 6,
    },
    {
        "name": "Normalize Em Dash",
        "description": "Convert em dash to regular dash with spaces",
        "pattern": r"\u2014",
        "replacement": encode_replacement(" - "),
        "rule_type": "cleanup",
        "active": True,
        "order": 7,
    },
    {
        "name": "Normalize Ellipsis",
        "description": "Convert ellipsis character to three periods",
        "pattern": r"\u2026",
        "replacement": encode_replacement("..."),
        "rule_type": "cleanup",
        "active": True,
        "order": 8,
    },
    {
        "name": "Normalize En Dash",
        "description": "Convert en dash to regular dash with spaces",
        "pattern": r"\u2013",
        "replacement": encode_replacement(" - "),
        "rule_type": "cleanup",
        "active": True,
        "order": 9,
    },
    {
        "name": "Reduce Blank Lines",
        "description": "Remove excessive blank lines (max 1 blank line)",
        "pattern": r"\n{3,}",
        "replacement": encode_replacement("\n\n"),
        "rule_type": "cleanup",
        "active": True,
        "order": 10,
    },
    {
        "name": "Section Label Detection",
        "description": "Detect Markdown-style section labels (Intro, Verse, Chorus, etc.)",
        "pattern": r"^\*\*\s*(Intro|Verse\s*\d+|Chorus|Bridge|Outro|Pre[-_\s]?chorus|Post[-_\s]?chorus)\s*\*\*$",
        "replacement": encode_replacement(""),
        "rule_type": "section",
        "active": True,
        "order": 2,
    },
]


def seed_lyric_parsing_rules():
    """Seed the database with lyric parsing rules"""
    db: Session = next(get_db())

    try:
        inserted_count = 0
        updated_count = 0

        print("Starting lyric parsing rules seeding...\n")

        for rule_data in RULES:
            print(f"Processing rule: {rule_data['name']}")

            # Check if rule already exists
            existing = db.query(LyricParsingRule).filter(LyricParsingRule.name == rule_data["name"]).first()

            if existing:
                print(f"  Rule exists (ID: {existing.id}), updating...")
                # Update existing rule with all fields
                existing.description = rule_data["description"]
                existing.pattern = rule_data["pattern"]
                existing.replacement = rule_data["replacement"]
                existing.rule_type = rule_data["rule_type"]
                existing.active = rule_data["active"]
                existing.order = rule_data["order"]
                updated_count += 1
            else:
                print("  Creating new rule...")
                # Create new rule
                new_rule = LyricParsingRule(
                    name=rule_data["name"],
                    description=rule_data["description"],
                    pattern=rule_data["pattern"],
                    replacement=rule_data["replacement"],
                    rule_type=rule_data["rule_type"],
                    active=rule_data["active"],
                    order=rule_data["order"],
                )
                db.add(new_rule)
                inserted_count += 1

        # Commit all changes
        db.commit()

        print("\n✅ Seeding completed successfully!")
        print(f"   - Inserted: {inserted_count} new rules")
        print(f"   - Updated:  {updated_count} existing rules")
        print(f"   - Total:    {inserted_count + updated_count} rules processed")

        return True

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback

        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


def verify_rules():
    """Verify that all rules were seeded correctly"""
    db: Session = next(get_db())

    try:
        rules = db.query(LyricParsingRule).filter(LyricParsingRule.active).order_by(LyricParsingRule.order).all()

        print("\n📊 Verification Results:")
        print(f"   Total active rules in DB: {len(rules)}")

        if len(rules) == 0:
            print("   ⚠️  WARNING: No rules found in database!")
            return False

        # Group by rule_type for display
        by_type = {}
        for rule in rules:
            if rule.rule_type not in by_type:
                by_type[rule.rule_type] = []
            by_type[rule.rule_type].append({"name": rule.name, "order": rule.order})

        print("\n   Rules by type:")
        for rule_type, rule_list in sorted(by_type.items()):
            print(f"\n   {rule_type}:")
            for rule_info in sorted(rule_list, key=lambda x: x["order"]):
                print(f"     [{rule_info['order']}] {rule_info['name']}")

        # Check if we have the expected number of rules
        expected_count = len(RULES)
        if len(rules) >= expected_count:
            print(f"\n   ✅ All {expected_count} expected rules are present")
            return True
        else:
            print(f"\n   ⚠️  Expected {expected_count} rules, but found {len(rules)}")
            return False

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Lyric Parsing Rules Seeding Script")
    print("=" * 60)
    print("This script will seed/update all lyric parsing rules")
    print("=" * 60 + "\n")

    if seed_lyric_parsing_rules():
        if verify_rules():
            print("\n🎉 Seeding and verification completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Rules seeded but verification has warnings!")
            sys.exit(1)
    else:
        print("\n💥 Seeding failed!")
        sys.exit(1)

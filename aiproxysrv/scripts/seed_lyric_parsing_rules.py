#!/usr/bin/env python3
"""
Seeding script for lyric parsing rules.
This script seeds default cleanup and section detection rules into the database.
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.orm import Session

from db.database import get_db
from db.models import LyricParsingRule


# Default lyric parsing rules
RULES = [
    # Cleanup Rules
    {
        "name": "Comma Line Breaks",
        "description": "Add line break after comma if followed by 5+ words",
        "pattern": r",\s+(?=(?:[^\s,]+\s*){5,})",
        "replacement": ",\n",
        "rule_type": "cleanup",
        "active": True,
        "order": 0,
    },
    {
        "name": "Line Break After Comma + Capital",
        "description": "Add line break after comma when followed by capital letter",
        "pattern": r",\s+(?=[A-Z])",
        "replacement": ",\n",
        "rule_type": "cleanup",
        "active": True,
        "order": 1,
    },
    {
        "name": "Remove Trailing Spaces",
        "description": "Remove whitespace at the end of each line",
        "pattern": r"\s+$",
        "replacement": "",
        "rule_type": "cleanup",
        "active": True,
        "order": 3,
    },
    {
        "name": "Normalize Smart Quotes (Double)",
        "description": "Convert curly double quotes to straight quotes",
        "pattern": r"[\u201C\u201D]",
        "replacement": '"',
        "rule_type": "cleanup",
        "active": True,
        "order": 4,
    },
    {
        "name": "Normalize Smart Quotes (Single)",
        "description": "Convert curly single quotes to straight quotes",
        "pattern": r"[\u2018\u2019]",
        "replacement": "'",
        "rule_type": "cleanup",
        "active": True,
        "order": 5,
    },
    {
        "name": "Line Break After Period + Capital",
        "description": "Add line break after period when followed by capital letter",
        "pattern": r"\.\s+(?=[A-Z])",
        "replacement": ".\n",
        "rule_type": "cleanup",
        "active": True,
        "order": 6,
    },
    {
        "name": "Normalize Em Dash",
        "description": "Convert em dash to regular dash with spaces",
        "pattern": r"\u2014",
        "replacement": " - ",
        "rule_type": "cleanup",
        "active": True,
        "order": 7,
    },
    {
        "name": "Normalize Ellipsis",
        "description": "Convert ellipsis character to three periods",
        "pattern": r"\u2026",
        "replacement": "...",
        "rule_type": "cleanup",
        "active": True,
        "order": 8,
    },
    {
        "name": "Normalize En Dash",
        "description": "Convert en dash to regular dash with spaces",
        "pattern": r"\u2013",
        "replacement": " - ",
        "rule_type": "cleanup",
        "active": True,
        "order": 9,
    },
    {
        "name": "Reduce Blank Lines",
        "description": "Remove excessive blank lines (max 1 blank line)",
        "pattern": r"\n{3,}",
        "replacement": r"\n\n",
        "rule_type": "cleanup",
        "active": True,
        "order": 10,
    },
    # Section Detection Rules
    {
        "name": "Section Label Detection",
        "description": "Detect Markdown-style section labels (Intro, Verse, Chorus, etc.)",
        "pattern": r"^\*\*\s*(Intro|Verse\s*\d+|Chorus|Bridge|Outro|Pre[-_\s]?chorus|Post[-_\s]?chorus)\s*\*\*$",
        "replacement": "",
        "rule_type": "section",
        "active": True,
        "order": 2,
    },
]


def seed_lyric_parsing_rules():
    """Seed the database with default lyric parsing rules"""
    db: Session = next(get_db())

    try:
        # Track what we're inserting
        inserted_count = 0
        updated_count = 0

        for rule_data in RULES:
            print(f"\nProcessing rule: {rule_data['name']} ({rule_data['rule_type']})")

            # Check if rule already exists (by name)
            existing = db.query(LyricParsingRule).filter(LyricParsingRule.name == rule_data["name"]).first()

            if existing:
                print("  Rule exists, updating...")
                # Update existing rule
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
                new_rule = LyricParsingRule(**rule_data)
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
        db.rollback()
        return False

    finally:
        db.close()


def verify_rules():
    """Verify that all rules were seeded correctly"""
    db: Session = next(get_db())

    try:
        cleanup_rules = db.query(LyricParsingRule).filter(LyricParsingRule.rule_type == "cleanup").all()
        section_rules = db.query(LyricParsingRule).filter(LyricParsingRule.rule_type == "section").all()

        print("\n📊 Verification Results:")
        print(f"   Total cleanup rules: {len(cleanup_rules)} (active: {sum(1 for r in cleanup_rules if r.active)})")
        print(f"   Total section rules: {len(section_rules)} (active: {sum(1 for r in section_rules if r.active)})")

        return True

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Starting lyric parsing rules seeding...")

    if seed_lyric_parsing_rules():
        verify_rules()
        print("\n🎉 All done!")
    else:
        print("\n💥 Seeding failed!")
        sys.exit(1)

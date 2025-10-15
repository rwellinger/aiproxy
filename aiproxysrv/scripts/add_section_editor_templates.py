#!/usr/bin/env python3
"""
Script to add Section Editor prompt templates to the database.
This script inserts three templates for the Lyric Magic - Section Editor feature:
- lyrics/improve-section: Improves a lyric section while maintaining context
- lyrics/rewrite-section: Completely rewrites a section with fresh perspectives
- lyrics/extend-section: Extends a section by adding more lines

Usage:
    python scripts/add_section_editor_templates.py

Requirements:
    - PostgreSQL database must be running
    - Database connection configured in src/db/database.py
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.orm import Session

from db.database import get_db
from db.models import PromptTemplate


# Section Editor template configurations
SECTION_TEMPLATES = [
    {
        "category": "lyrics",
        "action": "improve-section",
        "name": "Improve Lyric Section",
        "pre_condition": """You are a professional song lyricist. Your task is to improve the given song section while maintaining its core message and style. Consider:
- Rhyme scheme and rhythm
- Imagery and metaphors
- Emotional impact
- Word choice and clarity
- Flow and pacing

Keep the same general length and structure. Only improve the quality, do not change the fundamental meaning or add new concepts.""",
        "post_condition": 'Return ONLY the improved section text as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name (like "Verse1:") in your output. Keep all lines together as one continuous block of text.',
        "description": "Improves a specific lyric section while maintaining context and style",
        "version": "1.3",
        "model": "gpt-oss:20b",
        "temperature": 0.7,
        "max_tokens": 512,
    },
    {
        "category": "lyrics",
        "action": "rewrite-section",
        "name": "Rewrite Lyric Section",
        "pre_condition": """You are a professional song lyricist. Your task is to completely rewrite the given song section with fresh perspectives while keeping similar themes. Feel free to:
- Use different metaphors and imagery
- Change the rhyme scheme
- Explore new angles on the same topic
- Vary the rhythm and structure
- Add creative wordplay

The rewritten section should feel like a new take on the same emotional core.""",
        "post_condition": "Return ONLY the rewritten section text as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name in your output. Keep all lines together as one continuous block of text.",
        "description": "Completely rewrites a lyric section with fresh creative perspectives",
        "version": "1.3",
        "model": "gpt-oss:20b",
        "temperature": 0.8,
        "max_tokens": 512,
    },
    {
        "category": "lyrics",
        "action": "extend-section",
        "name": "Extend Lyric Section",
        "pre_condition": """You are a professional song lyricist. Your task is to extend the given song section by adding more lines. The extension should:
- Match the existing rhyme scheme and rhythm
- Continue the thematic development
- Maintain consistent imagery and tone
- Flow naturally from the existing content
- Add depth without being repetitive

Build upon what is already there to create a longer, more developed section.""",
        "post_condition": "Return the COMPLETE extended section (original + new lines) as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name in your output. Keep all lines together as one continuous block of text.",
        "description": "Extends a lyric section by adding more lines that match style and theme",
        "version": "1.3",
        "model": "gpt-oss:20b",
        "temperature": 0.7,
        "max_tokens": 512,
    },
]


def add_section_editor_templates():
    """Add all Section Editor templates to the database"""
    db: Session = next(get_db())
    results = []

    try:
        for template_config in SECTION_TEMPLATES:
            action = template_config["action"]

            # Check if template already exists
            existing = (
                db.query(PromptTemplate)
                .filter(
                    PromptTemplate.category == template_config["category"],
                    PromptTemplate.action == template_config["action"],
                )
                .first()
            )

            if existing:
                print(f"Template '{template_config['category']}/{action}' already exists, updating...")
                # Update existing template
                existing.pre_condition = template_config["pre_condition"]
                existing.post_condition = template_config["post_condition"]
                existing.description = template_config["description"]
                existing.version = template_config["version"]
                existing.model = template_config["model"]
                existing.temperature = template_config["temperature"]
                existing.max_tokens = template_config["max_tokens"]
                existing.active = True
                operation = "updated"
            else:
                print(f"Creating new template '{template_config['category']}/{action}'...")
                # Create new template
                new_template = PromptTemplate(
                    category=template_config["category"],
                    action=template_config["action"],
                    pre_condition=template_config["pre_condition"],
                    post_condition=template_config["post_condition"],
                    description=template_config["description"],
                    version=template_config["version"],
                    model=template_config["model"],
                    temperature=template_config["temperature"],
                    max_tokens=template_config["max_tokens"],
                    active=True,
                )
                db.add(new_template)
                operation = "created"

            results.append((template_config, operation))

        # Commit all changes
        db.commit()

        print("\n✅ Section Editor templates successfully processed!")
        for template_config, operation in results:
            print(f"\n   [{operation.upper()}] {template_config['name']}")
            print(f"   Category/Action: {template_config['category']}/{template_config['action']}")
            print(
                f"   Model: {template_config['model']} (temp: {template_config['temperature']}, "
                f"max_tokens: {template_config['max_tokens']})"
            )
            print(f"   Description: {template_config['description']}")

        return True

    except Exception as e:
        print(f"\n❌ Error adding Section Editor templates: {str(e)}")
        db.rollback()
        return False

    finally:
        db.close()


def verify_templates():
    """Verify that all Section Editor templates were added correctly"""
    db: Session = next(get_db())

    try:
        print("\n📊 Verifying templates in database...")
        all_found = True

        for template_config in SECTION_TEMPLATES:
            template = (
                db.query(PromptTemplate)
                .filter(
                    PromptTemplate.category == template_config["category"],
                    PromptTemplate.action == template_config["action"],
                    PromptTemplate.active,
                )
                .first()
            )

            if template:
                print(f"\n   ✓ {template_config['name']}")
                print(f"     ID: {template.id}")
                print(f"     Category/Action: {template.category}/{template.action}")
                print(f"     Model: {template.model}")
                print(f"     Temperature: {template.temperature}")
                print(f"     Max tokens: {template.max_tokens}")
                print(f"     Active: {template.active}")
            else:
                print(f"\n   ✗ {template_config['name']} - NOT FOUND")
                all_found = False

        return all_found

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("✏️  Adding Section Editor templates to database...")
    print("=" * 60)

    if add_section_editor_templates():
        if verify_templates():
            print("\n" + "=" * 60)
            print("🎉 Section Editor templates setup completed successfully!")
            print("\nThe Section Editor feature is now fully operational.")
            print("\nYou can now use the following AI actions in the Section Editor:")
            print("  • Improve Section  - Enhance quality while keeping meaning")
            print("  • Rewrite Section  - Fresh creative perspective")
            print("  • Extend Section   - Add more lines with matching style")
        else:
            print("\n⚠️  Templates added but verification failed!")
            sys.exit(1)
    else:
        print("\n💥 Failed to add Section Editor templates!")
        sys.exit(1)

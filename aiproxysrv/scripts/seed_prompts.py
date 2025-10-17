#!/usr/bin/env python3
"""
Seeding script for migrating existing prompt templates to the database.
This script reads the current templates from the TypeScript service and inserts them into the DB.
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.orm import Session

from db.database import get_db
from db.models import PromptTemplate


# Templates from the current TypeScript service
TEMPLATES = {
    "image": {
        "enhance": {
            "pre_condition": "One-sentence DALL-E prompt:",
            "post_condition": "Only respond with the prompt.",
            "description": "Enhances image generation prompts for DALL-E",
            "version": "1.0",
            "model_hint": "llama3",
        },
        "translate": {
            "pre_condition": "Translate this image prompt to english:",
            "post_condition": "Only respond with the translation.",
            "description": "Translates image prompts to English",
            "version": "1.0",
            "model_hint": "gpt-oss",
        },
    },
    "music": {
        "enhance": {
            "pre_condition": "One-sentence Suno Music Style prompt without artist names or band names:",
            "post_condition": "Only respond with the prompt.",
            "description": "Enhances music style prompts for Suno without artist references",
            "version": "1.0",
            "model_hint": "llama3",
        },
        "translate": {
            "pre_condition": "Translate this music style description to english:",
            "post_condition": "Only respond with the translation.",
            "description": "Translates music style descriptions to English",
            "version": "1.0",
            "model_hint": "gpt-oss",
        },
    },
    "lyrics": {
        "generate": {
            "pre_condition": """You are a professional song lyricist and songwriter. Your task is to completely write the given song idea with fresh perspectives while keeping similar themes. Feel free to:
- Use metaphors and imagery
- Explore angles on the same topic
- Vary the rhythm and structure
- Add creative wordplay
- Make the phrases fluent

The new lyric should feel like a new take on the same emotional core.

FORMATTING RULES:
1. Start each section with its label in Markdown bold format (**LABEL**) on its own line
2. Use these exact label formats: **INTRO**, **VERSE1**, **VERSE2**, **PRE-CHORUS**, **CHORUS**, **BRIDGE**, **OUTRO**
3. Write each phrase on a new line - break lines after commas or natural pauses
4. Each section should be separated by a blank line

Example format:
**INTRO**
First line here,
second line after comma,
third line with pause.

**VERSE1**
Each phrase on new line,
makes it easy to sing,
natural breathing points.""",
            "post_condition": """Only output completely original lyrics with each section as a single paragraph. Ensure all content is your own creation and not copied from existing songs.

IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English).

Do not include any other explanations, comments, or metadata in your output.""",
            "description": "Generates song lyrics with proper formatting and line breaks",
            "version": "2.0",
            "model_hint": "llama3",
        },
        "translate": {
            "pre_condition": "By a britisch songwriter and translate this lyric text to britisch english:",
            "post_condition": "Only respond with the translation.",
            "description": "Translates lyrics to British English",
            "version": "1.0",
            "model_hint": "gpt-oss",
        },
    },
}


def seed_prompt_templates():
    """Seed the database with initial prompt templates"""
    db: Session = next(get_db())

    try:
        # Track what we're inserting
        inserted_count = 0
        updated_count = 0

        for category, actions in TEMPLATES.items():
            print(f"\nProcessing category: {category}")

            for action, template_data in actions.items():
                print(f"  Processing action: {action}")

                # Check if template already exists
                existing = (
                    db.query(PromptTemplate)
                    .filter(PromptTemplate.category == category, PromptTemplate.action == action)
                    .first()
                )

                if existing:
                    print("    Template exists, updating...")
                    # Update existing template
                    existing.pre_condition = template_data["pre_condition"]
                    existing.post_condition = template_data["post_condition"]
                    existing.description = template_data["description"]
                    existing.version = template_data["version"]
                    existing.model_hint = template_data["model_hint"]
                    existing.active = True
                    updated_count += 1
                else:
                    print("    Creating new template...")
                    # Create new template
                    new_template = PromptTemplate(
                        category=category,
                        action=action,
                        pre_condition=template_data["pre_condition"],
                        post_condition=template_data["post_condition"],
                        description=template_data["description"],
                        version=template_data["version"],
                        model_hint=template_data["model_hint"],
                        active=True,
                    )
                    db.add(new_template)
                    inserted_count += 1

        # Commit all changes
        db.commit()

        print("\n✅ Seeding completed successfully!")
        print(f"   - Inserted: {inserted_count} new templates")
        print(f"   - Updated:  {updated_count} existing templates")
        print(f"   - Total:    {inserted_count + updated_count} templates processed")

        return True

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        return False

    finally:
        db.close()


def verify_templates():
    """Verify that all templates were seeded correctly"""
    db: Session = next(get_db())

    try:
        templates = db.query(PromptTemplate).filter(PromptTemplate.active).all()

        print("\n📊 Verification Results:")
        print(f"   Total active templates in DB: {len(templates)}")

        # Group by category for display
        by_category = {}
        for template in templates:
            if template.category not in by_category:
                by_category[template.category] = []
            by_category[template.category].append(template.action)

        for category, actions in by_category.items():
            print(f"   {category}: {', '.join(sorted(actions))}")

        return True

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Starting prompt template seeding...")

    if seed_prompt_templates():
        verify_templates()
        print("\n🎉 All done!")
    else:
        print("\n💥 Seeding failed!")
        sys.exit(1)

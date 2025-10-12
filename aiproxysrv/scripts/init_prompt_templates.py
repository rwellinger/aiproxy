#!/usr/bin/env python3
"""
Initial load script for prompt templates.
This script loads all current production prompt templates into the database.
Based on actual Test-DB data as of 2025-10-12.

Usage:
    python scripts/init_prompt_templates.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db
from db.models import PromptTemplate


# Current production templates from Test-DB (2025-10-12)
TEMPLATES = {
    "image": {
        "enhance": {
            "pre_condition": "One-sentence DALL-E prompt",
            "post_condition": "Only respond with the prompt.",
            "description": "Enhances image generation prompts for DALL-E3",
            "version": "2.4",
            "model": "llama3.2:3b",
            "temperature": 1.5,
            "max_tokens": 13,
            "active": True
        },
        "translate": {
            "pre_condition": "Translate this image prompt to english",
            "post_condition": "Only respond with the translation.",
            "description": "Translates image prompts to English",
            "version": "1.7",
            "model": "gpt-oss:20b",
            "temperature": 0.5,
            "max_tokens": 256,
            "active": True
        }
    },
    "lyrics": {
        "generate": {
            "pre_condition": "Be a songwriter and write a song with the given conditions and input text.",
            "post_condition": "Only output completely original lyrics with each section as a single paragraph. Ensure all content is your own creation and not copied from existing songs. Do not include any explanations, notes, or introductions.",
            "description": "Generates song lyrics from input text",
            "version": "2.3",
            "model": "gpt-oss:20b",
            "temperature": 0.7,
            "max_tokens": 2048,
            "active": True
        },
        "translate": {
            "pre_condition": "Be a British songwriter. Translate the following lyrics into fluent, natural British English with good lyrical flow. Keep the emotional tone, adapt for rhythm and rhyme where needed, and make it sound like it was written by a native English-speaking artist. Lyrics",
            "post_condition": "Only output the translated lyrics. Do not include any explanations, notes, or introductions.",
            "description": "Translates lyrics to British English",
            "version": "1.6",
            "model": "gpt-oss:20b",
            "temperature": 0.5,
            "max_tokens": 2048,
            "active": True
        }
    },
    "music": {
        "enhance": {
            "pre_condition": "One-sentence Suno Music Style prompt without artist names or band names",
            "post_condition": "Only respond with the prompt.",
            "description": "Enhances music style prompts for Mureka without artist references",
            "version": "1.7",
            "model": "llama3.2:3b",
            "temperature": 0.7,
            "max_tokens": 512,
            "active": True
        },
        "translate": {
            "pre_condition": "Translate this music style description to english",
            "post_condition": "Only respond with the translation.",
            "description": "Translates music style descriptions to English",
            "version": "1.7",
            "model": "gpt-oss:20b",
            "temperature": 0.5,
            "max_tokens": 512,
            "active": True
        }
    },
    "titel": {
        "generate": {
            "pre_condition": "Generate a short, creative, and engaging title in the same language as the input text. The title should:\n  - Capture the main subject, theme, or essence described\n  - Be memorable and impactful\n  - Match the style and context of the content (visual for images, artistic for songs/lyrics)\n  - Be concise (2-8 words) and suitable for the intended medium\n  - Avoid using commas, colons, or other punctuation marks\n  - Feel natural and relevant to the given input",
            "post_condition": "Respond only with the title, maximum 50 characters. Do not include any explanations, notes, or introductions.",
            "description": "Generates song titles from various inputs (title, lyrics, style, or default)",
            "version": "3.4",
            "model": "llama3.2:3b",
            "temperature": 0.7,
            "max_tokens": 20,
            "active": True
        }
    }
}


def init_prompt_templates():
    """Initialize the database with production prompt templates"""
    db: Session = next(get_db())

    try:
        inserted_count = 0
        updated_count = 0

        print("Starting prompt template initialization...\n")

        for category, actions in TEMPLATES.items():
            print(f"Processing category: {category}")

            for action, template_data in actions.items():
                print(f"  Processing action: {action}")

                # Check if template already exists
                existing = db.query(PromptTemplate).filter(
                    PromptTemplate.category == category,
                    PromptTemplate.action == action
                ).first()

                if existing:
                    print(f"    Template exists (ID: {existing.id}), updating...")
                    # Update existing template with all fields
                    existing.pre_condition = template_data["pre_condition"]
                    existing.post_condition = template_data["post_condition"]
                    existing.description = template_data["description"]
                    existing.version = template_data["version"]
                    existing.model = template_data["model"]
                    existing.temperature = template_data["temperature"]
                    existing.max_tokens = template_data["max_tokens"]
                    existing.active = template_data["active"]
                    updated_count += 1
                else:
                    print(f"    Creating new template...")
                    # Create new template
                    new_template = PromptTemplate(
                        category=category,
                        action=action,
                        pre_condition=template_data["pre_condition"],
                        post_condition=template_data["post_condition"],
                        description=template_data["description"],
                        version=template_data["version"],
                        model=template_data["model"],
                        temperature=template_data["temperature"],
                        max_tokens=template_data["max_tokens"],
                        active=template_data["active"]
                    )
                    db.add(new_template)
                    inserted_count += 1

        # Commit all changes
        db.commit()

        print(f"\n✅ Initialization completed successfully!")
        print(f"   - Inserted: {inserted_count} new templates")
        print(f"   - Updated:  {updated_count} existing templates")
        print(f"   - Total:    {inserted_count + updated_count} templates processed")

        return True

    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


def verify_templates():
    """Verify that all templates were initialized correctly"""
    db: Session = next(get_db())

    try:
        templates = db.query(PromptTemplate).filter(PromptTemplate.active == True).all()

        print(f"\n📊 Verification Results:")
        print(f"   Total active templates in DB: {len(templates)}")

        if len(templates) == 0:
            print("   ⚠️  WARNING: No templates found in database!")
            return False

        # Group by category for display
        by_category = {}
        for template in templates:
            if template.category not in by_category:
                by_category[template.category] = []
            by_category[template.category].append({
                'action': template.action,
                'model': template.model,
                'version': template.version
            })

        print("\n   Templates by category:")
        for category, actions in sorted(by_category.items()):
            print(f"\n   {category}:")
            for action_data in sorted(actions, key=lambda x: x['action']):
                print(f"     - {action_data['action']} (v{action_data['version']}, {action_data['model']})")

        # Check if we have the expected number of templates
        expected_count = sum(len(actions) for actions in TEMPLATES.values())
        if len(templates) >= expected_count:
            print(f"\n   ✅ All {expected_count} expected templates are present")
            return True
        else:
            print(f"\n   ⚠️  Expected {expected_count} templates, but found {len(templates)}")
            return False

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Prompt Template Initialization Script")
    print("=" * 60)
    print("This script will load/update all production prompt templates")
    print("=" * 60 + "\n")

    if init_prompt_templates():
        if verify_templates():
            print("\n🎉 Initialization and verification completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Templates loaded but verification has warnings!")
            sys.exit(1)
    else:
        print("\n💥 Initialization failed!")
        sys.exit(1)

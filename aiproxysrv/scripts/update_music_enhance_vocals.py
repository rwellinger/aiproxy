#!/usr/bin/env python3
"""
Update script for music/enhance prompt template
Updates the Pre-Condition and Post-Condition to improve vocal gender recognition in Mureka.
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.orm import Session

from db.database import get_db
from db.models import PromptTemplate


# Updated music/enhance template configuration
MUSIC_ENHANCE_TEMPLATE = {
    "category": "music",
    "action": "enhance",
    "pre_condition": """You are a professional Mureka or Suno music style prompt enhancer. Your task is to refine the input text into an ideal prompt by:
• Including the specified instruments
• Keeping the prompt concise, with a maximum of 400 characters
• Describing without using names of bands or singers
• Respecting the copyrights terms of Mureka/Suno
• CRITICAL: If vocals are mentioned, make them the FIRST element in your output and add descriptive adjectives (e.g., "strong male vocals", "powerful female voice", "energetic male singer")""",
    "post_condition": """Only output the enhanced prompt.

CRITICAL VOCAL HANDLING:
1. ALWAYS place the vocal description at the very beginning of the output prompt
2. ALWAYS add a descriptive adjective to vocals (e.g., "strong **male vocals**", "powerful **male voice**", "energetic **male vocals**", "smooth **female vocals**")
3. If the input mentions vocals, mention them at least TWICE in the output (beginning + middle/end)
4. ALWAYS wrap vocal descriptions in Markdown bold (**...**)

Examples:
  - Input: "male vocals" → Output: "Strong **male vocals** lead this energetic pop-rock track... driven by powerful **male voice**"
  - Input: "female vocals" → Output: "Smooth **female vocals** soar over... featuring expressive **female voice**"
  - Input: "männlicher Gesang" → Output: "Kraftvoller **männlicher Gesang** führt... mit energischem **männlichem Gesang**"

IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English).

Do not include labels, explanations, comments, or any other formatting in your output.""",
    "description": "Enhances music style prompts for Mureka/Suno with improved vocal gender handling",
    "version": "2.0",
}


def update_music_enhance_template():
    """Update the music/enhance template in the database"""
    db: Session = next(get_db())

    try:
        # Check if template exists
        existing = (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.category == MUSIC_ENHANCE_TEMPLATE["category"],
                PromptTemplate.action == MUSIC_ENHANCE_TEMPLATE["action"],
            )
            .first()
        )

        if not existing:
            print("\n❌ Template 'music/enhance' not found in database!")
            print("   Please run seed_prompts.py first to create the template.")
            return False

        print(f"Template 'music/enhance' found (ID: {existing.id}), updating...")
        print("\n📋 Current values:")
        print(f"   Version: {existing.version}")
        print(f"   Model: {existing.model}")
        print(f"   Temperature: {existing.temperature}")
        print(f"   Max tokens: {existing.max_tokens}")
        print(f"   Pre-condition length: {len(existing.pre_condition)} chars")
        print(f"   Post-condition length: {len(existing.post_condition)} chars")

        # Update template (preserve model, temperature, max_tokens)
        existing.pre_condition = MUSIC_ENHANCE_TEMPLATE["pre_condition"]
        existing.post_condition = MUSIC_ENHANCE_TEMPLATE["post_condition"]
        existing.description = MUSIC_ENHANCE_TEMPLATE["description"]
        existing.version = MUSIC_ENHANCE_TEMPLATE["version"]
        existing.active = True

        # Commit the changes
        db.commit()

        print("\n✅ Music enhance template successfully updated!")
        print(f"   Category/Action: {MUSIC_ENHANCE_TEMPLATE['category']}/{MUSIC_ENHANCE_TEMPLATE['action']}")
        print(f"   Version: {existing.version} → {MUSIC_ENHANCE_TEMPLATE['version']}")
        print(f"   Pre-condition: {len(MUSIC_ENHANCE_TEMPLATE['pre_condition'])} chars")
        print(f"   Post-condition: {len(MUSIC_ENHANCE_TEMPLATE['post_condition'])} chars")
        print(f"   Description: {MUSIC_ENHANCE_TEMPLATE['description']}")

        return True

    except Exception as e:
        print(f"\n❌ Error updating music enhance template: {str(e)}")
        db.rollback()
        return False

    finally:
        db.close()


def verify_template():
    """Verify that the template was updated correctly"""
    db: Session = next(get_db())

    try:
        template = (
            db.query(PromptTemplate)
            .filter(PromptTemplate.category == "music", PromptTemplate.action == "enhance", PromptTemplate.active)
            .first()
        )

        if template:
            print("\n📊 Verification successful:")
            print(f"   Template ID: {template.id}")
            print(f"   Category/Action: {template.category}/{template.action}")
            print(f"   Version: {template.version}")
            print(f"   Model: {template.model}")
            print(f"   Temperature: {template.temperature}")
            print(f"   Max tokens: {template.max_tokens}")
            print(f"   Pre-condition preview: {template.pre_condition[:100]}...")
            print(f"   Post-condition preview: {template.post_condition[:100]}...")
            print(f"   Active: {template.active}")
            return True
        else:
            print("\n❌ Verification failed: Template not found in database")
            return False

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("🎵 Updating music/enhance prompt template for improved vocal handling...")

    if update_music_enhance_template():
        if verify_template():
            print("\n🎉 Music enhance template update completed successfully!")
            print("\n💡 Changes will be immediately available (no restart required)")
        else:
            print("\n⚠️  Template updated but verification failed!")
            sys.exit(1)
    else:
        print("\n💥 Failed to update music enhance template!")
        sys.exit(1)

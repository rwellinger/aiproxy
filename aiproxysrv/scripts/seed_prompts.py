#!/usr/bin/env python3
"""
Seeding script for prompt templates.
Exported from Dev-DB on 2025-10-17.
This script seeds the database with the current production prompt templates.

Usage:
    python scripts/seed_prompts.py
"""

import os
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.orm import Session

from db.database import get_db
from db.models import PromptTemplate


# Current production templates from Dev-DB (2025-10-17)
TEMPLATES = {
    "image": {
        "enhance": {
            "pre_condition": """You are a professional DALL-E 3 prompt enhancer. Create detailed, vivid prompts optimized for image generation.

Guidelines:
- Describe visual elements with precision (composition, lighting, colors, mood)
- Include artistic style references when relevant (e.g., "photorealistic", "watercolor", "3D render")
- Avoid any content violating DALL-E 3 usage policies
- Keep prompts concise but descriptive (100-150 words)
- Use the input as creative inspiration

Answer in the same language as the input text.""",
            "post_condition": "Return only the enhanced prompt. IMPORTANT: Keep the same language as input (German → German, English → English). No labels, explanations, or meta-commentary. Single continuous paragraph.",
            "description": "Enhances general image generation prompts for DALL-E 3",
            "version": "5.0",
            "model": "gpt-oss:20b",
            "temperature": 0.8,
            "max_tokens": 150,
            "active": True,
        },
        "enhance-cover": {
            "pre_condition": """You are a DALL-E 3 prompt enhancer specialized in album/song cover artwork with text rendering.

CRITICAL TEXT-RENDERING RULES:
- When text elements are specified, include them with EXACT wording in quotes
- Add explicit rendering instructions: "PROMINENTLY featuring the text", "large clear readable letters"
- Specify text placement: "at the top", "centered", "at the bottom"
- Emphasize legibility: "perfectly legible professional typography", "sharp text rendering"

Visual Design:
- Describe cover composition, color palette, mood
- Include artistic style (e.g., "album cover design", "minimalist", "vibrant")
- Balance text prominence with visual appeal

Answer in the same language as the input text.""",
            "post_condition": """Return only the enhanced prompt.

IMPORTANT:
- Preserve all specified text elements with exact wording in quotes
- Include explicit text rendering instructions for each text element
- Keep same language as input (German → German, English → English)
- No labels, explanations, or comments
- Single continuous paragraph

Example format:
"Album cover design PROMINENTLY featuring the text 'Song Title' in large, bold, readable letters at the top, and 'by Artist Name' in elegant smaller professional typography at the bottom. [visual description]. Text must be perfectly legible and sharp.""",
            "description": "Enhances prompts for album covers with optimized text rendering",
            "version": "1.0",
            "model": "gpt-oss:20b",
            "temperature": 0.7,
            "max_tokens": 200,
            "active": True,
        },
        "translate": {
            "pre_condition": "You are a professional English translator. Your task is to translate the provided image prompt into clear and concise language optimized for DALL-E 3. Use only words permitted in a DALL-E 3 prompt.",
            "post_condition": "Only respond with the translation.",
            "description": "Translates image prompts to English",
            "version": "2.0",
            "model": "gpt-oss:20b",
            "temperature": 0.5,
            "max_tokens": 256,
            "active": True,
        },
    },
    "lyrics": {
        "extend-section": {
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
            "active": True,
        },
        "generate": {
            "pre_condition": """You are a professional song lyricist and songwriter. Your task is to completely write the given song idea with fresh perspectives while keeping similar themes. Feel free to:
- Use metaphors and imagery
- Explore angles on the same topic
- Vary the rhythm and structure
- Add creative wordplay
- Make the phrases fluent

The new lyric should feel like a new take on the same emotional core.""",
            "post_condition": """Only output completely original lyrics with each section as a single paragraph. Ensure all content is your own creation and not copied from existing songs.

IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English).

FORMAT REQUIREMENT: Start each section with its label in Markdown bold format (**LABEL**) on its own line, followed by the lyrics text. Use these exact label formats:
  - **INTRO**
  - **VERSE1**, **VERSE2**, etc.
  - **PRE-CHORUS**
  - **CHORUS**
  - **BRIDGE**
  - **OUTRO**

  Example format:
  **INTRO**
  First lines of intro here...

  **VERSE1**
  First verse lyrics here...

  **CHORUS**
  Chorus lyrics here...

Do not include any other explanations, comments, or metadata in your output.""",
            "description": "Generates song lyrics from input text",
            "version": "2.8",
            "model": "gpt-oss:20b",
            "temperature": 0.7,
            "max_tokens": 2048,
            "active": True,
        },
        "improve-section": {
            "pre_condition": """You are a professional song lyricist and songwriter. Your task is to improve the given song section while maintaining its core message and style. Consider:
- Rhyme scheme and rhythm
- Imagery and metaphors
- Emotional impact
- Word choice and clarity
- Flow and pacing
- Fluent language

Keep the same general length and structure. Only improve the quality, do not change the fundamental meaning or add new concepts.""",
            "post_condition": 'Return ONLY the improved section text as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name (like "Verse1:") in your output. Keep all lines together as one continuous block of text.',
            "description": "Improves a specific lyric section while maintaining context and style",
            "version": "1.4",
            "model": "gpt-oss:20b",
            "temperature": 0.7,
            "max_tokens": 256,
            "active": True,
        },
        "rewrite-section": {
            "pre_condition": """You are a professional song lyricist and songwriter. Your task is to completely rewrite the given song section with fresh perspectives while keeping similar themes. Feel free to:
- Use different metaphors and imagery
- Change the rhyme scheme
- Explore new angles on the same topic
- Vary the rhythm and structure
- Add creative wordplay
- Fluent language

The rewritten section should feel like a new take on the same emotional core.""",
            "post_condition": "Return ONLY the rewritten section text as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name in your output. Keep all lines together as one continuous block of text.",
            "description": "Completely rewrites a lyric section with fresh creative perspectives",
            "version": "1.7",
            "model": "gpt-oss:20b",
            "temperature": 0.8,
            "max_tokens": 256,
            "active": True,
        },
        "translate": {
            "pre_condition": """You are a professional native English lyricist and songwriter. Your task is to fully translate the provided song lyrics. You may:
* Use different metaphors and imagery
* Adjust the rhythm and structure
* Employ fluent and natural English expressions
Ensure the translated lyrics convey the original meaning while sounding as though crafted by an English songwriter for a global audience.""",
            "post_condition": "Only output the translated lyrics. Do not include explanations or comments in your output.",
            "description": "Translates lyrics to British English",
            "version": "2.0",
            "model": "gpt-oss:20b",
            "temperature": 0.5,
            "max_tokens": 2048,
            "active": True,
        },
        "optimize-phrasing": {
            "pre_condition": """You are a professional music lyricist. Your task is to reformat the given lyrics into short, musical phrases (4-8 words per line) optimized for AI music generation.

- Preserve the exact content and meaning
- Only change line breaks for better musical phrasing
- Allow for natural pauses, breathing, and emotional expression
- If section labels (**VERSE1**, **CHORUS**, etc.) are present, preserve them""",
            "post_condition": "Return ONLY the reformatted lyrics. Keep the same language as input. Preserve section labels if present. No explanations or comments.",
            "description": "Optimizes lyric phrasing for music generation (4-8 words per line)",
            "version": "1.0",
            "model": "gpt-oss:20b",
            "temperature": 0.5,
            "max_tokens": 2048,
            "active": True,
        },
    },
    "music": {
        "enhance": {
            "pre_condition": """You are a professional music style prompt enhancer for Mureka and Suno AI.
Refine the input into an ideal prompt by:
  • Describing genre and subgenre precisely (e.g., "melodic death metal", "synthwave pop")
  • Including mood and emotional quality (e.g., "melancholic", "uplifting", "dark")
  • Specifying 3-4 main instruments and arrangement details
  • Mentioning production style or era if relevant (e.g., "80s production", "lo-fi", "polished modern mix")
  • Maximum 400 characters, concise and clear
  • NO band/artist names (copyright compliance)
  • Same language as input (German → German, English → English)""",
            "post_condition": """Only output the enhanced prompt.

AVOID these verbs (interpreted as audio effects):
  • "echo", "fade", "distort", "layer", "compress", "saturate"

SAFE verbs for describing music:
  • drive, build, anchor, feature, center, blend, flow

DO NOT:
  • Include vocal descriptions (APIs handle this separately)
  • Use Markdown formatting
  • Add labels, explanations, or comments
  • Exceed 1000 characters total

Examples:
    - Input: "electronic music with guitar" → Output: "Upbeat electronic techno with driving synths, distorted electric guitar riffs, punchy drums. Modern polished production."
    - Input: "traurige Ballade" → Output: "Melancholische Pop-Ballade mit Klavier, sanften Streichern, subtilen Drums. Emotionale, intime Stimmung.\"""",
            "description": "Enhances music style prompts for Mureka and Suno (optimized for genre, mood, instruments, production)",
            "version": "4.0",
            "model": "gpt-oss:20b",
            "temperature": 0.9,
            "max_tokens": 512,
            "active": True,
        },
        "translate": {
            "pre_condition": "Translate this music style description to english",
            "post_condition": "Only respond with the translation.",
            "description": "Translates music style descriptions to English",
            "version": "1.7",
            "model": "gpt-oss:20b",
            "temperature": 0.5,
            "max_tokens": 512,
            "active": True,
        },
    },
    "titel": {
        "generate": {
            "pre_condition": """Generate a short, creative, and engaging title in the same language as the input text. The title should:
  - Capture the main subject, theme, or essence described
  - Be memorable and impactful
  - Match the style and context of the content (visual for images, artistic for songs/lyrics)
  - Be concise (2-8 words) and suitable for the intended medium
  - Avoid using commas, colons, or other punctuation marks
  - Feel natural and relevant to the given input""",
            "post_condition": "Respond only with the title, maximum 50 characters. Do not include any explanations, notes, or introductions.",
            "description": "Generates song titles from various inputs (title, lyrics, style, or default)",
            "version": "3.4",
            "model": "llama3.2:3b",
            "temperature": 0.7,
            "max_tokens": 20,
            "active": True,
        },
    },
}


def seed_prompt_templates():
    """Seed the database with current prompt templates"""
    db: Session = next(get_db())

    try:
        inserted_count = 0
        updated_count = 0

        print("Starting prompt template seeding...\n")

        for category, actions in TEMPLATES.items():
            print(f"Processing category: {category}")

            for action, template_data in actions.items():
                print(f"  Processing action: {action}")

                # Check if template already exists
                existing = (
                    db.query(PromptTemplate)
                    .filter(PromptTemplate.category == category, PromptTemplate.action == action)
                    .first()
                )

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
                    print("    Creating new template...")
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
                        active=template_data["active"],
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
        import traceback

        traceback.print_exc()
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

        if len(templates) == 0:
            print("   ⚠️  WARNING: No templates found in database!")
            return False

        # Group by category for display
        by_category = {}
        for template in templates:
            if template.category not in by_category:
                by_category[template.category] = []
            by_category[template.category].append(
                {"action": template.action, "model": template.model, "version": template.version}
            )

        print("\n   Templates by category:")
        for category, actions in sorted(by_category.items()):
            print(f"\n   {category}:")
            for action_data in sorted(actions, key=lambda x: x["action"]):
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
    print("🌱 Prompt Template Seeding Script")
    print("=" * 60)
    print("This script will seed/update all prompt templates")
    print("=" * 60 + "\n")

    if seed_prompt_templates():
        if verify_templates():
            print("\n🎉 Seeding and verification completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Templates seeded but verification has warnings!")
            sys.exit(1)
    else:
        print("\n💥 Seeding failed!")
        sys.exit(1)

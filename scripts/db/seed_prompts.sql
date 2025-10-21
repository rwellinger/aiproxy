-- ============================================================
-- Prompt Templates Seeding Script
-- ============================================================
-- Exported from Dev-DB on 2025-10-17
-- This script seeds/updates all production prompt templates
--
-- Usage (PostgreSQL):
--   psql -h localhost -U aiuser -d aiproxy -f seed_prompts.sql
--
-- Usage (Docker):
--   cat seed_prompts.sql | docker exec -i mac_ki_service-postgres-1 psql -U aiuser -d aiproxy
--
-- ============================================================

BEGIN;

-- ============================================================
-- Ensure UNIQUE constraint exists (idempotent)
-- ============================================================
DO $$
BEGIN
    -- Check if constraint exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_prompt_category_action'
    ) THEN
        -- Create constraint if missing
        ALTER TABLE prompt_templates
        ADD CONSTRAINT uq_prompt_category_action UNIQUE (category, action);
        RAISE NOTICE 'Created UNIQUE constraint uq_prompt_category_action';
    ELSE
        RAISE NOTICE 'UNIQUE constraint uq_prompt_category_action already exists';
    END IF;
END $$;

-- Helper function for upsert operations
CREATE OR REPLACE FUNCTION upsert_prompt_template(
    p_category VARCHAR,
    p_action VARCHAR,
    p_pre_condition TEXT,
    p_post_condition TEXT,
    p_description TEXT,
    p_version VARCHAR,
    p_model VARCHAR,
    p_temperature FLOAT,
    p_max_tokens INTEGER,
    p_active BOOLEAN
) RETURNS VOID AS $$
BEGIN
    INSERT INTO prompt_templates (
        category, action, pre_condition, post_condition, description,
        version, model, temperature, max_tokens, active,
        created_at, updated_at
    ) VALUES (
        p_category, p_action, p_pre_condition, p_post_condition, p_description,
        p_version, p_model, p_temperature, p_max_tokens, p_active,
        NOW(), NOW()
    )
    ON CONFLICT (category, action) DO UPDATE SET
        pre_condition = EXCLUDED.pre_condition,
        post_condition = EXCLUDED.post_condition,
        description = EXCLUDED.description,
        version = EXCLUDED.version,
        model = EXCLUDED.model,
        temperature = EXCLUDED.temperature,
        max_tokens = EXCLUDED.max_tokens,
        active = EXCLUDED.active,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- IMAGE TEMPLATES
-- ============================================================

-- image/enhance (v6.0)
SELECT upsert_prompt_template(
    'image',
    'enhance',
    'You are a professional DALL-E 3 prompt enhancer. Create detailed, vivid prompts optimized for image generation.

IMPORTANT: Always respond in English - DALL-E 3 works best with English prompts.

Guidelines:
- Describe visual elements with precision (composition, lighting, colors, mood, perspective)
- Include artistic style references when relevant (e.g., "photorealistic", "watercolor painting", "3D render", "digital art")
- Specify composition details (e.g., "close-up", "wide-angle", "centered", "rule of thirds")
- Add atmospheric elements (lighting, weather, time of day)
- Keep prompts concise but descriptive (maximum 800 characters)
- Avoid content violating DALL-E 3 usage policies (no violence, explicit content, copyrighted characters)
- Use the input as creative inspiration and expand it with visual details',
    'Return only the enhanced English prompt.

DO NOT:
- Use labels, explanations, or meta-commentary
- Include multiple paragraphs - single continuous paragraph only
- Exceed 800 characters

Examples:
Input: "sunset over mountains"
Output: "Breathtaking sunset over snow-capped mountain peaks, golden hour lighting casting warm orange and pink hues across dramatic clouds, wide-angle landscape composition, photorealistic rendering with rich color gradients and atmospheric perspective"

Input: "futuristic city"
Output: "Sprawling futuristic metropolis with towering glass skyscrapers, neon lights reflecting on wet streets, flying vehicles in the distance, cyberpunk aesthetic, moody blue and purple lighting, cinematic wide shot, highly detailed digital art"',
    'Enhances image generation prompts for DALL-E 3 (always outputs English)',
    '6.0',
    'gpt-oss:20b',
    0.8,
    200,
    true
);

-- image/enhance-cover (v1.0)
SELECT upsert_prompt_template(
    'image',
    'enhance-cover',
    'You are a DALL-E 3 prompt enhancer specialized in song artwork with text rendering.

CRITICAL TEXT-RENDERING RULES:
- When text elements are specified, include them with EXACT wording in quotes
- Add explicit rendering instructions: "PROMINENTLY featuring the text", "large clear readable letters"
- Specify text placement: "at the top", "centered", "at the bottom"
- Emphasize legibility: "perfectly legible professional typography", "sharp text rendering"
- IMPORTANT: Add "NO other text elements" or "ONLY these specified text elements" to prevent random text generation

Visual Design:
- Describe artwork composition, color palette, mood
- Include artistic style (e.g., "digital art", "minimalist", "vibrant", "illustration", "photorealistic")
- DO NOT use terms like "cover", "album", "CD" - just describe the visual composition
- Balance text prominence with visual appeal

Answer in the same language as the input text.',
    'Return only the enhanced prompt.

IMPORTANT:
- Preserve all specified text elements with exact wording in quotes
- Include explicit text rendering instructions for each text element
- Add "NO other text elements" or "ONLY these specified texts" at the end to prevent random text generation
- DO NOT use "cover", "album", "CD" or similar terms - just describe the artwork
- Keep same language as input (German → German, English → English)
- No labels, explanations, or comments
- Single continuous paragraph

Example format:
"Digital artwork PROMINENTLY featuring the text ''Song Title'' in large, bold, readable letters at the top, and ''by Artist Name'' in elegant smaller professional typography at the bottom. [visual description]. Text must be perfectly legible and sharp. NO other text elements."',
    'Enhances prompts for song artwork with optimized text rendering',
    '1.0',
    'gpt-oss:20b',
    0.7,
    200,
    true
);

-- image/translate (v3.0)
SELECT upsert_prompt_template(
    'image',
    'translate',
    'You are a native English speaker translating image prompts for DALL-E 3. Your task is to translate the provided text into natural, idiomatic English.

Guidelines:
- Use native English expressions and phrasing (not literal word-for-word translation)
- Preserve the visual intent and creative direction
- Adapt idioms and cultural references to English equivalents when necessary
- Use vocabulary that works well with DALL-E 3 (clear, descriptive visual terms)
- Avoid content violating DALL-E 3 usage policies',
    'Only respond with the natural English translation. No explanations or comments.

Examples:
Input (German): "Ein gemütlicher Winterabend mit Schnee"
Output: "A cozy winter evening with snow"

Input (German): "Sonnenuntergang am Meer, traumhaft schön"
Output: "Stunning sunset over the ocean"

Input (German): "Futuristische Stadt bei Nacht mit vielen Lichtern"
Output: "Futuristic city at night with bright lights"',
    'Translates image prompts to natural, idiomatic English for DALL-E 3',
    '3.0',
    'gpt-oss:20b',
    0.5,
    256,
    true
);

-- ============================================================
-- LYRICS TEMPLATES
-- ============================================================

-- lyrics/extend-section (v1.3)
SELECT upsert_prompt_template(
    'lyrics',
    'extend-section',
    'You are a professional song lyricist. Your task is to extend the given song section by adding more lines. The extension should:
- Match the existing rhyme scheme and rhythm
- Continue the thematic development
- Maintain consistent imagery and tone
- Flow naturally from the existing content
- Add depth without being repetitive

Build upon what is already there to create a longer, more developed section.',
    'Return the COMPLETE extended section (original + new lines) as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name in your output. Keep all lines together as one continuous block of text.',
    'Extends a lyric section by adding more lines that match style and theme',
    '1.3',
    'gpt-oss:20b',
    0.7,
    512,
    true
);

-- lyrics/generate (v2.8)
SELECT upsert_prompt_template(
    'lyrics',
    'generate',
    'You are a professional song lyricist and songwriter. Your task is to completely write the given song idea with fresh perspectives while keeping similar themes. Feel free to:
- Use metaphors and imagery
- Explore angles on the same topic
- Vary the rhythm and structure
- Add creative wordplay
- Make the phrases fluent

The new lyric should feel like a new take on the same emotional core.',
    'Only output completely original lyrics with each section as a single paragraph. Ensure all content is your own creation and not copied from existing songs.

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

Do not include any other explanations, comments, or metadata in your output.',
    'Generates song lyrics from input text',
    '2.8',
    'gpt-oss:20b',
    0.7,
    2048,
    true
);

-- lyrics/improve-section (v1.4)
SELECT upsert_prompt_template(
    'lyrics',
    'improve-section',
    'You are a professional song lyricist and songwriter. Your task is to improve the given song section while maintaining its core message and style. Consider:
- Rhyme scheme and rhythm
- Imagery and metaphors
- Emotional impact
- Word choice and clarity
- Flow and pacing
- Fluent language

Keep the same general length and structure. Only improve the quality, do not change the fundamental meaning or add new concepts.',
    'Return ONLY the improved section text as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name (like "Verse1:") in your output. Keep all lines together as one continuous block of text.',
    'Improves a specific lyric section while maintaining context and style',
    '1.4',
    'gpt-oss:20b',
    0.7,
    256,
    true
);

-- lyrics/rewrite-section (v1.7)
SELECT upsert_prompt_template(
    'lyrics',
    'rewrite-section',
    'You are a professional song lyricist and songwriter. Your task is to completely rewrite the given song section with fresh perspectives while keeping similar themes. Feel free to:
- Use different metaphors and imagery
- Change the rhyme scheme
- Explore new angles on the same topic
- Vary the rhythm and structure
- Add creative wordplay
- Fluent language

The rewritten section should feel like a new take on the same emotional core.',
    'Return ONLY the rewritten section text as a SINGLE paragraph without blank lines. IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English). Do not include labels, explanations, comments, or the section name in your output. Keep all lines together as one continuous block of text.',
    'Completely rewrites a lyric section with fresh creative perspectives',
    '1.7',
    'gpt-oss:20b',
    0.8,
    256,
    true
);

-- lyrics/translate (v3.0)
SELECT upsert_prompt_template(
    'lyrics',
    'translate',
    'You are a professional native English lyricist and songwriter. Your task is to translate the provided song lyrics into natural, fluent English optimized for singing.

Guidelines:
- Use natural English expressions (not literal word-for-word translation)
- Adapt idioms and cultural references to English equivalents
- Optimize line breaks for singability: 4-8 words per line
- Include natural breathing points and pauses between phrases
- Try to preserve or improve the rhythm and flow
- Maintain the emotional tone and imagery of the original
- Ensure the translation sounds like it was written by a native English songwriter
- IMPORTANT: Preserve all section labels exactly as they appear (e.g., **INTRO**, **VERSE1**, **CHORUS**, **BRIDGE**, **OUTRO**)
- Keep the song structure completely intact - only translate and optimize phrasing of lyric content',
    'Only output the translated lyrics with optimized phrasing. Do not include explanations or comments.

CRITICAL:
- Preserve section labels exactly: **INTRO**, **VERSE1**, **VERSE2**, **PRE-CHORUS**, **CHORUS**, **BRIDGE**, **OUTRO**
- Only translate the actual lyric text within each section
- Break lines into singable phrases (4-8 words per line)
- Allow for natural breathing points
- Maintain blank lines between sections if present

Example:
Input (German):
**VERSE1**
Ich vermisse dich so sehr, ohne dich ist alles leer

**CHORUS**
Du bist mein Licht in dunkler Nacht, hast mich zum Lachen gebracht

Output (English):
**VERSE1**
I miss you more each day
Without you I''ve lost my way

**CHORUS**
You are my light
In darkest night
You made me smile
You made things right',
    'Translates lyrics to natural English with optimized phrasing for singability (4-8 words/line, breathing points)',
    '3.0',
    'gpt-oss:20b',
    0.5,
    2048,
    true
);

-- lyrics/optimize-phrasing (v1.0)
SELECT upsert_prompt_template(
    'lyrics',
    'optimize-phrasing',
    'You are a professional music lyricist. Your task is to reformat the given lyrics into short, musical phrases (4-8 words per line) optimized for AI music generation.

- Preserve the exact content and meaning
- Only change line breaks for better musical phrasing
- Allow for natural pauses, breathing, and emotional expression
- If section labels (**VERSE1**, **CHORUS**, etc.) are present, preserve them',
    'Return ONLY the reformatted lyrics. Keep the same language as input. Preserve section labels if present. No explanations or comments.',
    'Optimizes lyric phrasing for music generation (4-8 words per line)',
    '1.0',
    'gpt-oss:20b',
    0.5,
    2048,
    true
);

-- ============================================================
-- MUSIC TEMPLATES
-- ============================================================

-- music/enhance (v4.0)
SELECT upsert_prompt_template(
    'music',
    'enhance',
    'You are a professional music style prompt enhancer for Mureka and Suno AI.
Refine the input into an ideal prompt by:
  • Describing genre and subgenre precisely (e.g., "melodic death metal", "synthwave pop")
  • Including mood and emotional quality (e.g., "melancholic", "uplifting", "dark")
  • Specifying 3-4 main instruments and arrangement details
  • Mentioning production style or era if relevant (e.g., "80s production", "lo-fi", "polished modern mix")
  • Maximum 400 characters, concise and clear
  • NO band/artist names (copyright compliance)
  • Same language as input (German → German, English → English)',
    'Only output the enhanced prompt.

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
    - Input: "traurige Ballade" → Output: "Melancholische Pop-Ballade mit Klavier, sanften Streichern, subtilen Drums. Emotionale, intime Stimmung."',
    'Enhances music style prompts for Mureka and Suno (optimized for genre, mood, instruments, production)',
    '4.0',
    'gpt-oss:20b',
    0.9,
    512,
    true
);

-- music/translate (v2.0)
SELECT upsert_prompt_template(
    'music',
    'translate',
    'You are a professional music expert translating music style descriptions to English.

Guidelines:
- Use natural, idiomatic English (not literal word-for-word translation)
- Preserve music terminology and genre names accurately
- Use standard English music terms (e.g., "synths" for synthesizers, "drums" not "percussion")
- Keep genre names in English convention (e.g., "Death Metal" not "Todesmetall")
- Maintain technical accuracy for instruments, production styles, and moods
- Keep the description concise and clear',
    'Only respond with the natural English translation. No explanations or comments.

Examples:
Input (German): "Melancholische Pop-Ballade mit Klavier und Streichern"
Output: "Melancholic pop ballad with piano and strings"

Input (German): "Schneller Metal mit verzerrten Gitarren und aggressiven Drums"
Output: "Fast metal with distorted guitars and aggressive drums"

Input (German): "Elektronische Tanzmusik mit treibenden Synths, moderne Produktion"
Output: "Electronic dance music with driving synths, modern production"',
    'Translates music style descriptions to natural English with accurate terminology',
    '2.0',
    'gpt-oss:20b',
    0.5,
    512,
    true
);

-- ============================================================
-- TITEL TEMPLATES
-- ============================================================

-- titel/generate (v4.0)
SELECT upsert_prompt_template(
    'titel',
    'generate',
    'Generate a short, creative, and engaging title in the same language as the input text. The title should:
  - Capture the main subject, theme, or essence described
  - Be memorable and impactful
  - Match the style and context of the content (visual for images, artistic for songs/lyrics)
  - Be very concise (2-5 words maximum) - optimized for cover image text generation
  - Use only simple, common words that render well in images
  - Avoid ALL punctuation marks (no commas, colons, apostrophes, quotes, hyphens, dashes)
  - Use only alphanumeric characters and spaces
  - Feel natural and relevant to the given input',
    'Respond only with the title, maximum 35 characters. Absolutely NO punctuation marks (no apostrophes, no quotes, no hyphens, no special characters). Do not include any explanations, notes, or introductions.',
    'Generates short song titles optimized for cover image text generation (2-5 words, max 35 chars, no punctuation)',
    '4.0',
    'llama3.2:3b',
    0.7,
    15,
    true
);

-- ============================================================
-- Cleanup and Statistics
-- ============================================================

-- Drop helper function
DROP FUNCTION IF EXISTS upsert_prompt_template;

-- Show results
DO $$
DECLARE
    total_count INTEGER;
    active_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM prompt_templates;
    SELECT COUNT(*) INTO active_count FROM prompt_templates WHERE active = true;

    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Seeding completed successfully!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Total templates in DB:  %', total_count;
    RAISE NOTICE 'Active templates:       %', active_count;
    RAISE NOTICE '';
    RAISE NOTICE 'Templates by category:';
    RAISE NOTICE '';
END $$;

-- Show templates by category
SELECT
    category,
    action,
    version,
    model,
    CASE WHEN active THEN '✓' ELSE '✗' END as active
FROM prompt_templates
ORDER BY category, action;

COMMIT;

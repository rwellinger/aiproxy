-- ============================================================
-- Suno Enhancer Prompt Template Seeding Script
-- ============================================================
-- Created: 2025-10-26
-- This script adds the Suno-specific music style enhancer template
--
-- Usage (PostgreSQL):
--   psql -h localhost -U aiproxy -d aiproxysrv -f seed_prompts_suno_enhancer.sql
--
-- Usage (Docker):
--   cat seed_prompts_suno_enhancer.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv
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
-- SUNO MUSIC ENHANCER TEMPLATE
-- ============================================================

-- music/enhance-suno (v1.0)
SELECT upsert_prompt_template(
    'music',
    'enhance-suno',
    'You are a professional music style prompt enhancer specialized for Suno AI, optimized for vocal post-processing workflows.

CRITICAL: Suno vocals need to be processed further (editing, mixing, mastering). Your enhanced prompts MUST optimize for clean, workable vocal tracks.

PRIMARY OPTIMIZATION GOALS:
  • Completely dry vocals with NO reverb, NO echo, NO hall effects (critical for post-processing)
  • Stable, consistent tempo throughout the song (no tempo variations)
  • Natural vocal pitch (avoid unnaturally high or processed voices)
  • Direct, unprocessed vocal signal that can be processed later

MUSIC STYLE ENHANCEMENT:
  • Describe genre and subgenre precisely (e.g., "melodic death metal", "synthwave pop")
  • Include mood and emotional quality (e.g., "melancholic", "uplifting", "dark")
  • Specify 3-4 main instruments and arrangement details
  • Mention production style or era if relevant (e.g., "80s production", "lo-fi", "polished modern mix")
  • Maximum 400 characters for style description

VOCAL OPTIMIZATION KEYWORDS TO USE:
  • "dry vocals", "direct vocals", "unprocessed vocals"
  • "stable tempo", "consistent rhythm", "steady beat"
  • "natural voice", "clear vocals"
  • "no reverb", "no echo", "no vocal effects"

AVOID THESE TERMS (create problems for post-processing):
  • ANY mention of reverb, echo, or hall (even "minimal" or "controlled")
  • "tempo variations", "tempo changes", "dynamic tempo"
  • "processed vocals", "vocal effects", "layered vocals"

VOICE GENDER HANDLING:
  • If input contains "male-voice" or "male voice": preserve it, add "natural pitch for male vocals"
  • If input contains "female-voice" or "female voice": preserve it, add "natural pitch for female vocals"
  • Otherwise: gender-neutral enhancement

NO band/artist names (copyright compliance)
Same language as input (German → German, English → English)',
    'Only output the enhanced prompt optimized for Suno AI with post-processing in mind.

CRITICAL LANGUAGE RULE:
  • ALWAYS keep the EXACT same language as the input
  • If input is English → output MUST be English
  • If input is German → output MUST be German
  • NEVER translate or change the language

STRUCTURE:
1. First describe the music style (genre, mood, instruments, production)
2. Then add vocal optimization keywords (dry vocals, stable tempo, natural pitch)
3. Keep total output under 400 characters

CRITICAL RULES:
  • Include "dry vocals" or "direct vocals" or "unprocessed vocals" in the description
  • Include "stable tempo" or "steady beat" or "consistent rhythm"
  • Add "no reverb" or "no echo" or "no vocal effects"
  • NEVER mention reverb, echo, or hall (not even "minimal" or "controlled")
  • NO tempo variation keywords
  • DO NOT use Markdown formatting
  • DO NOT add labels, explanations, or comments

Examples:

Input (English): "electronic music with guitar"
Output (English): "Upbeat electronic techno with driving synths, clean electric guitar riffs, punchy drums. Modern polished production, dry vocals, stable tempo, no reverb, no echo."

Input (English): "rock song with energy, female-voice"
Output (English): "Energetic alternative rock with distorted guitars, powerful drums, bass-driven. Dynamic modern sound, direct female vocals, natural pitch, steady tempo, no vocal effects."

Input (German): "traurige Ballade"
Output (German): "Melancholische Pop-Ballade mit Klavier, sanften Streichern, subtilen Drums. Emotionale, intime Stimmung, trockene Vocals, gleichmäßiges Tempo, kein Hall, kein Echo."',
    'Enhances music style prompts specifically for Suno AI with focus on post-processing optimization (dry vocals, stable tempo, minimal effects)',
    '1.0',
    'gpt-oss:20b',
    0.9,
    512,
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
    suno_template_exists BOOLEAN;
BEGIN
    SELECT COUNT(*) INTO total_count FROM prompt_templates;
    SELECT COUNT(*) INTO active_count FROM prompt_templates WHERE active = true;
    SELECT EXISTS(SELECT 1 FROM prompt_templates WHERE category = 'music' AND action = 'enhance-suno') INTO suno_template_exists;

    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Suno Enhancer Template Seeding completed!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Total templates in DB:  %', total_count;
    RAISE NOTICE 'Active templates:       %', active_count;
    RAISE NOTICE 'Suno template exists:   %', CASE WHEN suno_template_exists THEN 'YES' ELSE 'NO' END;
    RAISE NOTICE '';
END $$;

-- Show Suno template details
SELECT
    category,
    action,
    version,
    model,
    temperature,
    max_tokens,
    CASE WHEN active THEN '✓' ELSE '✗' END as active,
    description
FROM prompt_templates
WHERE category = 'music' AND action = 'enhance-suno';

COMMIT;

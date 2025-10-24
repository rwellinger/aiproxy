-- ============================================================
-- Sketch Description Prompt Templates Seeding Script
-- ============================================================
-- Purpose: AI-assisted generation of release descriptions and tags
-- Usage (PostgreSQL):
--   psql -h localhost -U aiproxy -d aiproxysrv -f seed_sketch_description_prompts.sql
--
-- Usage (Docker):
--   cat seed_sketch_description_prompts.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv
--
-- ============================================================

BEGIN;

-- ============================================================
-- Ensure UNIQUE constraint exists (idempotent)
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_prompt_category_action'
    ) THEN
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
-- DESCRIPTION TEMPLATES
-- ============================================================

-- description/generate-long (v1.0)
SELECT upsert_prompt_template(
    'description',
    'generate-long',
    'You are a professional music marketing copywriter specializing in song release descriptions for streaming platforms and music stores.

Your task is to create an engaging, descriptive text about the song based on the provided lyrics. The description should:
- Capture the emotional essence and themes of the song
- Describe the mood, atmosphere, and story
- Highlight key lyrical elements and imagery
- Appeal to potential listeners and create interest
- Be informative yet concise
- Sound professional and authentic

IMPORTANT: Keep the same language as the input lyrics (if input is German, output must be German; if input is English, output must be English).

Maximum 1000 characters - focus on quality over quantity.',
    'Return ONLY the long description text. No labels, explanations, or meta-commentary.

RULES:
- Same language as input lyrics
- 3-5 sentences describing the song
- Focus on: themes, emotions, mood, story, imagery
- Professional tone suitable for streaming platforms
- Maximum 1000 characters
- No quotation marks around the output

Example (German lyrics → German description):
Input: "**VERSE1** Die Nacht ist dunkel, der Mond scheint hell..."
Output: Ein atmosphärischer Song über die Schönheit der Nacht und die Kraft der Stille. Mit poetischen Bildern von Mondlicht und Schatten entfaltet sich eine Geschichte der inneren Einkehr und Selbstfindung. Die melancholische Stimmung wird durch hoffnungsvolle Momente durchbrochen.

Example (English lyrics → English description):
Input: "**VERSE1** Walking through the empty streets at dawn..."
Output: A reflective journey through solitude and self-discovery. This song paints vivid imagery of urban landscapes at dawn, exploring themes of loneliness, hope, and renewal. The lyrics balance melancholic introspection with optimistic undertones.',
    'Generates long release descriptions from song lyrics (max 1000 chars)',
    '1.0',
    'gpt-oss:20b',
    0.7,
    512,
    true
);

-- description/generate-short (v1.0)
SELECT upsert_prompt_template(
    'description',
    'generate-short',
    'You are a professional music marketing copywriter creating short, impactful song descriptions for platforms with character limits (like social media or compact player displays).

Your task is to condense the provided long description into a concise, punchy summary that:
- Captures the core essence of the song in one sentence
- Maintains the key themes and mood
- Remains engaging and interesting
- Uses vivid, impactful language

IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English).

Maximum 150 characters - every word must count.',
    'Return ONLY the short description (max 150 characters). No labels or explanations.

RULES:
- Same language as input
- ONE concise sentence
- Maximum 150 characters (strict limit)
- Capture core essence: theme + mood
- No quotation marks around output

Examples:

Input (German): "Ein atmosphärischer Song über die Schönheit der Nacht und die Kraft der Stille. Mit poetischen Bildern von Mondlicht und Schatten..."
Output: Poetische Reise durch die Nacht – melancholisch, hoffnungsvoll, atmosphärisch.

Input (English): "A reflective journey through solitude and self-discovery. This song paints vivid imagery of urban landscapes at dawn..."
Output: Dawn-lit reflections on solitude, hope, and urban renewal.',
    'Generates short release descriptions from long descriptions (max 150 chars)',
    '1.0',
    'gpt-oss:20b',
    0.6,
    100,
    true
);

-- description/generate-tags (v1.0)
SELECT upsert_prompt_template(
    'description',
    'generate-tags',
    'You are a music metadata specialist creating tags for song releases on streaming platforms and music stores.

Your task is to generate 10 relevant, searchable tags based on the provided song description. Tags should cover:
- Musical moods and emotions (e.g., melancholic, uplifting, energetic)
- Themes and topics (e.g., love, nature, urban life, self-discovery)
- Atmospheric qualities (e.g., dark, bright, dreamy, intense)
- Contextual usage (e.g., night drive, workout, meditation, party)
- Genre hints if clearly indicated (e.g., electronic, acoustic, cinematic)

IMPORTANT: Keep the same language as the input text (if input is German, output must be German; if input is English, output must be English).

Generate exactly 10 tags that are:
- Relevant and descriptive
- Searchable and commonly used
- Diverse (covering different aspects)
- Concise (1-2 words per tag)',
    'Return ONLY the 10 tags as a comma-separated list. No labels, numbering, or explanations.

RULES:
- Same language as input
- Exactly 10 tags
- Comma-separated format
- 1-2 words per tag
- Diverse coverage: mood, theme, atmosphere, context
- No quotation marks or special formatting

Examples:

Input (German): "Ein atmosphärischer Song über die Schönheit der Nacht und die Kraft der Stille..."
Output: Nacht, Atmosphärisch, Melancholisch, Poetisch, Stille, Mondlicht, Introspektiv, Hoffnungsvoll, Dunkel, Emotional

Input (English): "A reflective journey through solitude and self-discovery. This song paints vivid imagery of urban landscapes..."
Output: Reflective, Solitude, Urban, Dawn, Self-Discovery, Melancholic, Hopeful, Introspective, Atmospheric, Cinematic',
    'Generates 10 searchable release tags from song description',
    '1.0',
    'gpt-oss:20b',
    0.6,
    150,
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
    SELECT COUNT(*) INTO total_count FROM prompt_templates WHERE category = 'description';
    SELECT COUNT(*) INTO active_count FROM prompt_templates WHERE category = 'description' AND active = true;

    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Sketch Description Prompts seeded successfully!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Total description templates:  %', total_count;
    RAISE NOTICE 'Active description templates: %', active_count;
    RAISE NOTICE '';
END $$;

-- Show inserted templates
SELECT
    category,
    action,
    version,
    model,
    CASE WHEN active THEN '✓' ELSE '✗' END as active
FROM prompt_templates
WHERE category = 'description'
ORDER BY action;

COMMIT;

-- SQL Script to create Prompt Templates for Section Editor Feature
-- These templates are used by the ChatService to improve, rewrite, and extend lyric sections
-- Execute this script in your PostgreSQL database

-- 1. Template: lyrics/improve-section
INSERT INTO prompt_templates (
    name,
    category,
    action,
    pre_condition,
    post_condition,
    temperature,
    max_tokens,
    model,
    description,
    is_active
) VALUES (
    'Improve Lyric Section',
    'lyrics',
    'improve-section',
    'You are a professional song lyricist. Your task is to improve the given song section while maintaining its core message and style. Consider:
- Rhyme scheme and rhythm
- Imagery and metaphors
- Emotional impact
- Word choice and clarity
- Flow and pacing

Keep the same general length and structure. Only improve the quality, do not change the fundamental meaning or add new concepts.',
    'Return ONLY the improved section text without any labels, explanations, or comments. Do not include the section name (like "Verse1:") in your output.',
    0.7,
    2048,
    'llama3.2:3b',
    'Improves a specific lyric section while maintaining context and style',
    true
) ON CONFLICT (category, action) DO UPDATE SET
    name = EXCLUDED.name,
    pre_condition = EXCLUDED.pre_condition,
    post_condition = EXCLUDED.post_condition,
    temperature = EXCLUDED.temperature,
    max_tokens = EXCLUDED.max_tokens,
    model = EXCLUDED.model,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active;

-- 2. Template: lyrics/rewrite-section
INSERT INTO prompt_templates (
    name,
    category,
    action,
    pre_condition,
    post_condition,
    temperature,
    max_tokens,
    model,
    description,
    is_active
) VALUES (
    'Rewrite Lyric Section',
    'lyrics',
    'rewrite-section',
    'You are a professional song lyricist. Your task is to completely rewrite the given song section with fresh perspectives while keeping similar themes. Feel free to:
- Use different metaphors and imagery
- Change the rhyme scheme
- Explore new angles on the same topic
- Vary the rhythm and structure
- Add creative wordplay

The rewritten section should feel like a new take on the same emotional core.',
    'Return ONLY the rewritten section text without any labels, explanations, or comments. Do not include the section name in your output.',
    0.8,
    2048,
    'llama3.2:3b',
    'Completely rewrites a lyric section with fresh creative perspectives',
    true
) ON CONFLICT (category, action) DO UPDATE SET
    name = EXCLUDED.name,
    pre_condition = EXCLUDED.pre_condition,
    post_condition = EXCLUDED.post_condition,
    temperature = EXCLUDED.temperature,
    max_tokens = EXCLUDED.max_tokens,
    model = EXCLUDED.model,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active;

-- 3. Template: lyrics/extend-section
INSERT INTO prompt_templates (
    name,
    category,
    action,
    pre_condition,
    post_condition,
    temperature,
    max_tokens,
    model,
    description,
    is_active
) VALUES (
    'Extend Lyric Section',
    'lyrics',
    'extend-section',
    'You are a professional song lyricist. Your task is to extend the given song section by adding more lines. The extension should:
- Match the existing rhyme scheme and rhythm
- Continue the thematic development
- Maintain consistent imagery and tone
- Flow naturally from the existing content
- Add depth without being repetitive

Build upon what is already there to create a longer, more developed section.',
    'Return the COMPLETE extended section (original + new lines) without any labels, explanations, or comments. Do not include the section name in your output.',
    0.7,
    2048,
    'llama3.2:3b',
    'Extends a lyric section by adding more lines that match style and theme',
    true
) ON CONFLICT (category, action) DO UPDATE SET
    name = EXCLUDED.name,
    pre_condition = EXCLUDED.pre_condition,
    post_condition = EXCLUDED.post_condition,
    temperature = EXCLUDED.temperature,
    max_tokens = EXCLUDED.max_tokens,
    model = EXCLUDED.model,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active;

-- Verify the inserts
SELECT name, category, action, model, temperature, max_tokens
FROM prompt_templates
WHERE category = 'lyrics' AND action IN ('improve-section', 'rewrite-section', 'extend-section')
ORDER BY action;

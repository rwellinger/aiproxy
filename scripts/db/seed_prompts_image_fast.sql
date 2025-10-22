-- ============================================================
-- Prompt Templates Seeding Script - Image Fast Enhancement
-- ============================================================
-- Created: 2025-10-22
-- Purpose: Add fast image enhancement template using small Ollama model
--
-- Usage (PostgreSQL):
--   psql -h localhost -U aiproxy -d aiproxysrv -f seed_prompts_image_fast.sql
--
-- Usage (Docker):
--   cat seed_prompts_image_fast.sql | docker exec -i postgres psql -U aiproxy -d aiproxysrv
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

-- ============================================================
-- Ensure helper function exists (idempotent)
-- ============================================================
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
-- IMAGE FAST ENHANCEMENT TEMPLATE
-- ============================================================

-- image/enhance-fast (v1.0)
-- Fast enhancement using small Ollama model (llama3.2:3b)
-- For manual mode where user already selected specific styles
SELECT upsert_prompt_template(
    'image',
    'enhance-fast',
    'You are a DALL-E 3 prompt enhancer. Enhance the user input by adding technical details while staying true to the original subject.

IMPORTANT: Always respond in English - DALL-E 3 works best with English prompts.

RULES:
- Keep the original subject exactly as given
- Add only technical details: style, lighting, composition
- Stay concise - maximum 300 characters
- No explanations or meta-commentary

Technical enhancements:
- Artistic style (photorealistic, digital art, oil painting, etc.)
- Lighting (soft studio lighting, dramatic, natural daylight, etc.)
- Composition (centered portrait, wide-angle, rule of thirds, etc.)
- Rendering (highly detailed, sharp focus, etc.)

DO NOT mention resolution or size.',
    'Return ONLY the enhanced English prompt. No explanations.

RULES:
- Keep the SAME subject - add NO new objects
- Add: style, lighting, composition, rendering
- Single paragraph
- Maximum 300 characters
- No labels

Example:
Input: "a clown"
Output: "A clown character, vibrant costume, expressive face paint, centered portrait, soft studio lighting, digital art"',
    'Fast image prompt enhancement using small Ollama model - for manual style mode',
    '1.0',
    'llama3.2:3b',
    0.5,
    150,
    true
);

-- Update existing image/enhance template to use larger model
-- (Quality mode)
SELECT upsert_prompt_template(
    'image',
    'enhance',
    'You are a professional DALL-E 3 prompt enhancer. Enhance the user input by adding technical and stylistic details while STAYING TRUE to the original subject.

IMPORTANT: Always respond in English - DALL-E 3 works best with English prompts.

CRITICAL RULES:
- PRESERVE the original subject exactly as given - do NOT add new objects, characters, or scene elements
- ONLY enhance with technical details: artistic style, lighting quality, camera angle, composition framing, rendering technique
- If input says "a clown" → output describes ONE clown, not a circus scene
- If input says "sunset" → output describes the sunset itself, not adding mountains/beaches unless mentioned
- Stay minimal and focused on what was actually requested

Technical enhancements to add:
- Artistic style (e.g., "photorealistic", "digital art", "oil painting", "minimalist illustration")
- Lighting quality (e.g., "soft studio lighting", "dramatic side light", "natural daylight")
- Composition (e.g., "centered portrait", "rule of thirds", "wide-angle shot")
- Rendering details (e.g., "highly detailed", "sharp focus", "crisp details")
- Color palette (e.g., "vibrant colors", "muted tones", "high contrast")

DO NOT mention resolution/size - this is handled separately by the API.
Maximum 400 characters - keep it concise and precise.',
    'Return ONLY the enhanced English prompt. No explanations.

STRICT RULES:
- Keep the SAME subject as the input - add NO new objects or characters
- Only add: style, lighting, composition, technical rendering details
- Single continuous paragraph
- Maximum 400 characters
- No labels or meta-commentary

Examples:
Input: "a clown"
Output: "A clown character, vibrant costume, expressive face paint, centered portrait, soft studio lighting, digital art, detailed rendering"

Input: "sunset over mountains"
Output: "Breathtaking sunset over snow-capped mountain peaks, golden hour lighting, warm orange and pink hues, wide-angle landscape, photorealistic, rich color gradients"

Input: "futuristic city"
Output: "Futuristic metropolis with glass skyscrapers, neon lights, flying vehicles, cyberpunk aesthetic, moody blue lighting, cinematic wide shot, highly detailed digital art"',
    'Enhances image generation prompts for DALL-E 3 with minimal hallucination - stays true to input',
    '7.1',
    'llama3.1:70b',
    0.7,
    200,
    true
);

COMMIT;

-- ============================================================
-- Verification Query
-- ============================================================
-- Uncomment to verify the seeded templates:
-- SELECT category, action, model, temperature, max_tokens, active, version
-- FROM prompt_templates
-- WHERE category = 'image' AND action IN ('enhance', 'enhance-fast')
-- ORDER BY action;

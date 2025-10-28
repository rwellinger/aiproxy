"""Prompt Template Processor - Pure business logic for template processing

This module contains core business logic for processing prompt templates.
All functions are pure (no DB, no file system) and 100% unit-testable.

Architecture:
- Uses PromptTemplateFallbackHandler for parameter resolution
- Pure functions only (transformations, string manipulation)
- No database queries (Repository layer handles that)
- No HTTP calls (Controller layer handles that)
"""

from typing import TYPE_CHECKING, Any

from business.prompt_template_fallback_handler import PromptTemplateFallbackHandler
from utils.logger import logger


if TYPE_CHECKING:
    from db.models import PromptTemplate


class PromptTemplateProcessor:
    """
    Pure business logic for prompt template processing.

    All methods are static and pure functions (100% testable without mocks).
    Uses FallbackHandler for parameter resolution with WARNING logging.
    """

    @staticmethod
    def build_prompt(template: "PromptTemplate", user_input: str) -> str:
        """
        Build complete prompt from template and user input.

        Pure function - no side effects, fully unit-testable

        Args:
            template: PromptTemplate instance
            user_input: User's input text

        Returns:
            Complete prompt string combining pre_condition + user_input + post_condition

        Example:
            template = PromptTemplate(
                pre_condition="You are a lyric writer.",
                post_condition="Format as verse-chorus structure."
            )
            prompt = build_prompt(template, "Write about love")
            # Returns:
            # "You are a lyric writer.
            #
            # Write about love
            #
            # Format as verse-chorus structure."
        """
        pre_condition = template.pre_condition or ""
        post_condition = template.post_condition or ""

        # Build the complete prompt with double newlines as separators
        parts = []
        if pre_condition.strip():
            parts.append(pre_condition.strip())
        if user_input.strip():
            parts.append(user_input.strip())
        if post_condition.strip():
            parts.append(post_condition.strip())

        complete_prompt = "\n\n".join(parts)

        logger.debug(
            "Built prompt",
            category=template.category,
            action=template.action,
            template_id=template.id,
            prompt_length=len(complete_prompt),
            has_pre_condition=bool(pre_condition.strip()),
            has_post_condition=bool(post_condition.strip()),
        )

        return complete_prompt

    @staticmethod
    def process_template(template: "PromptTemplate", user_input: str) -> dict[str, Any]:
        """
        Complete template processing: resolve AI parameters and build prompt.

        This is the main entry point for template processing.
        Combines parameter resolution (with fallback handling) and prompt building.

        Pure function - only logs, no other side effects

        Args:
            template: PromptTemplate instance
            user_input: User's input text

        Returns:
            Dict with complete processing result:
            {
                "prompt": str,              # Complete prompt text
                "model": str,               # Resolved model name
                "temperature": float,       # Resolved temperature
                "max_tokens": int,          # Resolved max_tokens
                "fallback_count": int,      # Number of fallbacks used (0-3)
                "fallbacks_used": {         # Which parameters used fallback
                    "model": bool,
                    "temperature": bool,
                    "max_tokens": bool
                }
            }

        Side Effects:
            Logs DEBUG for success, WARNING if fallbacks used (via FallbackHandler)

        Example:
            result = PromptTemplateProcessor.process_template(template, "Write a song")
            if result["fallback_count"] > 0:
                # Alert: Template is incomplete!
            # Use result["prompt"], result["model"], etc. for API call
        """
        # Step 1: Resolve AI parameters (with fallback tracking)
        ai_params = PromptTemplateFallbackHandler.resolve_all_parameters(template, template.category, template.action)

        # Step 2: Build prompt
        prompt = PromptTemplateProcessor.build_prompt(template, user_input)

        # Step 3: Combine everything
        result = {
            "prompt": prompt,
            "model": ai_params["model"],
            "temperature": ai_params["temperature"],
            "max_tokens": ai_params["max_tokens"],
            "fallback_count": ai_params["fallback_count"],
            "fallbacks_used": ai_params["fallbacks_used"],
        }

        logger.info(
            "Processed template",
            category=template.category,
            action=template.action,
            template_id=template.id,
            model=result["model"],
            temperature=result["temperature"],
            max_tokens=result["max_tokens"],
            fallback_count=result["fallback_count"],
            prompt_length=len(prompt),
        )

        return result

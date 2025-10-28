"""
Fallback Handler for Prompt Templates

CRITICAL: This class handles ALL fallback scenarios for prompt templates.
When a template is missing or has invalid parameters, this handler provides
safe defaults AND logs warnings to detect configuration issues.

⚠️ WARNING: Fallback usage indicates a problem:
- Template not found in DB
- Template has NULL/empty required fields
- Template data is corrupted

Production systems should monitor WARNING logs from this handler to detect
configuration issues before they cause user-facing problems.

MONITORING:
- Filter: level:WARNING AND message:FALLBACK
- Alert: If fallback_rate > 5% of requests → Database Problem!
- Dashboard: Track fallback_count per template → Shows corrupted templates
"""

from typing import TYPE_CHECKING, Any

from utils.logger import logger


if TYPE_CHECKING:
    from db.models import PromptTemplate


class PromptTemplateFallbackError(Exception):
    """Raised when fallback cannot provide safe defaults"""

    pass


class FallbackReason:
    """Enum-like class for fallback reasons (for structured logging)"""

    TEMPLATE_NOT_FOUND = "template_not_found"
    MODEL_MISSING = "model_missing"
    MODEL_EMPTY = "model_empty"
    TEMPERATURE_MISSING = "temperature_missing"
    MAX_TOKENS_MISSING = "max_tokens_missing"


class PromptTemplateFallbackHandler:
    """
    Handles fallback scenarios for prompt template parameters.

    ALL fallback usage is logged at WARNING level with context.
    This is NOT normal operation - fallbacks indicate configuration problems.

    Pure functions - no side effects except logging, 100% testable.
    """

    # Default values (centralized for easy modification)
    DEFAULT_MODEL = "llama3.2:3b"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048

    @staticmethod
    def resolve_model(template: "PromptTemplate", category: str, action: str) -> tuple[str, bool]:
        """
        Resolve model with fallback logging.

        Pure function - only logs, no side effects

        Args:
            template: PromptTemplate instance
            category: Template category (for logging context)
            action: Template action (for logging context)

        Returns:
            Tuple of (model_name, used_fallback)
            - model_name: Resolved model (from template or default)
            - used_fallback: True if default was used

        Side Effects:
            Logs WARNING if fallback is used (indicates config problem!)

        Example:
            model, fallback = FallbackHandler.resolve_model(template, "lyrics", "generate")
            if fallback:
                # Alert: Template is corrupted!
        """
        if template.model and template.model.strip():
            logger.debug(
                "Using template model",
                category=category,
                action=action,
                model=template.model,
                template_id=template.id,
            )
            return template.model, False

        # FALLBACK: Log WARNING (not INFO - this is a problem!)
        reason = FallbackReason.MODEL_EMPTY if template.model is not None else FallbackReason.MODEL_MISSING

        logger.warning(
            "FALLBACK: Using default model (template has no model configured)",
            category=category,
            action=action,
            template_id=template.id,
            fallback_model=PromptTemplateFallbackHandler.DEFAULT_MODEL,
            reason=reason,
            template_model_value=template.model,
            # ⚠️ This indicates a configuration problem - template should be fixed in DB!
        )

        return PromptTemplateFallbackHandler.DEFAULT_MODEL, True

    @staticmethod
    def resolve_temperature(template: "PromptTemplate", category: str, action: str) -> tuple[float, bool]:
        """
        Resolve temperature with fallback logging.

        Pure function - only logs, no side effects

        Args:
            template: PromptTemplate instance
            category: Template category (for logging context)
            action: Template action (for logging context)

        Returns:
            Tuple of (temperature, used_fallback)

        Side Effects:
            Logs WARNING if fallback is used
        """
        if template.temperature is not None:
            logger.debug(
                "Using template temperature",
                category=category,
                action=action,
                temperature=template.temperature,
                template_id=template.id,
            )
            return template.temperature, False

        # FALLBACK: Log WARNING
        logger.warning(
            "FALLBACK: Using default temperature (template has no temperature configured)",
            category=category,
            action=action,
            template_id=template.id,
            fallback_temperature=PromptTemplateFallbackHandler.DEFAULT_TEMPERATURE,
            reason=FallbackReason.TEMPERATURE_MISSING,
            # ⚠️ This indicates a configuration problem - template should be fixed in DB!
        )

        return PromptTemplateFallbackHandler.DEFAULT_TEMPERATURE, True

    @staticmethod
    def resolve_max_tokens(template: "PromptTemplate", category: str, action: str) -> tuple[int, bool]:
        """
        Resolve max_tokens with fallback logging.

        Pure function - only logs, no side effects

        Args:
            template: PromptTemplate instance
            category: Template category (for logging context)
            action: Template action (for logging context)

        Returns:
            Tuple of (max_tokens, used_fallback)

        Side Effects:
            Logs WARNING if fallback is used
        """
        if template.max_tokens is not None:
            logger.debug(
                "Using template max_tokens",
                category=category,
                action=action,
                max_tokens=template.max_tokens,
                template_id=template.id,
            )
            return template.max_tokens, False

        # FALLBACK: Log WARNING
        logger.warning(
            "FALLBACK: Using default max_tokens (template has no max_tokens configured)",
            category=category,
            action=action,
            template_id=template.id,
            fallback_max_tokens=PromptTemplateFallbackHandler.DEFAULT_MAX_TOKENS,
            reason=FallbackReason.MAX_TOKENS_MISSING,
            # ⚠️ This indicates a configuration problem - template should be fixed in DB!
        )

        return PromptTemplateFallbackHandler.DEFAULT_MAX_TOKENS, True

    @staticmethod
    def resolve_all_parameters(template: "PromptTemplate", category: str, action: str) -> dict[str, Any]:
        """
        Resolve all AI parameters with comprehensive fallback tracking.

        Pure function - only logs, no side effects

        This is the main entry point for parameter resolution.
        Use this method to get ALL parameters at once with fallback tracking.

        Args:
            template: PromptTemplate instance
            category: Template category (for logging context)
            action: Template action (for logging context)

        Returns:
            Dict with resolved parameters AND fallback tracking:
            {
                "model": str,               # Resolved model name
                "temperature": float,       # Resolved temperature
                "max_tokens": int,          # Resolved max_tokens
                "fallbacks_used": {         # Which parameters used fallback
                    "model": bool,
                    "temperature": bool,
                    "max_tokens": bool
                },
                "fallback_count": int       # Total fallbacks used (0-3)
            }

        Side Effects:
            Logs WARNING for each fallback + summary if any fallback used

        Example:
            result = FallbackHandler.resolve_all_parameters(template, "lyrics", "generate")
            if result["fallback_count"] > 0:
                # Alert: Template is incomplete!
                # result["fallbacks_used"] shows which fields are missing
        """
        model, model_fallback = PromptTemplateFallbackHandler.resolve_model(template, category, action)
        temperature, temp_fallback = PromptTemplateFallbackHandler.resolve_temperature(template, category, action)
        max_tokens, tokens_fallback = PromptTemplateFallbackHandler.resolve_max_tokens(template, category, action)

        fallbacks_used = {"model": model_fallback, "temperature": temp_fallback, "max_tokens": tokens_fallback}

        fallback_count = sum(fallbacks_used.values())

        # CRITICAL: Log summary if ANY fallback was used
        if fallback_count > 0:
            logger.warning(
                "FALLBACK SUMMARY: Template incomplete - using defaults",
                category=category,
                action=action,
                template_id=template.id,
                fallback_count=fallback_count,
                fallbacks_used=fallbacks_used,
                resolved_model=model,
                resolved_temperature=temperature,
                resolved_max_tokens=max_tokens,
                # ⚠️ ACTION REQUIRED: Fix template in database!
                # This template is missing required configuration.
            )

        return {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "fallbacks_used": fallbacks_used,
            "fallback_count": fallback_count,
        }

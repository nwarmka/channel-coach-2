"""Privacy-safe OpenAI Responses API usage logging.

Log final responses only; no prompts, responses, API keys, or user identifiers.
"""
import json
import logging

logger = logging.getLogger("channel_coach.api_usage")


def record_response_usage(response, feature="unknown"):
    usage = getattr(response, "usage", None)
    if usage is None:
        return False
    input_details = getattr(usage, "input_tokens_details", None)
    output_details = getattr(usage, "output_tokens_details", None)
    record = {
        "event": "openai_token_usage",
        "feature": str(feature),
        "model": getattr(response, "model", None),
        "service_tier": getattr(response, "service_tier", None),
        "input_tokens": getattr(usage, "input_tokens", 0),
        "cached_input_tokens": getattr(input_details, "cached_tokens", 0) if input_details else 0,
        "output_tokens": getattr(usage, "output_tokens", 0),
        "reasoning_output_tokens": getattr(output_details, "reasoning_tokens", 0) if output_details else 0,
        "total_tokens": getattr(usage, "total_tokens", 0),
        "status": getattr(response, "status", None),
        "incomplete_reason": getattr(getattr(response, "incomplete_details", None), "reason", None),
    }
    logger.warning(json.dumps(record, default=str))
    return True


def install_usage_tracking(client):
    """Wrap sync Responses calls, including streaming completion events."""
    responses = client.responses
    original_create = responses.create

    def tracked_create(*args, **kwargs):
        result = original_create(*args, **kwargs)
        feature = "coach_stream" if kwargs.get("stream") else "coach_request"
        if kwargs.get("stream"):
            def tracked_events():
                try:
                    for event in result:
                        if getattr(event, "type", None) in ("response.completed", "response.incomplete"):
                            try:
                                record_response_usage(getattr(event, "response", None), feature)
                            except Exception:
                                logger.exception("Could not log OpenAI usage")
                        yield event
                finally:
                    close = getattr(result, "close", None)
                    if callable(close):
                        close()
            return tracked_events()
        try:
            record_response_usage(result, feature)
        except Exception:
            logger.exception("Could not log OpenAI usage")
        return result

    responses.create = tracked_create

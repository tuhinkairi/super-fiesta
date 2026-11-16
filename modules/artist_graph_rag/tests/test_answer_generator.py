from unittest.mock import MagicMock, patch

from graphrag_app.generation.models import (
    GenerationRequest,
    GenerationResult,
)
from graphrag_app.generation.answer_generator import (
    AnswerGenerator,
)


def create_request():
    """Create a sample generation request."""

    return GenerationRequest(
        query="How is Python used in machine learning?",
        context=(
            "Python is a programming language. "
            "Python is widely used for machine learning."
        ),
        temperature=0.2,
        max_output_tokens=2048,
    )


@patch("graphrag_app.generation.answer_generator.settings")
def test_successful_answer_generation(mock_settings):
    """Test successful answer generation."""

    mock_settings.llm_model = "test-gemini-model"

    gemini_client = MagicMock()

    gemini_client.generate_text.return_value = (
        "Python is used in machine learning "
        "to implement algorithms and build models."
    )

    generator = AnswerGenerator(
        gemini_client=gemini_client
    )

    request = create_request()

    result = generator.generate(request)

    assert isinstance(result, GenerationResult)

    assert result.query == request.query

    assert "Python" in result.answer

    assert result.model == "test-gemini-model"

    assert result.context_used is True

    assert result.metadata["temperature"] == 0.2

    assert result.metadata["max_output_tokens"] == 2048

    gemini_client.generate_text.assert_called_once()


@patch("graphrag_app.generation.answer_generator.settings")
def test_generation_uses_retrieved_context(mock_settings):
    """Test that retrieved context is included in the prompt."""

    mock_settings.llm_model = "test-gemini-model"

    gemini_client = MagicMock()

    gemini_client.generate_text.return_value = (
        "Python supports machine learning."
    )

    generator = AnswerGenerator(
        gemini_client=gemini_client
    )

    request = create_request()

    generator.generate(request)

    call_arguments = gemini_client.generate_text.call_args.kwargs

    assert request.query in call_arguments["prompt"]

    assert request.context in call_arguments["prompt"]

    assert (
        call_arguments["temperature"]
        == request.temperature
    )


@patch("graphrag_app.generation.answer_generator.settings")
def test_generation_uses_system_instruction(mock_settings):
    """Test that the system instruction is passed to Gemini."""

    mock_settings.llm_model = "test-gemini-model"

    gemini_client = MagicMock()

    gemini_client.generate_text.return_value = "Test answer."

    generator = AnswerGenerator(
        gemini_client=gemini_client
    )

    generator.generate(create_request())

    call_arguments = gemini_client.generate_text.call_args.kwargs

    assert call_arguments["system_instruction"] == (
        AnswerGenerator.SYSTEM_INSTRUCTION
    )


@patch("graphrag_app.generation.answer_generator.settings")
def test_empty_gemini_response(mock_settings):
    """Test handling of an empty Gemini response."""

    mock_settings.llm_model = "test-gemini-model"

    gemini_client = MagicMock()

    gemini_client.generate_text.return_value = "   "

    generator = AnswerGenerator(
        gemini_client=gemini_client
    )

    request = create_request()

    try:
        generator.generate(request)
        assert False, "Expected RuntimeError was not raised."
    except RuntimeError as error:
        assert "empty answer" in str(error)


def test_generator_can_be_initialized():
    """Test generator initialization with a supplied client."""

    gemini_client = MagicMock()

    generator = AnswerGenerator(
        gemini_client=gemini_client
    )

    assert generator.gemini_client is gemini_client

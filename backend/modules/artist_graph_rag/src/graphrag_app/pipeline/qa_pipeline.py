from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph

from modules.artist_graph_rag.src.graphrag_app.retrieval import (
    RetrievalRequest,
    RetrievalResult,
    RetrievalService,
)

from modules.artist_graph_rag.src.graphrag_app.generation import (
    GenerationRequest,
    GenerationResult,
    AnswerGenerator,
)


class QAPipelineState(TypedDict, total=False):
    """Shared state passed between QA workflow nodes."""

    request: RetrievalRequest
    retrieval_result: RetrievalResult
    generation_request: GenerationRequest
    generation_result: GenerationResult


class QAPipeline:
    """Coordinates knowledge retrieval and answer generation using LangGraph."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        answer_generator: AnswerGenerator,
    ):
        self.retrieval_service = retrieval_service
        self.answer_generator = answer_generator

        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """Construct and compile the QA workflow."""

        graph = StateGraph(QAPipelineState)

        graph.add_node("retrieve_knowledge", self._retrieve_knowledge)
        graph.add_node("prepare_generation", self._prepare_generation)
        graph.add_node("generate_answer", self._generate_answer)

        graph.add_edge(START, "retrieve_knowledge")
        graph.add_edge("retrieve_knowledge", "prepare_generation")
        graph.add_edge("prepare_generation", "generate_answer")
        graph.add_edge("generate_answer", END)

        return graph.compile()

    def _retrieve_knowledge(
        self,
        state: QAPipelineState,
    ) -> dict:
        """Retrieve relevant entities and relationships from Neo4j."""

        retrieval_result = self.retrieval_service.retrieve(state["request"])

        return {
            "retrieval_result": retrieval_result,
        }

    @staticmethod
    def _prepare_generation(
        state: QAPipelineState,
    ) -> dict:
        """Prepare the generation request using retrieved context."""

        retrieval_result = state["retrieval_result"]
        original_request = state["request"]

        generation_request = GenerationRequest(
            query=original_request.query,
            context=retrieval_result.context,
        )

        return {
            "generation_request": generation_request,
        }

    def _generate_answer(
        self,
        state: QAPipelineState,
    ) -> dict:
        """Generate an answer grounded in retrieved knowledge."""

        generation_result = self.answer_generator.generate(state["generation_request"])

        return {
            "generation_result": generation_result,
        }

    def answer(
        self,
        request: RetrievalRequest,
    ) -> tuple[RetrievalResult, GenerationResult]:
        """Execute the QA workflow and return retrieval and generation results."""

        initial_state: QAPipelineState = {
            "request": request,
        }

        result = self.workflow.invoke(initial_state)

        return (
            result["retrieval_result"],
            result["generation_result"],
        )

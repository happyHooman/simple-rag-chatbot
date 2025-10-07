"""Ask question endpoint logic with AI routing and LangChain pipeline."""
from typing import Any

from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from ..config import settings
from ..config.logging_config import get_logger
from ..models import AskQuestionRequest, AskQuestionResponse, QuestionRoute
from ..prompts import AI_ROUTER_SYSTEM_PROMPT
from ..sql_queries import SIMILARITY_SEARCH
from .embeddings import get_db_cursor

logger = get_logger(__name__)

# Constants
NON_IT_RESPONSE = "This is not really what I was trained for, therefore I cannot answer. Try again."

# Initialize LangChain components
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
chat_model = ChatOpenAI(
    model=settings.OPENAI_CHAT_MODEL,
    temperature=settings.OPENAI_CHAT_TEMPERATURE
)


# AI Router
class AIRouter:
    """AI Router for classifying questions as IT or non-IT."""

    def __init__(self) -> None:
        """Initialize the AI Router with LangChain components."""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.1  # Low temperature for consistent classification
        )
        self.structured_llm = self.llm.with_structured_output(QuestionRoute)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", AI_ROUTER_SYSTEM_PROMPT),
            ("human", "{question}")
        ])

        self.router = self.prompt | self.structured_llm
        logger.info("AI Router initialized")

    def classify_question(self, question: str) -> str:
        """
        Classify a question as IT or non-IT.

        Args:
            question: User question to classify

        Returns:
            str: Category ('it' or 'non_it')
        """
        try:
            logger.info(f"Classifying question: {question[:100]}...")
            result = self.router.invoke({"question": question})
            # Type narrowing: check if result is a QuestionRoute instance
            if isinstance(result, QuestionRoute):
                logger.info(f"Question classified as: {result.category}")
                return result.category
            else:
                logger.error(f"Unexpected result type from router: {type(result)}")
                return "it"
        except Exception as e:
            logger.error(f"Error classifying question: {str(e)}")
            # Default to IT category if classification fails
            return "it"


# Global router instance
ai_router = AIRouter()



def find_best_match(user_question: str, threshold: float | None = None) -> dict[str, Any] | None:
    """Find the best matching FAQ question using pgvector's native similarity search."""
    try:
        if threshold is None:
            threshold = settings.SIMILARITY_THRESHOLD

        user_embedding = embeddings.embed_query(user_question)
        logger.debug(f"Generated embedding for user question: {user_question[:50]}...")

        embedding_str = "[" + ",".join(map(str, user_embedding)) + "]"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                SIMILARITY_SEARCH,
                (embedding_str, embedding_str, embedding_str, threshold, embedding_str)
            )
            result = cursor.fetchone()

        if result:
            stored_id, stored_question, stored_answer, distance, similarity = result
            logger.debug(f"Found match with similarity {similarity:.3f} (distance: {distance:.3f})")
            return {
                "id": stored_id,
                "question": stored_question,
                "answer": stored_answer,
                "similarity": float(similarity)
            }
        else:
            logger.debug(f"No matches found above threshold {threshold}")
            return None

    except Exception as e:
        logger.error(f"Error finding best match: {str(e)}")
        return None


def get_openai_answer(user_question: str) -> str:
    """Get an answer from OpenAI when no local match is found."""
    try:
        logger.debug(f"Getting OpenAI answer for: {user_question[:50]}...")

        # Use chat model directly - no complex prompt needed
        response = chat_model.invoke(user_question)
        answer = response.content
        # Handle potential list/dict response types
        if isinstance(answer, str):
            logger.debug(f"OpenAI provided answer: {answer[:100]}...")
            return answer
        else:
            logger.warning(f"Unexpected response type from OpenAI: {type(answer)}")
            return "I apologize, but I received an unexpected response. Please try again."

    except Exception as e:
        logger.error(f"Error getting OpenAI answer: {str(e)}", exc_info=True)
        return "I apologize, but I'm unable to provide an answer at this time. Please try again later or contact support for assistance."


# Pipeline component functions
def process_question_and_decide(inputs: dict) -> dict:
    """Process question, find similarity match, and decide response type."""
    user_question = inputs["user_question"]

    # Find similarity match
    similarity_result = find_best_match(user_question, settings.SIMILARITY_THRESHOLD)

    # Decide response type based on similarity
    if similarity_result and similarity_result.get("similarity", 0) >= settings.SIMILARITY_THRESHOLD:
        return {
            "type": "local",
            "question": similarity_result["question"],
            "answer": similarity_result["answer"],
            "similarity": similarity_result["similarity"],
            "user_question": user_question
        }
    else:
        return {
            "type": "openai",
            "question": None,
            "answer": None,
            "similarity": 0,
            "user_question": user_question
        }

def get_response_and_format(state: dict) -> dict:
    """Get the appropriate response and format the final result."""
    if state["type"] == "local":
        # Use local response
        return {
            "source": "local",
            "matched_question": state["question"],
            "answer": state["answer"]
        }
    else:
        # Get OpenAI response
        openai_answer = get_openai_answer(state["user_question"])
        return {
            "source": "openai",
            "matched_question": "N/A",
            "answer": openai_answer
        }


def ask_question_service(request: AskQuestionRequest) -> AskQuestionResponse:
    """Process a question using AI Router and LangChain pipeline."""
    try:
        user_question = request.user_question
        logger.info(f"Processing question: {user_question}")

        # Classify the question using AI Router
        category = ai_router.classify_question(user_question)

        # Route based on classification
        if category == "it":
            # IT question - use existing pipeline
            logger.info("Routing to IT pipeline")

            qa_pipeline = (
                RunnableLambda(process_question_and_decide)
                | RunnableLambda(get_response_and_format)
            )

            pipeline_input = {"user_question": user_question}
            result = qa_pipeline.invoke(pipeline_input)

            return AskQuestionResponse(
                source=result["source"],
                matched_question=result["matched_question"],
                answer=result["answer"]
            )
        else:
            # Non-IT question - return default response
            logger.info("Non-IT question detected, returning default response")
            return AskQuestionResponse(
                source="compliance",
                matched_question="N/A",
                answer=NON_IT_RESPONSE
            )

    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return AskQuestionResponse(
            source="error",
            matched_question="N/A",
            answer="Sorry, there was an error processing your question. Please try again."
        )



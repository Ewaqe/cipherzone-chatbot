from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.llama_cpp import LlamaCPP

from app.llm.events import (
    TopicClassifierEvent,
    ExplicitFilteringEvent,
)
from app.llm.prompts import (
    TOPIC_CLASSIFICATION_PROMPT,
    messages_to_prompt,
    completion_to_prompt,
)
from app.core.config import MODEL_PATH


qwen = LlamaCPP(
    model_path=MODEL_PATH,
    temperature=0.3,
    max_new_tokens=512,
    context_window=4000,
    generate_kwargs={},
    model_kwargs={"n_gpu_layers": 0, "repeat_penaly": 1.1},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=True,
)


class PreprocessFlow(Workflow):
    llm = qwen

    @step
    async def detect_prompt_injection(self, ev: StartEvent) -> TopicClassifierEvent | StopEvent:
        query = ev.query
        # Some prompt injection detection logic
        detected = False
        if detected:
            return StopEvent(result='Обнаружена попытка взлома')

        return TopicClassifierEvent(query=query)

    @step
    async def classify_topic(self, ev: TopicClassifierEvent) -> ExplicitFilteringEvent:
        query = ev.query

        response = await self.llm.apredict(TOPIC_CLASSIFICATION_PROMPT, query=query)
        return ExplicitFilteringEvent(query=query, topic=str(response))

    @step
    async def detect_explicit_content(self, ev: ExplicitFilteringEvent) -> StopEvent:
        query = ev.query
        topic = ev.topic

        detected = False
        if detected:
            return StopEvent(result='Обнаружен нежелательный запрос')

        return StopEvent(result=topic)
    
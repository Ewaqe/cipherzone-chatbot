from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.llama_cpp import LlamaCPP

from app.llm.prompts import (
    INTENT_CLASSIFICATION_PROMPT,
    EXTRACT_COUNTERS_PROMPT,
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


class IntentClassifier(Workflow):
    llm = qwen

    @step
    async def classify_intent(self, ev: StartEvent) -> StopEvent:
        query = ev.query

        intent = await self.llm.apredict(INTENT_CLASSIFICATION_PROMPT, query=query)
        return StopEvent(result=intent)


class CountersExtractor(Workflow):
    llm = qwen

    @step
    async def exctract_counters(self, ev: StartEvent) -> StopEvent:
        query = ev.query
        
        response = await self.llm.apredict(EXTRACT_COUNTERS_PROMPT, query=query)

        if 'NONE' in response.strip():
            return StopEvent(result={'pairs': None})

        result = response.split('\n')
        pairs = [
            {'name': line.split(':', 1)[0].strip(), 
              'value': line.split(':', 1)[1].strip()} 
            for line in response.splitlines() if ':' in line
        ]
        return StopEvent(result={'pairs': pairs})
    
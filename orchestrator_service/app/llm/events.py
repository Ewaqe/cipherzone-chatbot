from llama_index.core.workflow import Event


class TopicClassifierEvent(Event):
    query: str


class ExplicitFilteringEvent(Event):
    topic: str
    query: str

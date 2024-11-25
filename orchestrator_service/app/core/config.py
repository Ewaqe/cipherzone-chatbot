from environs import Env

env = Env()
env.read_env()

KAFKA_BROKER = env.str("KAFKA_BROKER")
REQUESTS_TOPIC = env.str("REQUESTS_TOPIC")
RESPONSES_TOPIC = env.str("RESPONSES_TOPIC")
RAG_TOPIC = env.str("RAG_TOPIC")

PG_LOGIN = env.str("PG_LOGIN")
PG_PASSWORD = env.str("PG_PASSWORD")
PG_DB = env.str("PG_DB")

MODEL_PATH = env.str("MODEL_PATH")

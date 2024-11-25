from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
BASE_URL = env.str("BASE_URL")
ADMINS = env.list("ADMINS")

KAFKA_BROKER = env.str("KAFKA_BROKER")
COUNTERS_TOPIC = env.str("COUNTERS_TOPIC")

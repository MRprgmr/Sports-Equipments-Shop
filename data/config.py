from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
SERVER = env.str("SERVER")
PAYMENT_PROVIDER = env.str("PAYMENT_PROVIDER")
CONTACT_NUMBER = env.str("CONTACT_NUMBER")
ORDERS_GROUP = env.str("ORDERS_GROUP")
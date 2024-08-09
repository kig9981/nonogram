import environ


env = environ.Env()
environ.Env.read_env()
LOG_PATH = env("LOG_PATH")
DEBUG = env.bool("DEBUG")

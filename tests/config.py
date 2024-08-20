from pathlib import Path
import os


def load_env(env_path: Path):
    env_path = env_path.joinpath('test.env')
    if env_path.exists():
        with env_path.open() as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
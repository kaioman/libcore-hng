import os
import json

config = json.load(os.environ["DAMMY_SECRETS_DEV"])

print(config)
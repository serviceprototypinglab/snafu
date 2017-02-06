import os
def lambda_handler(event, context):
    return os.getenv("THEANSWER") or ""

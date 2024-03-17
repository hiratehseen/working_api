# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# (developer): ETG Team
# Copyright © 2023 <ETG>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import sys
import asyncio
import uvicorn
from pyngrok import ngrok  # Import ngrok from pyngrok

# Set the project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Set the 'AudioSubnet' directory path
sys.path.insert(0, project_root)

from classes.tts import TextToSpeechService 
from classes.vc import VoiceCloningService
from classes.ttm import MusicGenerationService

# Check if the 'app' folder exists
if os.path.exists(os.path.join(project_root, 'app')):
    from app.fastapi_server import create_app

async def run_fastapi_with_ngrok(app):
    # Setup ngrok tunnel
    ngrok_tunnel = ngrok.connect(8000)
    print('Public URL:', ngrok_tunnel.public_url)
    try:
        # Run the server using uvicorn
        config = uvicorn.Config(app=app, host="0.0.0.0", port=40337)
        server = uvicorn.Server(config)
        await server.serve()
    finally:
        # Close ngrok tunnel when server exits
        ngrok_tunnel.close()

async def main():
    services = [
        # MusicGenerationService(),
        # TextToSpeechService(),
        # VoiceCloningService(),
    ]

    # Initialize an empty list to hold our tasks
    tasks = []

    # Iterate through each service and create an asynchronous task for its run_async method
    for service in services:
        if isinstance(service, TextToSpeechService):
            service.new_wandb_run()  # Initialize the Weights & Biases run if the service is TextToSpeechService
        task = asyncio.create_task(service.run_async())
        tasks.append(task)

        await asyncio.sleep(0.1)  # Short delay between task initializations if needed

    # If the 'app' folder exists, create and run the FastAPI app
    if os.path.exists(os.path.join(project_root, 'app')):
        # Read secret key from environment variable
        secret_key = os.getenv("LOGIN_SECRET_KEY")
        if not secret_key:
            raise ValueError("Login Secret key not found in environment variable LOGIN_SECRET_KEY")
        app = create_app(secret_key)
        # Create a task for running FastAPI with ngrok
        fastapi_task = asyncio.create_task(run_fastapi_with_ngrok(app))

        # Wait for all tasks to complete, prioritizing the FastAPI task
        await asyncio.gather(fastapi_task, *tasks)
    else:
        # If the 'app' folder does not exist, continue running other tasks normally
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
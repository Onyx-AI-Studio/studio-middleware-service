# Studio - Middleware Service

Built an end-user configurable Generative AI Studio, which can handle multiple input types, use various large language models (LLMs) locally or via an API, supports multiple speech-to-text models, etc.

It has three main components built with Python, the UI, the Middleware service and the LLM Service.

This repository has the code for the Middleware service, which is responsible for interacting with 3rd party services like Deepgram, AWS, etc., and passes relevant data to the LLM service.

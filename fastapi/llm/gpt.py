# llm/gpt.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, TypedDict, Optional

import openai

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import os

api_key = "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"
os.environ['ANTHROPIC_API_KEY'] = api_key
anthropic = Anthropic()

class GptMessage(TypedDict):
    role: str
    name: Optional[str]
    content: str


class GPT:
    def __init__(self, api_key):
        self.api_key = "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"
        self.executor = ThreadPoolExecutor()
    print("completion")
    async def create_chat_completion(self, model, system_message, user_message) -> str:
        response = await self.create_conversation_completion(model, [
            {"role": "system", "name": "system", "content": system_message},
            {"role": "user", "name": "user", "content": user_message}
        ])
        return response["content"]

    async def create_conversation_completion(self, model, conversation: List[GptMessage]) -> GptMessage:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._create_conversation_completion,
            model, conversation
        )

    def _create_conversation_completion(self, model, conversation: List[GptMessage]) -> GptMessage:
        """
        thread-blocking version of create_conversation_completion
        """
        print("_create_conversation_completion called for conversation: " + str(conversation))
        
        completion = anthropic.completions.create(
            model="claude-2",
            max_tokens_to_sample=5000,
            prompt=f'{HUMAN_PROMPT} {str(conversation)}{AI_PROMPT}[{{"action": "respond_to_user"',
        )
        return {'content': '[{"action": "respond_to_user"'+completion.completion.split(']')[0] + ']'}

        openai.api_key = self.api_key
        chat_completion = openai.ChatCompletion.create(
            model=model,
            messages=conversation
        )
        response = chat_completion.choices[0].message
        return response

    async def create_image(self, prompt, size='256x256') -> str:
        """
        :return: a short-lived image URL
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._create_image,
            prompt, size
        )

    def _create_image(self, prompt, size='256x256') -> str:
        """
        thread-blocking version of create_image
        """
        print("Generating image for prompt: " + prompt)
        openai.api_key = self.api_key
        result = openai.Image.create(
            prompt=prompt,
            n=1,
            size=size
        )
        image_url = result.data[0].url
        print(".... finished generating image for prompt" + prompt + ":\n" + image_url)
        return image_url


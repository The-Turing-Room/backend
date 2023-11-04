import asyncio

from dotenv import load_dotenv

from ace.ace_system import AceSystem
from channels.web.fastapi_app import FastApiApp
from llm.gpt import GPT
from media.giphy_finder import GiphyFinder
from util import get_environment_variable



async def stacey_main(start_web):
    load_dotenv()
    openai_api_key = get_environment_variable('OPENAI_API_KEY')
    llm = GPT(openai_api_key)
    ace = AceSystem(llm, "claude-2")



    await ace.start()


    web_task = asyncio.create_task(asyncio.sleep(0))
    if start_web:
        web_backend = FastApiApp(ace, None)
        print('Starting web backend')
        web_task = asyncio.create_task(web_backend.run())
        print('Started web backend')

    await asyncio.gather(web_task)

if __name__ == '__main__':
    asyncio.run(stacey_main(start_web=True))

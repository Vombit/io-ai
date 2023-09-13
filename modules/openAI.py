import openai, os
from dotenv import load_dotenv
load_dotenv()


openai.api_key = os.getenv('API_OPENAI')

presystem = {"role": "system", "content": "assistant"}

async def gpt_try(user, msg):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            presystem,
            {"role": "user", "content": msg}
        ]
    )
    res = completion['choices'][0]['message']['content'].encode('utf-8').decode('utf8')
    return str(res)

async def gpt_try_context(user, msg, context):
    context.insert(0, presystem)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0.7,
        messages=context
    )
    res = completion['choices'][0]['message']['content']
    return str(res)
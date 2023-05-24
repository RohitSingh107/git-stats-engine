from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os


from . import top_langs_fetch as tlf

load_dotenv()

token = os.getenv('PAT')
headers = {"Authorization": "Bearer {}".format(token)}


app = FastAPI()


@app.get('/')
async def index():
    return RedirectResponse(url='https://github.com/RohitSingh107/git-stats-engine')

@app.get('/api/top-langs/')
async def top_langs_handle(username : str, lang_count : int = 10, layout:str = 'pie', exclude_repo: str = "", exclude_lang: str = ""):
    return await tlf.top_langs(headers, username=username, lang_count=lang_count, layout=layout, exclude_repo= exclude_repo, exclude_lang=exclude_lang)

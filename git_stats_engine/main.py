from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os



# from fastapi.responses import FileResponse
# from PIL import Image
# import matplotlib.pyplot as plt
# import io

# from top_langs_fetch import top_langs
from . import top_langs_fetch as tlf

load_dotenv()

token = os.getenv('PAT')
headers = {"Authorization": "Bearer {}".format(token)}


app = FastAPI()


@app.get('/')
async def index():
    # return {"data": "Hello FastAPI"}
    return RedirectResponse(url='https://github.com/RohitSingh107/git-stats-engine')


# @app.get('/bar')
# async def barPlot():
#     return Response(content=githubApi.bar_plot(), media_type='image/svg+xml; charset=utf-8')
#

@app.get('/api/top-langs/')
async def top_langs_handle(username : str, noOfRepos: int = 100, lang_count : int = 10, layout:str = 'pie'):
    return await tlf.top_langs(headers, username=username, noOfRepos=noOfRepos, lang_count=lang_count, layout=layout)

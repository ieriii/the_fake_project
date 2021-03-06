import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

export_file_url = 'https://www.dropbox.com/s/ou0jmstqtu1llah/AZ_final_model.pkl?dl=1'
export_file_name = 'AZ_final_model.pkl'

classes = ['Fake review', 'Genuine review']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def index(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())

@app.route('/analyze', methods=['POST'])
async def analyze(request):
    terms = ['hotel', 'staff', 'reception', 'room', 'stay', 'desk', 'food', 'restaurant',
             'bed', 'chair', 'carpet', 'shower', 'napkin', 'bread', 'course', 'dish', 'stay'
             'vacation', 'holiday', 'holidays', 'table', 'knife', 'fork', 'spoon', 'dessert',
             'waiter', 'waitress', 'receptionist', 'tv', 'bartender', 'lunch', 'dinner', 'menu'
             'chef', 'meal', 'amenity', 'amenities', 'check-in', 'door', 'bath', 'bathtub', 
             'minibar', 'bar', 'television', 'telly', 'suite', 'ensuite', 'bathroom', 'service'
            ]
    
    data = await request.json()
    review = data["textField"]
    
    is_review = [element for element in terms if(element in review.lower())]
    if bool(is_review):
        prediction = learn.predict(review)
        return JSONResponse({'result': str(prediction)})
    else:
        return JSONResponse({'result': '(Category Uhm... Sorry. This does not seem to be an hotel or restaurant review. Try a different one?, tensor(0), tensor([0, 0])'})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")

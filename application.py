import asyncio, time, shutil, os, random, string, imghdr
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.page import Page
from pyppeteer.element_handle import ElementHandle
from PIL import Image

async def log(page: Page, name: str, **kwargs):

    handle = None

    if "handle" in kwargs: 
        handle = kwargs.get("handle")
        if handle is not None:
            await page.evaluate("x => x.style.border = '2px dashed red'", handle)

    # TODO: print log info
    # await page.screenshot({'path': f'debug/{name}.png'})

    if handle is not None and "click" in kwargs:
        await page.evaluate("x => x.click()", handle)

async def download(browser: Browser, url: str, **kwargs):

    page = await browser.newPage()

    try:

        response = (await asyncio.gather(
            page.waitForResponse(url),
            page.goto(url),
        ))[0]
      
        buffer = await response.buffer()

        if "file_name" in kwargs: fileName = kwargs.get("file_name")
        else: fileName = "".join(random.sample(string.ascii_lowercase+string.digits,20))

        if "file_path" in kwargs: filePath = kwargs.get("file_path")
        else: filePath = "downloads"

        if not os.path.isdir(filePath):
            os.makedirs(filePath)

        path = os.path.join(filePath, fileName)

        with open(path,'wb') as f:
            f.write(buffer)
        
        ext = imghdr.what(path)
        
        if ext == "jpeg":
            os.rename(path, path + ".jpg")
        else:
            im = Image.open(path).convert("RGB")
            im.save(path + ".jpg", "jpeg")
            os.remove(path)

    except:
        pass

    await page.close()

async def similar(engine: str, path: str, **kwargs):

    browser = await launch(options= {'headless': True, 'args': ['--no-sandbox'],'defaultViewport': {'height': 1080, 'width': 1920}})
    page = await browser.newPage()

    await page.goto(engine)
    await page.waitForSelector("form div[aria-label")
    
    searchButtons = await page.querySelectorAll("form div[aria-label] span")

    for item in searchButtons:
        buttonImage = await page.evaluate("x => window.getComputedStyle(x, false).backgroundImage", item)
        if "camera" in buttonImage:
            searchByImage = item
            break
    
    if searchByImage is None: return
    await log(page, "001", handle=searchByImage, click=True)
    await page.waitForSelector("form a[onclick*='(true)']")
    uploadTab = await page.querySelector("form a[onclick*='(true)']")
    await log(page, "002", handle=uploadTab, click=True)
    inputFile = await page.querySelector("#qbfile")
    await inputFile.uploadFile(path)

    try:
        await page.waitForSelector("g-section-with-header h3 a[href*='/search']")
    except:
        await log(page, "003")
        return

    similar = await page.querySelector("g-section-with-header h3 a[href*='/search']")
    await log(page, "004", handle=similar, click=True)
    
    try:
        await page.waitForSelector("img")
    except:
        await log(page, "005")
        return
    
    firstImage = await page.querySelector("#islrg > div > div:nth-child(1) img")
    await log(page, "006", handle=firstImage, click=True)

    result = []

    while True:

        await asyncio.sleep(1)

        images = await page.querySelectorAll("#islsp img[src^='http']")
        newImages = 0

        for image in images:
            currentUrl = await page.evaluate("x => x.src", image)
            if currentUrl not in result and "gstatic.com" not in currentUrl:
                newImages += 1
                result.append(currentUrl)
                await download(browser, currentUrl, **kwargs)
                print(currentUrl)

        if newImages == 0: 
            break
        
        await page.keyboard.press("ArrowRight")
        await asyncio.sleep(random.randint(5,16))
    
    await browser.close()

def run(engine: str, folder: str):

    if os.path.isdir("debug"): 
        shutil.rmtree('debug')
        time.sleep(0.1)

    os.makedirs('debug')

    loop = asyncio.get_event_loop()

    for filename in os.listdir(folder):
        if ".jpeg" in filename or ".jpg" in filename or ".png" in filename or ".gif" in filename:
            path = os.path.join(folder, filename)
            loop.run_until_complete(similar(engine, path, file_path="downloads"))

if __name__ == "__main__":
    engine = os.environ.get("ENGINE") # Image search engine URL
    folder = os.environ.get("FOLDER") # Folder to iterate
    run(engine, folder)

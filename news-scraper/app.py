from utils import get_google_news, scrape_article

import asyncio


async def main():
    urls = get_google_news('covid 19')
    tasks = []
    async with asyncio.TaskGroup() as tg:
        #tasks = [tg.create_task(scrape_article(url)) async for url in urls]
        async for url in urls: 
            task = tg.create_task(scrape_article(url))
            tasks.append(task)
    return [task.result() for task in tasks]
            
if __name__ == '__main__':
    res = asyncio.run(main())
    print(res)



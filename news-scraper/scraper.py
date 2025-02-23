from utils import get_google_news, scrape_article


def main():
    urls = get_google_news('ukraine')

    for url in urls: 
        
        a = scrape_article(url)   
            


if __name__ == '__main__':
    main()



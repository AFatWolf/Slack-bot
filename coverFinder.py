from bs4 import BeautifulSoup   # parse website source code
from selenium import webdriver  # chrome driver
from selenium.webdriver.chrome.options import Options
import urllib.parse   # url encode

class CoverFinder:
    def __init__(self, book_name):
        self.book_name = book_name
        
        # we are going to use goodread for 
        self.url = "https://www.goodreads.com/search?q={0}".format(urllib.parse.quote_plus(book_name))

    def getBookCoverUrl(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # it is guru advice that you should add this
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        
        driver.get(self.url)
        
        try:
            first_book = driver.find_element_by_xpath("//img[@class='bookCover']")
            # click on the first book
            first_book.click()
        except Exception as e:
            print(e)

        # after clicking, the website is at the book's page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        bookCover = soup.find('img', id='coverImage')
        try:
            bookCover_url = bookCover['src']
        except:
            bookCover_url = "None"
        
        try:
            bookTitle = str(soup.find(id="bookTitle").string)
        except:
            bookTitle = "Cannot find."

        try:
            authorName = str(soup.find(class_="authorName").span.string)
        except:
            authorName = "Cannot find."

        driver.close()
        return {"image_url": bookCover_url,
                "title": bookTitle,
                "author_name": authorName
                 }
        
        

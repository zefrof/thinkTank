import requests
from bs4 import BeautifulSoup

def main():

    errCount = 0
    url = "https://www.mtgtop8.com/event?e="

    index = 0
    while errCount < 4:
        page = requests.get(url + str(index))

        if(page.status_code == 404):
            errCount += 1
            break

        text = BeautifulSoup(page.text, "html.parser")

        print(text)

        index += 1




if __name__== "__main__":
    main()
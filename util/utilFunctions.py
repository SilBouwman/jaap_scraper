# Importing external libraries
import requests
from bs4 import BeautifulSoup

# Importing internal libraries




def largestNumber(in_str):
    l=[int(x) for x in in_str.split() if x.isdigit()]
    return max(l) if l else None


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup
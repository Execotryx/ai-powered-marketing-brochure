from bs4 import BeautifulSoup
from requests import get

class Website:
    """
    A class to represent a website.
    """

    __title: str
    __website_url: str
    __text: str

    @property
    def title(self) -> str:
        return self.__title

    @property
    def text(self) -> str:
        return self.__text

    @property
    def website_url(self) -> str:
        return self.__website_url

    @website_url.setter
    def website_url(self, value: str) -> None:
        if not value:
            raise ValueError("Website URL must be provided")
        self.__website_url = value
        self.__fetch_website_data()

    def __fetch_website_data(self) -> None:
        try:
            response = get(self.website_url)
        except Exception as e:
            print(f"Connection error: {e}")
            self.__title = "Error"
            self.__text = "Error"
            return
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            self.__title = soup.title.get_text() if soup.title else "No title"
            for irrelevant in soup.find_all(["script", "style", "img", "figure", "video", "audio", "button"]):
                irrelevant.decompose()
            if soup.body is None:
                self.__text = "No content"
            else:
                self.__text = soup.body.get_text(separator="\n")
        else:
            self.__title = "Error"
            self.__text = "Error"

    def __init__(self, website_url: str):
        self.website_url = website_url

    def __str__(self) -> str:
        return f"Website(title={self.title}, url={self.website_url})"
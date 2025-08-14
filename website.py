from ipaddress import ip_address, IPv4Address, IPv6Address
from urllib.parse import ParseResult, urlparse
from bs4 import BeautifulSoup
from requests import get, RequestException

class Extractor:
    __soup: BeautifulSoup

    __extracted_title: str = ""
    @property
    def extracted_title(self) -> str:
        if not self.__extracted_title:
            self.__extracted_title = self.get_title()
        return self.__extracted_title

    __extracted_text: str = ""
    @property
    def extracted_text(self) -> str:
        if not self.__extracted_text:
            self.__extracted_text = self.get_text()
        return self.__extracted_text

    @property
    def _soup(self) -> BeautifulSoup:
        return self.__soup
    
    def __init__(self, response_text_content: str) -> None:
        self.__soup = BeautifulSoup(response_text_content, "html.parser")

    def get_title(self) -> str:
        return self._soup.title.get_text() if self._soup.title is not None and hasattr(self._soup.title, "get_text") else "No title"

    def get_text(self) -> str:
        for irrelevant in self._soup.find_all(["script", "style", "img", "figure", "video", "audio", "button", "svg", "canvas"]):
            irrelevant.decompose()
        raw_text: str = self._soup.get_text(separator="\n")
        cleaned_text: str = " ".join(raw_text.split())
        return cleaned_text if cleaned_text else "No content"

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
        parsed_url: ParseResult = urlparse(value)
        if not parsed_url.netloc or parsed_url.scheme not in ("http", "https"):
            raise ValueError("Website URL must be a valid URL")

        if not parsed_url.hostname:
            raise ValueError("Website URL must contain a valid hostname")

        if self.__is_local_address(parsed_url.hostname):
            raise ValueError("Website URL must not be a local address")

        if not self.__is_allowed_domain(parsed_url.hostname):
            raise ValueError("Website URL must be an allowed domain")

        self.__website_url = value
        self.__fetch_website_data()

    def __is_local_address(self, hostname: str) -> bool:
        """
        Check if the given hostname is a local address.
        """
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return True

        try:
            ip: IPv4Address | IPv6Address = ip_address(hostname)
            if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved:
                return True
        except ValueError:
            return False

        return False

    def __is_allowed_domain(self, hostname: str) -> bool:
        """
        Check if the given hostname is an allowed domain.
        """
        allowed_domains = [".com", ".org", ".net"]
        return any(hostname.endswith(domain) for domain in allowed_domains)

    def __fetch_website_data(self) -> None:
        try:
            response = get(self.website_url, timeout=10)
        except RequestException as e:
            self.__title = "Error"
            self.__text = str(e)
            return
        
        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            self.__title = soup.title.get_text() if soup.title else "No title"
            if soup.body is None:
                self.__text = "No content"
            else:
                self.__text = self.__extract_text(soup)
        else:
            self.__title = "Error"
            self.__text = f"Error: {response.status_code} - {response.reason}"

    def __extract_text(self, soup: BeautifulSoup) -> str:
        """
        Extract visible text from the HTML soup.
        """
        for script in soup.find_all(["script", "style", "img", "figure", "video", "audio", "button"]):
            script.decompose()
        if soup.body is None:
            return "No content"
        return soup.get_text(separator="\n")

    def __init__(self, website_url: str):
        self.website_url = website_url

    def __str__(self) -> str:
        return f"Website(title={self.title}, url={self.website_url})"
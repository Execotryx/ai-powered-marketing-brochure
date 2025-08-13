import ipaddress
from urllib.parse import ParseResult, urlparse
from bs4 import BeautifulSoup
from requests import get, RequestException

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
            ip: ipaddress.IPv4Address | ipaddress.IPv6Address = ipaddress.ip_address(hostname)
            if ip.is_loopback or ip.is_private or ip.is_link_local:
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
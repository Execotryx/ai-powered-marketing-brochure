from ai_core import AICore
from ai_brochure_config import AIBrochureConfig
from extractor_of_relevant_links import ExtractorOfRelevantLinks
from website import Website
from openai.types.responses import Response
from rich.console import Console
from rich.markdown import Markdown

class BrochureCreator(AICore[str]):

    @property
    def _website(self) -> Website:
        return self.__website

    @property
    def _extractor(self) -> ExtractorOfRelevantLinks:
        return self.__extractor

    def __init__(self, config: AIBrochureConfig, website: Website) -> None:
        system_behavior: str = ("You are an assistant that analyzes the contents of several relevant pages from a company website "
                                "and creates a short brochure about the company for prospective customers, investors and recruits. "
                                "Include details of company culture, customers and careers/jobs if information is available. ")
        super().__init__(config, system_behavior)
        self.__website: Website = website
        self.__extractor: ExtractorOfRelevantLinks = ExtractorOfRelevantLinks(config, website)

    def create_brochure(self) -> str:
        relevant_pages: list[dict[str, str | Website]] = self._get_relevant_pages()
        if not relevant_pages:
            return "No relevant pages found to create a brochure."

        brochure_prompt_part: str = self._form_brochure_prompt(relevant_pages)
        inferred_company_name: str = self._infer_company_name(brochure_prompt_part)
        inferred_status: str = self._infer_status(inferred_company_name)

        full_brochure_prompt: str = self._form_full_prompt(inferred_company_name, inferred_status)
        response: str = self.ask(full_brochure_prompt)
        return response

    def _get_relevant_pages(self) -> list[dict[str, str | Website]]:
        relevant_pages: list[dict[str, str | Website]] = []
        relevant_links: list[dict[str, str]] = self._extractor.extract_relevant_links()["links"]
        for relevant_link in relevant_links:
            page = {"type": str(relevant_link["type"]), "page": Website(relevant_link["url"])}
            relevant_pages.append(page)
        return relevant_pages

    def _form_brochure_prompt(self, relevant_pages: list[dict[str, str | Website]]) -> str:
        QUOTE_DELIMETER: str = "\n\"\"\"\n"
        prompt: str = f"Main page:{QUOTE_DELIMETER}Title: {self._website.title}\nText:\n{self._website.text}{QUOTE_DELIMETER}\n"

        for page in relevant_pages:
            if isinstance(page['page'], Website) and not page['page'].fetch_failed:
                prompt += f"{page['type']}:{QUOTE_DELIMETER}Title: {page['page'].title}\nText:\n{page['page'].text}{QUOTE_DELIMETER}\n"

        return prompt

    def _infer_company_name(self, brochure_prompt_part: str) -> str:
        inferring_company_name_prompt: str = ("Infer the name of the company or the full name of the owner of this website based on the following information that was obtained from their website:\n"
                                               f"{brochure_prompt_part}\n"
                                               "Respond only with the name.")
        response: str = self.ask(inferring_company_name_prompt)
        return response

    def _infer_status(self, inferred_name: str) -> str:
        inferring_status_prompt: str = ("Infer the current status of the entity by the provided name based on the information obtained from their website previously. There can be only two statuses: a company or an individual.\n"
                                         f"Entity: {inferred_name}\n"
                                         "Respond only with the status of said entity.")
        response: str = self.ask(inferring_status_prompt)
        return response

    def _form_full_prompt(self, inferred_company_name: str, inferred_status: str) -> str:
        full_prompt: str = (f"You are looking at a {inferred_status} called {inferred_company_name}, to whom website {self._website.website_url} belongs.\n"
                            "Build a short brochure about the {inferred_status}. Use the information from the website that is already stored in the history.\n"
                            "Your response must be in a Markdown format.")
        return full_prompt

    def ask(self, question: str) -> str:
        self.history_manager.add_user_message(question)
        response: Response = self._ai_api.responses.create(
            model=self.config.model_name,
            instructions=self.history_manager.system_behavior,
            input=self.history_manager.chat_history,
            reasoning={
                "effort": "medium"
            })
        self.history_manager.add_assistant_message(response)
        return response.output_text    

console: Console = Console()

def display_markdown(content: str) -> None:
    """
    Display the markdown content using rich.
    """
    console.print(Markdown(content))

def show_summary(summary: str) -> None:
    """
    Show the summary of the website using rich.
    """
    if summary:
        display_markdown(summary)
    else:
        console.print("No summary found.")

if __name__ == "__main__":
    website: Website = Website("<put your site address here>")
    brochure_creator: BrochureCreator = BrochureCreator(AIBrochureConfig(), website)
    brochure: str = brochure_creator.create_brochure()
    display_markdown(brochure)
import openai
from abc import ABC, abstractmethod
from ai_brochure_config import AIBrochureConfig

class HistoryManager:
    """
    Manages the chat history for the AI core.
    """

    @property
    def chat_history(self) -> list[dict[str, str]]:
        """
        Get the chat history.
        """
        if len(self.__chat_history) == 0:
            self.__chat_history.append({"role": "system", "content": self.system_behavior})
        elif self.__chat_history[0].get("role") != "system":
            self.__chat_history.insert(0, {"role": "system", "content": self.system_behavior})
        else:
            self.__chat_history[0]["content"] = self.system_behavior

        return self.__chat_history

    @property
    def system_behavior(self) -> str:
        """
        Get the system behavior.
        """
        return self.__system_behavior

    def __init__(self, system_behavior: str) -> None:
        self.__chat_history: list[dict[str, str]] = []
        self.__system_behavior: str = system_behavior

    def add_user_message(self, message: str) -> None:
        """
        Adds a user message to the chat history.
        """
        self.__chat_history.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str) -> None:
        """
        Adds an assistant message to the chat history.
        """
        self.__chat_history.append({"role": "assistant", "content": message})


class AICore(ABC):
    """
    Abstract base class for AI core functionalities.
    """
    @property
    def config(self) -> AIBrochureConfig | None:
        """
        Return the stored AIBrochureConfig for this instance, or None if no configuration is set.

        Returns:
            AIBrochureConfig | None: The current configuration used by this object, or None when
            the configuration has not been initialized.

        Notes:
            - This accessor returns the internal configuration reference. Mutating the returned
              object may affect the internal state of this instance.
            - To change the configuration, use the appropriate setter or factory method rather
              than modifying the returned value in-place.
        """
        return self.__config

    @config.setter
    def config(self, config: AIBrochureConfig | None) -> None:
        """
        Set the instance configuration for the AI brochure generator.

        Parameters
        ----------
        config : AIBrochureConfig | None
            The configuration to assign to the instance. If None, the instance's
            configuration will be reset to a newly created default AIBrochureConfig.

        Returns
        -------
        None

        Notes
        -----
        This method stores the provided configuration on a private attribute
        (e.g., self.__config). Use None to explicitly reset to default settings.
        """
        if config is None:
            self.__config = AIBrochureConfig()
        else:
            self.__config = config

    @property
    def _ai_api(self) -> openai.OpenAI:
        """
        Return the cached OpenAI API client, initializing it on first access.

        This private helper lazily constructs and caches an openai.OpenAI client using
        the API key found on self.config.openai_api_key. On the first call, if the
        client has not yet been created, the method verifies that self.config is set,
        creates the client with openai.OpenAI(api_key=...), stores it on
        self.__ai_api, and returns it. Subsequent calls return the same cached
        instance.

        Returns:
            openai.OpenAI: A configured OpenAI API client.

        Raises:
            ValueError: If self.config is None when attempting to initialize the client.

        Notes:
            - The method mutates self.__ai_api as a side effect (caching).
            - The caller should treat this as a private implementation detail.
            - Thread safety is not guaranteed; concurrent initialization may result in
              multiple client instances if invoked from multiple threads simultaneously.
        """
        if self.__ai_api is None:
            if self.config is None:
                raise ValueError("Configuration must be set before accessing AI API")
            self.__ai_api = openai.OpenAI(api_key=self.config.openai_api_key)
        return self.__ai_api

    @property
    def history_manager(self) -> HistoryManager:
        """
        Return the history manager for this AI core instance.

        This property provides access to the HistoryManager that tracks the chat
        history and system behavior.

        Returns:
            HistoryManager: The current history manager. This property always returns
            a HistoryManager instance and never None.
        """
        return self.__history_manager

    def __init__(self, config: AIBrochureConfig, system_behavior: str) -> None:
        """
        Initializes the AI core with the provided configuration.

        Parameters:
            config (AIBrochureConfig): The configuration object for the AI core.
            system_behavior (str): The behavior of the system.
        """
        self.__config: AIBrochureConfig | None = None
        self.config = config
        self.__history_manager: HistoryManager = HistoryManager(system_behavior)
        self.__ai_api: openai.OpenAI | None = None

    @abstractmethod
    def ask(self, question: str) -> str:
        """
        Ask a question to the AI model.

        Parameters:
            question (str): The question to ask.

        Returns:
            str: The AI model's response.
        """
        pass
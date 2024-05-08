from abc import ABC, abstractmethod


class UserInput(ABC):
    def __init__(self, default_prompt: str = None):
        self.default_prompt = default_prompt

    @abstractmethod
    def get_input(self, prompt: str = None) -> str:
        """Get user input with the given prompt or default prompt."""
        pass


class InputRegistry:
    _registry = {}

    @classmethod
    def register(cls, name: str):
        def inner_wrapper(wrapped_class):
            cls._registry[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_input(cls, name) -> UserInput:
        input = cls._registry.get(name, None)
        if input is None:
            raise ValueError(f"Unknown input type: {name}")

        return input


# Register terminal user input
@InputRegistry.register('terminal')
class TerminalUserInput(UserInput):
    def get_input(self, prompt: str = None) -> str:
        prompt = prompt or self.default_prompt or ""
        return input(prompt)

"""Module for all KINETIC exceptions."""


class ControllerError(BaseException):
    """Exception raised by a Controller class instance."""


class ComponentError(BaseException):
    """Exception raised by a Component class instance."""


class AgentError(BaseException):
    """Exception raised by a Agent class instance."""

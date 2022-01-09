class ImpossibleActionError(Exception):
    """Raised when an impossible action is attempted.

    The reason is given as the exception message.
    """

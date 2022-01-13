class ImpossibleActionError(Exception):
    """Raised when an impossible action is attempted.

    The reason is given as the exception message.
    """


class QuitWithoutSaving(SystemExit):
    """Can be raised to exit the game without automatically saving."""

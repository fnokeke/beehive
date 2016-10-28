"""
Implements customized error handling
"""


class SLMError(Exception):
    """
      Displays user friendly error
    """
    unknown_err = '<b>Uh oh, weird error. Please contact admin :/ </b>'
    internal_server_error = 'Operation was not completed because of a glitch :('
    invalid_input_error = -1

class TokenValidationError(Exception):
    """Token Validation Error class."""

    def __init__(self, message="Token is not active.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message

class TokenGenerationError(Exception):
    """Token Generation Error class."""

    def __init__(self, message="Token Could not be generated.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message

class NoMatchingUserError(Exception):
    """No Matching User Error class."""

    def __init__(self, message="User could not be matched.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message

class MatchingUserError(Exception):
    """Matching User Error class."""

    def __init__(self, message="User already exists.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message

class NoMatchingOTPError(Exception):
    """No Matching OTP Error class."""

    def __init__(self, message="OTP could not be matched.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message
    
class NoMatchingSeedError(Exception):
    """No Matching Seed Error class."""

    def __init__(self, message="Seed could not be matched.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message

class SeedWaitingForConfirmationError(Exception):
    """Seed Waiting for Confirmation Error class."""

    def __init__(self, message="There is already and existing seed witing for confirmation.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message

class TechnicalError(Exception):
    """Technical Error class."""

    def __init__(self, message="Operation Failed Due to a Technical Error, Please contact administrator.", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message) # Call the base Exception constructor

    def __str__(self):
        if self.code:
            return f"Error Code {self.code}: {self.message}"
        return self.message
 
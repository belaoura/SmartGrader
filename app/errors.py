"""Custom exception classes for SmartGrader."""


class SmartGraderError(Exception):
    """Base exception for all SmartGrader errors."""

    def __init__(self, message="An error occurred", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ScannerError(SmartGraderError):
    """Raised when image scanning fails."""

    def __init__(self, message="Scanner error"):
        super().__init__(message, status_code=422)


class DetectionError(ScannerError):
    """Raised when bubble/marker detection fails."""

    def __init__(self, message="Detection failed"):
        super().__init__(message)


class GradingError(SmartGraderError):
    """Raised when grading logic fails."""

    def __init__(self, message="Grading error"):
        super().__init__(message, status_code=422)


class SheetGenerationError(SmartGraderError):
    """Raised when answer sheet generation fails."""

    def __init__(self, message="Sheet generation failed"):
        super().__init__(message, status_code=500)


class NotFoundError(SmartGraderError):
    """Raised when a resource is not found."""

    def __init__(self, resource="Resource", resource_id=None):
        msg = f"{resource} not found"
        if resource_id is not None:
            msg = f"{resource} with id {resource_id} not found"
        super().__init__(msg, status_code=404)


class AIModelError(SmartGraderError):
    """Raised when AI model fails to load or inference fails."""

    def __init__(self, message="AI model error"):
        super().__init__(message, status_code=503)

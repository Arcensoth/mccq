class MCCQError(Exception):
    """ MCCQ base error. """


class ArgumentParserFailed(MCCQError):
    """ Raised when the argument parser fails to process the given command string. """
    def __init__(self, command: str, *args):
        super().__init__(*args)
        self.command = command

    def __str__(self):
        return f'Argument parsers failed to process command: {self.command}'


class NoVersionRequested(MCCQError):
    """ Raised when no versions were requested. """

    def __str__(self):
        return 'No versions were requested'


class NoVersionsAvailable(MCCQError):
    """ Raised when none of the requested versions are available. """

    def __init__(self, requested_versions: tuple, *args):
        super().__init__(*args)
        self.versions = requested_versions

    def __str__(self):
        versions_str = ', '.join(self.versions)
        return f'None of the requested versions are available: {versions_str}'


class NoSuchVersion(MCCQError):
    """ Raised when the accessed version is not available. """
    def __init__(self, version: str, *args):
        super().__init__(*args)
        self.version = version

    def __str__(self):
        return f'Version {self.version} is not available'


class VersionNotWhitelisted(MCCQError):
    """ Raised when the version whitelist is enabled and the requested version is not present. """
    def __init__(self, version: str, *args):
        super().__init__(*args)
        self.version = version

    def __str__(self):
        return f'Version {self.version} is not whitelisted'


class MissingCommand(MCCQError):
    """ Raised when the provided command is empty or null. """

    def __str__(self):
        return 'No command was provided'


class NoSuchCommand(MCCQError):
    """ Raised when the given command does not contain a valid base command. """

    def __init__(self, command: str, *args):
        super().__init__(*args)
        self.command = command

    def __str__(self):
        return f'Command does not exist: {self.command}'


class InvalidLoader(MCCQError):
    """ Raised when an invalid data parser is provided. """

    def __init__(self, loader: str, *args):
        super().__init__(*args)
        self.loader = loader

    def __str__(self):
        return f'Invalid data loader: {self.loader}'


class LoaderFailure(MCCQError):
    """ Raised when the data file for the given version failed to load. """

    def __init__(self, version: str, *args):
        super().__init__(*args)
        self.version = version

    def __str__(self):
        return f'Failed to load data for version {self.version}'


class InvalidParser(MCCQError):
    """ Raised when an invalid data parser is provided. """

    def __init__(self, parser: str, *args):
        super().__init__(*args)
        self.parser = parser

    def __str__(self):
        return f'Invalid data parser: {self.parser}'


class ParserFailure(MCCQError):
    """ Raised when a parser fails to process data. """

    def __init__(self, version: str, *args):
        super().__init__(*args)
        self.version = version

    def __str__(self):
        return f'Failed to parse commands for version {self.version}'
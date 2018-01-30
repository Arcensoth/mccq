class MCCQError(Exception):
    """ MCCQ base error. """


class ArgumentParserFailedMCCQError(MCCQError):
    """ Raised when the argument parser fails to process the given command string. """
    def __init__(self, command: str, *args):
        super().__init__(*args)
        self.command = command

    def __str__(self):
        return 'Argument parsers failed to process command: {}'.format(self.command)


class NoVersionsAvailableMCCQError(MCCQError):
    """ Raised when none of the requested versions are available. """

    def __init__(self, requested_versions: tuple, *args):
        super().__init__(*args)
        self.requested_versions = requested_versions

    def __str__(self):
        return 'None of the requested versions are available: {}'.format(', '.join(self.requested_versions))


class NoSuchVersionMCCQError(MCCQError):
    """ Raised when the accessed version is not available. """
    def __init__(self, version: str, *args):
        super().__init__(*args)
        self.version = version

    def __str__(self):
        return 'Version {} is not available'.format(self.version)


class MissingCommandMCCQError(MCCQError):
    """ Raised when the provided command is empty or null. """

    def __str__(self):
        return 'No command was provided'


class NoSuchCommandMCCQError(MCCQError):
    """ Raised when the given command does not contain a valid base command. """

    def __init__(self, command: str, *args):
        super().__init__(*args)
        self.command = command

    def __str__(self):
        return 'Command does not exist: {}'.format(self.command)


class DataFileFailureMCCQError(MCCQError):
    """ Raised when the data file for the given version failed to load. """

    def __init__(self, version: str, data_path: str, *args):
        super().__init__(*args)
        self.version = version
        self.data_path = data_path

    def __str__(self):
        return 'Failed to load data for version {} from:'.format(self.version, self.data_path)


class UnknownParserMCCQError(MCCQError):
    """ Raised when an unknown parser is specified. """

    def __init__(self, parser: str, *args):
        super().__init__(*args)
        self.parser = parser

    def __str__(self):
        return 'Parser not recognized: {}'.format(self.parser)


class ParserFailureMCCQError(MCCQError):
    """ Raised when a parser fails to process data. """

    def __init__(self, version: str, *args):
        super().__init__(*args)
        self.version = version

    def __str__(self):
        return 'Failed to parse commands for version {}'.format(self.version)

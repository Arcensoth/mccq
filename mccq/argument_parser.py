import argparse


class ArgumentParserError(Exception):
    pass


class ArgumentParserExit(Exception):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

    def exit(self, status=0, message=None):
        raise ArgumentParserExit(status, message)

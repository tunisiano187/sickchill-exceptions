import argparse
import copy
import json
import logging
from pathlib import Path
from typing import Dict, Type

import coloredlogs
import verboselogs
from requests_cache import CacheMixin
from requests_html import HTMLSession

logger = logging.getLogger(__package__)


def read_json(infile: Path):
    if infile.exists():
        logger.info(f"Reading file {infile}")
        return json.loads(infile.read_text())
    return dict()


def write_json(outfile: Path, data: Dict, minify: bool = True, ugly: bool = True):
    if ugly:
        ugly_file = outfile.with_suffix(".json")
        logger.info(f"Writing file {ugly_file}")
        ugly_file.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    if minify:
        mini_file = outfile.with_suffix(".min.json")
        logger.info(f"Writing file {mini_file}")
        mini_file.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")), encoding="utf-8")


class CachedHTMLSession(CacheMixin, HTMLSession):
    """Session with features from both CachedSession and HTMLSession"""


class Settings:
    def __init__(self):
        self.location = Path(__file__).parent

        self.verbose = False
        self.debug = False
        self.quiet = False

        self.purge_old = False
        self.start_page = 1
        self.number_of_pages = -1
        self._sources = ["sickchill", "thexem"]
        self.throttle = True
        self.throttle_seconds = None
        self._sources_processed = []

        self.output_file = self.location / "sickchill_exceptions.json"
        self.raw_data_dir = self.location / "raw_data"

        CustomArgumentParser(self)

        self.main_list = {}

    def say_hello(self):
        logger.debug("Starting!")

    @property
    def sources(self):
        return self._sources

    @sources.setter
    def sources(self, value):
        self._sources = {name.strip().lower() for name in value.split(",")}


class CustomArgumentParser(argparse.ArgumentParser):
    def __init__(self, caller: Settings):
        super().__init__(
            epilog=f"""
                    Scene and season exceptions will be read from: {caller.output_file} and each plugin.
                    Raw data will be stored in {caller.raw_data_dir}
                    Scene and season exceptions will be stored in: {caller.output_file.with_suffix('.min.json')}
                """,
            description=caller.__doc__,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        self.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action="store_true",
            help="enable verbose logging",
        )
        self.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="store_true",
            help="enable debug output",
        )
        self.add_argument(
            "-q",
            "--quiet",
            dest="quiet",
            action="store_true",
            help="shush log output to only warnings and errors",
        )
        self.add_argument(
            "-p",
            "--purge-old",
            dest="purge_old",
            action="store_true",
            help="purge items not found on indexers",
        )
        self.add_argument(
            "-o",
            "--output-file",
            dest="output_file",
            default=caller.output_file,
            help="output filename",
        )
        self.add_argument(
            "-s",
            "--sources",
            dest="sources",
            default=",".join(caller.sources),
            help="sources to include",
        )

        self.parse_args(namespace=caller)

        if caller.verbose:
            self.set_log_level(logging.VERBOSE)
        elif caller.debug:
            self.set_log_level(logging.DEBUG)
        elif caller.quiet:
            self.set_log_level(logging.WARNING)
        else:
            self.set_log_level(logging.INFO)

    def set_log_level(self, level: Type[int]):
        verboselogs.install()
        global logger
        logger = verboselogs.VerboseLogger("")
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(level)

        coloredlogs.install(level=level, logger=logger)
        for handler in logger.handlers:
            handler.setLevel(level)


settings = Settings()


# Copyright Ferry Boender, released under the MIT license.
def deepupdate(target, src):
    """Deep update target dict with src
    For each k,v in src: if k doesn't exist in target, it is deep copied from
    src to target. Otherwise, if v is a list, target[k] is extended with
    src[k]. If v is a set, target[k] is updated with v, If v is a dict,
    recursively deep-update it.

    Examples:
    >>> t = {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi']}
    >>> deepupdate(t, {'hobbies': ['gaming']})
    >>> print t
    {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi', 'gaming']}
    """
    for k, v in src.items():
        if type(v) == list:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                target[k].extend(v)
        elif type(v) == dict:
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                deepupdate(target[k], v)
        elif type(v) == set:
            if not k in target:
                target[k] = v.copy()
            else:
                target[k].update(v.copy())
        else:
            target[k] = copy.copy(v)

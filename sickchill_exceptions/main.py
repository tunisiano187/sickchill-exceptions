"""main.py

An over-engineered script for scraping scene exceptions from theTVDB, theXEM, etc and formatting them into something we can use.
"""

import sys

from sickchill_exceptions.utils import logger, settings, write_json
from subliminal.extensions import RegistrableExtensionManager

plugin_manager = RegistrableExtensionManager(
    "sickchill_exceptions.plugins", ["sickchill = sickchill_exceptions.plugins.sickchill:Plugin", "thexem = sickchill_exceptions.plugins.thexem:Plugin"]
)


class Updater:
    def run(self):
        settings.say_hello()

        for entry in plugin_manager:
            instance = entry.plugin()
            if instance.name in settings.sources:
                instance.run()

    write_json(settings.output_file, settings.main_list, ugly=False)


if __name__ == "__main__":

    updater = Updater()
    if sys.getdefaultencoding() != "utf-8" or sys.getfilesystemencoding() != "utf-8":
        logger.error("Default encoding and file system encoding must me utf-8 for use this script")
        logger.info(f"File system encoding is: {sys.getfilesystemencoding()}")
        logger.info(f"Default system encoding is: {sys.getdefaultencoding()}")
        sys.exit(1)
    updater.run()

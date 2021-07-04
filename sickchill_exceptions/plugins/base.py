from abc import ABC

from sickchill_exceptions.utils import CachedHTMLSession, deepupdate, logger, read_json, settings, write_json


class BasePlugin(ABC):
    def __init__(self, name: str, no_session: bool = False):
        self.name = name
        self.logger = logger
        self.main_list = settings.main_list

        if not no_session:
            self.session = CachedHTMLSession(cache_name=settings.raw_data_dir / f"{self.name}_cache")

        self.outfile = settings.raw_data_dir / f"{self.name}_exceptions.json"

        self.data = {}
        self.old_data = read_json(self.outfile)

    def process(self):
        raise NotImplementedError

    def finish(self):
        if not settings.raw_data_dir.is_dir():
            settings.raw_data_dir.mkdir()

        write_json(self.outfile, self.data, minify=False)
        deepupdate(settings.main_list, self.data)
        self.logger.info(f"Finished plugin: {self.name}")

    def run(self):
        self.logger.info(f"Running plugin: {self.name}")
        self.process()
        self.finish()

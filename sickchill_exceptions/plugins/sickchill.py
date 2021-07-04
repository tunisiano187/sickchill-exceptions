from git import Repo
from sickchill_exceptions.plugins.base import BasePlugin
from sickchill_exceptions.utils import Path, read_json


class Plugin(BasePlugin):
    def __init__(self):
        super(Plugin, self).__init__("sickchill", no_session=True)

        repository_root = Repo(".", search_parent_directories=True).working_dir
        self.root_file = Path(repository_root) / f"{self.name}_exceptions.json"

    def process(self):
        self.logger.info(f"Processing {self.root_file}")
        self.old_data = read_json(self.root_file)
        self.data = self.old_data

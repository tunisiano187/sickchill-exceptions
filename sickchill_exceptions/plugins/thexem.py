from sickchill_exceptions.plugins.base import BasePlugin


class Plugin(BasePlugin):
    def __init__(self):
        super(Plugin, self).__init__("thexem")
        self.url = "http://thexem.de/map/allNames"
        self.params = {"origin": "tvdb", "seasonNumbers": 1, "defaultNames": 1}
        self.data = dict()

    def process(self):
        response = self.session.get(self.url, params=self.params)
        jdata = response.json()
        if jdata.get("result") != "success":
            message = jdata.get("message", "Unknown")
            self.logger.warning(f"Unable to get scene exceptions from {self.name}: {message}")
            return

        for show, exceptions in jdata["data"].items():
            for exception in exceptions:
                name, season = self.to_dict(exception).popitem()
                if show not in self.data:
                    self.data[show] = {}

                season = str(season)

                if season not in self.data[show]:
                    self.data[show][season] = []

                if name not in self.data[show][season]:
                    self.data[show][season].append(name)

        self.data = {"tvdb": self.data}

    def to_dict(self, exception):
        if isinstance(exception, dict):
            return exception

        return {exception: -1}

from typing import NamedTuple


class PluginConfig(NamedTuple):
    """
    PluginConfig represents the config required to setup and run a Plugin.
    """

    # TODO generalize to support different backends
    username: str
    password: str
    host: str
    port: int
    app_id: str

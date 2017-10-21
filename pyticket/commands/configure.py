from pyticket.utils import configuration, get_home_path

def configure(options,
              what : "Which configuration key to configure",
              value : "Key value"):
    config = configuration.load(get_home_path())
    config.set_value(what, value)
    config.save(get_home_path())

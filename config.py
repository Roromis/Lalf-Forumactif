import configparser

# Dictionnary containing the configuration
config = {
    "url" : "",
    "admin_name" : "",
    "admin_password" : "",
    "table_prefix" : ""
}

# Read the configuration from filename and write it in config
def read(filename):
    if not os.path.isfile(filename):
        raise NoConfigurationFile(filename)
        
    cfg = configparser.ConfigParser()
    with open(filename) as f:
        cfg.read(f)

    for k in config:
        config[k] = cfg.get("Configuration", k)

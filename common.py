import os
import yaml

# project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# full config path
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.yml')

CONFIG_LIST_SEP = ";"

def get_full_path(rel_path):
    return os.path.normpath(os.path.join(ROOT_DIR, rel_path))

def get_dict_from_config_value(s):
    values = s.split(CONFIG_LIST_SEP)
    keys = range(len(values))
    return dict(zip(keys, values))

with open(CONFIG_PATH, "r") as f:

    # yaml to python dict
    CONFIG = yaml.load(f, Loader=yaml.SafeLoader)

    CONFIG['path_data'] = get_full_path(CONFIG['path_data'])
    CONFIG['path_model'] = get_full_path(CONFIG['path_model'])
    CONFIG['num_features'] = get_dict_from_config_value(CONFIG['num_features'])
    CONFIG['cat_features'] = get_dict_from_config_value(CONFIG['cat_features'])
    CONFIG['random_state'] = int(CONFIG['random_state'])
    CONFIG['db_path'] = get_full_path(CONFIG['db_path'])
    CONFIG['endpoint'] = CONFIG['endpoint']

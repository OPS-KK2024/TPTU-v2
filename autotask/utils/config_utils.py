import os
import yaml


def update_config(config, base_config_path):
    # Get default config from yaml
    with open(base_config_path, 'r', encoding='utf-8') as f:
        # default_config = yaml.load(f.read(), Loader=yaml.FullLoader)
        default_config = yaml.safe_load(f)
    
    # Update default config with user config
    # Note that the config is a nested dictionary, so we need to update it recursively
    def update(d, u):
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    return update(default_config, config)


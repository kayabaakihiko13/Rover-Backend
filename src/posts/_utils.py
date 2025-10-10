from typing import List
import yaml

def _read_yaml_file(yaml_files:str)->List[str]:
    with open(yaml_files,"r",encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if "names" not in data:
        raise KeyError(f"YAML file {yaml_files} tidak memiliki key 'names'")
    return data['names']
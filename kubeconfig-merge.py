import yaml
import sys
from pathlib import Path

def merge_kubeconfigs(config1_path, config2_path, output_path):
    with open(config1_path, 'r') as f:
        config1 = yaml.safe_load(f)
    with open(config2_path, 'r') as f:
        config2 = yaml.safe_load(f)

    def merge_lists(key):
        items = {item['name']: item for item in config1.get(key, [])}
        for item in config2.get(key, []):
            items[item['name']] = item
        return list(items.values())

    merged = {
        'apiVersion': 'v1',
        'kind': 'Config',
        'clusters': merge_lists('clusters'),
        'users': merge_lists('users'),
        'contexts': merge_lists('contexts'),
        'current-context': config2.get('current-context', config1.get('current-context', '')),
        'preferences': {},
    }

    with open(output_path, 'w') as f:
        yaml.safe_dump(merged, f, default_flow_style=False)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_kubeconfigs.py <config1> <config2> <output>")
        sys.exit(1)
    merge_kubeconfigs(sys.argv[1], sys.argv[2], sys.argv[3])
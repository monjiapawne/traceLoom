import json, logging

def conv_json(target: str, node_list: list[str]) -> str:
    output_path = "results.json"
    output = {
        "target": target,
        "nodes": {
            str(i): node.to_dict() for i, node in enumerate(node_list, 1)
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    logging.info(f'[+] converted to:'.ljust(33) + f'{output_path}')
    return output
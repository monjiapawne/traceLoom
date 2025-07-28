import json
import logging
import os
from datetime import datetime


def conv_json(target: str, node_list: list[str]):
  now = datetime.now()
  output_folder = os.path.join("results", target)
  date_time = now.strftime("%m%d%Y-%H%M%S")
  output_file = f"tr_{target}_{date_time}.json"
  ab_file = os.path.join(output_folder, output_file)
  output = {
      "target": target,
      "nodes": {str(i): node.to_dict() for i,
                node in enumerate(node_list, 1)},
  }

  os.makedirs(output_folder, exist_ok=True)
  with open(ab_file, "w") as f:
    json.dump(output, f, indent=2)

  logging.info("[+] converted to:".ljust(35) + f"{ab_file}")
  return ab_file

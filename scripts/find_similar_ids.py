import json
from typing import Any

with open("sample-api-response/kubernetes/all_nodes.json", "r") as file:
    all_nodes: dict[str, list[dict[str, Any]]] = json.load(file)

with open("run_raw_data.json", "r") as file:
    run: dict[str, Any] = json.load(file)

for instance in run["hourlyUsage"]["instance"]:
    for details in instance["details"]:

        for cluster in all_nodes:
            for node in all_nodes[cluster]:

                if node["instanceId"] == details["instanceId"]:
                    print(node["instanceId"])
                elif node["instanceId"] == details["resourceId"]:
                    print(node["instanceId"])

import hashlib
import json
import logging
log = logging.getLogger(__name__)

def graph(data):
    # load graph details
    try:
        graph_specs = _ttp_["output_object"].attributes['load']
        edges_map = graph_specs["map"]["edges"]
        nodes_map = graph_specs["map"]["nodes"]
        if isinstance(nodes_map, dict):
            nodes_map = [nodes_map]
    except KeyError as e:
        log.critical("output.formatter_graph: output missing graph specification, error - '{}'. Exiting".format(e))
        raise SystemExit()
    edges = {}; nodes = {}
    path = _ttp_["output_object"].attributes.get('path', [])
    # normalize results_data to list:
    if isinstance(data, dict): # handle the case for group specific output
        data = [data]
    for result in data:
        result_datum = _ttp_["output"]["traverse_dict"](result, path)
        if isinstance(result_datum, dict):
            result_datum = [result_datum]
        for result_item in result_datum:
            # map edge
            edge = {ek: (result_item.get(ev, "") if ev else result_item.get(ek, "")) for ek, ev in edges_map.items()}
            edge_hash = hashlib.md5(json.dumps(edge, sort_keys=True).encode('utf-8')).hexdigest()
            if not edge_hash in edges:
                edges[edge_hash] = edge
            # map nodes
            for node_map in nodes_map:
                node = {nk: (result_item.get(nv, "") if nv else result_item.get(nk, "")) for nk, nv in node_map.items()}
                if not node["id"] in nodes:
                    nodes[node["id"]] = node
    # add missing nodes
    for edge in list(edges.values()):
        if not edge["source"] in nodes:
            nodes[edge["source"]] = {"id": edge["source"]}
        if not edge["target"] in nodes:
            nodes[edge["target"]] = {"id": edge["target"]}
    # form graph
    graph = {
        "edges": list(edges.values()),
        "nodes": list(nodes.values())
    }    
    return graph   
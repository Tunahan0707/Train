from math import hypot
from PySide6.QtCore import QPointF


def build_netlist(scene, tolerance=2.0):
    """Build connectivity groups from component terminals and wire endpoints.

    Wire crossings are intentionally not connected unless a wire endpoint
    touches the other wire or a component terminal.
    """
    nodes = []
    wire_pairs = []
    wire_segments = []
    component_counts = {}

    for item in scene.items():
        component_id = getattr(item, "component_id", None)
        if component_id is None:
            continue

        if component_id == "wire":
            start_index = len(nodes)
            nodes.append({
                "kind": "wire",
                "label": f"Tel ucu {start_index + 1}",
                "point": QPointF(item.start_point),
            })
            end_index = len(nodes)
            nodes.append({
                "kind": "wire",
                "label": f"Tel ucu {end_index + 1}",
                "point": QPointF(item.end_point),
            })
            wire_pairs.append((start_index, end_index))
            corner = QPointF(item.end_point.x(), item.start_point.y())
            wire_segments.append((start_index, item.start_point, corner))
            wire_segments.append((start_index, corner, item.end_point))
            continue

        component_counts[component_id] = component_counts.get(component_id, 0) + 1
        instance = component_counts[component_id]
        terminal_method = getattr(item, "terminal_positions", None)
        if terminal_method is None:
            continue

        pin_names = getattr(item, "terminal_names", lambda: [])()
        for pin_index, (local_x, local_y) in enumerate(terminal_method()):
            point = item.mapToScene(QPointF(local_x, local_y))
            pin_name = pin_names[pin_index] if pin_index < len(pin_names) else f"Uç {pin_index + 1}"
            nodes.append({
                "kind": "component",
                "label": f"{getattr(item, 'name', component_id)} {instance} · {pin_name}",
                "point": point,
                "item": item,
                "pin_index": pin_index,
            })

    parent = list(range(len(nodes)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first, second):
        first_root = find(first)
        second_root = find(second)
        if first_root != second_root:
            parent[second_root] = first_root

    for first, second in wire_pairs:
        union(first, second)

    def distance_to_segment(point, start, end):
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length_squared = dx * dx + dy * dy
        if length_squared == 0:
            return hypot(point.x() - start.x(), point.y() - start.y())
        projection = (
            (point.x() - start.x()) * dx
            + (point.y() - start.y()) * dy
        ) / length_squared
        projection = max(0.0, min(1.0, projection))
        closest_x = start.x() + projection * dx
        closest_y = start.y() + projection * dy
        return hypot(point.x() - closest_x, point.y() - closest_y)

    # Component pins and wire endpoints also connect to the middle of a wire.
    for node_index, node in enumerate(nodes):
        for wire_index, start, end in wire_segments:
            if distance_to_segment(node["point"], start, end) <= tolerance:
                union(node_index, wire_index)

    tolerance_squared = tolerance * tolerance
    for first in range(len(nodes)):
        point_a = nodes[first]["point"]
        for second in range(first + 1, len(nodes)):
            point_b = nodes[second]["point"]
            dx = point_a.x() - point_b.x()
            dy = point_a.y() - point_b.y()
            if dx * dx + dy * dy <= tolerance_squared:
                union(first, second)

    groups = {}
    for index, node in enumerate(nodes):
        groups.setdefault(find(index), []).append(node)

    nets = []
    unconnected = []
    component_nodes = {}
    ground_nodes = []
    for net_id, group in enumerate(groups.values()):
        terminals = [node["label"] for node in group if node["kind"] == "component"]
        wire_count = sum(node["kind"] == "wire" for node in group)
        for node in group:
            if node["kind"] != "component":
                continue
            item = node["item"]
            component_nodes.setdefault(item, {})[node["pin_index"]] = net_id
            if getattr(item, "component_id", None) == "ground":
                ground_nodes.append(net_id)
        if terminals:
            nets.append({
                "id": net_id,
                "terminals": terminals,
                "wire_endpoints": wire_count,
            })
            if len(terminals) == 1 and wire_count == 0:
                unconnected.append(terminals[0])

    return {
        "nets": nets,
        "component_nodes": {
            item: [pins[index] for index in sorted(pins)]
            for item, pins in component_nodes.items()
        },
        "ground_nodes": sorted(set(ground_nodes)),
        "unconnected_terminals": unconnected,
        "component_terminal_count": sum(node["kind"] == "component" for node in nodes),
        "wire_endpoint_count": sum(node["kind"] == "wire" for node in nodes),
    }


def format_netlist_report(scene):
    result = build_netlist(scene)
    lines = [
        f"Bileşen ucu: {result['component_terminal_count']}",
        f"Tel ucu: {result['wire_endpoint_count']}",
        f"Bulunan elektriksel düğüm: {len(result['nets'])}",
        "",
    ]

    for index, net in enumerate(result["nets"], start=1):
        lines.append(f"Düğüm {index}:")
        lines.extend(f"  • {terminal}" for terminal in net["terminals"])
        lines.append(f"  • Bağlı tel ucu: {net['wire_endpoints']}")
        lines.append("")

    if result["unconnected_terminals"]:
        lines.append("Bağlantısız bileşen uçları:")
        lines.extend(f"  • {terminal}" for terminal in result["unconnected_terminals"])
    else:
        lines.append("Tek başına kalmış bileşen ucu bulunamadı.")

    lines.extend([
        "",
        "Not: Tel uçları ve T-bağlantıları tel gövdesine bağlanır; iki telin yalnızca çapraz kesişmesi bağlantı sayılmaz.",
        "Bu analiz bağlantı topolojisini çıkarır; henüz akım/gerilim simülasyonu yapmaz.",
    ])
    return "\n".join(lines)

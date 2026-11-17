import re
import math

from circuit.netlist import build_netlist


SUFFIXES = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "µ": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "K": 1e3,
    "M": 1e6,
    "G": 1e9,
    "meg": 1e6,
}


def parse_engineering_value(value):
    text = str(value).strip().replace("Ω", "").replace("V", "").replace(" ", "")
    multiplier = 1.0
    for suffix in sorted(SUFFIXES, key=len, reverse=True):
        if text.endswith(suffix):
            multiplier = SUFFIXES[suffix]
            text = text[:-len(suffix)]
            break
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", text):
        raise ValueError(f"Geçersiz sayısal değer: {value}")
    result = float(text) * multiplier
    if not math.isfinite(result):
        raise ValueError(f"Değer sonlu bir sayı olmalı: {value}")
    return result


def gaussian_solve(matrix, vector):
    size = len(vector)
    if len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError("Doğrusal sistem kare bir katsayı matrisi gerektirir.")
    if size == 0:
        return []
    if any(not math.isfinite(float(value)) for row in matrix for value in row):
        raise ValueError("Katsayı matrisi sonlu olmayan değer içeriyor.")
    if any(not math.isfinite(float(value)) for value in vector):
        raise ValueError("Sağ taraf vektörü sonlu olmayan değer içeriyor.")
    augmented = [list(map(float, matrix[row])) + [float(vector[row])] for row in range(size)]

    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("Devre matrisi tekil. Bağlantıları, kaynakları ve referans GND'yi kontrol et.")

        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        for index in range(column, size + 1):
            augmented[column][index] /= pivot_value

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0:
                continue
            for index in range(column, size + 1):
                augmented[row][index] -= factor * augmented[column][index]

    return [augmented[row][size] for row in range(size)]


def _component_label(item):
    return getattr(item, "name", getattr(item, "component_id", "Bilinmeyen bileşen"))


def solve_dc_operating_point(scene):
    """Solve a linear DC operating point; never silently omit unsupported devices."""
    netlist = build_netlist(scene)
    component_nodes = netlist["component_nodes"]
    if not component_nodes:
        raise ValueError("Devrede analiz edilecek bileşen bulunamadı.")

    supported = {"resistor", "voltage_source", "battery", "switch", "ground"}
    unsupported = [
        f"{_component_label(item)} ({getattr(item, 'component_id', 'unknown')})"
        for item in component_nodes
        if getattr(item, "component_id", "") not in supported
    ]
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise ValueError(
            "DC çözümü durduruldu. Şu bileşenlerin fiziksel modeli henüz uygulanmadı: "
            + names
            + ". Kısmi sonuç gösterilmedi."
        )

    disconnected = netlist.get("unconnected_terminals", [])
    if disconnected:
        preview = ", ".join(disconnected[:8])
        extra = "" if len(disconnected) <= 8 else f" ve {len(disconnected) - 8} uç daha"
        raise ValueError(
            "DC çözümü durduruldu; bağlantısız bileşen uçları var: "
            + preview + extra + ". Kabloları ve uç temaslarını kontrol et."
        )

    net_ids = sorted({
        net_id
        for pin_nodes in component_nodes.values()
        for net_id in pin_nodes
    })
    if not net_ids:
        raise ValueError("Elektriksel düğüm bulunamadı.")

    ground_nodes = set(netlist["ground_nodes"])
    automatic_ground = not ground_nodes
    if automatic_ground:
        ground_nodes.add(net_ids[0])
    unknown_nodes = [node for node in net_ids if node not in ground_nodes]
    node_index = {node: index for index, node in enumerate(unknown_nodes)}

    resistors = []
    sources = []
    for item, pins in component_nodes.items():
        component_id = getattr(item, "component_id", "")
        if component_id == "resistor":
            if len(pins) != 2:
                raise ValueError(f"{_component_label(item)} iki uçlu olmalı.")
            resistors.append(item)
        elif component_id in ("voltage_source", "battery"):
            if len(pins) != 2:
                raise ValueError(f"{_component_label(item)} iki uçlu olmalı.")
            sources.append(item)
        elif component_id == "switch":
            if len(pins) != 2:
                raise ValueError(f"{_component_label(item)} iki uçlu olmalı.")

    size = len(unknown_nodes) + len(sources)
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    vector = [0.0 for _ in range(size)]

    def stamp_conductance(first_node, second_node, conductance):
        first = node_index.get(first_node)
        second = node_index.get(second_node)
        if first is not None:
            matrix[first][first] += conductance
        if second is not None:
            matrix[second][second] += conductance
        if first is not None and second is not None:
            matrix[first][second] -= conductance
            matrix[second][first] -= conductance

    for item in resistors:
        pins = component_nodes[item]
        resistance = parse_engineering_value(getattr(item, "value", ""))
        if resistance <= 0:
            raise ValueError(f"{_component_label(item)} direnci sıfırdan büyük olmalı.")
        stamp_conductance(pins[0], pins[1], 1.0 / resistance)

    for source_index, item in enumerate(sources):
        pins = component_nodes[item]
        positive_node, negative_node = pins
        source_column = len(unknown_nodes) + source_index
        positive = node_index.get(positive_node)
        negative = node_index.get(negative_node)

        if positive is not None:
            matrix[positive][source_column] += 1.0
            matrix[source_column][positive] += 1.0
        if negative is not None:
            matrix[negative][source_column] -= 1.0
            matrix[source_column][negative] -= 1.0

        source_voltage = parse_engineering_value(getattr(item, "value", ""))
        if source_voltage == 0:
            raise ValueError(f"{_component_label(item)} gerilimi sıfır olamaz.")
        vector[source_column] = source_voltage

    solution = gaussian_solve(matrix, vector) if size else []

    node_voltages = {node: 0.0 for node in net_ids}
    for node, index in node_index.items():
        node_voltages[node] = solution[index]

    resistor_results = []
    for item in resistors:
        pins = component_nodes[item]
        resistance = parse_engineering_value(getattr(item, "value", ""))
        voltage = node_voltages[pins[0]] - node_voltages[pins[1]]
        current = voltage / resistance
        resistor_results.append({
            "name": _component_label(item),
            "resistance": resistance,
            "current": current,
            "voltage": voltage,
            "power": current * current * resistance,
        })

    source_results = []
    for source_index, item in enumerate(sources):
        current_index = len(unknown_nodes) + source_index
        current = solution[current_index]
        source_results.append({
            "name": _component_label(item),
            "voltage": parse_engineering_value(getattr(item, "value", "")),
            "current": current,
            "power": parse_engineering_value(getattr(item, "value", "")) * current,
        })

    return {
        "node_voltages": node_voltages,
        "resistors": resistor_results,
        "sources": source_results,
        "unsupported": [],
        "automatic_ground": automatic_ground,
        "net_count": len(net_ids),
    }


def format_dc_report(scene):
    result = solve_dc_operating_point(scene)
    lines = [
        "DC ÇALIŞMA NOKTASI",
        f"Elektriksel düğüm: {result['net_count']}",
        "Referans: otomatik seçilen düğüm" if result["automatic_ground"] else "Referans: GND bileşeni",
        "",
        "DÜĞÜM GERİLİMLERİ",
    ]
    for node, voltage in sorted(result["node_voltages"].items()):
        lines.append(f"  Düğüm {node + 1}: {voltage:.6g} V")

    lines.extend(["", "DİRENÇLER"])
    for item in result["resistors"]:
        lines.append(
            f"  {item['name']}: {item['voltage']:.6g} V, "
            f"{item['current']:.6g} A, {item['power']:.6g} W"
        )

    lines.extend(["", "DC KAYNAKLARI"])
    for item in result["sources"]:
        lines.append(
            f"  {item['name']}: {item['voltage']:.6g} V, "
            f"kaynak akımı {item['current']:.6g} A, "
            f"güç {item['power']:.6g} W"
        )

    lines.extend([
        "",
        "Model kapsamı: direnç, ideal DC gerilim kaynağı, pil ve kapalı ideal anahtar.",
        "Diyot, LED, transistör, kondansatör, bobin, sigorta, potansiyometre ve AC kaynak için çözüm üretilmez.",
        "GND yoksa bir düğüm geçici referans olarak seçilir.",
        "Kaynak akımının pozitif yönü, kaynağın sol (+) ucundan sağ (-) ucuna doğrudur.",
    ])
    return "\n".join(lines)

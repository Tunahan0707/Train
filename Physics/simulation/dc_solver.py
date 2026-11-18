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
    """Solve a DC operating point with linear passive and piecewise-linear diode models."""
    netlist = build_netlist(scene)
    component_nodes = netlist["component_nodes"]
    if not component_nodes:
        raise ValueError("Devrede analiz edilecek bileşen bulunamadı.")

    supported = {
        "resistor", "voltage_source", "battery", "switch", "ground",
        "capacitor", "inductor", "diode", "led", "fuse", "potentiometer", "bjt", "mosfet",
    }
    unsupported = [
        f"{_component_label(item)} ({getattr(item, 'component_id', 'unknown')})"
        for item in component_nodes
        if getattr(item, "component_id", "") not in supported
    ]
    if unsupported:
        raise ValueError(
            "DC çözümü durduruldu. Şu bileşenlerin fiziksel modeli henüz uygulanmadı: "
            + ", ".join(sorted(unsupported)) + ". Kısmi sonuç gösterilmedi."
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
        net_id for pin_nodes in component_nodes.values() for net_id in pin_nodes
    })
    if not net_ids:
        raise ValueError("Elektriksel düğüm bulunamadı.")

    ground_nodes = set(netlist["ground_nodes"])
    automatic_ground = not ground_nodes
    if automatic_ground:
        ground_nodes.add(net_ids[0])
    unknown_nodes = [node for node in net_ids if node not in ground_nodes]
    node_index = {node: index for index, node in enumerate(unknown_nodes)}

    resistors, fuses, potentiometers, sources, inductors, capacitors, diodes, transistors, switches = [], [], [], [], [], [], [], [], []
    for item, pins in component_nodes.items():
        component_id = getattr(item, "component_id", "")
        expected_pins = 1 if component_id == "ground" else (3 if component_id in ("potentiometer", "bjt", "mosfet") else 2)
        if len(pins) != expected_pins:
            raise ValueError(f"{_component_label(item)} {expected_pins} uçlu olmalı.")
        if component_id == "resistor":
            resistors.append(item)
        elif component_id == "switch":
            switches.append(item)
        elif component_id == "fuse":
            fuses.append(item)
        elif component_id == "potentiometer":
            potentiometers.append(item)
        elif component_id in ("voltage_source", "battery"):
            sources.append(item)
        elif component_id == "inductor":
            inductors.append(item)
        elif component_id == "capacitor":
            capacitors.append(item)
        elif component_id in ("diode", "led"):
            diodes.append(item)
        elif component_id in ("bjt", "mosfet"):
            transistors.append(item)

    def component_resistance(item):
        raw = str(getattr(item, "value", "")).strip()
        resistance = parse_engineering_value(raw)
        unit = str(getattr(item, "unit", ""))
        has_suffix = any(raw.endswith(suffix) for suffix in SUFFIXES)
        if not has_suffix:
            if unit.startswith("k"):
                resistance *= 1e3
            elif unit.startswith("M"):
                resistance *= 1e6
        return resistance

    for item in resistors + fuses + potentiometers:
        resistance = component_resistance(item)
        if resistance <= 0:
            raise ValueError(f"{_component_label(item)} direnci sıfırdan büyük olmalı.")
    for item in potentiometers:
        position = float(getattr(item, "wiper_position", 0.5))
        if not 0.0 <= position <= 1.0:
            raise ValueError(f"{_component_label(item)} sürgü konumu 0 ile 1 arasında olmalı.")
    for item in inductors + capacitors:
        if parse_engineering_value(getattr(item, "value", "")) <= 0:
            raise ValueError(f"{_component_label(item)} değeri sıfırdan büyük olmalı.")

    source_voltages = {}
    for item in sources:
        voltage = parse_engineering_value(getattr(item, "value", ""))
        if voltage == 0:
            raise ValueError(f"{_component_label(item)} gerilimi sıfır olamaz.")
        source_voltages[item] = voltage

    diode_models = {
        item: (0.7, 0.01) if getattr(item, "component_id", "") == "diode" else (2.0, 10.0)
        for item in diodes
    }
    active_diodes = set()
    active_transistors = set()
    transistor_models = {
        item: (0.7, 0.1) if getattr(item, "component_id", "") == "bjt" else (2.0, 0.05)
        for item in transistors
    }
    solution = []
    branch_currents = {}

    # Active-set solution for piecewise-linear diode/LED models.
    # Off: open circuit. On: fixed forward drop plus a small series resistance.
    for _iteration in range(max(8, (len(diodes) + len(transistors)) * 4 + 4)):
        branches = [(item, source_voltages[item], 0.0, "source") for item in sources]
        branches.extend((item, 0.0, 0.0, "inductor") for item in inductors)
        branches.extend((item, 0.0, 0.0, "switch") for item in switches if getattr(item, "closed", False))
        branches.extend(
            (item, diode_models[item][0], diode_models[item][1], "diode")
            for item in diodes if item in active_diodes
        )
        branches.extend(
            (item, 0.0, transistor_models[item][1], "transistor")
            for item in transistors if item in active_transistors
        )

        size = len(unknown_nodes) + len(branches)
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

        for item in resistors + fuses:
            pins = component_nodes[item]
            resistance = component_resistance(item)
            stamp_conductance(pins[0], pins[1], 1.0 / resistance)
        for item in potentiometers:
            pins = component_nodes[item]
            total_resistance = component_resistance(item)
            position = float(getattr(item, "wiper_position", 0.5))
            effective_position = min(1.0 - 1e-9, max(1e-9, position))
            stamp_conductance(pins[0], pins[2], 1.0 / (total_resistance * effective_position))
            stamp_conductance(pins[2], pins[1], 1.0 / (total_resistance * (1.0 - effective_position)))

        branch_index_by_item = {}
        for branch_index, (item, branch_voltage, series_resistance, branch_kind) in enumerate(branches):
            branch_index_by_item[item] = len(unknown_nodes) + branch_index
            branch_pins = component_nodes[item][1:3] if branch_kind == "transistor" else component_nodes[item][:2]
            positive_node, negative_node = branch_pins
            source_column = len(unknown_nodes) + branch_index
            positive = node_index.get(positive_node)
            negative = node_index.get(negative_node)
            if positive is not None:
                matrix[positive][source_column] += 1.0
                matrix[source_column][positive] += 1.0
            if negative is not None:
                matrix[negative][source_column] -= 1.0
                matrix[source_column][negative] -= 1.0
            matrix[source_column][source_column] -= series_resistance
            vector[source_column] = branch_voltage

        solution = gaussian_solve(matrix, vector) if size else []
        node_voltages = {node: 0.0 for node in net_ids}
        for node, index in node_index.items():
            node_voltages[node] = solution[index]
        branch_currents = {
            item: solution[column]
            for item, column in branch_index_by_item.items()
        }

        changed = False
        for item in diodes:
            anode, cathode = component_nodes[item]
            diode_voltage = node_voltages[anode] - node_voltages[cathode]
            forward_voltage, _series_resistance = diode_models[item]
            if item not in active_diodes and diode_voltage > forward_voltage:
                active_diodes.add(item)
                changed = True
            elif item in active_diodes and branch_currents.get(item, 0.0) < -1e-10:
                active_diodes.remove(item)
                changed = True
        for item in transistors:
            pins = component_nodes[item]
            if getattr(item, "component_id", "") == "bjt":
                control_voltage = node_voltages[pins[0]] - node_voltages[pins[2]]
            else:
                control_voltage = node_voltages[pins[0]] - node_voltages[pins[2]]
            threshold, _on_resistance = transistor_models[item]
            if item not in active_transistors and control_voltage > threshold:
                active_transistors.add(item)
                changed = True
            elif item in active_transistors and control_voltage < threshold - 1e-6:
                active_transistors.remove(item)
                changed = True
        if not changed:
            break
    else:
        raise ValueError("Diyot çalışma noktası yakınsamadı; devreyi veya model varsayımlarını kontrol et.")

    node_voltages = {node: 0.0 for node in net_ids}
    for node, index in node_index.items():
        node_voltages[node] = solution[index]

    resistor_results = []
    for item in resistors:
        pins = component_nodes[item]
        resistance = component_resistance(item)
        voltage = node_voltages[pins[0]] - node_voltages[pins[1]]
        current = voltage / resistance
        resistor_results.append({
            "id": getattr(item, "instance_id", None), "name": _component_label(item), "resistance": resistance,
            "current": current, "voltage": voltage,
            "power": current * current * resistance,
        })

    fuse_results = []
    for item in fuses:
        pins = component_nodes[item]
        resistance = component_resistance(item)
        voltage = node_voltages[pins[0]] - node_voltages[pins[1]]
        current = voltage / resistance
        fuse_results.append({
            "id": getattr(item, "instance_id", None), "name": _component_label(item),
            "resistance": resistance, "voltage": voltage, "current": current,
            "power": current * current * resistance,
        })

    potentiometer_results = []
    for item in potentiometers:
        first, second, wiper = component_nodes[item]
        total_resistance = component_resistance(item)
        position = float(getattr(item, "wiper_position", 0.5))
        effective_position = min(1.0 - 1e-9, max(1e-9, position))
        first_resistance = total_resistance * effective_position
        second_resistance = total_resistance * (1.0 - effective_position)
        first_voltage = node_voltages[first] - node_voltages[wiper]
        second_voltage = node_voltages[wiper] - node_voltages[second]
        potentiometer_results.append({
            "id": getattr(item, "instance_id", None), "name": _component_label(item),
            "resistance": total_resistance,
            "voltage": node_voltages[first] - node_voltages[second],
            "wiper_voltage": node_voltages[wiper],
            "first_current": first_voltage / first_resistance,
            "second_current": second_voltage / second_resistance,
            "wiper_position": position,
        })

    source_results = []
    for item in sources:
        current = branch_currents[item]
        voltage = source_voltages[item]
        source_results.append({
            "id": getattr(item, "instance_id", None), "name": _component_label(item), "voltage": voltage,
            "current": current, "power_absorbed": voltage * current,
            "power_delivered": -voltage * current,
        })

    inductor_results = [{
        "id": getattr(item, "instance_id", None),
        "name": _component_label(item),
        "inductance": parse_engineering_value(getattr(item, "value", "")),
        "voltage": node_voltages[component_nodes[item][0]] - node_voltages[component_nodes[item][1]],
        "current": branch_currents[item],
        "power": 0.0,
    } for item in inductors]

    capacitor_results = [{
        "id": getattr(item, "instance_id", None),
        "name": _component_label(item),
        "current": 0.0,
        "voltage": node_voltages[component_nodes[item][0]] - node_voltages[component_nodes[item][1]],
    } for item in capacitors]

    diode_results = []
    for item in diodes:
        anode, cathode = component_nodes[item]
        voltage = node_voltages[anode] - node_voltages[cathode]
        current = branch_currents.get(item, 0.0)
        diode_results.append({
            "id": getattr(item, "instance_id", None),
            "name": _component_label(item),
            "type": getattr(item, "component_id", "diode"),
            "voltage": voltage,
            "current": current,
            "power": voltage * current,
            "conducting": item in active_diodes,
        })

    transistor_results = []
    for item in transistors:
        pins = component_nodes[item]
        control_voltage = node_voltages[pins[0]] - node_voltages[pins[2]]
        output_voltage = node_voltages[pins[1]] - node_voltages[pins[2]]
        current = branch_currents.get(item, 0.0)
        transistor_results.append({
            "id": getattr(item, "instance_id", None),
            "name": _component_label(item),
            "type": getattr(item, "component_id", ""),
            "control_voltage": control_voltage,
            "voltage": output_voltage,
            "current": current,
            "conducting": item in active_transistors,
        })

    component_measurements = {}
    for item in switch_results:
        component_measurements[item["id"]] = {
            "Durum": "Kapalı" if item["closed"] else "Açık",
            "Gerilim": f'{item["voltage"]:.6g} V',
            "Akım": f'{item["current"]:.6g} A',
        }
    for item in resistor_results:
        component_measurements[item["id"]] = {
            "Gerilim": f'{item["voltage"]:.6g} V',
            "Akım": f'{item["current"]:.6g} A',
            "Güç": f'{item["power"]:.6g} W',
        }
    for item in fuse_results:
        component_measurements[item["id"]] = {
            "Gerilim": f'{item["voltage"]:.6g} V', "Akım": f'{item["current"]:.6g} A',
            "Güç": f'{item["power"]:.6g} W',
        }
    for item in potentiometer_results:
        component_measurements[item["id"]] = {
            "Uçlar arası gerilim": f'{item["voltage"]:.6g} V',
            "Sürgü gerilimi": f'{item["wiper_voltage"]:.6g} V',
            "Sürgü konumu": f'{item["wiper_position"]:.3f}',
        }
    for item in source_results:
        component_measurements[item["id"]] = {
            "Gerilim": f'{item["voltage"]:.6g} V',
            "Akım": f'{item["current"]:.6g} A',
            "Devreye verilen güç": f'{item["power_delivered"]:.6g} W',
        }
    for item in inductor_results:
        component_measurements[item["id"]] = {
            "Gerilim": f'{item["voltage"]:.6g} V', "Akım": f'{item["current"]:.6g} A',
        }
    for item in capacitor_results:
        component_measurements[item["id"]] = {
            "Gerilim": f'{item["voltage"]:.6g} V', "Akım": "0 A (DC kararlı hâl)",
        }
    for item in transistor_results:
        component_measurements[item["id"]] = {
            "Kontrol gerilimi": f'{item["control_voltage"]:.6g} V',
            "Çıkış gerilimi": f'{item["voltage"]:.6g} V',
            "Çıkış akımı": f'{item["current"]:.6g} A',
            "Durum": "İletimde" if item["conducting"] else "Kesimde",
        }
    for item in diode_results:
        component_measurements[item["id"]] = {
            "Gerilim": f'{item["voltage"]:.6g} V', "Akım": f'{item["current"]:.6g} A',
            "Durum": "İletimde" if item["conducting"] else "Kesimde",
        }

    return {
        "node_voltages": node_voltages,
        "component_measurements": component_measurements,
        "resistors": resistor_results,
        "fuses": fuse_results,
        "potentiometers": potentiometer_results,
        "sources": source_results,
        "inductors": inductor_results,
        "capacitors": capacitor_results,
        "diodes": diode_results,
        "transistors": transistor_results,
        "switches": switch_results,
        "unsupported": [],
        "automatic_ground": automatic_ground,
        "net_count": len(net_ids),
    }


def format_dc_report(scene=None, result=None):
    result = result if result is not None else solve_dc_operating_point(scene)
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

    if result["fuses"]:
        lines.extend(["", "SİGORTALAR (sabit direnç modeli)"])
        for item in result["fuses"]:
            lines.append(f"  {item['name']}: {item['voltage']:.6g} V, {item['current']:.6g} A, {item['power']:.6g} W")
    if result["potentiometers"]:
        lines.extend(["", "POTANSİYOMETRELER (üç uçlu direnç bölücü)"])
        for item in result["potentiometers"]:
            lines.append(f"  {item['name']}: {item['voltage']:.6g} V uçlar arası, sürgü {item['wiper_voltage']:.6g} V")
    if result["switches"]:
        lines.extend(["", "ANAHTARLAR"])
        for item in result["switches"]:
            state = "Kapalı" if item["closed"] else "Açık"
            lines.append(f"  {item['name']}: {state}, {item['voltage']:.6g} V, {item['current']:.6g} A")
    if result["transistors"]:
        lines.extend(["", "TRANSİSTÖRLER (basitleştirilmiş anahtar modeli)"])
        for item in result["transistors"]:
            state = "İletimde" if item["conducting"] else "Kesimde"
            lines.append(f"  {item['name']}: kontrol {item['control_voltage']:.6g} V, çıkış {item['voltage']:.6g} V, {item['current']:.6g} A ({state})")
    if result["diodes"]:
        lines.extend(["", "DİYOTLAR / LED (parçalı doğrusal model)"])
        for item in result["diodes"]:
            state = "İletimde" if item["conducting"] else "Kesimde"
            lines.append(f"  {item['name']}: {item['voltage']:.6g} V, {item['current']:.6g} A ({state})")
    if result["inductors"]:
        lines.extend(["", "BOBİNLER (DC kararlı hâl)"])
        for item in result["inductors"]:
            lines.append(f"  {item['name']}: {item['voltage']:.6g} V, {item['current']:.6g} A")
    if result["capacitors"]:
        lines.extend(["", "KONDANSATÖRLER (DC kararlı hâl)"])
        for item in result["capacitors"]:
            lines.append(f"  {item['name']}: {item['voltage']:.6g} V, 0 A (ideal açık devre)")
    lines.extend(["", "DC KAYNAKLARI"])
    for item in result["sources"]:
        lines.append(
            f"  {item['name']}: {item['voltage']:.6g} V, "
            f"kaynak akımı {item['current']:.6g} A, "
            f"devreye verilen güç {item['power_delivered']:.6g} W"
        )

    lines.extend([
        "",
        "Model kapsamı: direnç, sabit dirençli sigorta, üç uçlu potansiyometre, ideal DC kaynak/pil/anahtar, ideal kondansatör/bobin, parçalı doğrusal diyot/LED ve basitleştirilmiş BJT/MOSFET anahtar modeli.",
        "DC kararlı hâlde kondansatör açık devre, bobin kısa devre kabul edilir; geçici rejim hesaplanmaz. Diyot/LED sabit eşik ve seri direnç; BJT/MOSFET ise kontrol gerilimine bağlı ideal anahtar yaklaşımıyla modellenir.",
        "AC kaynak için çözüm üretilmez.",
        "GND yoksa bir düğüm geçici referans olarak seçilir.",
        "Kaynak akımının pozitif yönü, kaynağın sol (+) ucundan sağ (-) ucuna doğrudur.",
    ])
    return "\n".join(lines)

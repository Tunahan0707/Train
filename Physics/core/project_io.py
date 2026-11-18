import json
from pathlib import Path

from components.resistor import Resistor
from components.basic import BasicComponent
from components.wire import WireItem


def save_circuit(scene, file_path, circuit_name=None):
    components = []
    for item in scene.items():
        component_id = getattr(item, "component_id", None)
        if component_id is None:
            continue
        if component_id == "wire":
            components.append({
                "type": "wire",
                "start": [item.start_point.x(), item.start_point.y()],
                "end": [item.end_point.x(), item.end_point.y()],
                "x": item.pos().x(),
                "y": item.pos().y(),
            })
        else:
            components.append({
                "type": component_id,
                "name": str(getattr(item, "name", component_id)),
                "x": item.pos().x(),
                "y": item.pos().y(),
                "rotation": item.rotation(),
                "value": getattr(item, "value", ""),
                "closed": getattr(item, "closed", None),
            })

    data = {
        "format": "physics-circuit",
        "version": 2,
        "circuit": {"name": str(circuit_name or Path(file_path).stem or "Devre")},
        "components": components,
    }
    Path(file_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_circuit(scene, file_path):
    data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    if data.get("format") != "physics-circuit":
        raise ValueError("Bu dosya bir Physics devre projesi değil.")
    version = data.get("version")
    if version not in (1, 2):
        raise ValueError("Desteklenmeyen proje dosyası sürümü.")

    constructors = {
        "resistor": Resistor,
        "capacitor": lambda: BasicComponent("capacitor"),
        "inductor": lambda: BasicComponent("inductor"),
        "diode": lambda: BasicComponent("diode"),
        "led": lambda: BasicComponent("led"),
        "voltage_source": lambda: BasicComponent("voltage_source"),
        "battery": lambda: BasicComponent("battery"),
        "switch": lambda: BasicComponent("switch"),
        "ground": lambda: BasicComponent("ground"),
        "fuse": lambda: BasicComponent("fuse"),
        "potentiometer": lambda: BasicComponent("potentiometer"),
        "ac_source": lambda: BasicComponent("ac_source"),
        "bjt": lambda: BasicComponent("bjt"),
        "mosfet": lambda: BasicComponent("mosfet"),
    }

    entries = data.get("components", [])
    if not isinstance(entries, list):
        raise ValueError("Proje bileşen listesi geçersiz.")
    new_items = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Proje içinde geçersiz bileşen kaydı var.")
        component_type = entry.get("type")
        if component_type == "wire":
            start = entry.get("start", [0, 0])
            end = entry.get("end", [0, 0])
            if len(start) != 2 or len(end) != 2:
                raise ValueError("Kablo koordinatları geçersiz.")
            item = WireItem((float(start[0]), float(start[1])), (float(end[0]), float(end[1])))
            item.setPos(float(entry.get("x", 0)), float(entry.get("y", 0)))
            new_items.append(item)
            continue
        if component_type not in constructors:
            raise ValueError(f"Desteklenmeyen bileşen türü: {component_type}")
        item = constructors[component_type]()
        item.setPos(float(entry.get("x", 0)), float(entry.get("y", 0)))
        item.setRotation(float(entry.get("rotation", 0)))
        if hasattr(item, "set_value"):
            item.set_value(entry.get("value", ""))
        if version >= 2:
            item.name = str(entry.get("name", getattr(item, "name", component_type)))
        if getattr(item, "component_id", None) == "switch":
            item.closed = bool(entry.get("closed", False))
        new_items.append(item)

    scene.clear()
    for item in new_items:
        scene.addItem(item)
    scene.clearSelection()
    return str(data.get("circuit", {}).get("name", Path(file_path).stem or "Devre"))

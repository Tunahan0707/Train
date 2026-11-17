import json
from pathlib import Path

from components.resistor import Resistor
from components.basic import BasicComponent
from components.wire import WireItem


def save_circuit(scene, file_path):
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
            })
        else:
            components.append({
                "type": component_id,
                "x": item.pos().x(),
                "y": item.pos().y(),
                "rotation": item.rotation(),
                "value": getattr(item, "value", ""),
            })

    data = {
        "format": "physics-circuit",
        "version": 1,
        "components": components,
    }
    Path(file_path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_circuit(scene, file_path):
    data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    if data.get("format") != "physics-circuit":
        raise ValueError("Bu dosya bir Physics devre projesi değil.")
    if data.get("version") != 1:
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
    }

    new_items = []
    for entry in data.get("components", []):
        component_type = entry.get("type")
        if component_type == "wire":
            start = entry.get("start", [0, 0])
            end = entry.get("end", [0, 0])
            item = WireItem((float(start[0]), float(start[1])),
                            (float(end[0]), float(end[1])))
            new_items.append(item)
            continue
        if component_type not in constructors:
            continue
        item = constructors[component_type]()
        item.setPos(float(entry.get("x", 0)), float(entry.get("y", 0)))
        item.setRotation(float(entry.get("rotation", 0)))
        if hasattr(item, "set_value"):
            item.set_value(entry.get("value", ""))
        new_items.append(item)

    scene.clear()
    for item in new_items:
        scene.addItem(item)
    scene.clearSelection()

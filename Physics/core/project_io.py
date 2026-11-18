import json
import uuid
from pathlib import Path

from components.resistor import Resistor
from components.basic import BasicComponent
from components.wire import WireItem


CONSTRUCTORS = {
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


def serialize_circuit(scene, circuit_name="Devre", circuit_id=None):
    components = []
    for item in scene.items():
        component_id = getattr(item, "component_id", None)
        if component_id is None:
            continue
        if component_id == "wire":
            components.append({
                "type": "wire",
                "id": item.instance_id,
                "start": [item.start_point.x(), item.start_point.y()],
                "end": [item.end_point.x(), item.end_point.y()],
                "x": item.pos().x(),
                "y": item.pos().y(),
            })
        else:
            components.append({
                "type": component_id,
                "id": item.instance_id,
                "name": str(getattr(item, "name", component_id)),
                "x": item.pos().x(),
                "y": item.pos().y(),
                "rotation": item.rotation(),
                "value": getattr(item, "value", ""),
                "closed": getattr(item, "closed", None),
                "wiper_position": getattr(item, "wiper_position", None),
            })
    return {
        "id": str(circuit_id or uuid.uuid4()),
        "name": str(circuit_name or "Devre"),
        "components": components,
    }


def create_circuit_items(circuit_data, version=3):
    entries = circuit_data.get("components", [])
    if not isinstance(entries, list):
        raise ValueError("Proje bileşen listesi geçersiz.")
    new_items = []
    seen_ids = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Proje içinde geçersiz bileşen kaydı var.")
        component_type = entry.get("type")
        if component_type == "wire":
            start = entry.get("start", [0, 0])
            end = entry.get("end", [0, 0])
            if not isinstance(start, (list, tuple)) or not isinstance(end, (list, tuple)) or len(start) != 2 or len(end) != 2:
                raise ValueError("Kablo koordinatları geçersiz.")
            item = WireItem((float(start[0]), float(start[1])), (float(end[0]), float(end[1])))
            item.setPos(float(entry.get("x", 0)), float(entry.get("y", 0)))
        else:
            if component_type not in CONSTRUCTORS:
                raise ValueError(f"Desteklenmeyen bileşen türü: {component_type}")
            item = CONSTRUCTORS[component_type]()
            item.setPos(float(entry.get("x", 0)), float(entry.get("y", 0)))
            item.setRotation(float(entry.get("rotation", 0)))
            if hasattr(item, "set_value"):
                stored_value = entry.get("value", "")
                if component_type == "fuse" and not str(stored_value).strip():
                    stored_value = "0.1"
                item.set_value(stored_value)
            if version >= 2:
                item.name = str(entry.get("name", getattr(item, "name", component_type)))
            if getattr(item, "component_id", None) == "switch":
                item.closed = bool(entry.get("closed", False))
            if getattr(item, "component_id", None) == "potentiometer":
                stored_wiper = entry.get("wiper_position")
                item.wiper_position = float(0.5 if stored_wiper is None else stored_wiper)
                if not 0.0 <= item.wiper_position <= 1.0:
                    raise ValueError("Potansiyometre sürgü konumu 0 ile 1 arasında olmalı.")

        raw_id = entry.get("id")
        if raw_id:
            try:
                item.instance_id = str(uuid.UUID(str(raw_id)))
            except (ValueError, AttributeError):
                raise ValueError("Bileşen kimliği geçersiz.")
        if item.instance_id in seen_ids:
            raise ValueError("Devrede yinelenen bileşen kimliği var.")
        seen_ids.add(item.instance_id)
        new_items.append(item)
    return new_items


def save_circuit(scene, file_path, circuit_name=None):
    circuit = serialize_circuit(scene, circuit_name or Path(file_path).stem or "Devre")
    data = {
        "format": "physics-circuit",
        "version": 3,
        "circuit": {"name": circuit["name"]},
        "components": circuit["components"],
    }
    Path(file_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_circuit(scene, file_path):
    data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    if data.get("format") != "physics-circuit":
        raise ValueError("Bu dosya tek devre biçiminde bir Physics projesi değil.")
    version = data.get("version")
    if version not in (1, 2, 3):
        raise ValueError("Desteklenmeyen proje dosyası sürümü.")
    items = create_circuit_items(data, version)
    scene.clear()
    for item in items:
        scene.addItem(item)
    scene.clearSelection()
    return str(data.get("circuit", {}).get("name", Path(file_path).stem or "Devre"))


def save_project(circuits, file_path, active_circuit_id=None):
    serialized = [
        serialize_circuit(entry["scene"], entry["name"], entry["id"])
        for entry in circuits
    ]
    if not serialized:
        raise ValueError("Kaydedilecek en az bir devre bulunmalı.")
    circuit_ids = [entry["id"] for entry in serialized]
    if len(circuit_ids) != len(set(circuit_ids)):
        raise ValueError("Projede yinelenen devre kimliği var.")
    component_ids = [component["id"] for circuit in serialized for component in circuit["components"]]
    if len(component_ids) != len(set(component_ids)):
        raise ValueError("Projede yinelenen bileşen kimliği var.")
    if active_circuit_id not in circuit_ids:
        active_circuit_id = circuit_ids[0]
    data = {
        "format": "physics-project",
        "version": 1,
        "project": {"name": Path(file_path).stem or "Physics Projesi"},
        "active_circuit_id": active_circuit_id,
        "circuits": serialized,
    }
    Path(file_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_project(file_path):
    data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    if data.get("format") == "physics-circuit":
        version = data.get("version")
        if version not in (1, 2, 3):
            raise ValueError("Desteklenmeyen proje dosyası sürümü.")
        name = str(data.get("circuit", {}).get("name", Path(file_path).stem or "Devre"))
        circuit_id = str(uuid.uuid4())
        return {
            "circuits": [{"id": circuit_id, "name": name, "items": create_circuit_items(data, version)}],
            "active_circuit_id": circuit_id,
        }
    if data.get("format") != "physics-project" or data.get("version") != 1:
        raise ValueError("Bu dosya desteklenen bir Physics projesi değil.")
    entries = data.get("circuits")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Projede en az bir devre bulunmalı.")
    circuits = []
    seen_circuit_ids = set()
    seen_component_ids = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Projede geçersiz devre kaydı var.")
        try:
            circuit_id = str(uuid.UUID(str(entry.get("id"))))
        except (ValueError, AttributeError):
            raise ValueError("Devre kimliği geçersiz.")
        if circuit_id in seen_circuit_ids:
            raise ValueError("Projede yinelenen devre kimliği var.")
        seen_circuit_ids.add(circuit_id)
        items = create_circuit_items(entry, 3)
        for item in items:
            if item.instance_id in seen_component_ids:
                raise ValueError("Projede yinelenen bileşen kimliği var.")
            seen_component_ids.add(item.instance_id)
        circuits.append({"id": circuit_id, "name": str(entry.get("name") or "Devre"), "items": items})
    active_id = str(data.get("active_circuit_id") or circuits[0]["id"])
    if active_id not in seen_circuit_ids:
        active_id = circuits[0]["id"]
    return {"circuits": circuits, "active_circuit_id": active_id}

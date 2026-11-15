
import json
import random
from pathlib import Path

from BrainOld.Noron import Noron
from BrainOld.ReseptorOrgan import ReseptorOrgan
from BrainOld.ReseptorNoron import ReseptorNoron
from BrainOld.MotorOrgan import MotorOrgan
from BrainOld.MotorNoron import MotorNoron


class Beyin:
    def __init__(
        self,
        neuron_count=0,
        receptor_organ_count=0,
        receptor_neuron_count=0,
        motor_organ_count=0,
        motor_neuron_count=0,
        randomize=True
    ):
        self.neurons = []
        self.receptor_organs = []
        self.motor_organs = []

        # Normal nöronları oluştur.
        for _ in range(neuron_count):
            self.create_neuron()

        # Reseptör organlarını oluştur.
        for _ in range(receptor_organ_count):
            organ = self.create_receptor_organ()

            for _ in range(receptor_neuron_count):
                self.create_receptor_neuron(organ)

        # Motor organlarını oluştur.
        for _ in range(motor_organ_count):
            organ = self.create_motor_organ()

            for _ in range(motor_neuron_count):
                self.create_motor_neuron(organ)

        # Bütün nöronlar oluşturulduktan sonra bağlantıları kur.
        if randomize:
            self.randomize_connections()

    # Normal nöronlar

    def add_neuron(self, neuron):
        if neuron not in self.neurons:
            self.neurons.append(neuron)

    def create_neuron(self, dendrit_count=None, terminal_count=None):
        dendrit_count = (
            dendrit_count if dendrit_count is not None
            else random.randint(6, 12)
        )

        terminal_count = (
            terminal_count if terminal_count is not None
            else random.randint(5, 10)
        )

        neuron = Noron(dendrit_count, terminal_count)
        self.add_neuron(neuron)
        return neuron

    # Reseptör organları

    def add_receptor_organ(self, organ):
        if organ not in self.receptor_organs:
            self.receptor_organs.append(organ)

    def create_receptor_organ(self):
        organ = ReseptorOrgan()
        self.add_receptor_organ(organ)
        return organ

    def create_receptor_neuron(
        self, organ, dendrit_count=None, terminal_count=None
    ):
        dendrit_count = (
            dendrit_count if dendrit_count is not None
            else random.randint(6, 12)
        )

        terminal_count = (
            terminal_count if terminal_count is not None
            else random.randint(5, 10)
        )

        neuron = ReseptorNoron(
            organ, dendrit_count, terminal_count
        )

        organ.add_neuron(neuron)
        return neuron

    # Motor organları

    def add_motor_organ(self, organ):
        if organ not in self.motor_organs:
            self.motor_organs.append(organ)

    def create_motor_organ(self):
        organ = MotorOrgan(0)
        self.add_motor_organ(organ)
        return organ

    def create_motor_neuron(
        self, organ, dendrit_count=None, terminal_count=None
    ):
        dendrit_count = (
            dendrit_count if dendrit_count is not None
            else random.randint(6, 12)
        )

        terminal_count = (
            terminal_count if terminal_count is not None
            else random.randint(5, 10)
        )

        neuron = MotorNoron(
            organ, dendrit_count, terminal_count
        )

        organ.add_neuron(neuron)
        return neuron

    # Bütün nöronları getir

    def _get_all_neurons(self):
        result = []

        result.extend(self.neurons)

        for organ in self.receptor_organs:
            result.extend(organ.receptor_neurons)

        for organ in self.motor_organs:
            result.extend(organ.motor_neurons)

        return result

    # Rastgele sinaps bağlantıları

    def randomize_connections(self):
        sources = self._get_all_neurons()
        targets = self._get_all_neurons()

        random.shuffle(sources)

        for source in sources:
            for terminal in source.synaptic_terminals:
                terminal.disconnect()

                terminal.source_neuron = source
                terminal.available_neurons = targets

                terminal.strength = round(random.uniform(0.2, 0.8), 3)

                # Başlangıçta %60 ihtimalle bağlantı kur.
                if random.random() > 0.60:
                    continue

                possible_targets = [
                    target for target in targets
                    if target is not source
                ]

                random.shuffle(possible_targets)

                for target in possible_targets:
                    available_dendrites = [
                        dendrite for dendrite in target.dendrits
                        if dendrite.presinaps is None
                    ]

                    if not available_dendrites:
                        continue

                    dendrite = random.choice(available_dendrites)
                    terminal.connect(dendrite)
                    break

    # Manuel bağlantı

    def connect(self, source, terminal_index, target, dendrite_index):
        terminal = source.synaptic_terminals[terminal_index]
        dendrite = target.dendrits[dendrite_index]

        terminal.connect(dendrite)

    # Nöronları kimliklendirme

    def _get_all_neurons_with_ids(self):
        result = []

        for i, neuron in enumerate(self.neurons):
            result.append((f"n{i}", neuron))

        for i, organ in enumerate(self.receptor_organs):
            for j, neuron in enumerate(organ.receptor_neurons):
                result.append((f"r{i}_{j}", neuron))

        for i, organ in enumerate(self.motor_organs):
            for j, neuron in enumerate(organ.motor_neurons):
                result.append((f"m{i}_{j}", neuron))

        return result

    # Nöron verilerini paketle

    def _pack_neuron(self, neuron, id_map):
        synapses = []

        for terminal in getattr(neuron, "synaptic_terminals", []):
            target = terminal.dendrit
            target_info = None

            if target is not None:
                target_id = id_map.get(id(target.neuron))

                if target_id is None:
                    raise ValueError(
                        "Bağlantılı nöron Beyin içerisinde kayıtlı değil."
                    )

                dendrite_index = target.neuron.dendrits.index(target)

                target_info = {
                    "neuron": target_id,
                    "dendrite": dendrite_index
                }

            synapses.append({
                "strength": terminal.strength,
                "activation_delay": terminal.activation_delay,
                "target": target_info
            })

        return {
            "dendrit_count": len(neuron.dendrits),
            "terminal_count": len(
                getattr(neuron, "synaptic_terminals", [])
            ),
            "activation_delay": neuron.activation_delay,
            "dendrite_delays": [
                d.activation_delay for d in neuron.dendrits
            ],
            "memory": neuron.memory.copy(),
            "synapses": synapses
        }

    # Kaydetme

    def save(self, path="brain.json"):
        all_neurons = self._get_all_neurons_with_ids()

        id_map = {
            id(neuron): neuron_id
            for neuron_id, neuron in all_neurons
        }

        data = {
            "version": 1,
            "neurons": [],
            "receptor_organs": [],
            "motor_organs": []
        }

        for neuron in self.neurons:
            data["neurons"].append(
                self._pack_neuron(neuron, id_map)
            )

        for organ in self.receptor_organs:
            data["receptor_organs"].append({
                "neurons": [
                    self._pack_neuron(n, id_map)
                    for n in organ.receptor_neurons
                ]
            })

        for organ in self.motor_organs:
            data["motor_organs"].append({
                "processing_delay": organ.processing_delay,
                "tokens": organ.tokens.copy(),
                "neurons": [
                    self._pack_neuron(n, id_map)
                    for n in organ.motor_neurons
                ]
            })

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    # Yükleme

    @classmethod
    def load(cls, path="brain.json"):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if data.get("version") != 1:
            raise ValueError("Desteklenmeyen beyin kayıt sürümü.")

        brain = cls(randomize=False)

        neuron_map = {}
        pending_connections = []

        def restore_common(neuron, neuron_id, spec):
            neuron.activation_delay = spec["activation_delay"]
            neuron.memory = spec["memory"].copy()

            for dendrite, delay in zip(
                neuron.dendrits,
                spec["dendrite_delays"]
            ):
                dendrite.activation_delay = delay

            neuron_map[neuron_id] = neuron
            pending_connections.append((neuron, spec))

        # Normal nöronlar

        for i, spec in enumerate(data["neurons"]):
            neuron = Noron(
                spec["dendrit_count"],
                spec["terminal_count"]
            )

            restore_common(neuron, f"n{i}", spec)
            brain.add_neuron(neuron)

        # Reseptör organları

        for i, organ_spec in enumerate(data["receptor_organs"]):
            organ = ReseptorOrgan()

            for j, spec in enumerate(organ_spec["neurons"]):
                neuron = ReseptorNoron(
                    organ,
                    spec["dendrit_count"],
                    spec["terminal_count"]
                )

                organ.add_neuron(neuron)
                restore_common(neuron, f"r{i}_{j}", spec)

            brain.add_receptor_organ(organ)

        # Motor organları

        for i, organ_spec in enumerate(data["motor_organs"]):
            organ = MotorOrgan(len(organ_spec["neurons"]))

            organ.processing_delay = organ_spec["processing_delay"]
            organ.tokens = organ_spec["tokens"].copy()

            for j, spec in enumerate(organ_spec["neurons"]):
                terminal_count = spec.get(
                    "terminal_count",
                    len(spec.get("synapses", []))
                )

                neuron = MotorNoron(
                    organ,
                    spec["dendrit_count"],
                    terminal_count
                )

                organ.add_neuron(neuron)
                restore_common(neuron, f"m{i}_{j}", spec)

            brain.add_motor_organ(organ)

        # Sinaps bağlantılarını yeniden kur

        for neuron, spec in pending_connections:
            terminals = neuron.synaptic_terminals

            for terminal, synapse_data in zip(
                terminals,
                spec["synapses"]
            ):
                terminal.strength = synapse_data["strength"]
                terminal.activation_delay = synapse_data["activation_delay"]

                target_info = synapse_data["target"]

                if target_info is not None:
                    target_neuron = neuron_map[target_info["neuron"]]

                    target_dendrite = target_neuron.dendrits[
                        target_info["dendrite"]
                    ]

                    terminal.connect(target_dendrite)

        all_neurons = brain._get_all_neurons()

        for neuron in all_neurons:
            for terminal in neuron.synaptic_terminals:
                terminal.source_neuron = neuron
                terminal.available_neurons = all_neurons

        return brain

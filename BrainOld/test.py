
import time
import random

from BrainOld.Beyin import Beyin


# 1. Yeni beyin oluştur
brain = Beyin(
    neuron_count=20,
    receptor_organ_count=1,
    receptor_neuron_count=2,
    motor_organ_count=1,
    motor_neuron_count=1,
    randomize=True
)

receptor_organ = brain.receptor_organs[0]
motor_organ = brain.motor_organs[0]
motor_neuron = motor_organ.motor_neurons[0]

print("Beyin oluşturuldu.")
print("Normal nöron:", len(brain.neurons))
print("Reseptör nöronu:", len(receptor_organ.receptor_neurons))
print("Motor nöronu:", len(motor_organ.motor_neurons))

# 2. Girdi uzunluğunu hesapla
input_length = sum(
    len(neuron.dendrits)
    for neuron in receptor_organ.receptor_neurons
)

binary_input = "1" * input_length

print("\nGirdi:", binary_input)
print("Girdi uzunluğu:", input_length)

# 3. Sinyali gönder
trace = receptor_organ.receive(binary_input)

print("\nSinyal gönderildi. Ağın ilerlemesi bekleniyor...")

# 4. Motor nöronuna ulaşmasını bekle
timeout = 30
start = time.monotonic()

while time.monotonic() - start < timeout:
    if motor_neuron.last_trace is trace:
        break

    time.sleep(0.05)

# 5. Sonucu incele
if motor_neuron.last_trace is not trace:
    print("\nMotor nöronuna ulaşılmadı.")
else:
    print("\nMotor nöronuna ulaşıldı!")

    with trace.lock:
        records = list(trace.records)

    print("Başarılı iletim sayısı:", len(records))

    for i, record in enumerate(records, 1):
        source = record["source_neuron"]
        target = record["target_neuron"]
        dendrite = record["target_dendrite"]

        print(f"\n--- İletim {i} ---")
        print("Kaynak:", type(source).__name__)
        print("Kaynak girdisi:", record["source_input"])
        print("Kaynak çıktısı:", record["source_output"])
        print("Hedef:", type(target).__name__)
        print(
            "Hedef dendrit:",
            target.dendrits.index(dendrite)
        )
        print(
            "Sinaps gücü:",
            record["terminal"].strength
        )

    # 6. Pozitif feedback
    before = [
        record["terminal"].strength
        for record in records
    ]

    print("\nPozitif feedback gönderiliyor...")

    motor_neuron.feedback(True)

    after = [
        record["terminal"].strength
        for record in records
    ]

    print("\nÖnceki güçler:", before)
    print("Yeni güçler:", after)

    # 7. Tekrar feedback gönderilemediğini kontrol et
    second_attempt = motor_neuron.feedback(False)

    print("\nİkinci feedback kabul edildi mi?", second_attempt)

print("\nTest sona erdi.")

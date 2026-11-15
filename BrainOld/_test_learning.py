import random
import time

from BrainOld.Beyin import Beyin


# BEYİN OLUŞTUR
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

input_length = sum(
    len(n.dendrits)
    for n in receptor_organ.receptor_neurons
)

binary_input = "1" * input_length

print("Beyin oluşturuldu.")
print("Girdi:", binary_input)
print("Girdi uzunluğu:", input_length)

results = []

# 20 ÖĞRENME TURU
output_length = sum(
    len(neuron.synaptic_terminals)
    for neuron in motor_organ.motor_neurons
)

target_output = "".join(
    random.choice("01")
    for _ in range(output_length)
)

print("Hedef çıktı:", target_output)
print("Çıktı uzunluğu:", output_length)
round_count = 20

for turn in range(1, round_count + 1):
    previous_count = motor_organ.output_count

    trace = receptor_organ.receive(binary_input)

    # Motor nöronunun bu girdiye ulaşmasını bekle
    timeout = time.time() + 10

    while time.time() < timeout:
        if motor_neuron.last_trace is trace:
            break
        time.sleep(0.01)
    else:
        print(f"{turn}. tur: Motor nörona ulaşılamadı.")
        continue

    # Motor organının çıktısını bekle
    timeout = time.time() + 3

    while time.time() < timeout:
        if motor_organ.output_count > previous_count:
            break
        time.sleep(0.01)
    else:
        print(f"{turn}. tur: Çıktı alınamadı.")
        continue

    output = motor_organ.last_output

    accuracy = sum(
        a == b for a, b in zip(output, target_output)
    ) / len(target_output)

    amount = accuracy * 0.01

    if accuracy >= 0.5:
        motor_neuron.feedback(amount, positive=True)
        print(f"Ödül: {amount}")
    else:
        motor_neuron.feedback((1 - accuracy) * 0.01, positive=False)
        print(f"Ceza: {(1 - accuracy) * 0.01}")

    if output == target_output:
        result = "BAŞARILI"
    else:
        result = "BAŞARISIZ"

    print(
        f"{turn:02} | "
        f"Çıktı: {output} | "
        f"Hedef: {target_output} | "
        f"{result} "
        f"Doğruluk: {accuracy}"
    )


# # SONUÇLAR
# print("\n\n========== DENEY SONUÇLARI ==========")

# for result in results:
#     print(
#         f"Tur {result['turn']:02}: "
#         f"Çıktı={result['output']} | "
#         f"İletim={result['transmissions']} | "
#         f"Feedback={result['feedback']}"
#     )

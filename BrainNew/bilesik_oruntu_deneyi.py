from BrainNew.Beyin import Beyin


def denemeyi_calistir(beyin, girdi, adim_sayisi=20):
    cikti = beyin.isle(girdi, adim_sayisi=adim_sayisi)
    beyin.deneme_sonu_sifirla()
    return cikti


beyin = Beyin(
    girdi_sayisi=2,
    cikti_sayisi=1,
    ara_noron_sayisi=30,
    seed=42
)

motor = beyin.motor_noronlari[0]

# Eğitimde yalnızca tekil örüntüler gösterilir.
egitim_oruntuleri = [
    ([1, 0], [1]),
    ([0, 1], [1]),
]

# İki öğrenilmiş özelliğin birleşimi eğitimde gösterilmez.
test_oruntusu = ([1, 1], [1])

epoch_sayisi = 20
adim_sayisi = 20


print("BİRLEŞİK ÖRÜNTÜ DENEYİ")
print("-" * 78)
print("Hipotez: Ayrı ayrı öğrenilen iki girdi örüntüsü birlikte sunulduğunda")
print("ağ, bu birleşime de doğru tepki verebilecek mi?")
print()

print("EĞİTİM ÖNCESİ")
for girdi, beklenen in egitim_oruntuleri + [test_oruntusu]:
    cikti = denemeyi_calistir(beyin, girdi, adim_sayisi)
    print(
        f"Girdi: {girdi} | Çıktı: {cikti} | "
        f"Beklenen: {beklenen} | Doğru: {cikti == beklenen}"
    )

print()
print("EĞİTİM")

toplam_duzeltme = 0

for epoch in range(1, epoch_sayisi + 1):
    dogru_sayisi = 0

    for girdi, beklenen in egitim_oruntuleri:
        cikti = beyin.isle(girdi, adim_sayisi=adim_sayisi)
        dogru = cikti == beklenen

        if dogru:
            dogru_sayisi += 1
        else:
            # Beklenen çıktı 1, gerçekleşen çıktı 0:
            # öğretici sinyal doğrudan hedef motor nöronuna gönderilir.
            beyin.geri_bildirim(
                1.0,
                baslangic_noronlari=[motor]
            )
            toplam_duzeltme += 1

        beyin.deneme_sonu_sifirla()

    print(
        f"Epoch: {epoch:02d} | "
        f"Eğitim doğruluğu: {dogru_sayisi}/{len(egitim_oruntuleri)}"
    )

print()
print("EĞİTİM SONRASI - GERİ BİLDİRİMSİZ TEST")

testler = egitim_oruntuleri + [test_oruntusu]
dogru_sayisi = 0

for girdi, beklenen in testler:
    cikti = denemeyi_calistir(beyin, girdi, adim_sayisi)
    dogru = cikti == beklenen

    if dogru:
        dogru_sayisi += 1

    etiket = "EĞİTİM ÖRÜNTÜSÜ" if (girdi, beklenen) in egitim_oruntuleri else "GÖRÜLMEMİŞ BİRLEŞİM"
    print(
        f"Girdi: {girdi} | Çıktı: {cikti} | "
        f"Beklenen: {beklenen} | Doğru: {dogru} | {etiket}"
    )

print("-" * 78)
print(f"Eğitim sırasında geri bildirim sayısı: {toplam_duzeltme}")
print(f"Test doğruluğu: {dogru_sayisi}/{len(testler)}")
print("Deney tamamlandı.")

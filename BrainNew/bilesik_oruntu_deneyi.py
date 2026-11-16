from BrainNew.Beyin import Beyin


def denemeyi_calistir(beyin, girdi, adim_sayisi=20):
    cikti = beyin.isle(girdi, adim_sayisi=adim_sayisi)
    beyin.deneme_sonu_sifirla()
    return cikti


beyin = Beyin(
    girdi_sayisi=3,
    cikti_sayisi=1,
    ara_noron_sayisi=30,
    seed=42
)

motor = beyin.motor_noronlari[0]

# Eğitim örüntüleri:
# [1, 1, 0] -> 1 : pozitif sınıf
# [0, 0, 1] -> 0 : negatif sınıf
egitim_oruntuleri = [
    ([1, 1, 0], [1]),
    ([0, 0, 1], [0]),
]

# Bu örüntü eğitimde gösterilmez. Pozitif örüntünün
# bir özelliği eksik olmasına rağmen aynı sınıfta olmalıdır.
gorulmemis_oruntu = ([1, 0, 0], [1])

epoch_sayisi = 30
adim_sayisi = 20


def ciktiyi_ogret(beyin, motor, cikti, beklenen):
    if cikti == beklenen:
        return False

    # Tek motorlu ikili görev:
    # beklenen 1, gerçek 0 -> pozitif geri bildirim
    # beklenen 0, gerçek 1 -> negatif geri bildirim
    deger = 1.0 if beklenen[0] == 1 else -1.0
    beyin.geri_bildirim(deger, baslangic_noronlari=[motor])
    return True


print("ÖRÜNTÜ AYIRT ETME VE GENELLEME DENEYİ")
print("-" * 82)
print("Hipotez: Ağ, pozitif ve negatif örüntüleri ayırt etmeyi öğrenirken,")
print("eğitimde görmediği fakat pozitif örüntüyle ortak özellik taşıyan")
print("bir örüntüyü de pozitif sınıfa atayabilecek mi?")
print()

print("EĞİTİM ÖNCESİ")
for girdi, beklenen in egitim_oruntuleri + [gorulmemis_oruntu]:
    cikti = denemeyi_calistir(beyin, girdi, adim_sayisi)
    print(
        f"Girdi: {girdi} | Çıktı: {cikti} | "
        f"Beklenen: {beklenen} | Doğru: {cikti == beklenen}"
    )

print()
print("EĞİTİM")

for epoch in range(1, epoch_sayisi + 1):
    dogru_sayisi = 0
    geri_bildirim_sayisi = 0

    for girdi, beklenen in egitim_oruntuleri:
        cikti = beyin.isle(girdi, adim_sayisi=adim_sayisi)

        if cikti == beklenen:
            dogru_sayisi += 1
        elif ciktiyi_ogret(beyin, motor, cikti, beklenen):
            geri_bildirim_sayisi += 1

        beyin.deneme_sonu_sifirla()

    print(
        f"Epoch: {epoch:02d} | "
        f"Eğitim doğruluğu: {dogru_sayisi}/{len(egitim_oruntuleri)} | "
        f"Geri bildirim: {geri_bildirim_sayisi}"
    )

print()
print("EĞİTİM SONRASI - GERİ BİLDİRİMSİZ TEST")

testler = egitim_oruntuleri + [gorulmemis_oruntu]
dogru_sayisi = 0

for girdi, beklenen in testler:
    cikti = denemeyi_calistir(beyin, girdi, adim_sayisi)
    dogru = cikti == beklenen
    dogru_sayisi += int(dogru)

    if (girdi, beklenen) == gorulmemis_oruntu:
        etiket = "GÖRÜLMEMİŞ BENZER ÖRÜNTÜ"
    else:
        etiket = "EĞİTİM ÖRÜNTÜSÜ"

    print(
        f"Girdi: {girdi} | Çıktı: {cikti} | "
        f"Beklenen: {beklenen} | Doğru: {dogru} | {etiket}"
    )

print("-" * 82)
print(f"Test doğruluğu: {dogru_sayisi}/{len(testler)}")
print("Deney tamamlandı.")

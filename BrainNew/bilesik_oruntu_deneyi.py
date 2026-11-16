import random

from BrainNew.Beyin import Beyin


# Görev: f(x1, x2, x3) = x1
# x2 ve x3 sonucu belirlememeli.
#
# Sekiz olası girdinin altısı eğitimde, ikisi yalnızca testte kullanılır.
# Test örnekleri eğitimde görülmeyen x2=x3=1 birleşimidir.
# Böylece her sınıfta x2 ve x3'ün 0 ve 1 değerleri eğitimde temsil edilir.

GIZLI_NORON_SAYISI = 100
AG_SEED = 42
KARISTIRMA_SEED = 43
ADIM_SAYISI = 32
MAKS_EPOCH = 200
ERKEN_DURDURMA_ESIGI = 5

egitim_oruntuleri = [
    ([1, 0, 0], [1]),
    ([1, 0, 1], [1]),
    ([1, 1, 0], [1]),
    ([0, 0, 0], [0]),
    ([0, 0, 1], [0]),
    ([0, 1, 0], [0]),
]

test_oruntuleri = [
    ([1, 1, 1], [1]),
    ([0, 1, 1], [0]),
]


def denemeyi_calistir(beyin, girdi):
    cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)
    beyin.deneme_sonu_sifirla()
    return cikti


def geri_bildirim_uygula(beyin, motor, cikti, beklenen):
    if cikti == beklenen:
        return False

    deger = 1.0 if beklenen[0] == 1 else -1.0
    beyin.geri_bildirim(deger, baslangic_noronlari=[motor])
    return True


def degerlendir(beyin, oruntuler):
    dogru = 0
    sonuclar = []

    for girdi, beklenen in oruntuler:
        cikti = denemeyi_calistir(beyin, girdi)
        basarili = cikti == beklenen
        dogru += int(basarili)
        sonuclar.append((girdi, beklenen, cikti, basarili))

    return dogru, sonuclar


beyin = Beyin(
    girdi_sayisi=3,
    cikti_sayisi=1,
    ara_noron_sayisi=GIZLI_NORON_SAYISI,
    seed=AG_SEED,
)
motor = beyin.motor_noronlari[0]
karistirici = random.Random(KARISTIRMA_SEED)

print("GENELLEME DENEYİ - GENİŞLETİLMİŞ ÖRNEKLEM")
print("=" * 88)
print("Kural: çıktı = ilk girdi biti (x1)")
print(f"Ara nöron: {GIZLI_NORON_SAYISI} | Eğitim örüntüsü: {len(egitim_oruntuleri)}")
print(f"Test örüntüsü: {len(test_oruntuleri)} | Maksimum epoch: {MAKS_EPOCH}")
print("Test örüntüleri eğitim sırasında kesinlikle kullanılmayacak.")
print()

egitim_oncesi, on_sonuclar = degerlendir(
    beyin, egitim_oruntuleri + test_oruntuleri
)
print(f"Eğitim öncesi: {egitim_oncesi}/8")
for girdi, beklenen, cikti, dogru in on_sonuclar:
    print(
        f"  {girdi} -> beklenen {beklenen}, çıkan {cikti}, "
        f"{'DOĞRU' if dogru else 'YANLIŞ'}"
    )

print()
print("EĞİTİM")
print("-" * 88)

ardisik_tam_basari = 0
geribildirim_toplami = 0
tam_basariya_ulasilan_epoch = None
gercek_epoch = 0

for epoch in range(1, MAKS_EPOCH + 1):
    sirali_oruntuler = egitim_oruntuleri.copy()
    karistirici.shuffle(sirali_oruntuler)

    dogru = 0
    geribildirim = 0

    for girdi, beklenen in sirali_oruntuler:
        cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)

        if cikti == beklenen:
            dogru += 1
        elif geri_bildirim_uygula(beyin, motor, cikti, beklenen):
            geribildirim += 1

        beyin.deneme_sonu_sifirla()

    gercek_epoch = epoch
    geribildirim_toplami += geribildirim

    if dogru == len(egitim_oruntuleri):
        ardisik_tam_basari += 1
    else:
        ardisik_tam_basari = 0

    print(
        f"Epoch {epoch:03d} | Eğitim: {dogru}/{len(egitim_oruntuleri)} "
        f"| Geri bildirim: {geribildirim}"
    )

    # Eğitim örneklerinin tamamında beş epoch üst üste doğru çıktı
    # alındığında dur. Test kümesi erken durdurma için kullanılmaz.
    if ardisik_tam_basari >= ERKEN_DURDURMA_ESIGI:
        tam_basariya_ulasilan_epoch = epoch - ERKEN_DURDURMA_ESIGI + 1
        print(
            f"Eğitim durduruldu: {ERKEN_DURDURMA_ESIGI} ardışık "
            "epoch boyunca eğitim başarısı tam."
        )
        break

print()
print("EĞİTİM SONRASI - GERİ BİLDİRİMSİZ DEĞERLENDİRME")
print("-" * 88)

egitim_dogrusu, egitim_sonuclari = degerlendir(beyin, egitim_oruntuleri)
test_dogrusu, test_sonuclari = degerlendir(beyin, test_oruntuleri)

for etiket, sonuclar in (
    ("EĞİTİM", egitim_sonuclari),
    ("GÖRÜLMEMİŞ TEST", test_sonuclari),
):
    print(f"{etiket}:")
    for girdi, beklenen, cikti, dogru in sonuclar:
        print(
            f"  {girdi} -> beklenen {beklenen}, çıkan {cikti}, "
            f"{'DOĞRU' if dogru else 'YANLIŞ'}"
        )

print()
print("=" * 88)
print(f"Gerçekleşen epoch: {gercek_epoch}/{MAKS_EPOCH}")
print(f"Toplam geri bildirim: {geribildirim_toplami}")
print(
    "Eğitim başarısı: "
    f"{egitim_dogrusu}/{len(egitim_oruntuleri)} "
    f"({egitim_dogrusu / len(egitim_oruntuleri) * 100:.1f}%)"
)
print(
    "Genelleme başarısı: "
    f"{test_dogrusu}/{len(test_oruntuleri)} "
    f"({test_dogrusu / len(test_oruntuleri) * 100:.1f}%)"
)
print(
    "Birleşik başarı: "
    f"{egitim_dogrusu + test_dogrusu}/8 "
    f"({(egitim_dogrusu + test_dogrusu) / 8 * 100:.1f}%)"
)
print("=" * 88)

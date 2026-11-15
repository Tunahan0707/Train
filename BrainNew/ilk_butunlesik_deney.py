
from Beyin import Beyin


beyin = Beyin(
    girdi_sayisi=1,
    cikti_sayisi=1,
    ara_noron_sayisi=0,
    seed=42
)

reseptor = beyin.reseptor_noronlari[0]
motor = beyin.motor_noronlari[0]

# Rastgele bağlantıları temizle.
for noron in beyin.noronlar:
    for akson in noron.aksonlar:
        for baglanti in tuple(akson.baglantilar):
            baglanti.sil()

# Aynı reseptör nöronunun iki ayrı akson terminali.
baglantilar = []

for indeks in range(2):
    baglanti = reseptor.aksonlar[indeks].baglan(
        motor.dendritler[0],
        etki_mv=10.0,
        gecikme_ms=1
    )
    baglantilar.append(baglanti)

beklenen_cikti = [0]
deneme_sayisi = 20

print("İLK BÜTÜNLEŞİK DENEY - DÜZELTİLMİŞ")
print("-" * 75)

for deneme in range(1, deneme_sayisi + 1):

    cikti = beyin.isle([1], adim_sayisi=6)

    dogru = cikti == beklenen_cikti

    if not dogru:
        beyin.geri_bildirim(-1.0)

    toplam_etki = sum(
        b.etki_mv for b in baglantilar if b.aktif
    )

    print(
        f"Deneme: {deneme:02d} | "
        f"Çıktı: {cikti} | "
        f"Doğru: {dogru} | "
        f"Toplam etki: {toplam_etki:.4f} | "
        f"İzler: {[round(b.uygunluk_izi, 4) for b in baglantilar]}"
    )

    # Öğrenilmiş bağlantı durumunu koruyarak
    # geçici fizyolojik durumu sıfırla.
    beyin.deneme_sonu_sifirla()

print("-" * 75)
print("Deney tamamlandı.")

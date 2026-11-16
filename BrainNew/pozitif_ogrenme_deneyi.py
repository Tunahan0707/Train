from BrainNew.Beyin import Beyin


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

# Başlangıçta motor nöronunu ateşletmeyecek zayıf uyarıcı bağlantılar.
for indeks in range(2):
    reseptor.aksonlar[indeks].baglan(
        motor.dendritler[0],
        etki_mv=2.0,
        gecikme_ms=1
    )

beklenen_cikti = [1]
deneme_sayisi = 30

print("POZİTİF ÖĞRENME DENEYİ")
print("-" * 90)

for deneme in range(1, deneme_sayisi + 1):
    cikti = beyin.isle([1], adim_sayisi=6)
    dogru = cikti == beklenen_cikti

    if not dogru:
        # Motor ateşlenmemiş olsa da öğretici sinyal hedefe ulaşmalı.
        beyin.geri_bildirim(
            1.0,
            baslangic_noronlari=[motor]
        )

    etkin_baglantilar = [
        baglanti
        for akson in reseptor.aksonlar
        for baglanti in akson.baglantilar
        if baglanti.aktif
    ]
    toplam_etki = sum(b.etki_mv for b in etkin_baglantilar)

    print(
        f"Deneme: {deneme:02d} | "
        f"Çıktı: {cikti} | "
        f"Doğru: {dogru} | "
        f"Etkin bağlantı: {len(etkin_baglantilar):02d} | "
        f"Toplam etki: {toplam_etki:.4f}"
    )

    # Öğrenilmiş bağlantıları koruyup geçici durumu sıfırla.
    beyin.deneme_sonu_sifirla()

print("-" * 90)
print("Deney tamamlandı.")

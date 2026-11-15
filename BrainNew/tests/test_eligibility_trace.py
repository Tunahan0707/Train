from BrainNew import Beyin, Noron


def baglanti_ateslenmesi(kaynak, hedef, etki=2.0):
    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=etki
    )
    hedef.membran_potansiyeli = -56.0
    baglanti.aktar(0)
    assert hedef.guncelle()
    return baglanti


def test_iletim_tek_basina_uygunluk_izi_olusturmaz():
    kaynak = Noron()
    hedef = Noron()
    baglanti = kaynak.aksonlar[0].baglan(hedef.dendritler[0])

    baglanti.aktar(0)

    assert baglanti.uygunluk_izi == 0.0
    assert baglanti.aktarim_sayisi == 1


def test_ateslenmeye_pozitif_katki_yapan_baglanti_iz_kazanir():
    kaynak = Noron()
    hedef = Noron()

    baglanti = baglanti_ateslenmesi(kaynak, hedef)

    assert baglanti.uygunluk_izi == 1.0


def test_ateslenmeye_negatif_katki_yapan_baglanti_iz_kazanmaz():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=-2.0
    )
    hedef.membran_potansiyeli = -50.0
    baglanti.aktar(0)
    assert hedef.guncelle()

    assert baglanti.uygunluk_izi == 0.0


def test_uygunluk_izi_belirlenen_ust_siniri_asmaz():
    kaynak = Noron()
    hedef = Noron()
    baglanti = kaynak.aksonlar[0].baglan(hedef.dendritler[0])

    for _ in range(10):
        baglanti.uygunluk_izini_artir()

    assert baglanti.uygunluk_izi == 5.0


def test_uygunluk_izi_zamanla_azalir():
    kaynak = Noron()
    hedef = Noron()
    baglanti = kaynak.aksonlar[0].baglan(hedef.dendritler[0])
    baglanti.uygunluk_izini_artir()

    baglanti.izi_azalt()

    assert baglanti.uygunluk_izi == 0.95


def test_uygunluk_izi_olmayan_baglanti_geri_bildirime_katilmaz():
    kaynak = Noron()
    hedef = Noron()
    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=2.0
    )

    hedef.geri_bildirim(-1.0)

    assert baglanti.etki_mv == 2.0
    assert baglanti.aktif


def test_beyin_esigi_altindaki_izleri_etkin_listeden_cikarir():
    beyin = Beyin(1, 1, 1, seed=42)
    kaynak = beyin.noronlar[0]
    hedef = beyin.noronlar[1]
    baglanti = kaynak.aksonlar[0].baglan(hedef.dendritler[0])

    baglanti.uygunluk_izi = 0.009
    beyin.etkin_baglantilar.add(baglanti)
    beyin.uygunluk_izlerini_guncelle()

    assert baglanti not in beyin.etkin_baglantilar
    assert baglanti.aktif

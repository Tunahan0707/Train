from BrainNew import Noron


def baglanti_ateslendir(etki):
    kaynak = Noron()
    hedef = Noron()
    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=etki
    )
    hedef.membran_potansiyeli = -56.0 if etki >= 1.0 else -54.2
    baglanti.aktar(0)
    assert hedef.guncelle()
    return kaynak, hedef, baglanti


def test_negatif_geri_bildirim_baglantiyi_zayiflatir():
    kaynak, hedef, baglanti = baglanti_ateslendir(2.0)
    hedef.geri_bildirim(-1.0)
    assert baglanti.etki_mv < 2.0
    assert baglanti.aktif


def test_negatif_geri_bildirim_zayif_baglantiyi_budar():
    kaynak, hedef, baglanti = baglanti_ateslendir(0.5)
    hedef.geri_bildirim(-1.0)
    assert not baglanti.aktif
    assert baglanti not in kaynak.aksonlar[0].baglantilar
    assert baglanti not in hedef.dendritler[0].gelen_baglantilar


def test_geri_bildirim_baglantinin_isaretini_degistirebilir():
    _, hedef, baglanti = baglanti_ateslendir(0.2)
    baglanti.uygunluk_izini_artir()
    hedef.geri_bildirim(-1.0)
    assert baglanti.aktif
    assert baglanti.etki_mv < 0


def test_uygunluk_izi_olmayan_baglanti_degismez():
    kaynak = Noron()
    hedef = Noron()
    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=2.0
    )
    hedef.geri_bildirim(-1.0)
    assert baglanti.etki_mv == 2.0
    assert baglanti.aktif


from BrainNew.Noron import Noron


def test_negatif_geri_bildirim_baglantiyi_zayiflatir():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=2.0
    )

    baglanti.aktar(0)
    hedef.geri_bildirim(-1.0)

    assert baglanti.etki_mv < 2.0
    assert baglanti.aktif


def test_negatif_geri_bildirim_zayif_baglantiyi_budar():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=0.5
    )

    baglanti.aktar(0)
    hedef.geri_bildirim(-1.0)

    assert not baglanti.aktif
    assert baglanti not in kaynak.aksonlar[0].baglantilar
    assert baglanti not in hedef.dendritler[0].gelen_baglantilar


def test_geri_bildirim_baglantinin_isaretini_degistirebilir():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0],
        etki_mv=0.3
    )

    baglanti.aktar(0)
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

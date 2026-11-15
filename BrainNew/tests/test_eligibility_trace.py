
from BrainNew.Noron import Noron
from BrainNew.Beyin import Beyin


def test_her_iletim_uygunluk_izini_artirir():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    baglanti.aktar(0)
    ilk_iz = baglanti.uygunluk_izi

    baglanti.aktar(1)

    assert ilk_iz > 0
    assert baglanti.uygunluk_izi > ilk_iz


def test_uygunluk_izi_belirlenen_ust_siniri_asmaz():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    for zaman in range(20):
        baglanti.aktar(zaman)

    assert baglanti.uygunluk_izi <= 5.0


def test_uygunluk_izi_zamanla_azalir():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    baglanti.aktar(0)
    ilk_iz = baglanti.uygunluk_izi

    baglanti.izi_azalt()

    assert baglanti.uygunluk_izi < ilk_iz
    assert baglanti.uygunluk_izi > 0


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

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    baglanti.uygunluk_izi = 0.009
    beyin.etkin_baglantilar.add(baglanti)

    beyin.uygunluk_izlerini_guncelle()

    assert baglanti not in beyin.etkin_baglantilar
    assert baglanti.aktif

from BrainNew.Noron import Noron
from BrainNew.Beyin import Beyin


def test_her_iletim_uygunluk_izini_artirir():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    baglanti.aktar(0)
    ilk_iz = baglanti.uygunluk_izi

    baglanti.aktar(1)

    assert ilk_iz > 0
    assert baglanti.uygunluk_izi > ilk_iz


def test_uygunluk_izi_belirlenen_ust_siniri_asmaz():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    for zaman in range(20):
        baglanti.aktar(zaman)

    assert baglanti.uygunluk_izi <= 5.0


def test_uygunluk_izi_zamanla_azalir():
    kaynak = Noron()
    hedef = Noron()

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    baglanti.aktar(0)
    ilk_iz = baglanti.uygunluk_izi

    baglanti.izi_azalt()

    assert baglanti.uygunluk_izi < ilk_iz
    assert baglanti.uygunluk_izi > 0


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

    baglanti = kaynak.aksonlar[0].baglan(
        hedef.dendritler[0]
    )

    baglanti.uygunluk_izi = 0.009
    beyin.etkin_baglantilar.add(baglanti)

    beyin.uygunluk_izlerini_guncelle()

    assert baglanti not in beyin.etkin_baglantilar
    assert baglanti.aktif

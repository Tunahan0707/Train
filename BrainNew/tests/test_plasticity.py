
import pytest

from BrainNew import Beyin, Noron


def baglanti_olustur(etki=2.0):
    noron_a = Noron()
    noron_b = Noron()

    baglanti = noron_a.aksonlar[0].baglan(
        noron_b.dendritler[0],
        etki_mv=etki
    )

    return noron_a, noron_b, baglanti


def test_aktivite_izi_aktarimla_artar():
    _, _, baglanti = baglanti_olustur()

    baglanti.aktar(0)

    assert baglanti.uygunluk_izi == 1.0
    assert baglanti.aktarim_sayisi == 1


def test_aktivite_izi_zamanla_azalir():
    _, _, baglanti = baglanti_olustur()

    baglanti.aktar(0)
    baglanti.izi_azalt()

    assert baglanti.uygunluk_izi == pytest.approx(0.95)


def test_olumlu_geri_bildirim_baglantiyi_guclendirir():
    _, _, baglanti = baglanti_olustur()

    baglanti.aktar(0)
    eski_etki = baglanti.etki_mv

    baglanti.geri_bildirim(1.0)

    assert baglanti.etki_mv > eski_etki


def test_olumsuz_geri_bildirim_baglantiyi_zayiflatir():
    _, _, baglanti = baglanti_olustur()

    baglanti.aktar(0)
    eski_etki = baglanti.etki_mv

    baglanti.geri_bildirim(-1.0)

    assert baglanti.etki_mv < eski_etki


def test_olumsuz_geri_bildirim_isareti_degistirebilir():
    _, _, baglanti = baglanti_olustur(etki=0.2)

    baglanti.aktar(0)
    baglanti.geri_bildirim(-1.0)

    assert baglanti.etki_mv < 0


def test_aktivite_izi_yoksa_geri_bildirim_etkisizdir():
    _, _, baglanti = baglanti_olustur()

    eski_etki = baglanti.etki_mv

    baglanti.geri_bildirim(1.0)

    assert baglanti.etki_mv == eski_etki


def test_beyin_geri_bildirim_aktif_baglantilari_etkiler():
    beyin = Beyin(4, 2, 5, seed=42)

    noron_a = beyin.noronlar[0]
    noron_b = beyin.noronlar[1]

    baglanti = noron_a.aksonlar[0].baglan(
        noron_b.dendritler[0],
        etki_mv=2.0
    )

    baglanti.aktar(0)
    beyin.etkin_baglantilar.add(baglanti)

    noron_b.geri_bildirim(1.0)

    assert baglanti.etki_mv > 2.0


def test_geri_bildirim_zayif_baglantiyi_budar():
    beyin = Beyin(4, 2, 5, seed=42)

    noron_a = beyin.noronlar[0]
    noron_b = beyin.noronlar[1]

    baglanti = noron_a.aksonlar[0].baglan(
        noron_b.dendritler[0],
        etki_mv=0.5
    )

    baglanti.aktar(0)
    beyin.etkin_baglantilar.add(baglanti)

    noron_b.geri_bildirim(-1.0)

    assert not baglanti.aktif
    assert baglanti not in noron_a.aksonlar[0].baglantilar
    assert baglanti not in noron_b.dendritler[0].gelen_baglantilar


def test_gecersiz_geri_bildirim():
    beyin = Beyin(4, 2, 5, seed=42)

    with pytest.raises(ValueError):
        beyin.geri_bildirim(2.0)

    with pytest.raises(ValueError):
        beyin.geri_bildirim(-2.0)

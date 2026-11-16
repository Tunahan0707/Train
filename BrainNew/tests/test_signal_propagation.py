from collections import Counter

from BrainNew.Beyin import Beyin


def test_duyusal_uyaran_sunum_boyunca_reseptoru_tekrar_atese_surukler():
    beyin = Beyin(1, 1, 0, seed=11)

    # Yalnizca reseptorun uyaran cevabini olc.
    for noron in beyin.noronlar:
        for akson in noron.aksonlar:
            for baglanti in tuple(akson.baglantilar):
                baglanti.sil()

    reseptor = beyin.reseptor_noronlari[0]
    beyin.girdi_al([1])

    for _ in range(16):
        beyin.adim()

    # Aksiyon potansiyonu/refrakter dongusu 5 ms'de bir ateslenmeye izin verir.
    assert reseptor.ateslenme_sayisi == 4


def test_sinyal_omurgasi_hesaplanan_fanout_ve_fanin_degerlerini_kurar():
    beyin = Beyin(3, 1, 100, seed=42)
    ara_kumesi = set(beyin.ara_noronlar)
    motor = beyin.motor_noronlari[0]

    for reseptor in beyin.reseptor_noronlari:
        baglantilar = [
            baglanti
            for akson in reseptor.aksonlar
            for baglanti in akson.baglantilar
        ]
        hedefler = {baglanti.hedef.noron for baglanti in baglantilar}

        assert len(hedefler) == 25
        assert hedefler <= ara_kumesi
        assert len(baglantilar) == 25
        assert all(b.etki_mv == 5.6 for b in baglantilar)

    motor_baglantilari = [
        baglanti
        for noron in beyin.ara_noronlar
        for akson in noron.aksonlar
        for baglanti in akson.baglantilar
        if baglanti.hedef.noron is motor
    ]
    kaynak_sayilari = Counter(
        baglanti.kaynak.noron for baglanti in motor_baglantilari
    )

    assert len(kaynak_sayilari) == 75
    assert len(motor_baglantilari) == 75 * 3
    assert set(kaynak_sayilari.values()) == {3}

    for kaynak in kaynak_sayilari:
        kaynak_baglantilari = [
            b for b in motor_baglantilari
            if b.kaynak.noron is kaynak
        ]
        assert len({b.gecikme_ms for b in kaynak_baglantilari}) == 1
        assert all(b.etki_mv == 5.6 for b in kaynak_baglantilari)


def test_reseptorden_ara_norona_ve_motor_noronuna_sinyal_ulasir():
    beyin = Beyin(3, 1, 100, seed=42)
    reseptor = beyin.reseptor_noronlari[0]
    hedef_ara_noronlar = {
        baglanti.hedef.noron
        for akson in reseptor.aksonlar
        for baglanti in akson.baglantilar
    }

    cikti = beyin.isle([1, 0, 0], adim_sayisi=32)

    assert hedef_ara_noronlar
    assert all(n.ateslenme_sayisi > 0 for n in hedef_ara_noronlar)
    assert cikti == [1]


from BrainNew.Beyin import Beyin


def geri_bildirimleri_yakala(monkeypatch, beyin, davranislar):
    """
    Nöronların yerel geri bildirimini geçici olarak taklit eder.
    Böylece yalnızca Beyin'in dalga koordinasyonunu test ederiz.
    """
    cagri_sirasi = []

    for noron in beyin.noronlar:
        def geri_bildirim(deger, noron=noron):
            cagri_sirasi.append(noron)
            return davranislar.get(noron, [])

        monkeypatch.setattr(
            noron,
            "geri_bildirim",
            geri_bildirim
        )

    return cagri_sirasi


def test_geri_bildirim_yalnizca_ateslenen_motor_noronlardan_baslar(
    monkeypatch
):
    beyin = Beyin(2, 2, 3, seed=42)

    motor_a = beyin.motor_noronlari[0]
    motor_b = beyin.motor_noronlari[1]

    cagri_sirasi = geri_bildirimleri_yakala(
        monkeypatch,
        beyin,
        {}
    )

    # Yalnızca ikinci motor nöron ateşlenmiş olsun.
    beyin.motor_organ.noron_ateslendi(1)

    beyin.geri_bildirim(1.0)

    assert cagri_sirasi == [motor_b]
    assert motor_a not in cagri_sirasi


def test_geri_bildirim_geriye_dogru_yayilir(monkeypatch):
    beyin = Beyin(2, 1, 3, seed=42)

    motor = beyin.motor_noronlari[0]
    ara = beyin.ara_noronlar[0]
    reseptor = beyin.reseptor_noronlari[0]

    davranislar = {
        motor: [ara],
        ara: [reseptor],
        reseptor: []
    }

    cagri_sirasi = geri_bildirimleri_yakala(
        monkeypatch,
        beyin,
        davranislar
    )

    beyin.motor_organ.noron_ateslendi(0)

    beyin.geri_bildirim(1.0)

    assert cagri_sirasi == [
        motor,
        ara,
        reseptor
    ]


def test_geri_bildirim_dalgasi_ayni_noronu_iki_kez_islemez(
    monkeypatch
):
    beyin = Beyin(2, 1, 2, seed=42)

    motor = beyin.motor_noronlari[0]
    noron_a = beyin.ara_noronlar[0]
    noron_b = beyin.ara_noronlar[1]

    # A -> B -> A döngüsü.
    davranislar = {
        motor: [noron_a],
        noron_a: [noron_b],
        noron_b: [noron_a]
    }

    cagri_sirasi = geri_bildirimleri_yakala(
        monkeypatch,
        beyin,
        davranislar
    )

    beyin.motor_organ.noron_ateslendi(0)

    beyin.geri_bildirim(1.0)

    assert cagri_sirasi.count(motor) == 1
    assert cagri_sirasi.count(noron_a) == 1
    assert cagri_sirasi.count(noron_b) == 1
    assert len(cagri_sirasi) == 3

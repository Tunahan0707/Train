
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


def baglantilari_temizle(beyin):
    for noron in beyin.noronlar:
        for akson in noron.aksonlar:
            for baglanti in tuple(akson.baglantilar):
                baglanti.sil()


def test_gercek_geri_bildirim_yalnizca_izli_nedensel_yola_ulasir():
    beyin = Beyin(2, 1, 1, seed=17)
    baglantilari_temizle(beyin)

    reseptor = beyin.reseptor_noronlari[0]
    ilgisiz_reseptor = beyin.reseptor_noronlari[1]
    ara = beyin.ara_noronlar[0]
    motor = beyin.motor_noronlari[0]

    # Baglanti agirliklari [-10, 10] araliginda sinirlanir.
    # Ara ve motor noronlarini esige yakin baslatarak 8 mV\n    # baglantilarla iki asamali aktarimi gercekci sekilde tetikle.
    ilk = reseptor.aksonlar[0].baglan(
        ara.dendritler[0], etki_mv=8.0, gecikme_ms=1
    )
    ikinci = ara.aksonlar[0].baglan(
        motor.dendritler[0], etki_mv=8.0, gecikme_ms=1
    )
    ilgisiz = ilgisiz_reseptor.aksonlar[0].baglan(
        motor.dendritler[1], etki_mv=3.0, gecikme_ms=1
    )

    ara.membran_potansiyeli = -56.0
    motor.membran_potansiyeli = -56.0

    assert beyin.isle([1, 0], adim_sayisi=3) == [1]
    assert ilk.uygunluk_izi > 0
    assert ikinci.uygunluk_izi > 0
    assert ilgisiz.uygunluk_izi == 0

    ilk_etki = ilk.etki_mv
    ikinci_etki = ikinci.etki_mv

    beyin.geri_bildirim(1.0)

    assert ilk.etki_mv > ilk_etki
    assert ikinci.etki_mv > ikinci_etki
    assert ilgisiz.etki_mv == 3.0


def test_noron_guncelleme_sirasi_simulasyon_sonucunu_degistirmez():
    beyin_a = Beyin(1, 1, 0, seed=23)
    beyin_b = Beyin(1, 1, 0, seed=23)

    for beyin in (beyin_a, beyin_b):
        baglantilari_temizle(beyin)
        beyin.reseptor_noronlari[0].aksonlar[0].baglan(
            beyin.motor_noronlari[0].dendritler[0],
            etki_mv=20.0,
            gecikme_ms=1
        )
        beyin.girdi_al([1])

    beyin_b.noronlar.reverse()

    for _ in range(4):
        beyin_a.adim()
        beyin_b.adim()

    assert beyin_a.motor_organ.ciktilar == beyin_b.motor_organ.ciktilar

    def durum_imzasi(beyin):
        return [
            (
                noron.membran_potansiyeli,
                noron.durum,
                noron.ateslenme_sayisi
            )
            for noron in beyin.reseptor_noronlari
            + beyin.motor_noronlari
        ]

    assert durum_imzasi(beyin_a) == durum_imzasi(beyin_b)



def test_hedefi_ateslenmeyen_motor_noron_esik_alti_girdilerden_ogrenir():
    beyin = Beyin(1, 1, 0, seed=31)
    baglantilari_temizle(beyin)

    reseptor = beyin.reseptor_noronlari[0]
    motor = beyin.motor_noronlari[0]

    baglanti = reseptor.aksonlar[0].baglan(
        motor.dendritler[0],
        etki_mv=2.0,
        gecikme_ms=1
    )

    # Bağlantı sinyali hedefi eşik altı bırakır; motor nöron ateşlenmez.
    baglanti.aktar(0)
    assert motor.guncelle() is False
    assert motor.ateslenme_sayisi == 0
    assert baglanti.uygunluk_izi == 0.0

    onceki_etki = baglanti.etki_mv
    beyin.ogren([1])

    assert baglanti.uygunluk_izi > 0.0
    assert baglanti.etki_mv > onceki_etki
    assert beyin.motor_organ.ciktilar == [0]

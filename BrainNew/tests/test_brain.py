
import pytest

from BrainNew import (
    Beyin,
    Noron,
    ActivationTrace,
)


def test_noron_morfolojisi():
    noron = Noron(
        dendrit_sayisi=8,
        akson_sayisi=7
    )

    assert len(noron.dendritler) == 8
    assert len(noron.aksonlar) == 7
    assert noron.membran_potansiyeli == -70.0
    assert noron.durum == Noron.DINLENME


def test_sinaptik_baglanti_olusturma():
    kaynak_noron = Noron()
    hedef_noron = Noron()

    akson = kaynak_noron.aksonlar[0]
    dendrit = hedef_noron.dendritler[0]

    baglanti = akson.baglan(
        dendrit,
        etki_mv=2.0,
        gecikme_ms=3
    )

    assert baglanti in akson.baglantilar
    assert baglanti in dendrit.gelen_baglantilar
    assert baglanti.etki_mv == 2.0
    assert baglanti.gecikme_ms == 3
    assert baglanti.aktif


def test_sinaptik_iletim():
    kaynak_noron = Noron()
    hedef_noron = Noron()

    dendrit = hedef_noron.dendritler[0]

    baglanti = kaynak_noron.aksonlar[0].baglan(
        dendrit,
        etki_mv=2.5
    )

    baglanti.aktar(zaman=0)

    assert dendrit.bekleyen_etki_mv == 2.5
    assert baglanti.aktarim_sayisi == 1


def test_sinaptik_isaret_degistirme():
    noron_a = Noron()
    noron_b = Noron()

    baglanti = noron_a.aksonlar[0].baglan(
        noron_b.dendritler[0],
        etki_mv=2.0
    )

    baglanti.isaret_degistir()

    assert baglanti.etki_mv == -2.0


def test_sinaptik_guclendirme_ve_zayiflatma():
    noron_a = Noron()
    noron_b = Noron()

    baglanti = noron_a.aksonlar[0].baglan(
        noron_b.dendritler[0],
        etki_mv=2.0
    )

    baglanti.guclendir(1.0)
    assert baglanti.etki_mv == 3.0

    baglanti.zayiflat(1.5)
    assert baglanti.etki_mv == 1.5

    baglanti.zayiflat(5.0)
    assert baglanti.etki_mv == 0.0


def test_sinaptik_baglanti_silme():
    noron_a = Noron()
    noron_b = Noron()

    akson = noron_a.aksonlar[0]
    dendrit = noron_b.dendritler[0]

    baglanti = akson.baglan(dendrit)

    baglanti.sil()

    assert not baglanti.aktif
    assert baglanti not in akson.baglantilar
    assert baglanti not in dendrit.gelen_baglantilar


def test_gecersiz_sinaptik_gecikme():
    noron_a = Noron()
    noron_b = Noron()

    with pytest.raises(ValueError):
        noron_a.aksonlar[0].baglan(
            noron_b.dendritler[0],
            gecikme_ms=0
        )


def test_noron_ateslenmesi():
    noron = Noron()

    noron.membran_potansiyeli = -54.0

    ateslendi = noron.guncelle()

    assert ateslendi
    assert noron.durum == Noron.DEPOLARIZASYON
    assert noron.membran_potansiyeli == 30.0
    assert noron.ateslenme_sayisi == 1


def test_aksiyon_potansiyonu_dongusu():
    noron = Noron()

    noron.membran_potansiyeli = -54.0
    noron.guncelle()

    noron.guncelle()
    assert noron.durum == Noron.REPOLARIZASYON

    noron.guncelle()
    assert noron.durum == Noron.HIPERPOLARIZASYON

    noron.guncelle()
    assert noron.durum == Noron.HIPERPOLARIZASYON

    noron.guncelle()
    assert noron.durum == Noron.DINLENME
    assert noron.membran_potansiyeli == -70.0


def test_beyin_olusturma():
    beyin = Beyin(
        girdi_sayisi=21,
        cikti_sayisi=8,
        ara_noron_sayisi=50,
        seed=42
    )

    assert len(beyin.reseptor_noronlari) == 21
    assert len(beyin.ara_noronlar) == 50
    assert len(beyin.motor_noronlari) == 8
    assert len(beyin.noronlar) == 79


def test_noron_morfolojileri_belirlenen_aralikta():
    beyin = Beyin(
        girdi_sayisi=21,
        cikti_sayisi=8,
        ara_noron_sayisi=50,
        seed=42
    )

    for noron in beyin.noronlar:
        assert 6 <= len(noron.dendritler) <= 12
        assert 5 <= len(noron.aksonlar) <= 10


def test_baglantilarin_hedefleri_gecerli():
    beyin = Beyin(
        girdi_sayisi=10,
        cikti_sayisi=4,
        ara_noron_sayisi=20,
        seed=42
    )

    tum_dendritler = {
        dendrit
        for noron in beyin.noronlar
        for dendrit in noron.dendritler
    }

    for noron in beyin.noronlar:
        for akson in noron.aksonlar:
            for baglanti in akson.baglantilar:
                assert baglanti.kaynak is akson
                assert baglanti.hedef in tum_dendritler
                assert baglanti in baglanti.hedef.gelen_baglantilar


def test_ayni_seed_ayni_beyni_olusturur():
    beyin_a = Beyin(10, 4, 20, seed=42)
    beyin_b = Beyin(10, 4, 20, seed=42)

    def baglanti_imzasi(beyin):
        noron_indeksleri = {
            noron: indeks
            for indeks, noron in enumerate(beyin.noronlar)
        }

        imzalar = []

        for noron_indeksi, noron in enumerate(beyin.noronlar):
            for akson_indeksi, akson in enumerate(noron.aksonlar):
                for baglanti in akson.baglantilar:
                    imzalar.append((
                        noron_indeksi,
                        akson_indeksi,
                        noron_indeksleri[baglanti.hedef.noron],
                        baglanti.hedef.noron.dendritler.index(
                            baglanti.hedef
                        ),
                        baglanti.etki_mv,
                        baglanti.gecikme_ms
                    ))

        return imzalar

    assert baglanti_imzasi(beyin_a) == baglanti_imzasi(beyin_b)


def test_reseptor_girdisi():
    beyin = Beyin(
        girdi_sayisi=4,
        cikti_sayisi=2,
        ara_noron_sayisi=5,
        seed=42
    )

    beyin.girdi_al([1, 0, 1, 0])

    assert beyin.reseptor_organ.ciktilar == [1, 0, 1, 0]
    assert beyin.reseptor_noronlari[0].membran_potansiyeli == -50.0
    assert beyin.reseptor_noronlari[1].membran_potansiyeli == -70.0


def test_gecersiz_reseptor_girdisi():
    beyin = Beyin(4, 2, 5, seed=42)

    with pytest.raises(ValueError):
        beyin.girdi_al([1, 0])

    with pytest.raises(ValueError):
        beyin.girdi_al([1, 0, 2, 0])


def test_beyin_simulasyon_zamani():
    beyin = Beyin(4, 2, 5, seed=42)

    beyin.calistir(25)

    assert beyin.zaman == 25


def test_motor_organ_ciktilari():
    beyin = Beyin(4, 2, 5, seed=42)

    beyin.motor_organ.noron_ateslendi(1)

    assert beyin.motor_organ.ciktilar == [0, 1]

    beyin.motor_organ.reset()

    assert beyin.motor_organ.ciktilar == [0, 0]


def test_trace_kayitlari():
    trace = ActivationTrace()

    beyin = Beyin(
        girdi_sayisi=4,
        cikti_sayisi=2,
        ara_noron_sayisi=5,
        seed=42,
        trace=trace
    )

    noron = beyin.noronlar[0]
    noron.membran_potansiyeli = -54.0

    beyin.adim()

    assert any(
        olay["tur"] == "ateslenme"
        for olay in trace.olaylar
    )

    trace.temizle()

    assert len(trace.olaylar) == 0


def test_simulasyon_ciktilarinin_bicimi():
    beyin = Beyin(
        girdi_sayisi=21,
        cikti_sayisi=8,
        ara_noron_sayisi=50,
        seed=42
    )

    sonuc = beyin.isle([1] * 21, 100)

    assert len(sonuc) == 8
    assert all(bit in (0, 1) for bit in sonuc)



def test_deneme_sonu_sifirlama_gecici_izleri_temizler_ve_ogrenmeyi_korur():
    beyin = Beyin(1, 1, 0, seed=42)
    kaynak = beyin.reseptor_noronlari[0]
    hedef = beyin.motor_noronlari[0]
    baglanti = kaynak.aksonlar[0].baglan(hedef.dendritler[0])

    baglanti.etki_mv = 4.25
    baglanti.uygunluk_izi = 1.5
    beyin.etkin_baglantilar.add(baglanti)
    beyin._iletim_planla(baglanti)
    kaynak.membran_potansiyeli = -60.0

    beyin.deneme_sonu_sifirla()

    assert baglanti.uygunluk_izi == 0.0
    assert baglanti not in beyin.etkin_baglantilar
    assert baglanti.etki_mv == 4.25
    assert baglanti.aktif
    assert beyin._olay_kuyrugu == []
    assert kaynak.membran_potansiyeli == kaynak.dinlenme_mv

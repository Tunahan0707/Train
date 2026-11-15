from BrainNew import Noron


def baglanti_ateslendir(etki=2.0):
    kaynak = Noron(dendrit_sayisi=1, akson_sayisi=1)
    hedef = Noron(dendrit_sayisi=3, akson_sayisi=1)
    akson = kaynak.aksonlar[0]
    baglanti = akson.baglan(
        hedef.dendritler[0],
        etki_mv=etki,
        gecikme_ms=4
    )
    hedef.membran_potansiyeli = -56.0
    baglanti.aktar(0)
    assert hedef.guncelle()
    return akson, hedef, baglanti


def test_pozitif_geri_bildirim_yeni_baglanti_olusturur():
    akson, hedef, _ = baglanti_ateslendir()
    hedef.geri_bildirim(1.0)

    assert len(akson.baglantilar) == 2
    yeni_baglanti = akson.baglantilar[1]
    assert yeni_baglanti.hedef is hedef.dendritler[1]
    assert yeni_baglanti.etki_mv == 1.0
    assert yeni_baglanti.gecikme_ms == 4


def test_inhibitor_baglanti_tek_basina_yeni_baglanti_olusturmaz():
    akson, hedef, baglanti = baglanti_ateslendir(etki=-2.0)
    onceki_sayi = len(akson.baglantilar)

    hedef.geri_bildirim(1.0)

    assert baglanti.uygunluk_izi == 0.0
    assert len(akson.baglantilar) == onceki_sayi


def test_bir_geri_bildirimde_en_fazla_bir_yeni_baglanti_olur():
    akson, hedef, _ = baglanti_ateslendir()
    onceki_sayi = len(akson.baglantilar)

    hedef.geri_bildirim(1.0)

    assert len(akson.baglantilar) - onceki_sayi == 1


def test_baglantili_tum_dendritlere_yeni_baglanti_eklenmez():
    kaynak = Noron(dendrit_sayisi=1, akson_sayisi=1)
    hedef = Noron(dendrit_sayisi=3, akson_sayisi=1)
    akson = kaynak.aksonlar[0]
    baglantilar = [
        akson.baglan(dendrit, etki_mv=2.0)
        for dendrit in hedef.dendritler
    ]

    hedef.membran_potansiyeli = -56.0
    baglantilar[0].aktar(0)
    assert hedef.guncelle()

    onceki_sayi = len(akson.baglantilar)
    hedef.geri_bildirim(1.0)

    assert len(akson.baglantilar) == onceki_sayi

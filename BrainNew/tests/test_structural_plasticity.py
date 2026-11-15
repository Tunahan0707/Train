
from BrainNew.Noron import Noron


def test_pozitif_geri_bildirim_yeni_baglanti_olusturur():
    kaynak = Noron(dendrit_sayisi=1, akson_sayisi=1)
    hedef = Noron(dendrit_sayisi=3, akson_sayisi=1)

    akson = kaynak.aksonlar[0]

    eski_baglanti = akson.baglan(
        hedef.dendritler[0],
        etki_mv=2.0,
        gecikme_ms=4
    )

    eski_baglanti.aktar(0)

    hedef.geri_bildirim(1.0)

    assert len(akson.baglantilar) == 2

    yeni_baglanti = akson.baglantilar[1]

    assert yeni_baglanti.hedef is hedef.dendritler[1]
    assert yeni_baglanti.etki_mv == 1.0
    assert yeni_baglanti.gecikme_ms == 4


def test_yeni_baglanti_mevcut_baglantinin_isaretini_korur():
    kaynak = Noron(dendrit_sayisi=1, akson_sayisi=1)
    hedef = Noron(dendrit_sayisi=3, akson_sayisi=1)

    akson = kaynak.aksonlar[0]

    eski_baglanti = akson.baglan(
        hedef.dendritler[0],
        etki_mv=-2.0,
        gecikme_ms=3
    )

    eski_baglanti.aktar(0)

    hedef.geri_bildirim(1.0)

    yeni_baglanti = akson.baglantilar[1]

    assert yeni_baglanti.etki_mv == -1.0
    assert yeni_baglanti.gecikme_ms == 3


def test_bir_geri_bildirimde_en_fazla_bir_yeni_baglanti_olur():
    kaynak = Noron(dendrit_sayisi=1, akson_sayisi=1)
    hedef = Noron(dendrit_sayisi=6, akson_sayisi=1)

    akson = kaynak.aksonlar[0]

    baglanti = akson.baglan(
        hedef.dendritler[0],
        etki_mv=2.0
    )

    baglanti.aktar(0)

    onceki_sayi = len(akson.baglantilar)

    hedef.geri_bildirim(1.0)

    sonraki_sayi = len(akson.baglantilar)

    assert sonraki_sayi - onceki_sayi <= 1
    assert sonraki_sayi - onceki_sayi == 1


def test_baglantili_tum_dendritlere_yeni_baglanti_eklenmez():
    kaynak = Noron(dendrit_sayisi=1, akson_sayisi=1)
    hedef = Noron(dendrit_sayisi=3, akson_sayisi=1)

    akson = kaynak.aksonlar[0]

    baglantilar = [
        akson.baglan(
            dendrit,
            etki_mv=2.0
        )
        for dendrit in hedef.dendritler
    ]

    # Yalnızca ilk bağlantı uygunluk izi taşıyor.
    baglantilar[0].aktar(0)

    onceki_sayi = len(akson.baglantilar)

    hedef.geri_bildirim(1.0)

    assert len(akson.baglantilar) == onceki_sayi

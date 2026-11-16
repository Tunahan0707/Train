import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.Noron import Noron


def ag_kur(kimyasal_alan=None):
    beyin = Beyin(kimyasal_alan)
    kaynak = Noron("kaynak")
    hedef = Noron("hedef")
    kaynak_giris = Dendrid("kaynak_giris")
    hedef_giris = Dendrid("hedef_giris")
    cikis = Baglanti(
        "cikis", kaynak, hedef, uzunluk=2.0, iletim_hizi=1.0,
        esik=0.2, hedef_dendrit_id="hedef_giris", etki=100.0
    )
    kaynak_giris.sinaps_bagla(cikis, 1.0)
    kaynak.dendrit_ekle(kaynak_giris)
    kaynak.cikis_sinapsi_ekle(cikis)
    hedef.dendrit_ekle(hedef_giris)
    beyin.noron_ekle(kaynak)
    beyin.noron_ekle(hedef)
    return beyin, kaynak, hedef, cikis


class ZamanKayitliNoron(Noron):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.girdi_zamanlari = []

    def girdi_al(self, dendrit_id, etki, zaman=None):
        super().girdi_al(dendrit_id, etki, zaman)
        self.girdi_zamanlari.append(zaman)


class OrkestrasyonTestleri(unittest.TestCase):
    """Beyin'in saat, olay kuyruğu ve bileşen koordinasyonu davranışları."""

    def test_yeni_beyin_sifir_zamanla_baslar(self):
        self.assertEqual(Beyin().zaman, 0.0)

    def test_bos_olay_kuyrugu_adim_islemez(self):
        beyin = Beyin()
        self.assertFalse(beyin.adim())
        self.assertEqual(beyin.zaman, 0.0)

    def test_sifir_gecikmeli_olay_reddedilir(self):
        with self.assertRaises(ValueError):
            Beyin().olay_planla(0, "bilinmeyen", "x")

    def test_negatif_ve_sonsuz_gecikme_reddedilir(self):
        beyin = Beyin()
        for gecikme in (-1, float("inf"), float("nan")):
            with self.subTest(gecikme=gecikme):
                with self.assertRaises(ValueError):
                    beyin.olay_planla(gecikme, "bilinmeyen", "x")

    def test_float_hassasiyetinde_zamani_ilerletmeyen_gecikme_reddedilir(self):
        beyin = Beyin()
        beyin.zaman = 1e20
        with self.assertRaises(ValueError):
            beyin.olay_planla(1e-6, "duyusal_girdi", "n")

    def test_olay_zamani_planlanan_gecikme_kadar_ilerler(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d"))
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d", 1, gecikme=2.5)
        self.assertEqual(beyin._olaylar[0][0], 2.5)

    def test_olaylar_zaman_sirasiyla_islenir(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d"))
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d", 1, gecikme=3.0)
        beyin.duyusal_girdi("n", "d", 1, gecikme=1.0)
        zamanlar = []
        while beyin.adim():
            zamanlar.append(beyin.zaman)
        self.assertEqual(zamanlar, sorted(zamanlar))

    def test_ayni_zamanli_girdiler_entegrasyondan_once_toplanir(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d1"))
        n.dendrit_ekle(Dendrid("d2"))
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d1", 8.0)
        beyin.duyusal_girdi("n", "d2", 8.0)
        beyin.calistir()
        self.assertEqual(n.ateslenme_sayisi, 1)

    def test_ayni_zaman_damgasinda_girdi_entegrasyondan_once_islenir(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d"))
        beyin.noron_ekle(n)
        # Entegrasyon önce kuyruğa eklenmiş olsa bile girdi önceliklidir.
        beyin.olay_planla(1.0, "entegrasyon", "n")
        beyin.duyusal_girdi("n", "d", 100.0, gecikme=1.0)
        beyin.adim()
        beyin.adim()
        self.assertEqual(beyin.zaman, 1.0)
        self.assertEqual(n.ateslenme_sayisi, 1)

    def test_entegrasyon_olaylari_hedef_ve_zaman_bazinda_tekillestirilir(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d1"))
        n.dendrit_ekle(Dendrid("d2"))
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d1", 1.0)
        beyin.duyusal_girdi("n", "d2", 1.0)
        beyin.adim()
        beyin.adim()
        entegrasyonlar = [
            olay for olay in beyin._olaylar if olay[3] == "entegrasyon"
        ]
        self.assertEqual(len(entegrasyonlar), 1)

    def test_calistir_islenen_olay_sayisini_dondurur_ve_kuyrugu_tuketir(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d"))
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d", 1.0)
        islenen = beyin.calistir()
        self.assertGreaterEqual(islenen, 2)
        self.assertFalse(beyin._olaylar)

    def test_calistir_bos_kuyrukta_sifir_dondurur(self):
        self.assertEqual(Beyin().calistir(), 0)

    def test_olay_limiti_asildiginda_guvenlik_hatasi_verir(self):
        beyin, _, _, _ = ag_kur()
        beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
        with self.assertRaises(RuntimeError):
            beyin.calistir(olay_limiti=0)

    def test_negatif_olay_limiti_reddedilir(self):
        with self.assertRaises(ValueError):
            Beyin().calistir(olay_limiti=-1)

    def test_sinyal_gonderme_simulasyon_zamaniyla_eslesmelidir(self):
        beyin, _, _, cikis = ag_kur()
        with self.assertRaises(ValueError):
            beyin.sinyal_gonder(cikis, zaman=1.0)

    def test_hedef_dendrit_yoksa_sinyal_gonderme_reddedilir(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        sinaps = Baglanti(
            "s", kaynak, hedef, hedef_dendrit_id="olmayan", etki=1.0
        )
        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)
        with self.assertRaises(ValueError):
            beyin.sinyal_gonder(sinaps, zaman=0.0)

    def test_sinaptik_agirlik_hedefe_iletilen_etkiyi_olcekler(self):
        beyin, kaynak, hedef, sinaps = ag_kur()
        sinaps.etki = 20.0
        sinaps.sinaptik_agirligi_ayarla(0.5)
        beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
        beyin.calistir()

        # 20 birim temel etki, 0.5 ağırlıkla 10 birim iletilir.
        # Dinlenme membranı -70 olduğundan hedef -60'a ulaşır;
        # ateşleme eşiği -55'tir, dolayısıyla ateşlenmemelidir.
        self.assertEqual(hedef.ateslenme_sayisi, 0)
        self.assertAlmostEqual(hedef.membran, -60.0)
    def test_sinyal_hedefe_baglanti_uzunlugu_bolum_iletim_hizi_gecikmesiyle_ulasir(self):
        beyin, kaynak, hedef, _ = ag_kur()
        hedef = ZamanKayitliNoron("hedef")
        hedef.dendrit_ekle(Dendrid("hedef_giris"))
        # Aynı iletim parametreleriyle hedef nesnesini ağdaki hedefle değiştir.
        sinaps = Baglanti(
            "cikis", kaynak, hedef, uzunluk=2.0, iletim_hizi=1.0,
            esik=0.2, hedef_dendrit_id="hedef_giris", etki=100.0
        )
        kaynak.cikis_sinapslari.clear()
        kaynak.dendritler["kaynak_giris"].sinaps_katkilari.clear()
        kaynak.dendritler["kaynak_giris"].sinaps_bagla(sinaps, 1.0)
        kaynak.cikis_sinapsi_ekle(sinaps)
        beyin.noronlar["hedef"] = hedef

        beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
        beyin.calistir()
        self.assertEqual(kaynak.ateslenme_sayisi, 1)
        self.assertEqual(hedef.ateslenme_sayisi, 1)
        self.assertAlmostEqual(hedef.girdi_zamanlari[0], 2.000002)

    def test_refrakter_sirada_gelen_girdi_dinlenmeye_donuste_islenir(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d"))
        n.durum = n.DEPOLARIZASYON
        n.membran = n.depolarizasyon_degeri
        beyin.noron_ekle(n)
        beyin.olay_planla(1.0, "faz", "n")
        beyin.duyusal_girdi("n", "d", 100.0, gecikme=0.5)

        beyin.calistir()
        self.assertEqual(n.ateslenme_sayisi, 1)
        self.assertEqual(n.durum, n.DINLENME)
        self.assertFalse(n.bekleyen_girdi_var_mi())

    def test_kimyasal_alan_beyne_opsiyonel_verilebilir(self):
        alan = KimyasalAlan()
        self.assertIs(Beyin(kimyasal_alan=alan).kimyasal_alan, alan)

    def test_ayni_baslangicla_iki_calistirma_ayni_sonucu_verir(self):
        sonuclar = []
        for _ in range(2):
            beyin, kaynak, hedef, cikis = ag_kur()
            beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
            beyin.calistir()
            sonuclar.append((
                kaynak.ateslenme_sayisi, hedef.ateslenme_sayisi,
                cikis.aktivasyon_sayisi, hedef.son_girdi_zamani
            ))
        self.assertEqual(sonuclar[0], sonuclar[1])


if __name__ == "__main__":
    unittest.main()

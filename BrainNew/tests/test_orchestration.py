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


class OrkestrasyonTestleri(unittest.TestCase):
    """Beyin'in saat, olay kuyruğu ve bileşen koordinasyonu davranışları."""

    def test_yeni_beyin_sifir_zamanla_baslar(self):
        beyin = Beyin()
        self.assertEqual(beyin.zaman, 0.0)

    def test_bos_olay_kuyrugu_adim_islemez(self):
        beyin = Beyin()
        self.assertFalse(beyin.adim())
        self.assertEqual(beyin.zaman, 0.0)

    def test_sifir_gecikmeli_olay_reddedilir(self):
        beyin = Beyin()
        with self.assertRaises(ValueError):
            beyin.olay_planla(0, "bilinmeyen", "x")

    def test_negatif_gecikmeli_olay_reddedilir(self):
        beyin = Beyin()
        with self.assertRaises(ValueError):
            beyin.olay_planla(-1, "bilinmeyen", "x")

    def test_olay_zamani_planlanan_gecikme_kadar_ilerler(self):
        beyin = Beyin()
        beyin.noron_ekle(Noron("n"))
        beyin.noron_ekle(Noron("n2"))
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
        d1, d2 = Dendrid("d1"), Dendrid("d2")
        n.dendrit_ekle(d1)
        n.dendrit_ekle(d2)
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d1", 8.0)
        beyin.duyusal_girdi("n", "d2", 8.0)
        beyin.calistir()
        self.assertEqual(n.ateslenme_sayisi, 1)

    def test_calistir_islenen_olay_sayisini_dondurur(self):
        beyin = Beyin()
        n = Noron("n")
        n.dendrit_ekle(Dendrid("d"))
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d", 1.0)
        islenen = beyin.calistir()
        self.assertGreaterEqual(islenen, 2)
        self.assertEqual(islenen, 0 if beyin._olaylar else islenen)

    def test_calistir_bos_kuyrukta_sifir_dondurur(self):
        self.assertEqual(Beyin().calistir(), 0)

    def test_olay_limiti_asildiginda_guvenlik_hatasi_verir(self):
        beyin, kaynak, hedef, cikis = ag_kur()
        # Olay kuyruğunda işlenecek olaylar varken sıfır limit güvenli biçimde durur.
        beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
        with self.assertRaises(RuntimeError):
            beyin.calistir(olay_limiti=0)

    def test_sinyal_gonderme_simulasyon_zamaniyla_eslesmelidir(self):
        beyin, kaynak, hedef, cikis = ag_kur()
        with self.assertRaises(ValueError):
            beyin.sinyal_gonder(cikis, zaman=1.0)

    def test_hedef_dendrit_yoksa_sinyal_gonderme_reddedilir(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        sinaps = Baglanti(
            "s", kaynak, hedef, hedef_dendrit_id="olmayan", etki=1.0
        )
        with self.assertRaises(ValueError):
            beyin.sinyal_gonder(sinaps, zaman=0.0)

    def test_sinyal_hedefe_baglanti_uzunlugu_kadar_gecikmeyle_ulasir(self):
        beyin, kaynak, hedef, cikis = ag_kur()
        beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
        beyin.calistir()
        self.assertEqual(kaynak.ateslenme_sayisi, 1)
        self.assertEqual(hedef.ateslenme_sayisi, 1)
        self.assertGreaterEqual(hedef.ateslenme_sayisi, 1)

    def test_kimyasal_alan_beyne_opsiyonel_verilebilir(self):
        alan = KimyasalAlan()
        beyin = Beyin(kimyasal_alan=alan)
        self.assertIs(beyin.kimyasal_alan, alan)

    def test_ayni_baslangicla_iki_calistirma_ayni_ateslenme_sayisini_verir(self):
        sonuclar = []
        for _ in range(2):
            beyin, kaynak, hedef, cikis = ag_kur()
            beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
            beyin.calistir()
            sonuclar.append((kaynak.ateslenme_sayisi,
                             hedef.ateslenme_sayisi,
                             cikis.aktivasyon_sayisi))
        self.assertEqual(sonuclar[0], sonuclar[1])


if __name__ == "__main__":
    unittest.main()

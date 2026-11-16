import math
import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.Mikroglia import Mikroglia
from BrainNew.Noron import Noron
from BrainNew.UzamsalIndeks import UzamsalIndeks


class MikrogliaTestleri(unittest.TestCase):
    def test_mikroglia_bagimsiz_bir_yapidir(self):
        mikroglia = Mikroglia("m1", konum=(2.0, 3.0))
        self.assertEqual(mikroglia.konum, (2.0, 3.0))
        self.assertEqual(mikroglia.algilama_yaricapi, 5.0)

    def test_yalnizca_algilama_yaricapindaki_sinapslari_tarar(self):
        indeks = UzamsalIndeks()
        yakin = Baglanti("yakin", None, None, terminal_konumu=(1.0, 0.0))
        uzak = Baglanti("uzak", None, None, terminal_konumu=(20.0, 0.0))
        indeks.ekle(yakin)
        indeks.ekle(uzak)
        mikroglia = Mikroglia("m", algilama_yaricapi=3.0)

        mikroglia.bakim_yap(indeks, None, 1.0)

        self.assertEqual(mikroglia.taranan_baglanti_sayisi, 1)
        self.assertEqual(yakin.son_bakim_zamani, 1.0)
        self.assertEqual(uzak.son_bakim_zamani, 0.0)

    def test_yalnizca_kullanim_azligi_baglantiyi_koparmaz(self):
        indeks = UzamsalIndeks()
        sinaps = Baglanti(
            "s", None, None, budama_kazanci=10.0,
            budama_esigi=0.1, kopma_esigi=0.9
        )
        indeks.ekle(sinaps)
        mikroglia = Mikroglia("m", algilama_yaricapi=2.0)
        mikroglia.bakim_yap(indeks, None, 10.0)
        self.assertFalse(sinaps.kopuk)

    def test_kullanim_suruyorsa_budama_sinyali_tek_basina_koparmaz(self):
        alan = KimyasalAlan()
        indeks = UzamsalIndeks()
        sinaps = Baglanti(
            "s", None, None, budama_kazanci=10.0,
            budama_esigi=0.1, kopma_esigi=0.5
        )
        sinaps.iz = 1.0
        indeks.ekle(sinaps)
        alan.sal("budama", sinaps.terminal_konumu, 10.0, 0.0)
        mikroglia = Mikroglia("m", algilama_yaricapi=2.0, bakim_araligi=1.0)

        mikroglia.bakim_yap(indeks, alan, 1.0)

        self.assertFalse(sinaps.kopuk)
        self.assertGreater(sinaps.yapisal_butunluk, sinaps.kopma_esigi)

    def test_budama_sinyali_ve_dusuk_kullanim_birlikte_koparabilir(self):
        alan = KimyasalAlan()
        indeks = UzamsalIndeks()
        sinaps = Baglanti(
            "s", None, None, budama_kazanci=10.0,
            budama_esigi=0.1, kopma_esigi=0.5,
            yapisal_yaslanma_tau=100000.0
        )
        indeks.ekle(sinaps)
        alan.sal("budama", sinaps.terminal_konumu, 10.0, 0.0)
        mikroglia = Mikroglia("m", algilama_yaricapi=2.0, bakim_araligi=1.0)

        kopanlar = mikroglia.bakim_yap(indeks, alan, 1.0)

        self.assertTrue(sinaps.kopuk)
        self.assertEqual(kopanlar, (sinaps,))

    def test_stabilizasyon_sinyali_butunlugu_korur(self):
        alan = KimyasalAlan()
        indeks = UzamsalIndeks()
        sinaps = Baglanti(
            "s", None, None, yapisal_yaslanma_tau=10.0,
            bakim_kazanci=0.5
        )
        indeks.ekle(sinaps)
        alan.sal("stabilizasyon", sinaps.terminal_konumu, 2.0, 0.0)
        mikroglia = Mikroglia("m", algilama_yaricapi=2.0, bakim_araligi=1.0)

        mikroglia.bakim_yap(indeks, alan, 1.0)

        self.assertGreater(sinaps.yapisal_butunluk, math.exp(-0.1))

    def test_otomatik_bakim_son_zaman_siniriyla_tekrarlar(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        sinaps = Baglanti(
            "s", kaynak, None, terminal_konumu=(0.0, 0.0)
        )
        kaynak.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(kaynak)
        mikroglia = Mikroglia(
            "m", algilama_yaricapi=2.0, bakim_araligi=1.0
        )
        beyin.mikroglia_ekle(mikroglia)
        beyin.mikroglia_bakim_baslat("m")

        islenen = beyin.calistir(son_zaman=2.5)

        self.assertEqual(islenen, 2)
        self.assertEqual(mikroglia.son_tarama_zamani, 2.0)
        self.assertEqual(sinaps.son_bakim_zamani, 2.0)
        self.assertEqual(beyin.zaman, 2.5)
        self.assertEqual(beyin._olaylar[0][0], 3.0)

        beyin.calistir(son_zaman=3.0)
        self.assertEqual(mikroglia.son_tarama_zamani, 3.0)

    def test_otomatik_bakim_sinirsiz_calistirmayi_engeller(self):
        beyin = Beyin()
        beyin.mikroglia_ekle(Mikroglia("m", bakim_araligi=1.0))
        beyin.mikroglia_bakim_baslat("m")

        with self.assertRaises(ValueError):
            beyin.calistir()

    def test_otomatik_bakim_durdurulunca_yalnizca_bekleyen_olay_islenir(self):
        beyin = Beyin()
        mikroglia = Mikroglia("m", bakim_araligi=1.0)
        beyin.mikroglia_ekle(mikroglia)
        beyin.mikroglia_bakim_baslat("m")

        self.assertTrue(beyin.mikroglia_bakim_durdur("m"))
        beyin.calistir()

        self.assertEqual(mikroglia.son_tarama_zamani, 1.0)
        self.assertEqual(beyin._olaylar, [])

    def test_beyin_mikroglia_bakim_olayini_koordine_eder(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        sinaps = Baglanti(
            "s", kaynak, None, terminal_konumu=(0.0, 0.0),
            budama_kazanci=10.0, budama_esigi=0.1, kopma_esigi=0.5
        )
        kaynak.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(kaynak)
        mikroglia = Mikroglia("m", algilama_yaricapi=2.0, bakim_araligi=1.0)
        beyin.mikroglia_ekle(mikroglia)
        beyin.kimyasal_alan.sal("budama", sinaps.terminal_konumu, 10.0, 0.0)
        beyin.mikroglia_bakim_planla("m", 1.0)

        beyin.calistir()

        self.assertTrue(sinaps.kopuk)
        self.assertNotIn(sinaps, kaynak.cikis_sinapslari)
        self.assertNotIn(sinaps, beyin.baglanti_indeksi.yakinindakileri_bul(
            (0.0, 0.0), 1.0
        ))


if __name__ == "__main__":
    unittest.main()

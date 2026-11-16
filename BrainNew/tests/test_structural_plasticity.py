import unittest

from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron


class YapısalBağlantıOluşumuTestleri(unittest.TestCase):
    def _ag_kur(self, hedef_duyarliligi=1.0, hedef_konumu=(2.0, 0.0)):
        beyin = Beyin()
        kaynak = Noron("kaynak", konum=(0.0, 0.0))
        kaynak_dendrit = Dendrid("kaynak_giris", konum=(0.0, 0.0))
        kaynak.dendrit_ekle(kaynak_dendrit)

        hedef = Noron("hedef", konum=hedef_konumu)
        hedef_dendrit = Dendrid("hedef_giris", konum=hedef_konumu)
        hedef_dendrit.transmitter_duyarliligi_ayarla(
            "buyume", hedef_duyarliligi
        )
        hedef.dendrit_ekle(hedef_dendrit)

        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)
        beyin.kimyasal_alan.sal(
            "buyume", kaynak.konum, 100.0, 0.0,
            yayilim=1.0, temizlenme=0.0
        )
        beyin.zaman = 1.0
        return beyin, kaynak, hedef, kaynak_dendrit, hedef_dendrit

    def test_yerel_buyume_ve_reseptor_uygunluguyla_baglanti_olusturur(self):
        beyin, kaynak, hedef, kaynak_dendrit, hedef_dendrit = self._ag_kur()

        sinaps = beyin.yapisal_buyume_degerlendir("kaynak", 5.0)

        self.assertIsNotNone(sinaps)
        self.assertIs(sinaps.kaynak, kaynak)
        self.assertIs(sinaps.hedef, hedef)
        self.assertEqual(sinaps.hedef_dendrit_id, "hedef_giris")
        self.assertIn(sinaps, kaynak.cikis_sinapslari)
        self.assertIn(sinaps, hedef.gelen_sinapslari)
        self.assertIn(sinaps, kaynak_dendrit.sinaps_katkilari)
        self.assertIn(
            sinaps,
            beyin.baglanti_indeksi.yakinindakileri_bul(kaynak.konum, 0.0)
        )

    def test_yeni_baglanti_zayif_ve_olgunlasmamis_baslar(self):
        beyin, kaynak, _, _, _ = self._ag_kur()

        sinaps = beyin.yapisal_buyume_degerlendir("kaynak", 5.0)

        self.assertAlmostEqual(sinaps.sinaptik_agirlik, 0.1)
        self.assertAlmostEqual(sinaps.yapisal_butunluk, 0.25)
        self.assertEqual(sinaps.potansiyel, 0.0)
        self.assertTrue(all(
            -0.1 <= katkı <= 0.1
            for dendrit in kaynak.dendritler.values()
            for baglanti, katkı in dendrit.sinaps_katkilari.items()
            if baglanti is sinaps
        ))

    def test_buyume_sinyali_yoksa_baglanti_olusturmaz(self):
        beyin, _, _, _, _ = self._ag_kur()
        beyin.kimyasal_alan.kaynaklar.clear()

        self.assertIsNone(beyin.yapisal_buyume_degerlendir("kaynak", 5.0))

    def test_hedef_dendritin_olumlu_buyume_reseptoru_yoksa_baglanti_olusturmaz(self):
        beyin, _, _, _, hedef_dendrit = self._ag_kur(
            hedef_duyarliligi=-1.0
        )

        self.assertIsNone(beyin.yapisal_buyume_degerlendir("kaynak", 5.0))
        self.assertEqual(hedef_dendrit.sinaps_katkilari, {})

    def test_yari_cap_disindaki_hedefe_baglanti_olusturmaz(self):
        beyin, _, _, _, _ = self._ag_kur(hedef_konumu=(20.0, 0.0))

        self.assertIsNone(beyin.yapisal_buyume_degerlendir("kaynak", 5.0))

    def test_ayni_kaynak_hedef_dendrit_ucgeni_ikinci_kez_olusturulmaz(self):
        beyin, kaynak, _, _, _ = self._ag_kur()

        ilk = beyin.yapisal_buyume_degerlendir("kaynak", 5.0)
        ikinci = beyin.yapisal_buyume_degerlendir("kaynak", 5.0)

        self.assertIsNotNone(ilk)
        self.assertIsNone(ikinci)
        self.assertEqual(len(kaynak.cikis_sinapslari), 1)

    def test_en_uygun_hedef_dendrit_deterministik_secilir(self):
        beyin, kaynak, _, _, _ = self._ag_kur()
        hedef2 = Noron("hedef2", konum=(3.0, 0.0))
        dendrit2 = Dendrid("daha_uygun", konum=(3.0, 0.0))
        dendrit2.transmitter_duyarliligi_ayarla("buyume", 2.0)
        hedef2.dendrit_ekle(dendrit2)
        beyin.noron_ekle(hedef2)

        sinaps = beyin.yapisal_buyume_degerlendir("kaynak", 5.0)

        self.assertIs(sinaps.hedef, hedef2)
        self.assertEqual(sinaps.hedef_dendrit_id, "daha_uygun")


if __name__ == "__main__":
    unittest.main()

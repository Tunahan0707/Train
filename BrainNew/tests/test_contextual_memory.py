import unittest

from BrainNew.BaglamaDuyarliHafizaDeneyi import BaglamaDuyarliHafizaDeneyi


class BaglamaDuyarliHafizaTestleri(unittest.TestCase):
    def test_tek_basina_ipucu_ve_baglam_kapilari_ateslenmez(self):
        sonuc = BaglamaDuyarliHafizaDeneyi().calistir()

        for ad, kayit in sonuc["baseline"].items():
            self.assertEqual(
                kayit["gerceklesen"], (),
                msg=f"{ad} tek başına kapı ateşledi",
            )

    def test_ayni_ipucu_baglama_gore_farkli_oruntuleri_cagirir(self):
        sonuc = BaglamaDuyarliHafizaDeneyi().calistir()

        self.assertEqual(
            sonuc["egitim_X"]["gerceklesen"], ("B", "C", "Gx")
        )
        self.assertEqual(
            sonuc["egitim_Y"]["gerceklesen"], ("D", "E", "Gy")
        )

        # A+X: Y yolunun kapısı ve hedefleri sessiz kalmalı.
        self.assertEqual(
            sonuc["geri_cagirma_X"]["gerceklesen"], ("B", "C", "Gx")
        )
        self.assertTrue(sonuc["geri_cagirma_X"]["dogru"])

        # A+Y: X yolunun kapısı ve hedefleri sessiz kalmalı.
        self.assertEqual(
            sonuc["geri_cagirma_Y"]["gerceklesen"], ("D", "E", "Gy")
        )
        self.assertTrue(sonuc["geri_cagirma_Y"]["dogru"])

    def test_baglama_ozel_dort_sinaps_ogrenilir(self):
        sonuc = BaglamaDuyarliHafizaDeneyi().calistir()

        for kimlik, baslangic in sonuc["baslangic_agirliklari"].items():
            self.assertGreater(
                sonuc["ogrenilmis_agirliklar"][kimlik],
                baslangic,
                msg=f"{kimlik} bağlantısı güçlenmedi",
            )

    def test_deney_tekrarlanabilirdir(self):
        bir = BaglamaDuyarliHafizaDeneyi().calistir()
        iki = BaglamaDuyarliHafizaDeneyi().calistir()

        for ad in ("geri_cagirma_X", "geri_cagirma_Y"):
            self.assertEqual(
                bir[ad]["gerceklesen"],
                iki[ad]["gerceklesen"],
            )
        self.assertEqual(
            bir["ogrenilmis_agirliklar"],
            iki["ogrenilmis_agirliklar"],
        )


if __name__ == "__main__":
    unittest.main()

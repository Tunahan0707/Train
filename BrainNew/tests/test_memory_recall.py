import unittest

from BrainNew.HafizaDeneyi import HafizaDeneyi


class HafizaVeGeriCagirmaTestleri(unittest.TestCase):
    def test_kismi_ipucu_egitimden_sonra_eksik_oruntuyu_geri_cagirir(self):
        sonuc = HafizaDeneyi().calistir()

        self.assertEqual(sonuc["baseline"]["gerceklesen"], ("A",))
        self.assertFalse(sonuc["baseline"]["dogru"])

        self.assertEqual(
            sonuc["egitim"]["gerceklesen"], ("A", "B", "C")
        )
        self.assertTrue(sonuc["egitim"]["dogru"])

        self.assertEqual(
            sonuc["geri_cagirma"]["gerceklesen"], ("A", "B", "C")
        )
        self.assertTrue(sonuc["geri_cagirma"]["dogru"])

        for hedef in ("B", "C"):
            self.assertGreater(
                sonuc["ogrenilmis_agirliklar"][hedef],
                sonuc["baslangic_agirliklari"][hedef],
            )
            # Eğitilmemiş kontrol ağı aynı kısmi ipucuyla bağlantılarını
            # güçlendirmemiş olmalı.
            self.assertEqual(
                sonuc["baseline_agirliklari"][hedef],
                sonuc["baslangic_agirliklari"][hedef],
            )

    def test_iliski_geri_cagirma_deneyi_tekrarlanabilirdir(self):
        bir = HafizaDeneyi().calistir()
        iki = HafizaDeneyi().calistir()

        self.assertEqual(
            bir["geri_cagirma"]["gerceklesen"],
            iki["geri_cagirma"]["gerceklesen"],
        )
        self.assertEqual(
            bir["ogrenilmis_agirliklar"],
            iki["ogrenilmis_agirliklar"],
        )


if __name__ == "__main__":
    unittest.main()

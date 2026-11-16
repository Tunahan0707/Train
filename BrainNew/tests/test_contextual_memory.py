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


    def test_baglam_geri_cagirma_bes_yuzde_genlik_gurultusune_dayanir(self):
        rapor = BaglamaDuyarliHafizaDeneyi().gurultu_taramasi(
            olcekler=(0.95, 1.05)
        )

        for olcek in (0.95, 1.05):
            self.assertEqual(
                rapor[olcek]["X"]["gerceklesen"], ("B", "C", "Gx")
            )
            self.assertEqual(
                rapor[olcek]["Y"]["gerceklesen"], ("D", "E", "Gy")
            )

    def test_ipucu_ve_baglam_genlikleri_bagimsiz_degerlendirilir(self):
        rapor = BaglamaDuyarliHafizaDeneyi().bagimsiz_genlik_taramasi(
            olcek_ciftleri=((0.90, 1.0), (1.0, 0.90), (0.90, 0.90))
        )

        # Kanallardan yalnızca biri %10 zayıfladığında diğeri kapıyı taşır.
        for cift in ((0.90, 1.0), (1.0, 0.90)):
            self.assertEqual(rapor[cift]["X"]["gerceklesen"], ("B", "C", "Gx"))
            self.assertEqual(rapor[cift]["Y"]["gerceklesen"], ("D", "E", "Gy"))

        # İki kanal aynı anda %10 zayıfladığında birleşik girdi eşik altında kalır.
        self.assertEqual(rapor[(0.90, 0.90)]["X"]["gerceklesen"], ())
        self.assertEqual(rapor[(0.90, 0.90)]["Y"]["gerceklesen"], ())


    def test_bagimsiz_genlik_taramasi_gecersiz_olcegi_reddeder(self):
        with self.assertRaises(ValueError):
            BaglamaDuyarliHafizaDeneyi().bagimsiz_genlik_taramasi(
                olcek_ciftleri=((0.0, 1.0),)
            )


if __name__ == "__main__":
    unittest.main()

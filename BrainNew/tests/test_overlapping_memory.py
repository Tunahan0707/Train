import unittest

from BrainNew.CakisikHafizaDeneyi import CakisikHafizaDeneyi


class CakisikHafizaTestleri(unittest.TestCase):
    def test_ortak_elemanli_iki_oruntu_ayri_ayri_geri_cagrilir(self):
        sonuc = CakisikHafizaDeneyi().calistir()

        self.assertEqual(sonuc["baseline_A"]["gerceklesen"], ("A",))
        self.assertEqual(sonuc["baseline_D"]["gerceklesen"], ("D",))

        self.assertEqual(
            sonuc["egitim_A"]["gerceklesen"], ("A", "B", "C")
        )
        self.assertEqual(
            sonuc["egitim_D"]["gerceklesen"], ("B", "D", "E")
        )

        # A ipucu B ve C'yi çağırmalı; D/E yanlış pozitif olmamalı.
        self.assertEqual(
            sonuc["geri_cagirma_A"]["gerceklesen"], ("A", "B", "C")
        )
        self.assertTrue(sonuc["geri_cagirma_A"]["dogru"])

        # D ipucu B ve E'yi çağırmalı; A/C yanlış pozitif olmamalı.
        self.assertEqual(
            sonuc["geri_cagirma_D"]["gerceklesen"], ("B", "D", "E")
        )
        self.assertTrue(sonuc["geri_cagirma_D"]["dogru"])

    def test_iki_oruntunun_dort_baglantisi_da_ayri_ayri_ogrenilir(self):
        sonuc = CakisikHafizaDeneyi().calistir()

        for kimlik, baslangic in sonuc["baslangic_agirliklari"].items():
            self.assertGreater(
                sonuc["ogrenilmis_agirliklar"][kimlik],
                baslangic,
                msg=f"{kimlik} bağlantısı güçlenmedi",
            )

    def test_cakisik_hafiza_deneyi_tekrarlanabilirdir(self):
        bir = CakisikHafizaDeneyi().calistir()
        iki = CakisikHafizaDeneyi().calistir()

        for ad in ("geri_cagirma_A", "geri_cagirma_D"):
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

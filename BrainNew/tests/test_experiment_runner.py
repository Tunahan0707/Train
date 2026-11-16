import unittest

from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.DeneySurucusu import DeneyGorevi, DeneyOrnegi, DeneySurucusu
from BrainNew.Noron import Noron


def ag_kur():
    beyin = Beyin()
    noron = Noron("N")
    noron.dendrit_ekle(Dendrid("D"))
    beyin.noron_ekle(noron)
    return beyin


def ornek(kimlik, etki, beklenen):
    return DeneyOrnegi(
        kimlik,
        [("N", "D", etki, 1e-6)],
        beklenen,
    )


class DeneySurucusuTestleri(unittest.TestCase):
    def setUp(self):
        self.gorev = DeneyGorevi(
            "esik-baseline",
            "B1",
            egitim=[ornek("egitim-pozitif", 100.0, {"N"})],
            test=[
                ornek("test-pozitif", 100.0, {"N"}),
                ornek("test-negatif", 1.0, set()),
            ],
        )
        self.surucu = DeneySurucusu(ag_kur)

    def test_her_ornek_bagimsiz_yeni_agda_calistirilir(self):
        rapor = self.surucu.gorevi_degerlendir(self.gorev)
        self.assertEqual(rapor["ornek_sayisi"], 2)
        self.assertEqual(rapor["tam_eslesme"], 2)
        self.assertEqual(rapor["tam_eslesme_orani"], 1.0)

    def test_egitim_ve_test_sonuclari_ayri_raporlanir(self):
        rapor = self.surucu.gorevi_calistir(self.gorev)
        self.assertEqual(rapor["egitim"]["bolum"], "egitim")
        self.assertEqual(rapor["test"]["bolum"], "test")
        self.assertEqual(rapor["egitim"]["ornek_sayisi"], 1)
        self.assertEqual(rapor["test"]["ornek_sayisi"], 2)

    def test_yanlis_pozitif_ve_negatifleri_ayri_sayar(self):
        gorev = DeneyGorevi(
            "hata-olcumu",
            "B2",
            egitim=[ornek("egitim", 100.0, {"N"})],
            test=[ornek("test-yanlis-pozitif", 100.0, set())],
        )
        rapor = self.surucu.gorevi_degerlendir(gorev)
        self.assertEqual(rapor["yanlis_pozitif"], 1)
        self.assertEqual(rapor["yanlis_negatif"], 0)

    def test_egitim_ve_test_ornek_kimlikleri_cakisamaz(self):
        with self.assertRaises(ValueError):
            DeneyGorevi(
                "cakisma", "B1",
                [ornek("ortak", 1.0, set())],
                [ornek("ortak", 1.0, set())],
            )

    def test_egitim_ve_test_kumeleri_bos_olamaz(self):
        with self.assertRaises(ValueError):
            DeneyGorevi("bos", "B1", [], [ornek("t", 1.0, set())])

    def test_desteklenmeyen_gorev_turu_reddedilir(self):
        with self.assertRaises(ValueError):
            DeneyGorevi("x", "B7", [ornek("e", 1.0, set())],
                        [ornek("t", 1.0, set())])

    def test_girdi_ve_gecikme_dogrulanir(self):
        with self.assertRaises(ValueError):
            DeneyOrnegi("x", [("N", "D", float("nan"), 1.0)], set())
        with self.assertRaises(ValueError):
            DeneyOrnegi("x", [("N", "D", 1.0, 0.0)], set())

    def test_bilinmeyen_beklenen_cikti_noronu_reddedilir(self):
        hatali = DeneyOrnegi("x", [], {"yok"})
        with self.assertRaises(ValueError):
            self.surucu.ornegi_calistir(hatali)

    def test_ayni_deney_tekrarlanabilir_sonuclar_uretir(self):
        bir = self.surucu.gorevi_calistir(self.gorev)
        iki = self.surucu.gorevi_calistir(self.gorev)
        self.assertEqual(bir, iki)

    def test_baseline_yurutucusu_ogrenme_parametrelerini_degistirmez(self):
        beyin = ag_kur()
        noron = beyin.noronlar["N"]
        dendrit = noron.dendritler["D"]
        once = dict(dendrit.sinaps_katkilari)

        surucu = DeneySurucusu(lambda: beyin)
        surucu.ornegi_calistir(ornek("tek", 100.0, {"N"}))

        self.assertEqual(dendrit.sinaps_katkilari, once)

    def test_ag_kurucu_ayni_agi_ikinci_kez_verirse_reddedilir(self):
        beyin = ag_kur()
        surucu = DeneySurucusu(lambda: beyin)
        surucu.ornegi_calistir(ornek("ilk", 100.0, {"N"}))
        with self.assertRaises(ValueError):
            surucu.ornegi_calistir(ornek("ikinci", 100.0, {"N"}))

    def test_bolum_parametresi_gecersizse_hata_verir(self):
        with self.assertRaises(ValueError):
            self.surucu.gorevi_degerlendir(self.gorev, "dogrulama")


if __name__ == "__main__":
    unittest.main()

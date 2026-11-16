import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.DeneySurucusu import DeneyOrnegi
from BrainNew.EgitimSurucusu import EgitimSurucusu
from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.Noron import Noron


class TrainingFoundationTests(unittest.TestCase):
    def test_chemical_source_is_finite_immediately_after_release(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 1.0, 0.0)
        self.assertTrue(
            __import__("math").isfinite(
                alan.yogunluk("A", (0.0, 0.0), 1e-12)
            )
        )

    def test_positive_and_negative_feedback_follow_local_threshold_rule(self):
        noron = Noron("n")
        dendrit = Dendrid("d")
        active = Baglanti("active", noron, None, esik=0.5)
        inactive = Baglanti("inactive", noron, None, esik=0.5)
        noron.dendrit_ekle(dendrit)
        noron.cikis_sinapsi_ekle(active)
        noron.cikis_sinapsi_ekle(inactive)

        noron.geri_bildirim_uygula({active}, pozitif=True, miktar=0.1)
        self.assertAlmostEqual(active.esik, 0.4)
        self.assertAlmostEqual(inactive.esik, 0.6)

        noron.geri_bildirim_uygula({active}, pozitif=False, miktar=0.1)
        self.assertAlmostEqual(active.esik, 0.5)
        self.assertAlmostEqual(inactive.esik, 0.5)

    def test_episode_reset_preserves_learned_parameters(self):
        beyin = Beyin()
        noron = Noron("n")
        dendrit = Dendrid("d")
        sinaps = Baglanti("s", noron, None)
        dendrit.sinaps_bagla(sinaps, 0.7)
        noron.dendrit_ekle(dendrit)
        noron.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(noron)
        sinaps.sinaptik_agirligi_ayarla(1.4)
        sinaps.etki_uygula(0.8, 0.0)
        noron.membran = -20.0

        beyin.episode_baslat()

        self.assertEqual(noron.membran, noron.dinlenme_degeri)
        self.assertEqual(sinaps.potansiyel, 0.0)
        self.assertEqual(sinaps.sinaptik_agirlik, 1.4)
        self.assertEqual(dendrit.sinaps_katkilari[sinaps], 0.7)

    def test_training_runner_reuses_same_brain_across_episodes(self):
        beyin = Beyin()
        noron = Noron("N")
        noron.dendrit_ekle(Dendrid("D"))
        beyin.noron_ekle(noron)
        surucu = EgitimSurucusu(beyin)
        ornek = DeneyOrnegi(
            "input", [("N", "D", 100.0, 1e-6)], {"N"}
        )
        bir = surucu.episode_calistir(ornek)
        iki = surucu.episode_calistir(ornek)
        self.assertTrue(bir["dogru"])
        self.assertTrue(iki["dogru"])
        self.assertEqual(surucu.episode_sayisi, 2)
        self.assertIs(surucu.beyin, beyin)


if __name__ == "__main__":
    unittest.main()

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

    def test_pruned_synapse_cannot_deliver_already_queued_input(self):
        beyin = Beyin()
        kaynak = Noron("source")
        hedef = Noron("target")
        hedef.dendrit_ekle(Dendrid("D"))
        sinaps = Baglanti(
            "s", kaynak, hedef, uzunluk=1.0,
            hedef_dendrit_id="D", etki=100.0
        )
        kaynak.dendrit_ekle(Dendrid("out"))
        kaynak.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)
        beyin._iletim_olayini_planla(sinaps, 1.0)
        sinaps.kopuk = True
        beyin.calistir()
        self.assertEqual(hedef.ateslenme_sayisi, 0)

    def test_refractory_input_is_processed_once_after_recovery(self):
        beyin = Beyin()
        noron = Noron("N")
        dendrit = Dendrid("D")
        noron.dendrit_ekle(dendrit)
        beyin.noron_ekle(noron)
        noron.durum = noron.DEPOLARIZASYON
        noron.membran = noron.depolarizasyon_degeri

        # Girdi refrakter dönemde gelir; faz döngüsü tamamlanınca
        # tamponlanan girdi bir kez değerlendirilmelidir.
        beyin.olay_planla(1.0, "faz", "N")
        beyin.duyusal_girdi("N", "D", 100.0, gecikme=0.5)
        beyin.calistir()

        self.assertEqual(noron.ateslenme_sayisi, 1)
        self.assertEqual(noron.durum, noron.DINLENME)
        self.assertFalse(noron.bekleyen_girdi_var_mi())

    def test_positive_feedback_branches_only_through_causal_input(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        kaynak_giris = Dendrid("giris")
        hedef_giris = Dendrid("giris")
        kaynak.dendrit_ekle(kaynak_giris)
        hedef.dendrit_ekle(hedef_giris)

        etkin = Baglanti(
            "etkin", kaynak, hedef, hedef_dendrit_id="giris",
            uzunluk=1.0, etki=100.0, esik=0.2
        )
        etkisiz = Baglanti(
            "etkisiz", kaynak, None, esik=0.5
        )
        kaynak_giris.sinaps_bagla(etkin, 1.0)
        kaynak_giris.sinaps_bagla(etkisiz, 0.0)
        kaynak.cikis_sinapsi_ekle(etkin)
        kaynak.cikis_sinapsi_ekle(etkisiz)
        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)

        beyin.duyusal_girdi("kaynak", "giris", 100.0)
        beyin.calistir()
        self.assertEqual(kaynak.ateslenme_sayisi, 1)
        self.assertEqual(hedef.ateslenme_sayisi, 1)
        self.assertIn(etkin, hedef._son_nedensel_girdi_sinapslari)

        beyin.geri_bildirim_baslat(
            "hedef", pozitif=True, miktar=0.1,
            iz_esigi=0.001, dallanma_sonum=0.5
        )
        beyin.calistir()

        self.assertLess(etkin.esik, 0.2)
        self.assertGreater(etkisiz.esik, 0.5)

    def test_feedback_rejects_non_firing_origin(self):
        beyin = Beyin()
        noron = Noron("sessiz")
        noron.dendrit_ekle(Dendrid("D"))
        beyin.noron_ekle(noron)
        with self.assertRaises(ValueError):
            beyin.geri_bildirim_baslat("sessiz")

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

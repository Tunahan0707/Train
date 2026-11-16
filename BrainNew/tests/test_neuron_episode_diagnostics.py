import unittest

from BrainNew.Noron import Noron
from BrainNew.Dendrid import Dendrid
from BrainNew.Beyin import Beyin


class NoronEpisodeDiagnosticsTests(unittest.TestCase):
    def test_diagnostics_record_membrane_input_and_threshold_margin(self):
        brain = Beyin()
        neuron = Noron("N", dinlenme=-70.0, esik=-55.0)
        neuron.dendrit_ekle(Dendrid("D"))
        brain.noron_ekle(neuron)

        brain.duyusal_girdi("N", "D", 20.0)
        brain.calistir()

        self.assertEqual(neuron.tanilama_entegre_sayisi, 1)
        self.assertAlmostEqual(neuron.tanilama_toplam_membran_girdisi, 20.0)
        self.assertAlmostEqual(neuron.tanilama_mutlak_membran_girdisi, 20.0)
        self.assertAlmostEqual(neuron.tanilama_maksimum_membran_girdisi, 20.0)
        self.assertAlmostEqual(neuron.tanilama_maksimum_membran, -50.0)
        self.assertAlmostEqual(neuron.tanilama_maksimum_esik_marji, 5.0)

    def test_episode_reset_clears_only_episode_diagnostic_counters(self):
        neuron = Noron("N")
        neuron.dendrit_ekle(Dendrid("D"))
        neuron.tanilama_entegre_sayisi = 4
        neuron.tanilama_toplam_membran_girdisi = 12.5
        neuron.tanilama_maksimum_membran_girdisi = 8.0
        neuron.tanilama_maksimum_membran = -40.0
        neuron.tanilama_maksimum_esik_marji = 15.0

        neuron.episode_sifirla(1.0)

        self.assertEqual(neuron.tanilama_entegre_sayisi, 0)
        self.assertEqual(neuron.tanilama_toplam_membran_girdisi, 0.0)
        self.assertEqual(neuron.tanilama_maksimum_membran_girdisi, 0.0)
        self.assertEqual(neuron.tanilama_maksimum_membran, neuron.dinlenme_degeri)
        self.assertEqual(
            neuron.tanilama_maksimum_esik_marji,
            neuron.dinlenme_degeri - neuron.esik,
        )


if __name__ == "__main__":
    unittest.main()

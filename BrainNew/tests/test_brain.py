import math
import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.Noron import Noron


class BrainNewPrototypeTests(unittest.TestCase):
    def test_sensory_input_can_fire_neuron_and_propagate(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        kaynak_dendrit = Dendrid("giris")
        hedef_dendrit = Dendrid("hedef_giris")

        cikis = Baglanti(
            "s1", kaynak, hedef, uzunluk=1.0, iletim_hizi=1.0,
            esik=0.2, hedef_dendrit_id="hedef_giris", etki=100.0
        )
        kaynak_dendrit.sinaps_bagla(cikis, 1.0)
        kaynak.dendrit_ekle(kaynak_dendrit)
        kaynak.cikis_sinapsi_ekle(cikis)
        hedef.dendrit_ekle(hedef_dendrit)

        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)
        beyin.duyusal_girdi("kaynak", "giris", 100.0)
        beyin.calistir()

        self.assertEqual(kaynak.ateslenme_sayisi, 1)
        self.assertEqual(cikis.aktivasyon_sayisi, 1)
        self.assertEqual(hedef.ateslenme_sayisi, 1)

    def test_only_locally_eligible_output_synapses_activate(self):
        beyin = Beyin()
        noron = Noron("n")
        dendrit = Dendrid("d")
        uygun = Baglanti("uygun", noron, None, esik=0.2)
        uygun_degil = Baglanti("uygun_degil", noron, None, esik=0.2)
        dendrit.sinaps_bagla(uygun, 1.0)
        dendrit.sinaps_bagla(uygun_degil, -1.0)
        noron.dendrit_ekle(dendrit)
        noron.cikis_sinapsi_ekle(uygun)
        noron.cikis_sinapsi_ekle(uygun_degil)
        beyin.noron_ekle(noron)

        beyin.duyusal_girdi("n", "d", 100.0)
        beyin.calistir()

        self.assertEqual(uygun.aktivasyon_sayisi, 1)
        self.assertEqual(uygun_degil.aktivasyon_sayisi, 0)

    def test_multiple_dendrites_use_per_synapse_sqrt_normalization(self):
        beyin = Beyin()
        noron = Noron("n")
        d1 = Dendrid("d1")
        d2 = Dendrid("d2")
        sinaps = Baglanti("s", noron, None, esik=0.2)
        d1.sinaps_bagla(sinaps, 0.5)
        d2.sinaps_bagla(sinaps, 0.5)
        noron.dendrit_ekle(d1)
        noron.dendrit_ekle(d2)
        noron.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(noron)

        beyin.duyusal_girdi("n", "d1", 10.0)
        beyin.duyusal_girdi("n", "d2", 10.0)
        beyin.calistir()

        u = math.tanh(1.0)
        delta = (0.5 * u + 0.5 * u) / (2.0 ** 0.5)
        expected = delta / (1.0 + delta)
        self.assertAlmostEqual(sinaps.potansiyel, expected)

    def test_learning_only_updates_dendrite_that_loaded_synapse(self):
        beyin = Beyin()
        noron = Noron("n")
        d1 = Dendrid("d1")
        d2 = Dendrid("d2")
        sinaps = Baglanti("s", noron, None, esik=0.2)
        d1.sinaps_bagla(sinaps, 0.4)
        d2.sinaps_bagla(sinaps, 0.7)
        noron.dendrit_ekle(d1)
        noron.dendrit_ekle(d2)
        noron.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(noron)

        beyin.duyusal_girdi("n", "d1", 100.0)
        beyin.calistir()

        self.assertAlmostEqual(d1.sinaps_katkilari[sinaps], 0.41)
        self.assertAlmostEqual(d2.sinaps_katkilari[sinaps], 0.7)

    def test_local_potential_is_bounded_and_decays_lazily(self):
        sinaps = Baglanti("s", None, None, sonum_tau=2.0)
        sinaps.etki_uygula(1e9, 0.0)
        self.assertLessEqual(sinaps.potansiyel, 1.0)
        self.assertGreaterEqual(sinaps.potansiyel, -1.0)
        sinaps.potansiyeli_guncelle(2.0)
        self.assertAlmostEqual(sinaps.potansiyel, math.exp(-1.0))

    def test_refractory_neuron_cannot_start_another_action_potential(self):
        noron = Noron("n")
        noron.membran = 10.0
        noron.durum = noron.DEPOLARIZASYON
        self.assertFalse(noron.aksiyon_potansiyeli_baslat())
        self.assertEqual(noron.ateslenme_sayisi, 0)

    def test_activated_terminal_can_release_multiple_transmitters(self):
        alan = KimyasalAlan()
        beyin = Beyin(alan)
        kaynak = Noron("kaynak")
        sinaps = Baglanti(
            "s", kaynak, None, transmitter_profili={"A": 2.0, "B": 3.0}
        )
        beyin.noron_ekle(kaynak)
        beyin.sinyal_gonder(sinaps, 0.0)

        self.assertEqual(alan.kaynak_sayisi(), 2)
        self.assertGreater(alan.yogunluk("A", (0.0, 0.0), 1.0), 0.0)
        self.assertGreater(alan.yogunluk("B", (0.0, 0.0), 1.0), 0.0)

    def test_chemical_types_are_kept_separate_and_decay_in_space_time(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 10.0, 0.0, yayilim=1.0, temizlenme=0.1)
        alan.sal("B", (0.0, 0.0), 20.0, 0.0, yayilim=1.0, temizlenme=0.1)

        a_yakin = alan.yogunluk("A", (0.0, 0.0), 1.0)
        a_uzak = alan.yogunluk("A", (10.0, 0.0), 1.0)
        b_yakin = alan.yogunluk("B", (0.0, 0.0), 1.0)
        a_gec = alan.yogunluk("A", (0.0, 0.0), 3.0)

        self.assertGreater(a_yakin, a_uzak)
        self.assertGreater(b_yakin, a_yakin)
        self.assertGreater(a_yakin, a_gec)
        self.assertEqual(alan.yogunluk("C", (0.0, 0.0), 1.0), 0.0)


if __name__ == "__main__":
    unittest.main()

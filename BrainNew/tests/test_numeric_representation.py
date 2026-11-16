import unittest

from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.MotorOrgan import MotorOrgan
from BrainNew.Noron import Noron
from BrainNew.ReseptorOrgan import ReseptorOrgan
from BrainNew.SayisalTemsil import SayisalTemsil


class SayisalTemsilTests(unittest.TestCase):
    def setUp(self):
        self.temsil = SayisalTemsil()
        self.noronlar = tuple(f"S{i}" for i in range(1, 10))
        self.dendritler = tuple(f"D{i}" for i in range(1, 10))

    def test_preferred_number_has_maximum_response(self):
        for sayi, yanit in zip(
            self.temsil.tercih_edilen_sayilar,
            (
                self.temsil.aktivasyon_vektoru(x)
                for x in self.temsil.tercih_edilen_sayilar
            ),
        ):
            self.assertEqual(yanit[sayi - 1], 1.0)
            self.assertEqual(max(yanit), 1.0)

    def test_nearby_numbers_have_overlapping_population_patterns(self):
        sekiz = self.temsil.darbe_sayilari(8)
        dokuz = self.temsil.darbe_sayilari(9)
        bir = self.temsil.darbe_sayilari(1)
        iki = self.temsil.darbe_sayilari(2)

        self.assertGreater(
            sum(a > 0 and b > 0 for a, b in zip(sekiz, dokuz)), 0
        )
        yakin_fark = sum((a - b) ** 2 for a, b in zip(sekiz, dokuz))
        uzak_fark = sum((a - b) ** 2 for a, b in zip(bir, iki))
        self.assertLess(yakin_fark, uzak_fark)

    def test_codebook_decoder_recovers_every_integer_without_noise(self):
        for sayi in self.temsil.tercih_edilen_sayilar:
            sayilar = dict(zip(self.noronlar, self.temsil.darbe_sayilari(sayi)))
            self.assertEqual(self.temsil.coz(sayilar, self.noronlar), sayi)

    def test_encoder_builds_spaced_sensory_events(self):
        olaylar = self.temsil.kodla(9, self.noronlar, self.dendritler)
        self.assertTrue(olaylar)
        for noron_id in self.noronlar:
            gecikmeler = [
                olay[3] for olay in olaylar if olay[0] == noron_id
            ]
            self.assertEqual(
                gecikmeler,
                [
                    1e-6 + i * self.temsil.darbe_araligi
                    for i in range(len(gecikmeler))
                ],
            )

    def test_population_round_trip_through_brain_spikes(self):
        beyin = Beyin()
        for noron_id, dendrit_id in zip(self.noronlar, self.dendritler):
            noron = Noron(noron_id)
            noron.dendrit_ekle(Dendrid(dendrit_id))
            beyin.noron_ekle(noron)

        onceki = {
            kimlik: noron.ateslenme_sayisi
            for kimlik, noron in beyin.noronlar.items()
        }
        girdiler = self.temsil.kodla(8, self.noronlar, self.dendritler)
        ReseptorOrgan().kodla(beyin, girdiler)
        beyin.calistir()
        sayilar = MotorOrgan.ateslenme_sayilari_oku(beyin, onceki)

        self.assertEqual(self.temsil.coz(sayilar, self.noronlar), 8)

    def test_silent_population_decodes_to_none(self):
        self.assertIsNone(
            self.temsil.coz({noron: 0 for noron in self.noronlar}, self.noronlar)
        )

    def test_invalid_values_and_population_layout_are_rejected(self):
        with self.assertRaises(ValueError):
            self.temsil.kodla(0, self.noronlar, self.dendritler)
        with self.assertRaises(TypeError):
            self.temsil.aktivasyon_vektoru(2.5)
        with self.assertRaises(ValueError):
            self.temsil.kodla(3, self.noronlar[:-1], self.dendritler)
        with self.assertRaises(ValueError):
            self.temsil.coz({"S1": -1}, self.noronlar)


if __name__ == "__main__":
    unittest.main()

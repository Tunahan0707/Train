import unittest

from BrainNew.AgKurucu import AgKurucu


class AgKurucuTests(unittest.TestCase):
    def test_same_seed_produces_same_topology_and_parameters(self):
        ayarlar = dict(
            noron_sayisi=30, seed=42, dendrit_sayisi=6,
            baglanti_olasiligi=0.15, baglanti_yaricapi=100.0,
        )
        bir = AgKurucu(**ayarlar).kur()
        iki = AgKurucu(**ayarlar).kur()

        def imza(beyin):
            return tuple(sorted(
                (
                    sinaps.kimlik,
                    sinaps.kaynak.konum,
                    sinaps.hedef.konum,
                    sinaps.hedef_dendrit_id,
                    sinaps.etki,
                    sinaps.sinaptik_agirlik,
                )
                for noron in beyin.noronlar.values()
                for sinaps in noron.cikis_sinapslari
            ))

        self.assertEqual(imza(bir), imza(iki))
        self.assertEqual(bir.ag_ozeti, iki.ag_ozeti)

    def test_network_is_sparse_and_has_no_self_connections(self):
        beyin = AgKurucu(
            noron_sayisi=100, seed=7, baglanti_olasiligi=0.05,
            baglanti_yaricapi=1000.0,
        ).kur()
        sinapslar = [
            sinaps
            for noron in beyin.noronlar.values()
            for sinaps in noron.cikis_sinapslari
        ]
        self.assertEqual(len(beyin.noronlar), 100)
        self.assertLess(len(sinapslar), 100 * 99)
        self.assertTrue(all(s.kaynak is not s.hedef for s in sinapslar))
        self.assertEqual(len(sinapslar), beyin.ag_ozeti["baglanti_sayisi"])

    def test_invalid_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            AgKurucu(0)
        with self.assertRaises(ValueError):
            AgKurucu(10, baglanti_olasiligi=1.5)


if __name__ == "__main__":
    unittest.main()

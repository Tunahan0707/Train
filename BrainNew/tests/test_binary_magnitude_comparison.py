import unittest

from BrainNew.M2_BinaryBuyuklukKarsilastirma import (
    BinaryBuyuklukKarsilastirmaDeneyi,
)


class BinaryBuyuklukKarsilastirmaTests(unittest.TestCase):
    def test_numbers_use_four_bit_binary_codes(self):
        self.assertEqual(
            [BinaryBuyuklukKarsilastirmaDeneyi.binary_kodla(n) for n in range(1, 10)],
            [
                "0001", "0010", "0011", "0100", "0101",
                "0110", "0111", "1000", "1001",
            ],
        )

    def test_binary_encoder_rejects_zero_and_out_of_range_values(self):
        for value in (0, 10, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    BinaryBuyuklukKarsilastirmaDeneyi.binary_kodla(value)
        with self.assertRaises(TypeError):
            BinaryBuyuklukKarsilastirmaDeneyi.binary_kodla(True)

    def test_only_one_bits_create_sensory_events(self):
        events = BinaryBuyuklukKarsilastirmaDeneyi.girdi_olaylari_uret(5, 2)
        self.assertEqual(
            tuple((event[0], event[1]) for event in events),
            (
                ("SOL_GIRDI", "SOL_GIRDI:D1"),
                ("SOL_GIRDI", "SOL_GIRDI:D3"),
                ("SAG_GIRDI", "SAG_GIRDI:D2"),
            ),
        )
        self.assertTrue(all(event[2] == 100.0 for event in events))

    def test_network_has_two_four_dendrite_receptors_twenty_hidden_and_two_outputs(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=11)
        self.assertEqual(len(deney.duyusal_noronlari), 2)
        self.assertEqual(len(deney.ara_noronlari), 20)
        self.assertEqual(len(deney.KARAR_NORONLARI), 2)
        self.assertEqual(len(deney.beyin.noronlar), 24)
        for kimlik in deney.duyusal_noronlari:
            self.assertEqual(len(deney.beyin.noronlar[kimlik].dendritler), 4)
        self.assertEqual(deney.beyin.ag_ozeti["duyusal_dendrit"], 8)
        self.assertEqual(deney.beyin.ag_ozeti["dogrudan_duyusal_karar_baglantisi"], 0)

    def test_each_hidden_neuron_receives_one_projection_from_each_receptor(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=12)
        for ara_id in deney.ara_noronlari:
            gelenler = [
                sinaps for sinaps in deney.duyusal_ara_sinapslari
                if sinaps.hedef.kimlik == ara_id
            ]
            self.assertEqual(len(gelenler), 2)
            self.assertEqual(
                {sinaps.kaynak.kimlik for sinaps in gelenler},
                set(deney.duyusal_noronlari),
            )
            self.assertEqual(len({s.hedef_dendrit_id for s in gelenler}), 2)

    def test_each_receptor_terminal_reads_all_four_bit_dendrites(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=121)
        for sinaps in deney.duyusal_ara_sinapslari:
            katkili_dendritler = [
                dendrit
                for dendrit in sinaps.kaynak.dendritler.values()
                if sinaps in dendrit.sinaps_katkilari
            ]
            self.assertEqual(len(katkili_dendritler), 4)

    def test_sensory_neurons_do_not_project_directly_to_decisions(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=13)
        for kaynak_id in deney.duyusal_noronlari:
            kaynak = deney.beyin.noronlar[kaynak_id]
            self.assertTrue(kaynak.cikis_sinapslari)
            self.assertTrue(
                all(s.hedef.kimlik in deney.ara_noronlari for s in kaynak.cikis_sinapslari)
            )

    def test_each_hidden_neuron_projects_to_both_decision_neurons(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=14)
        for ara_id in deney.ara_noronlari:
            kaynak = deney.beyin.noronlar[ara_id]
            hedefler = {s.hedef.kimlik for s in kaynak.cikis_sinapslari}
            self.assertEqual(hedefler, set(deney.KARAR_NORONLARI))

    def test_same_seed_builds_same_topology_and_signed_weights(self):
        bir = BinaryBuyuklukKarsilastirmaDeneyi(seed=15)
        iki = BinaryBuyuklukKarsilastirmaDeneyi(seed=15)

        def imza(deney):
            return tuple(
                (
                    sinaps.kimlik,
                    sinaps.etki,
                    sinaps.sinaptik_agirlik,
                    sinaps.hedef.kimlik,
                    sinaps.hedef_dendrit_id,
                )
                for sinaps in deney.sinapslar
            )

        self.assertEqual(imza(bir), imza(iki))

    def test_reversed_pairs_stay_in_the_same_partition(self):
        egitim, test = BinaryBuyuklukKarsilastirmaDeneyi.ornekleri_ayir(
            seed=16, test_orani=0.2
        )
        egitim_kume = {frozenset(pair) for pair in egitim}
        test_kume = {frozenset(pair) for pair in test}
        self.assertTrue(egitim)
        self.assertTrue(test)
        self.assertTrue(egitim_kume.isdisjoint(test_kume))
        self.assertEqual(len(egitim), 2 * len(egitim_kume))
        self.assertEqual(len(test), 2 * len(test_kume))

    def test_task_feedback_only_releases_a_chemical_source(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=17)
        before = tuple(s.sinaptik_agirlik for s in deney.sinapslar)
        deney._geri_bildirim_sal(
            True, deney.beyin.zaman, deney.SOL, deney.SOL
        )
        after = tuple(s.sinaptik_agirlik for s in deney.sinapslar)
        self.assertEqual(before, after)
        source = deney.beyin.kimyasal_alan.kaynaklar[-1]
        self.assertEqual(source.tur, "odul")
        self.assertEqual(source.konum, deney.beyin.noronlar[deney.SOL].konum)

    def test_episode_runs_with_binary_inputs(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=18)
        result = deney.episode_calistir(9, 3, feedback=False)
        self.assertEqual(result["sol_kod"], "1001")
        self.assertEqual(result["sag_kod"], "0011")
        self.assertIn(result["gerceklesen"], (deney.SOL, deney.SAG, None))
        self.assertGreater(result["islenen_olay"], 0)

    def test_summary_reports_decision_bias_and_class_accuracy(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=20)
        results = (
            {
                "dogru": True,
                "beklenen": deney.SOL,
                "gerceklesen": deney.SOL,
                "sol_ateslenme": 2,
                "sag_ateslenme": 0,
            },
            {
                "dogru": False,
                "beklenen": deney.SAG,
                "gerceklesen": deney.SOL,
                "sol_ateslenme": 1,
                "sag_ateslenme": 0,
            },
            {
                "dogru": True,
                "beklenen": deney.SAG,
                "gerceklesen": deney.SAG,
                "sol_ateslenme": 0,
                "sag_ateslenme": 1,
            },
        )
        summary = deney.ozetle(results)
        self.assertEqual(
            summary["karar_dagilimi"],
            {deney.SOL: 2, deney.SAG: 1, None: 0},
        )
        self.assertEqual(summary["sinif_bazli"][deney.SOL]["dogruluk"], 1.0)
        self.assertEqual(summary["sinif_bazli"][deney.SAG]["dogruluk"], 0.5)

    def test_weight_diagnostic_separates_both_connection_stages(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=21)
        before = deney.sinaptik_agirliklari_oku()
        deney.duyusal_ara_sinapslari[0].sinaptik_agirlik += 0.1
        deney.ara_karar_sinapslari[0].sinaptik_agirlik -= 0.1
        summary = deney.agirlik_degisim_ozetle(deney, before)
        self.assertEqual(summary["reseptor->ara"]["baglanti_sayisi"], 40)
        self.assertEqual(summary["ara->karar"]["baglanti_sayisi"], 40)
        self.assertEqual(summary["reseptor->ara"]["degisen_baglanti"], 1)
        self.assertEqual(summary["ara->karar"]["degisen_baglanti"], 1)

    def test_test_examples_use_independent_brain_copies(self):
        deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=19)
        original_brain = deney.beyin
        weights_before = tuple(s.sinaptik_agirlik for s in deney.sinapslar)
        dendrite_gates_before = {
            (noron.kimlik, dendrit.kimlik): dict(dendrit.sinaps_katkilari)
            for noron in deney.beyin.noronlar.values()
            for dendrit in noron.dendritler.values()
        }

        results = deney.test_et(ornekler=((1, 2),))

        self.assertEqual(len(results), 1)
        self.assertIs(deney.beyin, original_brain)
        self.assertEqual(
            tuple(s.sinaptik_agirlik for s in deney.sinapslar),
            weights_before,
        )
        dendrite_gates_after = {
            (noron.kimlik, dendrit.kimlik): dict(dendrit.sinaps_katkilari)
            for noron in deney.beyin.noronlar.values()
            for dendrit in noron.dendritler.values()
        }
        self.assertEqual(dendrite_gates_after, dendrite_gates_before)


if __name__ == "__main__":
    unittest.main()

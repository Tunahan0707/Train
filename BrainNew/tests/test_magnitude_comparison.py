import unittest

from BrainNew.M1_BuyuklukKarsilastirma import BuyuklukKarsilastirmaDeneyi
from BrainNew.M1_Tanilama import (
    _agirlik_gruplari, _davranis_ozeti, _projeksiyon_imzasi,
    _projeksiyon_ozeti, _episode_akisini_ozetle,
)


class BuyuklukKarsilastirmaTests(unittest.TestCase):
    def test_split_keeps_reversed_pairs_in_same_partition(self):
        egitim, test = BuyuklukKarsilastirmaDeneyi.ornekleri_ayir(
            seed=17, test_orani=0.2
        )
        egitim_kume = {frozenset(cift) for cift in egitim}
        test_kume = {frozenset(cift) for cift in test}

        self.assertTrue(egitim)
        self.assertTrue(test)
        self.assertTrue(egitim_kume.isdisjoint(test_kume))
        self.assertEqual(len(egitim), 2 * len(egitim_kume))
        self.assertEqual(len(test), 2 * len(test_kume))
        self.assertTrue(all(sol != sag for sol, sag in egitim + test))

    def test_same_seed_builds_same_initial_projection(self):
        bir = BuyuklukKarsilastirmaDeneyi(seed=31)
        iki = BuyuklukKarsilastirmaDeneyi(seed=31)

        def imza(deney):
            return tuple(
                (
                    sinaps.kimlik,
                    sinaps.etki,
                    sinaps.sinaptik_agirlik,
                    sinaps.esik,
                )
                for sinaps in deney.sinapslar
            )

        self.assertEqual(imza(bir), imza(iki))

    def test_both_sensory_channels_project_to_both_decisions(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=9)
        for kaynak_id in deney.sol_noronlari + deney.sag_noronlari:
            kaynak = deney.beyin.noronlar[kaynak_id]
            hedefler = {
                sinaps.hedef.kimlik
                for sinaps in kaynak.cikis_sinapslari
                if sinaps.hedef is not None
            }
            self.assertEqual(
                hedefler, set(deney.KARAR_NORONLARI)
            )

    def test_task_feedback_only_adds_chemical_source(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=4)
        onceki = tuple(s.sinaptik_agirlik for s in deney.sinapslar)
        deney._geri_bildirim_sal(
            True, deney.beyin.zaman, deney.SOL, deney.SOL
        )
        sonraki = tuple(s.sinaptik_agirlik for s in deney.sinapslar)

        self.assertEqual(onceki, sonraki)
        kaynak = deney.beyin.kimyasal_alan.kaynaklar[-1]
        self.assertEqual(kaynak.tur, "odul")
        self.assertEqual(
            kaynak.konum, deney.beyin.noronlar[deney.SOL].konum
        )

    def test_input_terminals_are_located_at_their_target_output(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=12)
        for sinaps in deney.sinapslar:
            if sinaps.kimlik.endswith(":WTA"):
                continue
            self.assertEqual(
                sinaps.terminal_konumu, sinaps.hedef.konum
            )

    def test_equal_output_activity_is_an_explicit_no_decision(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=5)
        self.assertIsNone(deney._karar_ver(0, 0))
        self.assertIsNone(deney._karar_ver(3, 3))
        self.assertEqual(deney._karar_ver(4, 2), deney.SOL)
        self.assertEqual(deney._karar_ver(1, 2), deney.SAG)


    def test_diagnostic_reports_decision_and_expected_class_separately(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=20261120)
        sonuclar = (
            {
                "gerceklesen": deney.SOL,
                "beklenen": deney.SOL,
                "dogru": True,
            },
            {
                "gerceklesen": deney.SOL,
                "beklenen": deney.SAG,
                "dogru": False,
            },
            {
                "gerceklesen": None,
                "beklenen": deney.SAG,
                "dogru": False,
            },
        )

        ozet = _davranis_ozeti(sonuclar, deney)

        self.assertEqual(
            ozet["karar_dagilimi"],
            {deney.SOL: 2, deney.SAG: 0, None: 1},
        )
        self.assertEqual(ozet["sinif_bazli"][deney.SOL]["dogruluk"], 1.0)
        self.assertEqual(ozet["sinif_bazli"][deney.SAG]["dogruluk"], 0.0)

    def test_weight_diagnostic_separates_sensory_and_wta_connections(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=20261120)
        baslangic = {
            sinaps.kimlik: sinaps.sinaptik_agirlik
            for sinaps in deney.sinapslar
        }

        ozet = _agirlik_gruplari(deney, baslangic)

        self.assertEqual(ozet[deney.SOL]["baslangic"]["n"], 18)
        self.assertEqual(ozet[deney.SAG]["baslangic"]["n"], 18)
        self.assertEqual(ozet["WTA"]["baglanti_sayisi"], 2)
        self.assertEqual(ozet["WTA"]["maksimum_mutlak_delta"], 0.0)


    def test_projection_diagnostic_reports_signed_effect_and_dendrite_gate(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=20261120)
        imza = _projeksiyon_imzasi(deney)
        self.assertEqual(len(imza), 36)
        for kayit in imza.values():
            self.assertAlmostEqual(
                kayit["iletim_katsayisi"],
                kayit["baz_etki"] * kayit["sinaptik_agirlik"] * kayit["yapisal_olgunluk"],
            )
            self.assertGreaterEqual(kayit["dendrit_katkisi"], 0.3)
            self.assertLessEqual(kayit["dendrit_katkisi"], 0.8)
        ozet = _projeksiyon_ozeti(imza)
        self.assertEqual(ozet["SOL_GIRDI->SOL_BUYUK"]["n"], 9)
        self.assertEqual(ozet["SAG_GIRDI->SAG_BUYUK"]["n"], 9)

    def test_terminal_flow_uses_activation_count_delta_and_signed_coefficient(self):
        deney = BuyuklukKarsilastirmaDeneyi(seed=8)
        sinaps = next(s for s in deney.sinapslar if s.kimlik == "SL1->SOL_BUYUK")
        onceki = {s.kimlik: s.aktivasyon_sayisi for s in deney.sinapslar}
        katsayi = sinaps.iletim_etkisi()
        sinaps.aktivasyon_sayisi += 3
        katsayilar = {s.kimlik: s.iletim_etkisi() for s in deney.sinapslar}
        kayit = _episode_akisini_ozetle(deney, onceki, katsayilar)["SOL_GIRDI->SOL_BUYUK"]
        self.assertEqual(kayit["terminal_aktivasyonu"], 3)
        self.assertAlmostEqual(kayit["imzali_iletim_toplami"], 3 * katsayi)


if __name__ == "__main__":
    unittest.main()

import unittest

from BrainNew.ActivationTrace import ActivationTrace
from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron


def ag_kur(izleyici=None):
    beyin = Beyin(aktivasyon_izi=izleyici)
    kaynak = Noron("kaynak")
    hedef = Noron("hedef")
    kaynak_dendrit = Dendrid("kaynak_giris")
    hedef_dendrit = Dendrid("hedef_giris")
    sinaps = Baglanti(
        "kaynak_hedef", kaynak, hedef, uzunluk=1.0,
        iletim_hizi=1.0, esik=0.2,
        hedef_dendrit_id="hedef_giris", etki=100.0,
    )
    kaynak_dendrit.sinaps_bagla(sinaps, 1.0)
    kaynak.dendrit_ekle(kaynak_dendrit)
    kaynak.cikis_sinapsi_ekle(sinaps)
    hedef.dendrit_ekle(hedef_dendrit)
    beyin.noron_ekle(kaynak)
    beyin.noron_ekle(hedef)
    beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
    return beyin, kaynak, hedef, sinaps


class AktivasyonIziTestleri(unittest.TestCase):
    def test_noron_ateslenmesini_ve_gercek_aktif_terminali_kaydeder(self):
        iz = ActivationTrace()
        beyin, kaynak, hedef, sinaps = ag_kur(iz)
        beyin.calistir()

        self.assertEqual(kaynak.ateslenme_sayisi, 1)
        self.assertEqual(hedef.ateslenme_sayisi, 1)
        self.assertTrue(any(
            kayit["noron_id"] == "kaynak"
            and "kaynak_hedef" in kayit["aktif_cikis_sinapslari"]
            for kayit in iz.ateslenmeler
        ))
        self.assertTrue(any(
            kayit["sinaps_id"] == "kaynak_hedef"
            for kayit in iz.sinaps_aktivasyonlari
        ))

    def test_hedef_icin_kronolojik_nedensel_yol_geri_izlenebilir(self):
        iz = ActivationTrace()
        beyin, _, _, _ = ag_kur(iz)
        beyin.calistir()

        yol = iz.nedensel_yol("hedef")
        turler = [kayit["kayit_turu"] for kayit in yol]
        self.assertIn("olay", turler)
        self.assertIn("noron_ateslenmesi", turler)
        self.assertIn("sinaps_aktivasyonu", turler)
        self.assertEqual(
            [kayit["sira"] for kayit in yol],
            sorted(kayit["sira"] for kayit in yol),
        )
        ateslenenler = [
            kayit["noron_id"] for kayit in yol
            if kayit["kayit_turu"] == "noron_ateslenmesi"
        ]
        self.assertEqual(ateslenenler, ["kaynak", "hedef"])

    def test_izleyici_simulasyon_davranisini_degistirmez(self):
        iz = ActivationTrace()
        izli, izli_kaynak, izli_hedef, izli_sinaps = ag_kur(iz)
        normal, normal_kaynak, normal_hedef, normal_sinaps = ag_kur()

        izli.calistir()
        normal.calistir()

        self.assertEqual(izli.zaman, normal.zaman)
        self.assertEqual(izli_kaynak.ateslenme_sayisi, normal_kaynak.ateslenme_sayisi)
        self.assertEqual(izli_hedef.ateslenme_sayisi, normal_hedef.ateslenme_sayisi)
        self.assertEqual(izli_sinaps.aktivasyon_sayisi, normal_sinaps.aktivasyon_sayisi)
        self.assertEqual(
            izli_sinaps.sinaptik_agirlik, normal_sinaps.sinaptik_agirlik
        )

    def test_iz_temizleme_kayitlari_ve_sirayi_sifirlar(self):
        iz = ActivationTrace()
        beyin, _, _, _ = ag_kur(iz)
        beyin.calistir()
        self.assertGreater(iz.ozet()["olay_sayisi"], 0)

        iz.temizle()

        self.assertEqual(
            iz.ozet(),
            {"olay_sayisi": 0, "noron_ateslenmesi": 0, "sinaps_aktivasyonu": 0},
        )
        self.assertEqual(iz.nedensel_yol("hedef"), tuple())

    def test_geri_bildirim_olayindaki_frozenset_pasif_kayda_alinir(self):
        iz = ActivationTrace()
        iz.olay_kaydet(
            1.0, 7, "geri_bildirim", "n",
            (3, True, 0.1, 0.01, 0.5, frozenset({"n", "onceki"})),
        )
        self.assertEqual(
            iz.olaylar[0]["veri"][-1],
            ("n", "onceki"),
        )

    def test_gecersiz_derinlik_reddedilir(self):
        with self.assertRaises(ValueError):
            ActivationTrace().nedensel_yol("hedef", max_derinlik=0)


if __name__ == "__main__":
    unittest.main()

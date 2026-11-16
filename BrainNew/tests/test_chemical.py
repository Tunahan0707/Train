import math
import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.KimyasalAlan import KimyasalAlan, KimyasalKaynak
from BrainNew.Noron import Noron


class KimyasalMekanizmaTestleri(unittest.TestCase):
    """Transmitter salımı, alan yayılımı, sönüm ve reseptör yanıtı testleri."""

    def test_bos_kimyasal_alanin_yogunlugu_sifirdir(self):
        alan = KimyasalAlan()
        self.assertEqual(alan.yogunluk("A", (0.0, 0.0), 1.0), 0.0)

    def test_kimyasal_kaynak_eklendiginde_kaynak_sayisi_artar(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 2.0, 0.0)
        self.assertEqual(alan.kaynak_sayisi(), 1)

    def test_farkli_transmitter_turleri_birbirine_karismaz(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 2.0, 0.0)
        self.assertEqual(alan.yogunluk("B", (0.0, 0.0), 1.0), 0.0)
        self.assertGreater(alan.yogunluk("A", (0.0, 0.0), 1.0), 0.0)

    def test_gelecekte_salinacak_kaynak_mevcut_yogunluga_eklenmez(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 2.0, 5.0)
        self.assertEqual(alan.yogunluk("A", (0.0, 0.0), 4.0), 0.0)

    def test_salim_aninda_yogunluk_sifir_kabul_edilir(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 2.0, 1.0)
        self.assertEqual(alan.yogunluk("A", (0.0, 0.0), 1.0), 0.0)

    def test_kimyasal_yogunluk_salim_noktasindan_uzaklastikca_azalir(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 5.0, 0.0, yayilim=1.0)
        yakin = alan.yogunluk("A", (0.0, 0.0), 1.0)
        uzak = alan.yogunluk("A", (2.0, 0.0), 1.0)
        self.assertGreater(yakin, uzak)

    def test_kimyasal_yayilim_uzamsal_olarak_simetriktir(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 5.0, 0.0)
        sag = alan.yogunluk("A", (1.0, 0.0), 1.0)
        sol = alan.yogunluk("A", (-1.0, 0.0), 1.0)
        self.assertAlmostEqual(sag, sol)

    def test_kimyasal_yogunluk_zamanla_sonumlenir(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 5.0, 0.0, temizlenme=0.5)
        erken = alan.yogunluk("A", (0.0, 0.0), 1.0)
        gec = alan.yogunluk("A", (0.0, 0.0), 2.0)
        self.assertGreater(erken, gec)

    def test_ayni_turdeki_kaynaklarin_yogunluklari_toplanir(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 2.0, 0.0)
        alan.sal("A", (0.0, 0.0), 3.0, 0.0)
        tek = KimyasalAlan()
        tek.sal("A", (0.0, 0.0), 5.0, 0.0)
        self.assertAlmostEqual(
            alan.yogunluk("A", (0.5, 0.0), 1.0),
            tek.yogunluk("A", (0.5, 0.0), 1.0)
        )

    def test_yogunluk_analitik_kaynak_formuluyle_eslesir(self):
        alan = KimyasalAlan()
        miktar, yayilim, temizlenme, yas = 4.0, 2.0, 0.3, 1.5
        alan.sal("A", (0.0, 0.0), miktar, 0.0,
                 yayilim=yayilim, temizlenme=temizlenme)
        beklenen = (
            miktar / (4.0 * math.pi * yayilim * yas)
            * math.exp(-temizlenme * yas)
        )
        self.assertAlmostEqual(
            alan.yogunluk("A", (0.0, 0.0), yas), beklenen
        )

    def test_kaynak_uzakligi_formulde_uzaysal_sonum_olusturur(self):
        alan = KimyasalAlan()
        D, t, x = 1.5, 2.0, 1.25
        alan.sal("A", (0.0, 0.0), 3.0, 0.0, yayilim=D)
        merkez = alan.yogunluk("A", (0.0, 0.0), t)
        nokta = alan.yogunluk("A", (x, 0.0), t)
        self.assertAlmostEqual(
            nokta / merkez, math.exp(-(x * x) / (4.0 * D * t))
        )

    def test_negatif_salım_miktari_reddedilir(self):
        alan = KimyasalAlan()
        with self.assertRaises(ValueError):
            alan.sal("A", (0.0, 0.0), -1.0, 0.0)

    def test_sifir_ve_negatif_yayilim_reddedilir(self):
        with self.assertRaises(ValueError):
            KimyasalKaynak("A", (0.0, 0.0), 1.0, 0.0, 0.0, 0.1)
        with self.assertRaises(ValueError):
            KimyasalKaynak("A", (0.0, 0.0), 1.0, 0.0, -1.0, 0.1)

    def test_negatif_temizlenme_hizi_reddedilir(self):
        with self.assertRaises(ValueError):
            KimyasalKaynak("A", (0.0, 0.0), 1.0, 0.0, 1.0, -0.1)

    def test_sonsuz_kaynak_parametresi_ve_gecersiz_konum_reddedilir(self):
        with self.assertRaises(ValueError):
            KimyasalKaynak("A", (0.0, 0.0), float("inf"), 0.0, 1.0, 0.1)
        with self.assertRaises(ValueError):
            KimyasalKaynak("A", (0.0, float("nan")), 1.0, 0.0, 1.0, 0.1)

    def test_gecersiz_alan_sorgu_zamani_ve_konumu_reddedilir(self):
        alan = KimyasalAlan()
        with self.assertRaises(ValueError):
            alan.yogunluk("A", (0.0, 0.0), float("nan"))
        with self.assertRaises(ValueError):
            alan.yogunluk("A", (0.0, float("inf")), 1.0)

    def test_terminal_profili_birden_fazla_transmitter_tutabilir(self):
        s = Baglanti(
            "s", None, None,
            transmitter_profili={"uyarici": 2.0, "modulator": 0.5}
        )
        self.assertEqual(s.transmitter_profili["uyarici"], 2.0)
        self.assertEqual(s.transmitter_profili["modulator"], 0.5)

    def test_terminal_profili_negatif_salimi_reddeder(self):
        with self.assertRaises(ValueError):
            Baglanti("s", None, None, transmitter_profili={"A": -1.0})

    def test_terminal_ayri_miktarlarda_coklu_transmitter_salar(self):
        alan = KimyasalAlan()
        s = Baglanti(
            "s", None, None,
            transmitter_profili={"A": 2.0, "B": 0.5}
        )
        s.kimyasal_sal(alan, zaman=0.0)
        self.assertEqual(alan.kaynak_sayisi(), 2)
        self.assertGreater(alan.yogunluk("A", (0.0, 0.0), 1.0),
                           alan.yogunluk("B", (0.0, 0.0), 1.0))

    def test_kimyasal_alan_verilmezse_terminal_salimi_hata_vermez(self):
        s = Baglanti("s", None, None, transmitter_profili={"A": 1.0})
        self.assertIsNone(s.kimyasal_sal(None, zaman=0.0))

    def test_beyin_sinyal_iletiminde_terminal_kimyasal_salimi_yapar(self):
        alan = KimyasalAlan()
        beyin = Beyin(alan)
        kaynak = Noron("kaynak")
        s = Baglanti(
            "s", kaynak, None,
            transmitter_profili={"A": 1.0, "B": 2.0}
        )
        beyin.sinyal_gonder(s, zaman=0.0)
        self.assertEqual(alan.kaynak_sayisi(), 2)
        self.assertEqual(s.aktivasyon_sayisi, 1)

    def test_pozitif_reseptor_duyarliligi_dendrit_yanitini_artirir(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 10.0, 0.0)
        baz = Dendrid("baz")
        pozitif = Dendrid("pozitif")
        pozitif.transmitter_duyarliligi_ayarla("A", 1.0)
        baz.girdi_al(2.0)
        pozitif.girdi_al(2.0)
        _, baz_u = baz.sinyali_hazirla(1.0, alan)
        _, pozitif_u = pozitif.sinyali_hazirla(1.0, alan)
        self.assertGreater(pozitif_u, baz_u)

    def test_negatif_reseptor_duyarliligi_dendrit_yanitini_azaltir(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 10.0, 0.0)
        baz = Dendrid("baz")
        negatif = Dendrid("negatif")
        negatif.transmitter_duyarliligi_ayarla("A", -1.0)
        baz.girdi_al(2.0)
        negatif.girdi_al(2.0)
        _, baz_u = baz.sinyali_hazirla(1.0, alan)
        _, negatif_u = negatif.sinyali_hazirla(1.0, alan)
        self.assertLess(negatif_u, baz_u)

    def test_sifir_reseptor_duyarliligi_kimyasal_etki_olusturmaz(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 10.0, 0.0)
        duyarsiz = Dendrid("duyarsiz")
        duyarsiz.transmitter_duyarliligi_ayarla("A", 0.0)
        duyarsiz.girdi_al(2.0)
        _, u = duyarsiz.sinyali_hazirla(1.0, alan)
        self.assertAlmostEqual(u, math.tanh(0.2))

    def test_ayni_transmitter_farkli_dendritlerde_farkli_yanit_olusturur(self):
        alan = KimyasalAlan()
        alan.sal("A", (0.0, 0.0), 10.0, 0.0)
        d1, d2 = Dendrid("d1"), Dendrid("d2")
        d1.transmitter_duyarliligi_ayarla("A", 1.0)
        d2.transmitter_duyarliligi_ayarla("A", -1.0)
        d1.girdi_al(1.0)
        d2.girdi_al(1.0)
        _, u1 = d1.sinyali_hazirla(1.0, alan)
        _, u2 = d2.sinyali_hazirla(1.0, alan)
        self.assertGreater(u1, u2)


if __name__ == "__main__":
    unittest.main()

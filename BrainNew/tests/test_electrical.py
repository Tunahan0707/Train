import math
import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron


class ElektrikselMekanizmaTestleri(unittest.TestCase):
    """Membran, dendrit, yerel sinaps potansiyeli ve ateşleme testleri."""

    def test_noron_dinlenme_potansiyelinde_baslar(self):
        n = Noron("n")
        self.assertEqual(n.membran, -70.0)
        self.assertEqual(n.durum, n.DINLENME)

    def test_membran_esigin_altinda_ateslenmez(self):
        n = Noron("n")
        self.assertFalse(n.membrani_guncelle(14.9, 0.0))
        self.assertLess(n.membran, n.esik)

    def test_membran_esige_ulastiginda_ateslenmeye_hazirdir(self):
        n = Noron("n")
        self.assertTrue(n.membrani_guncelle(15.0, 0.0))
        self.assertEqual(n.membran, n.esik)

    def test_membran_esigi_astiginda_ateslenmeye_hazirdir(self):
        n = Noron("n")
        self.assertTrue(n.membrani_guncelle(20.0, 0.0))

    def test_membran_sizintisi_dinlenme_degerine_yaklastirir(self):
        n = Noron("n", sizinti=0.1)
        n.membrani_guncelle(20.0, 0.0)
        n.membrani_guncelle(0.0, 1.0)
        self.assertAlmostEqual(n.membran, -70.0 + 20.0 * 0.9)

    def test_membran_guncellemesi_zamani_geriye_goturmez(self):
        n = Noron("n")
        n.membrani_guncelle(1.0, 2.0)
        with self.assertRaises(ValueError):
            n.membrani_guncelle(1.0, 1.0)

    def test_aksiyon_potansiyeli_durumunu_depolarizasyona_cevirir(self):
        n = Noron("n")
        n.membran = n.esik
        self.assertTrue(n.aksiyon_potansiyeli_baslat())
        self.assertEqual(n.durum, n.DEPOLARIZASYON)
        self.assertEqual(n.membran, n.depolarizasyon_degeri)

    def test_ateslenme_sayaci_ateslenmede_birer_artar(self):
        n = Noron("n")
        n.membran = n.esik
        n.aksiyon_potansiyeli_baslat()
        self.assertEqual(n.ateslenme_sayisi, 1)

    def test_refrakter_durumda_ikinci_aksiyon_potansiyeli_baslamaz(self):
        n = Noron("n")
        n.membran = 100.0
        n.durum = n.DEPOLARIZASYON
        self.assertFalse(n.aksiyon_potansiyeli_baslat())
        self.assertEqual(n.ateslenme_sayisi, 0)

    def test_aksiyon_potansiyeli_fazlari_sirayla_ilerler(self):
        n = Noron("n")
        n.membran = n.esik
        n.aksiyon_potansiyeli_baslat()
        self.assertEqual(n.faz_degistir(), 1.0)
        self.assertEqual(n.durum, n.REPOLARIZASYON)
        self.assertEqual(n.membran, n.repolarizasyon_degeri)
        self.assertEqual(n.faz_degistir(), 2.0)
        self.assertEqual(n.durum, n.HIPERPOLARIZASYON)
        self.assertEqual(n.membran, n.hiperpolarizasyon_degeri)
        self.assertIsNone(n.faz_degistir())
        self.assertEqual(n.durum, n.DINLENME)
        self.assertEqual(n.membran, n.dinlenme_degeri)

    def test_dinlenmedeki_norona_faz_gecisi_uygulanamaz(self):
        with self.assertRaises(RuntimeError):
            Noron("n").faz_degistir()

    def test_beyin_noronun_ateslenme_kararini_delege_eder(self):
        beyin = Beyin()
        n = Noron("n")
        d = Dendrid("d")
        n.dendrit_ekle(d)
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d", 100.0)
        beyin.calistir()
        self.assertEqual(n.ateslenme_sayisi, 1)
        self.assertIsNotNone(n.son_entegrasyon_zamani)

    def test_normal_akista_sinaps_aktivasyonu_ve_kimyasal_salim_noronda_yurutulur(self):
        from BrainNew.KimyasalAlan import KimyasalAlan

        alan = KimyasalAlan()
        beyin = Beyin(alan)
        n = Noron("n")
        d = Dendrid("d")
        sinaps = Baglanti(
            "s", n, None, esik=0.2, transmitter_profili={"A": 1.0}
        )
        d.sinaps_bagla(sinaps, 1.0)
        n.dendrit_ekle(d)
        n.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(n)

        def beyin_aktivasyon_yapmamali(*args, **kwargs):
            raise AssertionError("Normal akışta Beyin sinapsı aktive etmemeli.")

        beyin.sinyal_gonder = beyin_aktivasyon_yapmamali
        beyin.duyusal_girdi("n", "d", 100.0)
        beyin.calistir()

        self.assertEqual(sinaps.aktivasyon_sayisi, 1)
        self.assertEqual(alan.kaynak_sayisi(), 1)

    def test_dendrit_pozitif_ve_negatif_girdileri_isaretli_toplar(self):
        d = Dendrid("d")
        d.girdi_al(3.0)
        d.girdi_al(-1.0)
        elektriksel, yerel = d.sinyali_hazirla(0.0)
        self.assertEqual(elektriksel, 2.0)
        self.assertAlmostEqual(yerel, math.tanh(0.2))

    def test_dendrit_girdileri_isledikten_sonra_tamponu_temizler(self):
        d = Dendrid("d")
        d.girdi_al(2.0)
        d.sinyali_hazirla(0.0)
        self.assertEqual(d.girdiler, [])

    def test_dendrit_girdi_yokken_sifir_sinyal_doner(self):
        self.assertEqual(Dendrid("d").sinyali_hazirla(0.0), (0.0, 0.0))

    def test_dendrit_sinyali_buyuk_girdide_doyuma_yaklasir(self):
        d = Dendrid("d", sinyal_olcegi=1.0)
        d.girdi_al(1000.0)
        _, u = d.sinyali_hazirla(0.0)
        self.assertAlmostEqual(u, 1.0)

    def test_dendrit_sinaps_katkisi_pozitif_yerel_potansiyel_olusturur(self):
        n = Noron("n")
        d = Dendrid("d")
        s = Baglanti("s", n, None, esik=0.2)
        d.sinaps_bagla(s, 1.0)
        n.dendrit_ekle(d)
        d.girdi_al(10.0)
        n.girdileri_birlestir(0.0)
        self.assertGreater(s.potansiyel, 0.0)

    def test_negatif_dendrit_katkisi_sinaps_potansiyelini_negatif_yapar(self):
        n = Noron("n")
        d = Dendrid("d")
        s = Baglanti("s", n, None)
        d.sinaps_bagla(s, -1.0)
        n.dendrit_ekle(d)
        d.girdi_al(10.0)
        n.girdileri_birlestir(0.0)
        self.assertLess(s.potansiyel, 0.0)

    def test_sinaps_potansiyeli_esik_altindaysa_aktive_olamaz(self):
        s = Baglanti("s", None, None, esik=0.2)
        s.etki_uygula(0.1, 0.0)
        self.assertFalse(s.aktive_olabilir_mi(0.0))

    def test_sinaps_potansiyeli_esigi_gecerse_aktive_olabilir(self):
        s = Baglanti("s", None, None, esik=0.2)
        s.etki_uygula(1.0, 0.0)
        self.assertTrue(s.aktive_olabilir_mi(0.0))

    def test_pozitif_sinaptik_etki_potansiyeli_artirir(self):
        s = Baglanti("s", None, None)
        s.etki_uygula(1.0, 0.0)
        self.assertAlmostEqual(s.potansiyel, 0.5)

    def test_negatif_sinaptik_etki_potansiyeli_azaltir(self):
        s = Baglanti("s", None, None)
        s.etki_uygula(-1.0, 0.0)
        self.assertAlmostEqual(s.potansiyel, -0.5)

    def test_sinaptik_potansiyel_eksi_bir_arti_bir_araliginda_kalir(self):
        s = Baglanti("s", None, None)
        s.etki_uygula(1e12, 0.0)
        self.assertLessEqual(s.potansiyel, 1.0)
        s.etki_uygula(-1e12, 0.0)
        self.assertGreaterEqual(s.potansiyel, -1.0)

    def test_sinaptik_potansiyel_lazy_sonumle_azalir(self):
        s = Baglanti("s", None, None, sonum_tau=2.0)
        s.etki_uygula(1.0, 0.0)
        ilk = s.potansiyel
        s.potansiyeli_guncelle(2.0)
        self.assertAlmostEqual(s.potansiyel, ilk * math.exp(-1.0))

    def test_sonum_zamani_geriye_goturulurse_hata_verir(self):
        s = Baglanti("s", None, None)
        s.potansiyeli_guncelle(2.0)
        with self.assertRaises(ValueError):
            s.potansiyeli_guncelle(1.0)

    def test_ateslenme_sadece_esigi_gecen_cikis_sinapsini_aktive_eder(self):
        beyin = Beyin()
        n = Noron("n")
        d = Dendrid("d")
        uygun = Baglanti("uygun", n, None, esik=0.2)
        baskilanan = Baglanti("baskilanan", n, None, esik=0.2)
        d.sinaps_bagla(uygun, 1.0)
        d.sinaps_bagla(baskilanan, -1.0)
        n.dendrit_ekle(d)
        n.cikis_sinapsi_ekle(uygun)
        n.cikis_sinapsi_ekle(baskilanan)
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d", 100.0)
        beyin.calistir()
        self.assertEqual(uygun.aktivasyon_sayisi, 1)
        self.assertEqual(baskilanan.aktivasyon_sayisi, 0)

    def test_birden_cok_dendritin_katkisi_sinaps_bazinda_normalize_edilir(self):
        n = Noron("n")
        d1, d2 = Dendrid("d1"), Dendrid("d2")
        s = Baglanti("s", n, None)
        d1.sinaps_bagla(s, 0.5)
        d2.sinaps_bagla(s, 0.5)
        n.dendrit_ekle(d1)
        n.dendrit_ekle(d2)
        d1.girdi_al(10.0)
        d2.girdi_al(10.0)
        n.girdileri_birlestir(0.0)
        u = math.tanh(1.0)
        delta = (0.5 * u + 0.5 * u) / math.sqrt(2.0)
        beklenen = delta / (1.0 + delta)
        self.assertAlmostEqual(s.potansiyel, beklenen)

    def test_ogrenme_yalnizca_katki_yukleyen_dendritte_gerceklesir(self):
        beyin = Beyin()
        n = Noron("n")
        d1, d2 = Dendrid("d1"), Dendrid("d2")
        s = Baglanti("s", n, None, esik=0.2)
        d1.sinaps_bagla(s, 0.4)
        d2.sinaps_bagla(s, 0.7)
        n.dendrit_ekle(d1)
        n.dendrit_ekle(d2)
        n.cikis_sinapsi_ekle(s)
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d1", 100.0)
        beyin.calistir()
        self.assertAlmostEqual(d1.sinaps_katkilari[s], 0.41)
        self.assertAlmostEqual(d2.sinaps_katkilari[s], 0.7)

    def test_yeni_degerlendirme_olmayan_cifte_ilk_firsatta_ceza_verilmez(self):
        d = Dendrid("d")
        s = Baglanti("s", None, None)
        d.sinaps_bagla(s, 0.5)
        d.son_islenen_sinapslar.add(s)
        d.firsat_sonucu_ogren([], zaman=0.0)
        self.assertEqual(d.sinaps_katkilari[s], 0.5)

    def test_sonsuz_girdi_ve_konum_degerleri_reddedilir(self):
        with self.assertRaises(ValueError):
            Dendrid("d", konum=(0.0, float("nan")))
        with self.assertRaises(ValueError):
            Dendrid("d").girdi_al(float("inf"))
        with self.assertRaises(ValueError):
            Noron("n", esik=float("nan"))
        with self.assertRaises(ValueError):
            Baglanti("s", None, None, iletim_hizi=float("inf"))
        with self.assertRaises(ValueError):
            Baglanti("s", None, None, transmitter_profili={"A": float("nan")})


if __name__ == "__main__":
    unittest.main()

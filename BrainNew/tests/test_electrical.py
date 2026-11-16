import math
import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron
from BrainNew.KimyasalAlan import KimyasalAlan


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
        self.assertEqual(n.faz_gecisi_gecikmesi(), 1.0)

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

    def test_sinaps_esigi_potansiyel_araligi_disinda_olamaz(self):
        with self.assertRaises(ValueError):
            Baglanti("dusuk", None, None, esik=-1.01)
        with self.assertRaises(ValueError):
            Baglanti("yuksek", None, None, esik=1.01)

    def test_noron_baska_noronun_cikis_sinapsini_sahiplenemez(self):
        n1, n2 = Noron("n1"), Noron("n2")
        sinaps = Baglanti("s", n1, None)
        with self.assertRaises(ValueError):
            n2.cikis_sinapsi_ekle(sinaps)

    def test_ateslenme_terminal_salimini_dendritik_sinyalle_moduler(self):
        from BrainNew.KimyasalAlan import KimyasalAlan

        alan = KimyasalAlan()
        beyin = Beyin(alan)
        n = Noron("n")
        d = Dendrid("d")
        s = Baglanti(
            "s", n, None, esik=0.2,
            transmitter_profili={"A": 1.0},
            transmitter_salimi_duyarliliklari={"A": 0.5}
        )
        d.sinaps_bagla(s, 1.0)
        n.dendrit_ekle(d)
        n.cikis_sinapsi_ekle(s)
        beyin.noron_ekle(n)
        beyin.duyusal_girdi("n", "d", 100.0)
        beyin.calistir()
        self.assertEqual(alan.kaynak_sayisi(), 1)
        self.assertGreater(alan.kaynaklar[0].miktar, 1.0)

    def test_yerel_budama_sinyali_kullanim_izi_yokken_baglantiyi_koparabilir(self):
        alan = KimyasalAlan()
        s = Baglanti(
            "s", None, None, yapisal_yaslanma_tau=1000.0,
            budama_kazanci=1.0, budama_esigi=0.1,
            kopma_esigi=0.5
        )
        alan.sal("budama", s.terminal_konumu, 10.0, 0.0)
        self.assertFalse(s.yerel_bakim(alan, 1.0))
        self.assertTrue(s.kopuk)
        self.assertFalse(s.aktive_olabilir_mi(1.0))

    def test_stabilizasyon_sinyali_mevcut_baglantiyi_korur(self):
        alan = KimyasalAlan()
        s = Baglanti(
            "s", None, None, yapisal_yaslanma_tau=10.0,
            bakim_kazanci=0.5
        )
        once = s.yapisal_butunluk
        alan.sal("stabilizasyon", s.terminal_konumu, 2.0, 0.0)
        s.yerel_bakim(alan, 1.0)
        self.assertGreater(s.yapisal_butunluk, once * math.exp(-0.1))

    def test_ateslenme_olmasa_da_entegrasyon_olayinda_yerel_budama_isler(self):
        from BrainNew.KimyasalAlan import KimyasalAlan

        alan = KimyasalAlan()
        n = Noron("n")
        d = Dendrid("d")
        s = Baglanti(
            "s", n, None, budama_kazanci=1.0,
            budama_esigi=0.1, kopma_esigi=0.5
        )
        d.sinaps_bagla(s, 0.4)
        n.dendrit_ekle(d)
        n.cikis_sinapsi_ekle(s)
        alan.sal("budama", s.terminal_konumu, 10.0, 0.0)
        d.girdi_al(0.1)

        ateslendi, _ = n.entegrasyonu_isle(1.0, alan)
        self.assertFalse(ateslendi)
        self.assertTrue(s.kopuk)
        self.assertNotIn(s, n.cikis_sinapslari)
        self.assertNotIn(s, d.sinaps_katkilari)

    def test_kopmus_baglanti_yeniden_aktive_edilemez(self):
        s = Baglanti("s", None, None)
        s.kopuk = True
        self.assertFalse(s.aktive_olabilir_mi(1.0))
        with self.assertRaises(RuntimeError):
            s.aktive_et(1.0)

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

    def test_sinaptik_agirlik_kalici_elektriksel_iletim_etkisini_olcekler(self):
        sinaps = Baglanti("s", None, None, etki=4.0, sinaptik_agirlik=0.5)
        self.assertEqual(sinaps.iletim_etkisi(), 2.0)
        sinaps.sinaptik_agirligi_ayarla(1.5)
        self.assertEqual(sinaps.iletim_etkisi(), 6.0)

    def test_sinaptik_agirlik_sifirda_fonksiyonel_iletimi_kapatir(self):
        sinaps = Baglanti("s", None, None, etki=-4.0, sinaptik_agirlik=0.0)
        self.assertEqual(sinaps.iletim_etkisi(), 0.0)
        sinaps.sinaptik_agirligi_ayarla(0.5)
        self.assertEqual(sinaps.iletim_etkisi(), -2.0)

    def test_sinaptik_agirlik_sinirlanir_ve_gecersiz_degerleri_reddeder(self):
        sinaps = Baglanti("s", None, None)
        self.assertEqual(sinaps.sinaptik_agirligi_ayarla(3.0), 2.0)
        self.assertEqual(sinaps.sinaptik_agirligi_ayarla(-1.0), 0.0)
        with self.assertRaises(ValueError):
            Baglanti("nan", None, None, sinaptik_agirlik=float("nan"))
        with self.assertRaises(ValueError):
            sinaps.sinaptik_agirligi_ayarla(float("inf"))
    def test_hebbian_ogrenme_pre_post_birlikteliginde_agirligi_artirir(self):
        sinaps = Baglanti("s", None, None, hebbian_oran=0.1)
        sinaps.presinaptik_iz_arttir(0.0)
        degisim = sinaps.hebbian_ogren(1.0)

        beklenen_iz = math.exp(-1.0 / sinaps.pre_iz_tau)
        beklenen_degisim = 0.1 * beklenen_iz * 0.5
        self.assertAlmostEqual(degisim, beklenen_degisim)
        self.assertAlmostEqual(
            sinaps.sinaptik_agirlik, 1.0 + beklenen_degisim
        )
        self.assertEqual(sinaps.hebbian_guncelleme_sayisi, 1)

    def test_hebbian_ogrenme_presinaptik_iz_yokken_agirligi_degistirmez(self):
        sinaps = Baglanti("s", None, None)
        onceki = sinaps.sinaptik_agirlik
        self.assertEqual(sinaps.hebbian_ogren(1.0), 0.0)
        self.assertEqual(sinaps.sinaptik_agirlik, onceki)
        self.assertEqual(sinaps.hebbian_guncelleme_sayisi, 0)

    def test_hebbian_ogrenme_agirligi_ust_sinirda_tutar(self):
        sinaps = Baglanti(
            "s", None, None, sinaptik_agirlik=1.999,
            hebbian_oran=10.0
        )
        sinaps.presinaptik_iz_arttir(0.0)
        sinaps.hebbian_ogren(0.0)
        self.assertLessEqual(sinaps.sinaptik_agirlik, 2.0)
        self.assertAlmostEqual(sinaps.sinaptik_agirlik, 2.0)

    def test_hebbian_orani_gecersiz_degerleri_reddeder(self):
        with self.assertRaises(ValueError):
            Baglanti("negatif", None, None, hebbian_oran=-0.1)
        with self.assertRaises(ValueError):
            Baglanti("nan", None, None, hebbian_oran=float("nan"))

    def test_stdp_pre_sonra_post_agirligi_artirir(self):
        sinaps = Baglanti("pre_post", None, None)
        sinaps.stdp_presinaptik_olayi_isle(0.0)
        onceki = sinaps.sinaptik_agirlik
        artis = sinaps.stdp_postsinaptik_olayi_isle(1.0)
        self.assertGreater(artis, 0.0)
        self.assertGreater(sinaps.sinaptik_agirlik, onceki)

    def test_stdp_post_sonra_pre_agirligi_azaltir(self):
        sinaps = Baglanti("post_pre", None, None)
        sinaps.stdp_postsinaptik_olayi_isle(0.0)
        onceki = sinaps.sinaptik_agirlik
        azalis = sinaps.stdp_presinaptik_olayi_isle(1.0)
        self.assertGreater(azalis, 0.0)
        self.assertLess(sinaps.sinaptik_agirlik, onceki)

    def test_stdp_iz_olmadan_ters_sira_depresyonu_uygulamaz(self):
        sinaps = Baglanti("iz_yok", None, None)
        onceki = sinaps.sinaptik_agirlik
        self.assertEqual(sinaps.stdp_presinaptik_olayi_isle(1.0), 0.0)
        self.assertEqual(sinaps.sinaptik_agirlik, onceki)

    def test_stdp_agirlik_sinirlarini_korur(self):
        sinaps = Baglanti("sinir", None, None, sinaptik_agirlik=0.001)
        sinaps.stdp_postsinaptik_olayi_isle(0.0)
        sinaps.stdp_presinaptik_olayi_isle(0.0)
        self.assertGreaterEqual(sinaps.sinaptik_agirlik, 0.0)
        self.assertLessEqual(sinaps.sinaptik_agirlik, 2.0)

    def test_stdp_depresyon_orani_gecersiz_degerleri_reddeder(self):
        with self.assertRaises(ValueError):
            Baglanti("negatif", None, None, stdp_depresyon_oran=-0.1)
        with self.assertRaises(ValueError):
            Baglanti("nan", None, None, stdp_depresyon_oran=float("nan"))

    def test_presinaptik_iz_sinaps_aktivasyonunda_artar(self):
        sinaps = Baglanti("s", None, None)
        sinaps.aktive_et(1.0)
        self.assertAlmostEqual(sinaps.pre_iz, 1.0)
        self.assertEqual(sinaps.post_iz, 0.0)

    def test_post_izi_tum_gelen_sinapslarda_tutulur_ama_yalnizca_preli_sinaps_guclenir(self):
        beyin = Beyin()
        kaynak_aktif = Noron("kaynak_aktif")
        kaynak_sessiz = Noron("kaynak_sessiz")
        hedef = Noron("hedef")
        aktif_giris = Dendrid("aktif_giris")
        sessiz_giris = Dendrid("sessiz_giris")
        aktif_sinaps = Baglanti(
            "aktif_sinaps", kaynak_aktif, hedef,
            hedef_dendrit_id="aktif_giris", etki=50.0
        )
        sessiz_sinaps = Baglanti(
            "sessiz_sinaps", kaynak_sessiz, hedef,
            hedef_dendrit_id="sessiz_giris", etki=50.0
        )
        kaynak_giris = Dendrid("kaynak_giris")
        kaynak_giris.sinaps_bagla(aktif_sinaps, 1.0)
        kaynak_aktif.dendrit_ekle(kaynak_giris)
        kaynak_aktif.cikis_sinapsi_ekle(aktif_sinaps)
        kaynak_sessiz.cikis_sinapsi_ekle(sessiz_sinaps)
        hedef.dendrit_ekle(aktif_giris)
        hedef.dendrit_ekle(sessiz_giris)
        beyin.noron_ekle(kaynak_aktif)
        beyin.noron_ekle(kaynak_sessiz)
        beyin.noron_ekle(hedef)

        beyin.duyusal_girdi("kaynak_aktif", "kaynak_giris", 100.0)
        beyin.calistir()

        self.assertEqual(hedef.ateslenme_sayisi, 1)
        self.assertGreater(aktif_sinaps.post_iz, 0.0)
        self.assertGreater(aktif_sinaps.sinaptik_agirlik, 1.0)
        self.assertEqual(sessiz_sinaps.sinaptik_agirlik, 1.0)
        self.assertEqual(sessiz_sinaps.pre_iz, 0.0)
        # Post izi, daha sonra gelecek pre olayının LTD üretmesi için tutulur.
        self.assertGreater(sessiz_sinaps.post_iz, 0.0)

    def test_postsinaptik_iz_hedef_noron_ateslenince_artar(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        kaynak_giris = Dendrid("kaynak_giris")
        hedef_giris = Dendrid("hedef_giris")
        sinaps = Baglanti(
            "kaynak_hedef", kaynak, hedef,
            hedef_dendrit_id="hedef_giris", etki=50.0
        )
        kaynak_giris.sinaps_bagla(sinaps, 1.0)
        kaynak.dendrit_ekle(kaynak_giris)
        hedef.dendrit_ekle(hedef_giris)
        kaynak.cikis_sinapsi_ekle(sinaps)
        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)

        beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
        beyin.calistir()

        self.assertEqual(kaynak.ateslenme_sayisi, 1)
        self.assertEqual(hedef.ateslenme_sayisi, 1)
        # Presinaptik iz kaynak ateşlenmesinde t=0'da oluşur.
        # Hedefe iletim 1 zaman birimi sürdüğü için hedef ateşlenirken iz sönmüştür.
        self.assertAlmostEqual(sinaps.pre_iz, math.exp(-1.0 / sinaps.pre_iz_tau))
        self.assertAlmostEqual(sinaps.post_iz, 1.0)

    def test_pre_ve_post_izleri_bagimsiz_olarak_soner(self):
        sinaps = Baglanti("s", None, None)
        sinaps.pre_iz_tau = 2.0
        sinaps.post_iz_tau = 4.0
        sinaps.presinaptik_iz_arttir(0.0)
        sinaps.postsinaptik_iz_arttir(0.0)
        sinaps.izleri_guncelle(2.0)

        self.assertAlmostEqual(sinaps.pre_iz, math.exp(-1.0))
        self.assertAlmostEqual(sinaps.post_iz, math.exp(-0.5))

    def test_etkinlik_izleri_zamani_geriye_goturulemez(self):
        sinaps = Baglanti("s", None, None)
        sinaps.izleri_guncelle(2.0)
        with self.assertRaises(ValueError):
            sinaps.izleri_guncelle(1.0)

    def test_kopmus_gelen_sinaps_hedefin_gelen_listesinden_temizlenir(self):
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        sinaps = Baglanti(
            "s", kaynak, hedef, hedef_dendrit_id="d"
        )
        kaynak.cikis_sinapsi_ekle(sinaps)
        kaynak.baglantilari_bakimdan_gecir(1.0)
        # Bu testte kopma, bakım kuralıyla değil açık durumla tetiklenir.
        sinaps.kopuk = True
        kaynak.baglantilari_bakimdan_gecir(2.0)
        self.assertNotIn(sinaps, hedef.gelen_sinapslari)

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
        self.assertAlmostEqual(d1.sinaps_katkilari[s], 0.403)
        self.assertAlmostEqual(d2.sinaps_katkilari[s], 0.7)

    def test_dendrit_sinaps_ogrenmesi_sinirlar_icinde_kalir_ve_yakinlikta_yavaslar(self):
        d = Dendrid("d")
        s = Baglanti("s", None, None)
        d.sinaps_bagla(s, 0.99)
        d.son_islenen_sinapslar.add(s)
        d.firsat_sonucu_ogren([s], zaman=0.0, adim=0.1)
        self.assertGreater(d.sinaps_katkilari[s], 0.99)
        self.assertLess(d.sinaps_katkilari[s], 1.0)

        d.sinaps_katkilari[s] = 1.0
        d.son_islenen_sinapslar.add(s)
        d.firsat_sonucu_ogren([s], zaman=1.0, adim=0.1)
        self.assertEqual(d.sinaps_katkilari[s], 1.0)

        with self.assertRaises(ValueError):
            d.sinaps_bagla(Baglanti("disari", None, None), 1.1)
        with self.assertRaises(ValueError):
            d.firsat_sonucu_ogren([], zaman=2.0, adim=float("nan"))

    def test_ateslenmeyen_onceki_entegrasyonun_ogrenme_izi_sonraki_ateslenmeye_tasinmaz(self):
        n = Noron("n")
        d1, d2 = Dendrid("d1"), Dendrid("d2")
        s = Baglanti("s", n, None, esik=0.2)
        d1.sinaps_bagla(s, 0.4)
        d1.sinaps_degerlendirmeleri[s] = 1
        n.dendrit_ekle(d1)
        n.dendrit_ekle(d2)

        # İlk entegrasyon sinapsa katkı yükler fakat nöronu ateşletmez.
        d1.girdi_al(1.0)
        self.assertLess(n.girdileri_birlestir(0.0), n.esik - n.dinlenme_degeri)
        self.assertIn(s, d1.son_islenen_sinapslar)

        # Sonraki entegrasyonda d1 katkı sunmaz; d2 nöronu ateşletir.
        # Eski d1 izi taşınırsa s etkin olmadığı için hatalı negatif öğrenme olur.
        d2.girdi_al(100.0)
        ateslendi, _ = n.entegrasyonu_isle(1.0)
        self.assertTrue(ateslendi)
        self.assertAlmostEqual(d1.sinaps_katkilari[s], 0.4)

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

import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron


class HomeostazTestleri(unittest.TestCase):
    def test_sessiz_noron_simulasyon_zamani_ilerleyince_esigini_yavasca_dusurur(self):
        beyin = Beyin()
        noron = Noron(
            "sessiz", homeostatik_hedef_oran=0.02,
            homeostatik_tau=100.0, homeostatik_oran=0.01
        )
        beyin.noron_ekle(noron)

        beyin.calistir(son_zaman=100.0)

        self.assertLess(noron.esik, noron.esik_temel)
        self.assertGreaterEqual(
            noron.homeostatik_esik_kaymasi, noron.homeostatik_esik_alt
        )
        self.assertGreaterEqual(
            noron.esik, noron.esik_temel + noron.homeostatik_esik_alt
        )

    def test_asiri_ateslenme_esigi_yavasca_yukseltir(self):
        noron = Noron(
            "aktif", homeostatik_hedef_oran=0.02,
            homeostatik_tau=100.0, homeostatik_oran=0.01
        )
        for _ in range(5):
            noron.homeostatik_durumu_guncelle(0.0, yeni_ateslenme=True)

        noron.homeostatik_durumu_guncelle(100.0)

        self.assertGreater(noron.esik, noron.esik_temel)
        self.assertLessEqual(
            noron.homeostatik_esik_kaymasi, noron.homeostatik_esik_ust
        )

    def test_hedefe_yakin_aktivite_homeostatik_kaymayi_kucuk_tutar(self):
        noron = Noron(
            "denge", homeostatik_hedef_oran=0.02,
            homeostatik_tau=100.0, homeostatik_oran=0.01
        )
        # Her 10 zaman biriminde bir ateşlenme: hedef 0.02/zaman
        # değerinin yaklaşık yarısı değil, kontrollü düşük aktivite.
        for zaman in range(0, 101, 10):
            noron.homeostatik_durumu_guncelle(float(zaman))
            noron.homeostatik_durumu_guncelle(
                float(zaman), yeni_ateslenme=True
            )

        noron.homeostatik_durumu_guncelle(110.0)

        self.assertTrue(
            noron.homeostatik_esik_alt
            <= noron.homeostatik_esik_kaymasi
            <= noron.homeostatik_esik_ust
        )
        self.assertLess(abs(noron.homeostatik_esik_kaymasi), 0.1)

    def test_episode_sinirinda_uzun_donem_aktivite_izi_silinmez(self):
        beyin = Beyin()
        noron = Noron("n", homeostatik_tau=100.0)
        beyin.noron_ekle(noron)
        noron.homeostatik_durumu_guncelle(0.0, yeni_ateslenme=True)
        noron.homeostatik_durumu_guncelle(10.0)
        onceki_iz = noron.homeostatik_aktivite_izi

        beyin.zaman = 10.0
        beyin.episode_baslat()

        self.assertAlmostEqual(noron.homeostatik_aktivite_izi, onceki_iz)
        self.assertGreater(noron.homeostatik_aktivite_izi, 0.0)

    def test_homeostaz_sinaptik_ogrenilmis_parametreleri_degistirmez(self):
        beyin = Beyin()
        noron = Noron("n")
        hedef = Noron("hedef")
        dendrit = Dendrid("D")
        noron.dendrit_ekle(dendrit)
        sinaps = Baglanti("s", noron, hedef, hedef_dendrit_id="D")
        noron.cikis_sinapsi_ekle(sinaps)
        dendrit.sinaps_bagla(sinaps, -0.4)
        beyin.noron_ekle(noron)
        beyin.noron_ekle(hedef)
        sinaps.sinaptik_agirligi_ayarla(-1.25)
        onceki_agirlik = sinaps.sinaptik_agirlik
        onceki_katki = dendrit.sinaps_katkilari[sinaps]

        noron.homeostatik_durumu_guncelle(0.0, yeni_ateslenme=True)
        noron.homeostatik_durumu_guncelle(100.0)

        self.assertEqual(sinaps.sinaptik_agirlik, onceki_agirlik)
        self.assertEqual(dendrit.sinaps_katkilari[sinaps], onceki_katki)

    def test_homeostaz_ablasyonu_esigi_degistirmez(self):
        noron = Noron(
            "ablasyon", homeostatik_oran=0.0,
            homeostatik_hedef_oran=0.02
        )
        for _ in range(5):
            noron.homeostatik_durumu_guncelle(0.0, yeni_ateslenme=True)
        noron.homeostatik_durumu_guncelle(100.0)

        self.assertEqual(noron.esik, noron.esik_temel)
        self.assertEqual(noron.homeostatik_esik_kaymasi, 0.0)


if __name__ == "__main__":
    unittest.main()

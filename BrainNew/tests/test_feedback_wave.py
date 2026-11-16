import unittest

from BrainNew.Baglantı import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Noron import Noron


class GeriBildirimDallanmaTestleri(unittest.TestCase):
    def test_pozitif_feedback_yalnizca_noronun_aktiflik_kumesine_gore_esikleri_degistirir(self):
        beyin = Beyin()
        noron = Noron("hedef")
        aktif = Baglanti("aktif", noron, None)
        pasif = Baglanti("pasif", noron, None)
        noron.cikis_sinapsi_ekle(aktif)
        noron.cikis_sinapsi_ekle(pasif)
        noron.ateslenme_sayisi = 1
        noron._son_aktif_cikis_sinapslari = {aktif}
        beyin.noron_ekle(noron)

        beyin.geri_bildirim_baslat("hedef", pozitif=True, miktar=0.1)
        beyin.calistir()

        self.assertAlmostEqual(aktif.esik, 0.1)
        self.assertAlmostEqual(pasif.esik, 0.3)

    def test_feedback_nedensel_girdi_uzerinden_onceki_norona_dallanir(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        giris = Baglanti(
            "kaynak_hedef", kaynak, hedef, hedef_dendrit_id="hedef_d"
        )
        giris.presinaptik_iz_arttir(0.0)
        hedef.cikis_sinapsi_ekle(Baglanti("hedef_cikis", hedef, None))
        hedef.ateslenme_sayisi = 1
        hedef._son_nedensel_girdi_sinapslari = {giris}
        kaynak_cikis = Baglanti("kaynak_cikis", kaynak, None)
        kaynak.cikis_sinapsi_ekle(kaynak_cikis)
        kaynak.ateslenme_sayisi = 1
        kaynak._son_aktif_cikis_sinapslari = {kaynak_cikis}
        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)

        beyin.geri_bildirim_baslat("hedef", pozitif=True, miktar=0.1)
        beyin.calistir()

        self.assertAlmostEqual(kaynak_cikis.esik, 0.15)

    def test_geri_bildirim_dallanmasi_dongude_ziyaret_edilen_norona_donmez(self):
        beyin = Beyin()
        a = Noron("A")
        b = Noron("B")
        a_b = Baglanti("A_B", a, b, hedef_dendrit_id="B_d")
        b_a = Baglanti("B_A", b, a, hedef_dendrit_id="A_d")
        a_b.presinaptik_iz_arttir(0.0)
        b_a.presinaptik_iz_arttir(0.0)
        a._son_nedensel_girdi_sinapslari = {b_a}
        b._son_nedensel_girdi_sinapslari = {a_b}
        a_cikis = Baglanti("A_cikis", a, None)
        b_cikis = Baglanti("B_cikis", b, None)
        a.cikis_sinapsi_ekle(a_cikis)
        b.cikis_sinapsi_ekle(b_cikis)
        a._son_aktif_cikis_sinapslari = {a_cikis}
        b._son_aktif_cikis_sinapslari = {b_cikis}
        a.ateslenme_sayisi = 1
        b.ateslenme_sayisi = 1
        beyin.noron_ekle(a)
        beyin.noron_ekle(b)

        beyin.geri_bildirim_baslat("B", pozitif=True, miktar=0.1)
        beyin.calistir()

        self.assertAlmostEqual(b_cikis.esik, 0.1)
        self.assertAlmostEqual(a_cikis.esik, 0.15)


if __name__ == "__main__":
    unittest.main()

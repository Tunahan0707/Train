import unittest

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron


class SinyalYayilimiTestleri(unittest.TestCase):
    def test_duyusal_girdi_kaynagi_atesletir_ve_sinyal_hedefe_ulasir(self):
        beyin = Beyin()
        kaynak = Noron("kaynak")
        hedef = Noron("hedef")
        kaynak_dendrit = Dendrid("kaynak_giris")
        hedef_dendrit = Dendrid("hedef_giris")

        sinaps = Baglanti(
            "kaynak_hedef", kaynak, hedef,
            uzunluk=1.0, iletim_hizi=1.0,
            esik=0.2, hedef_dendrit_id="hedef_giris", etki=100.0,
        )
        kaynak_dendrit.sinaps_bagla(sinaps, 1.0)
        kaynak.dendrit_ekle(kaynak_dendrit)
        kaynak.cikis_sinapsi_ekle(sinaps)
        hedef.dendrit_ekle(hedef_dendrit)
        beyin.noron_ekle(kaynak)
        beyin.noron_ekle(hedef)

        beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)
        beyin.calistir()

        self.assertEqual(kaynak.ateslenme_sayisi, 1)
        self.assertEqual(sinaps.aktivasyon_sayisi, 1)
        self.assertEqual(hedef.ateslenme_sayisi, 1)


if __name__ == "__main__":
    unittest.main()

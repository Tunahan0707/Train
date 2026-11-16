import unittest

from BrainNew.Beyin import Beyin
from BrainNew.DeneyKaydi import DeneyKaydi
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron


def ag_kur(kayit=None):
    beyin = Beyin(deney_kaydi=kayit)
    noron = Noron("n")
    noron.dendrit_ekle(Dendrid("d"))
    beyin.noron_ekle(noron)
    beyin.duyusal_girdi("n", "d", 100.0)
    return beyin, noron


class DeneyKaydiTestleri(unittest.TestCase):
    def test_kayitli_ve_kayitsiz_simulasyon_ayni_davranir(self):
        kayit = DeneyKaydi()
        beyin_a, noron_a = ag_kur()
        beyin_b, noron_b = ag_kur(kayit)
        islenen_a = beyin_a.calistir()
        islenen_b = beyin_b.calistir()
        self.assertEqual(islenen_a, islenen_b)
        self.assertEqual(noron_a.ateslenme_sayisi, noron_b.ateslenme_sayisi)
        self.assertEqual(beyin_a.zaman, beyin_b.zaman)

    def test_kuyruktan_cikan_her_olay_kronolojik_kaydedilir(self):
        kayit = DeneyKaydi()
        beyin, _ = ag_kur(kayit)
        beyin.calistir()
        zamanlar = [olay[0] for olay in kayit.olaylar]
        self.assertEqual(zamanlar, sorted(zamanlar))
        self.assertEqual(kayit.olay_sayisi(), 5)

    def test_ayni_zamanli_olaylarda_sira_numarasi_korunur(self):
        kayit = DeneyKaydi()
        beyin, _ = ag_kur(kayit)
        beyin.duyusal_girdi("n", "d", 1.0)
        beyin.calistir()
        olaylar = [olay for olay in kayit.olaylar if olay[2] == "duyusal_girdi"]
        self.assertEqual([olay[1] for olay in olaylar], sorted(olay[1] for olay in olaylar))

    def test_kayit_verisi_kayit_aninda_kopyalanir(self):
        kayit = DeneyKaydi()
        veri = {"b": [2, 3], "a": 1}
        kayit.olay_kaydet(1.0, 0, "test", "hedef", veri)
        veri["b"].append(4)
        self.assertEqual(kayit.olaylar[0][4], (("a", 1), ("b", (2, 3))))

    def test_desteklenmeyen_veri_turu_acik_hata_verir(self):
        kayit = DeneyKaydi()
        with self.assertRaises(TypeError):
            kayit.olay_kaydet(0.0, 0, "test", "hedef", object())

    def test_kayit_temizleme_sayaci_sifirlar(self):
        kayit = DeneyKaydi()
        kayit.olay_kaydet(0.0, 0, "test", "hedef")
        kayit.temizle()
        self.assertEqual(kayit.olay_sayisi(), 0)


if __name__ == "__main__":
    unittest.main()

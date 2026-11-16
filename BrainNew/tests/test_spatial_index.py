import unittest

from BrainNew.Noron import Noron
from BrainNew.UzamsalIndeks import UzamsalIndeks


class UzamsalIndeksTestleri(unittest.TestCase):
    def test_yalnizca_yaricap_icindeki_noronlari_dondurur(self):
        indeks = UzamsalIndeks(hucre_boyu=5.0)
        yakin = Noron("yakin", konum=(3.0, 4.0))
        sinir = Noron("sinir", konum=(5.0, 0.0))
        uzak = Noron("uzak", konum=(5.01, 0.0))
        for n in (yakin, sinir, uzak):
            indeks.ekle(n)
        sonuc = indeks.yakinindakileri_bul((0.0, 0.0), 5.0)
        self.assertEqual({n.kimlik for n in sonuc}, {"yakin", "sinir"})

    def test_sorgu_mesafeye_gore_deterministik_siralar(self):
        indeks = UzamsalIndeks(hucre_boyu=2.0)
        uzak = Noron("a_uzak", konum=(2.0, 0.0))
        yakin_b = Noron("b", konum=(-1.0, 0.0))
        yakin_a = Noron("a", konum=(1.0, 0.0))
        for n in (uzak, yakin_b, yakin_a):
            indeks.ekle(n)
        self.assertEqual(
            [n.kimlik for n in indeks.yakinindakileri_bul((0.0, 0.0), 3.0)],
            ["a", "b", "a_uzak"]
        )

    def test_kendini_haric_tutabilir(self):
        indeks = UzamsalIndeks()
        a, b = Noron("a"), Noron("b", konum=(1.0, 0.0))
        indeks.ekle(a)
        indeks.ekle(b)
        self.assertEqual(indeks.yakinindakileri_bul(a.konum, 2.0, haric=a), [b])

    def test_konum_guncellemesi_hucreler_arasinda_tasinir(self):
        indeks = UzamsalIndeks(hucre_boyu=1.0)
        n = Noron("n")
        indeks.ekle(n)
        indeks.konumu_guncelle(n, (10.0, -3.0))
        self.assertEqual(indeks.yakinindakileri_bul((10.0, -3.0), 0.0), [n])
        self.assertEqual(indeks.yakinindakileri_bul((0.0, 0.0), 1.0), [])

    def test_kayit_silme_ve_tekrar_kayit(self):
        indeks = UzamsalIndeks()
        n = Noron("n")
        self.assertTrue(indeks.ekle(n))
        self.assertFalse(indeks.ekle(n))
        self.assertTrue(indeks.cikar(n))
        self.assertFalse(indeks.cikar(n))
        self.assertEqual(len(indeks), 0)
        self.assertTrue(indeks.ekle(n))

    def test_yinelenen_kimlikli_farkli_noron_reddedilir(self):
        indeks = UzamsalIndeks()
        indeks.ekle(Noron("n"))
        with self.assertRaises(ValueError):
            indeks.ekle(Noron("n", konum=(1.0, 1.0)))

    def test_gecersiz_parametreler_reddedilir(self):
        with self.assertRaises(ValueError):
            UzamsalIndeks(0.0)
        indeks = UzamsalIndeks()
        with self.assertRaises(ValueError):
            indeks.yakinindakileri_bul((0.0, 0.0), -1.0)
        with self.assertRaises(ValueError):
            indeks.yakinindakileri_bul((float("nan"), 0.0), 1.0)


if __name__ == "__main__":
    unittest.main()

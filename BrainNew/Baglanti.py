import math


class Baglanti:
    """Bir nöronun seçici çıkış sinapsı ve hedefe iletim bağlantısı."""

    def __init__(
        self, kimlik, kaynak, hedef, uzunluk=1.0, iletim_hizi=1.0,
        esik=0.2, sönum_tau=5.0, baslangic_potansiyeli=0.0
    ):
        if uzunluk < 0 or iletim_hizi <= 0 or sönum_tau <= 0:
            raise ValueError("Bağlantı parametreleri geçersiz.")
        self.kimlik = kimlik
        self.kaynak = kaynak
        self.hedef = hedef
        self.uzunluk = float(uzunluk)
        self.iletim_hizi = float(iletim_hizi)
        self.esik = float(esik)
        self.sönum_tau = float(sönum_tau)
        self.potansiyel = float(baslangic_potansiyeli)
        self.son_guncelleme = 0.0
        self.son_aktivasyon = None
        self.aktivasyon_sayisi = 0
        self.iz = 0.0
        self.son_iz_zamani = 0.0

    def potansiyeli_guncelle(self, zaman):
        if zaman < self.son_guncelleme:
            raise ValueError("Simülasyon zamanı geriye gidemez.")
        gecen = zaman - self.son_guncelleme
        if gecen:
            self.potansiyel *= math.exp(-gecen / self.sönum_tau)
            self.iz *= math.exp(-gecen / self.sönum_tau)
            self.son_guncelleme = zaman
            self.son_iz_zamani = zaman

    def etki_uygula(self, etki, zaman):
        self.potansiyeli_guncelle(zaman)
        r = abs(etki) / (1.0 + abs(etki))
        if etki >= 0:
            self.potansiyel += (1.0 - self.potansiyel) * r
        else:
            self.potansiyel -= (1.0 + self.potansiyel) * r
        self.potansiyel = max(-1.0, min(1.0, self.potansiyel))

    def aktive_olabilir_mi(self, zaman):
        self.potansiyeli_guncelle(zaman)
        return self.potansiyel >= self.esik

    def aktive_et(self, zaman):
        self.potansiyeli_guncelle(zaman)
        self.son_aktivasyon = zaman
        self.aktivasyon_sayisi += 1
        self.iz += 1.0
        self.son_iz_zamani = zaman
        return self.uzunluk / self.iletim_hizi

import math


class Baglanti:
    """Seçici çıkış sinapsı, kimyasal terminal profili ve iletim bağlantısı."""

    MINIMUM_GECIKME = 1e-6

    def __init__(
        self, kimlik, kaynak, hedef, uzunluk=1.0, iletim_hizi=1.0,
        esik=0.2, sonum_tau=5.0, baslangic_potansiyeli=0.0,
        hedef_dendrit_id=None, etki=1.0, terminal_konumu=None,
        transmitter_profili=None, kimyasal_yayilim=1.0,
        kimyasal_temizlenme=0.1
    ):
        if uzunluk < 0 or iletim_hizi <= 0 or sonum_tau <= 0:
            raise ValueError("Bağlantı parametreleri geçersiz.")
        if not -1.0 <= baslangic_potansiyeli <= 1.0:
            raise ValueError("Başlangıç potansiyeli [-1, 1] aralığında olmalı.")
        if kimyasal_yayilim <= 0 or kimyasal_temizlenme < 0:
            raise ValueError("Kimyasal yayılım parametreleri geçersiz.")
        self.kimlik = kimlik
        self.kaynak = kaynak
        self.hedef = hedef
        self.hedef_dendrit_id = hedef_dendrit_id
        self.etki = float(etki)
        self.uzunluk = float(uzunluk)
        self.iletim_hizi = float(iletim_hizi)
        self.esik = float(esik)
        self.sonum_tau = float(sonum_tau)
        self.potansiyel = float(baslangic_potansiyeli)
        self.son_guncelleme = 0.0
        self.son_aktivasyon = None
        self.aktivasyon_sayisi = 0
        self.iz = 0.0
        self.terminal_konumu = tuple(
            terminal_konumu if terminal_konumu is not None
            else getattr(kaynak, "konum", (0.0, 0.0))
        )
        self.transmitter_profili = dict(transmitter_profili or {})
        if any(miktar < 0 for miktar in self.transmitter_profili.values()):
            raise ValueError("Transmitter salım miktarları negatif olamaz.")
        self.kimyasal_yayilim = float(kimyasal_yayilim)
        self.kimyasal_temizlenme = float(kimyasal_temizlenme)

    def potansiyeli_guncelle(self, zaman):
        if zaman < self.son_guncelleme:
            raise ValueError("Simülasyon zamanı geriye gidemez.")
        gecen = zaman - self.son_guncelleme
        if gecen:
            carp = math.exp(-gecen / self.sonum_tau)
            self.potansiyel *= carp
            self.iz *= carp
            self.son_guncelleme = zaman

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
        return max(self.MINIMUM_GECIKME, self.uzunluk / self.iletim_hizi)

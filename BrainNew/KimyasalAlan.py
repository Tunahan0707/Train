import math


class KimyasalKaynak:
    """Bir kimyasal sinyalin uzay-zamandaki salım olayı."""

    def __init__(self, tur, konum, miktar, zaman, yayilim, temizlenme):
        sayisal = (miktar, zaman, yayilim, temizlenme)
        if not all(math.isfinite(float(v)) for v in sayisal):
            raise ValueError("Kimyasal kaynak parametreleri sonlu sayılar olmalı.")
        if miktar < 0 or zaman < 0 or yayilim <= 0 or temizlenme < 0:
            raise ValueError("Kimyasal kaynak parametreleri geçersiz.")
        if len(konum) != 2 or not all(math.isfinite(float(v)) for v in konum):
            raise ValueError("Kimyasal kaynak konumu sonlu iki boyutlu koordinat olmalı.")
        self.tur = tur
        self.konum = tuple(float(v) for v in konum)
        self.miktar = float(miktar)
        self.zaman = float(zaman)
        self.yayilim = float(yayilim)
        self.temizlenme = float(temizlenme)


class KimyasalAlan:
    """
    2B hacimsel iletim için analitik, kaynak-tabanlı ilk prototip.

    Her kaynak bağımsız tutulur. Alan sorgusu kaynakların uzaysal yayılımını
    ve zamansal sönümünü toplar. Performans için keyfî yarıçap kesmesi yoktur.
    """

    def __init__(self):
        self.kaynaklar = []

    def sal(self, tur, konum, miktar, zaman, yayilim=1.0, temizlenme=0.1):
        kaynak = KimyasalKaynak(
            tur, konum, miktar, zaman, yayilim, temizlenme
        )
        self.kaynaklar.append(kaynak)
        return kaynak

    def yogunluk(self, tur, konum, zaman):
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < 0:
            raise ValueError("Kimyasal alan sorgu zamanı sonlu ve negatif olmayan değer olmalı.")
        if len(konum) != 2 or not all(math.isfinite(float(v)) for v in konum):
            raise ValueError("Sorgu konumu sonlu iki boyutlu koordinat olmalı.")
        x, y = (float(v) for v in konum)
        toplam = 0.0

        for kaynak in self.kaynaklar:
            if kaynak.tur != tur or zaman <= kaynak.zaman:
                continue

            yas = zaman - kaynak.zaman
            dx = x - kaynak.konum[0]
            dy = y - kaynak.konum[1]
            uzaklik_kare = dx * dx + dy * dy

            payda = 4.0 * math.pi * kaynak.yayilim * yas
            uzaysal = math.exp(
                -uzaklik_kare / (4.0 * kaynak.yayilim * yas)
            )
            zamansal = math.exp(-kaynak.temizlenme * yas)
            toplam += kaynak.miktar * uzaysal * zamansal / payda

        return toplam

    def kaynak_sayisi(self):
        return len(self.kaynaklar)

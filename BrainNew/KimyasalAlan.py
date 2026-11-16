import math


class KimyasalKaynak:
    """Bir kimyasal sinyalin uzay-zamandaki salım olayı."""

    def __init__(self, tur, konum, miktar, zaman, yayilim, temizlenme):
        if miktar < 0 or yayilim <= 0 or temizlenme < 0:
            raise ValueError("Kimyasal kaynak parametreleri geçersiz.")
        self.tur = tur
        self.konum = tuple(konum)
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
        x, y = konum
        toplam = 0.0

        for kaynak in self.kaynaklar:
            if kaynak.tur != tur or zaman < kaynak.zaman:
                continue

            yas = zaman - kaynak.zaman
            yayilmis_zaman = max(yas, 1e-9)
            dx = x - kaynak.konum[0]
            dy = y - kaynak.konum[1]
            uzaklik_kare = dx * dx + dy * dy

            payda = 4.0 * math.pi * kaynak.yayilim * yayilmis_zaman
            uzaysal = math.exp(
                -uzaklik_kare / (4.0 * kaynak.yayilim * yayilmis_zaman)
            )
            zamansal = math.exp(-kaynak.temizlenme * yas)
            toplam += kaynak.miktar * uzaysal * zamansal / payda

        return toplam

    def kaynak_sayisi(self):
        return len(self.kaynaklar)

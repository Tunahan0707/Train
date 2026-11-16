import math
import random

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.Noron import Noron


class AgKurucu:
    """Seed'li, 2B uzamsal ve seyrek başlangıç ağı üretir.

    Bu sınıf yalnızca başlangıç topolojisini kurar. Öğrenme, feedback,
    budama veya bağlantı seçimi simülasyon sırasında burada yapılmaz.
    """

    def __init__(
        self,
        noron_sayisi,
        seed=0,
        dendrit_sayisi=8,
        baglanti_olasiligi=0.08,
        baglanti_yaricapi=20.0,
        uzay_boyutu=(100.0, 100.0),
        dendrit_yayilimi=1.0,
        iletim_hizi=1.0,
        uyarici_orani=0.8,
    ):
        sayisal = (
            baglanti_olasiligi, baglanti_yaricapi,
            dendrit_yayilimi, iletim_hizi, uyarici_orani,
            *uzay_boyutu,
        )
        if not all(math.isfinite(float(v)) for v in sayisal):
            raise ValueError("Ağ kurucu parametreleri sonlu olmalı.")
        if not isinstance(noron_sayisi, int) or noron_sayisi < 1:
            raise ValueError("Nöron sayısı pozitif tam sayı olmalı.")
        if not isinstance(dendrit_sayisi, int) or dendrit_sayisi < 1:
            raise ValueError("Dendrit sayısı pozitif tam sayı olmalı.")
        if not 0.0 <= baglanti_olasiligi <= 1.0:
            raise ValueError("Bağlantı olasılığı [0, 1] aralığında olmalı.")
        if baglanti_yaricapi < 0 or dendrit_yayilimi < 0:
            raise ValueError("Uzamsal yarıçaplar negatif olamaz.")
        if iletim_hizi <= 0 or not 0.0 <= uyarici_orani <= 1.0:
            raise ValueError("İletim hızı veya uyarıcı oranı geçersiz.")
        if len(uzay_boyutu) != 2 or any(float(v) <= 0 for v in uzay_boyutu):
            raise ValueError("Uzay boyutu pozitif iki koordinat olmalı.")

        self.noron_sayisi = noron_sayisi
        self.seed = seed
        self.dendrit_sayisi = dendrit_sayisi
        self.baglanti_olasiligi = float(baglanti_olasiligi)
        self.baglanti_yaricapi = float(baglanti_yaricapi)
        self.uzay_boyutu = tuple(float(v) for v in uzay_boyutu)
        self.dendrit_yayilimi = float(dendrit_yayilimi)
        self.iletim_hizi = float(iletim_hizi)
        self.uyarici_orani = float(uyarici_orani)

    def kur(self):
        """Aynı yapılandırma ve seed ile aynı ağı üretir."""
        rng = random.Random(self.seed)
        genislik, yukseklik = self.uzay_boyutu
        beyin = Beyin()
        noronlar = []

        for i in range(self.noron_sayisi):
            kimlik = f"N{i}"
            konum = (rng.uniform(0.0, genislik), rng.uniform(0.0, yukseklik))
            noron = Noron(kimlik, konum=konum)
            for j in range(self.dendrit_sayisi):
                dx = rng.uniform(-self.dendrit_yayilimi, self.dendrit_yayilimi)
                dy = rng.uniform(-self.dendrit_yayilimi, self.dendrit_yayilimi)
                dendrit = Dendrid(
                    f"{kimlik}:D{j}",
                    konum=(konum[0] + dx, konum[1] + dy),
                )
                noron.dendrit_ekle(dendrit)
            noronlar.append(noron)

        baglanti_sayisi = 0
        yaricap2 = self.baglanti_yaricapi ** 2
        for kaynak in noronlar:
            for hedef in noronlar:
                if kaynak is hedef:
                    continue
                dx = hedef.konum[0] - kaynak.konum[0]
                dy = hedef.konum[1] - kaynak.konum[1]
                uzaklik2 = dx * dx + dy * dy
                if uzaklik2 > yaricap2 or rng.random() >= self.baglanti_olasiligi:
                    continue

                hedef_dendrit = rng.choice(
                    tuple(hedef.dendritler.values())
                )
                kimlik = f"S:{kaynak.kimlik}->{hedef.kimlik}:{baglanti_sayisi}"
                etki = 1.0 if rng.random() < self.uyarici_orani else -1.0
                sinaps = Baglanti(
                    kimlik,
                    kaynak,
                    hedef,
                    uzunluk=math.sqrt(uzaklik2),
                    iletim_hizi=self.iletim_hizi,
                    hedef_dendrit_id=hedef_dendrit.kimlik,
                    etki=etki,
                    terminal_konumu=kaynak.konum,
                )
                for dendrit in kaynak.dendritler.values():
                    dendrit.sinaps_bagla(
                        sinaps, rng.uniform(-0.1, 0.1)
                    )
                kaynak.cikis_sinapsi_ekle(sinaps)
                baglanti_sayisi += 1

        for noron in noronlar:
            beyin.noron_ekle(noron)

        beyin.ag_ozeti = {
            "seed": self.seed,
            "noron_sayisi": len(noronlar),
            "baglanti_sayisi": baglanti_sayisi,
            "dendrit_sayisi": self.noron_sayisi * self.dendrit_sayisi,
        }
        return beyin

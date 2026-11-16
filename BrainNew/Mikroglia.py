import math


class Mikroglia:
    """Bağımsız, yerel çevreyi tarayan mikroglia-benzeri bakım ajanı.

    Hücre gövdesi bu ilk modelde sabittir. Algılama yarıçapı, hareketli
    uzantıların çevreyi taramasının hesaplamalı soyutlamasıdır.
    """

    def __init__(
        self, kimlik, konum=(0.0, 0.0), algilama_yaricapi=5.0,
        bakim_araligi=10.0
    ):
        sayisal = (algilama_yaricapi, bakim_araligi)
        if not all(math.isfinite(float(v)) for v in sayisal):
            raise ValueError("Mikroglia parametreleri sonlu olmalı.")
        if len(konum) != 2 or not all(math.isfinite(float(v)) for v in konum):
            raise ValueError("Mikroglia konumu sonlu iki boyutlu koordinat olmalı.")
        if algilama_yaricapi < 0 or bakim_araligi <= 0:
            raise ValueError("Algılama yarıçapı negatif olamaz; bakım aralığı pozitif olmalı.")

        self.kimlik = kimlik
        self.konum = tuple(float(v) for v in konum)
        self.algilama_yaricapi = float(algilama_yaricapi)
        self.bakim_araligi = float(bakim_araligi)
        self.son_tarama_zamani = 0.0
        self.taranan_baglanti_sayisi = 0
        self.koparilan_baglanti_sayisi = 0

    def bakim_yap(self, baglanti_indeksi, kimyasal_alan, zaman):
        """Yalnızca algılama alanındaki bağlantıları yerel olarak değerlendirir."""
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < self.son_tarama_zamani:
            raise ValueError("Mikroglia tarama zamanı sonlu olmalı ve geriye gitmemeli.")

        yakin_baglantilar = baglanti_indeksi.yakinindakileri_bul(
            self.konum, self.algilama_yaricapi
        )
        kopanlar = []

        for sinaps in yakin_baglantilar:
            if sinaps.kopuk:
                continue

            onceki_bakim = sinaps.son_bakim_zamani
            if zaman < onceki_bakim:
                raise ValueError("Bağlantı bakım zamanı mikroglia zamanından ileride.")
            gecen = zaman - onceki_bakim
            if gecen == 0.0:
                continue

            # Kullanım izi ve terminal potansiyeli kendi zaman sabitleriyle söner.
            sinaps.potansiyeli_guncelle(zaman)

            sinyaller = {"buyume": 0.0, "stabilizasyon": 0.0, "budama": 0.0}
            if kimyasal_alan is not None:
                for tur in sinyaller:
                    sinyaller[tur] = kimyasal_alan.yogunluk(
                        tur, sinaps.terminal_konumu, zaman
                    )
            sinaps.son_yapisal_sinyaller = sinyaller

            if sinaps.kullanim_izi_esigi > 0.0:
                kullanim = min(1.0, sinaps.iz / sinaps.kullanim_izi_esigi)
            else:
                kullanim = 1.0 if sinaps.iz > 0.0 else 0.0
            kullanilmama = 1.0 - kullanim

            # Etkin bağlantı daha yavaş yaşlanır. Kimyasal budama işareti
            # olmadan yalnızca kullanılmama fiziksel kopmaya yol açmaz.
            yaslanma = math.exp(
                -gecen * kullanilmama / sinaps.yapisal_yaslanma_tau
            )
            butunluk = sinaps.yapisal_butunluk * yaslanma

            zaman_olcegi = min(1.0, gecen / self.bakim_araligi)
            koruma = sinyaller["buyume"] + sinyaller["stabilizasyon"]
            budama = sinyaller["budama"]
            butunluk += sinaps.bakim_kazanci * koruma * zaman_olcegi
            butunluk -= (
                sinaps.budama_kazanci * budama
                * kullanilmama * zaman_olcegi
            )
            sinaps.yapisal_butunluk = max(0.0, min(1.0, butunluk))

            # Olgunluk, fiziksel bütünlükten ayrı bir işlevsel gelişim durumudur.
            # Kullanım ve stabilizasyon olgunlaştırır; kimyasal budama azaltır.
            olgunluk = sinaps.yapisal_olgunluk
            olgunluk += (
                sinaps.olgunlasma_kazanci
                * (kullanim + sinyaller["stabilizasyon"])
                * zaman_olcegi * (1.0 - olgunluk)
            )
            olgunluk -= (
                sinaps.olgunluk_budama_kazanci * budama
                * kullanilmama * zaman_olcegi * olgunluk
            )
            sinaps.yapisal_olgunluk = max(0.0, min(1.0, olgunluk))
            sinaps.son_bakim_zamani = zaman

            if (
                kullanilmama > 0.0
                and budama >= sinaps.budama_esigi
                and sinaps.yapisal_butunluk <= sinaps.kopma_esigi
            ):
                sinaps.kopuk = True
                kopanlar.append(sinaps)

        self.son_tarama_zamani = zaman
        self.taranan_baglanti_sayisi += len(yakin_baglantilar)
        self.koparilan_baglanti_sayisi += len(kopanlar)
        return tuple(kopanlar)

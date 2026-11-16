import math


class Dendrid:
    """İşaretli girdiyi toplar ve yerel sinapslar için sinyal üretir."""

    def __init__(
        self, kimlik, konum=(0.0, 0.0), sinyal_olcegi=10.0,
        katki_alt=-1.0, katki_ust=1.0
    ):
        sayisal = (sinyal_olcegi, katki_alt, katki_ust)
        if not all(math.isfinite(float(v)) for v in sayisal):
            raise ValueError("Dendrit parametreleri sonlu sayılar olmalı.")
        if sinyal_olcegi <= 0:
            raise ValueError("Sinyal ölçeği pozitif olmalı.")
        if katki_alt >= katki_ust:
            raise ValueError("Sinaps katkısı alt sınırı üst sınırdan küçük olmalı.")
        if len(konum) != 2 or not all(math.isfinite(float(v)) for v in konum):
            raise ValueError("Dendrit konumu sonlu iki boyutlu koordinat olmalı.")
        self.kimlik = kimlik
        self.konum = tuple(float(v) for v in konum)
        self.sinyal_olcegi = float(sinyal_olcegi)
        self.katki_alt = float(katki_alt)
        self.katki_ust = float(katki_ust)
        self.sinaps_katkilari = {}
        self.girdiler = []
        # Bu entegrasyonda dendrite ulaşan gerçek kaynak bağlantılar.
        self.bekleyen_kaynak_sinapslari = []
        self.son_girdi_kaynak_sinapslari = ()
        self.reseptor_duyarliliklari = {}
        self.son_islenen_sinapslar = set()
        self.sinaps_degerlendirmeleri = {}

    def sinaps_bagla(self, sinaps, katki):
        katki = float(katki)
        if not math.isfinite(katki):
            raise ValueError("Sinaps katkısı sonlu olmalı.")
        if not self.katki_alt <= katki <= self.katki_ust:
            raise ValueError("Sinaps katkısı tanımlı sınırların dışında.")
        self.sinaps_katkilari[sinaps] = katki

    def transmitter_duyarliligi_ayarla(self, tur, duyarlilik):
        duyarlilik = float(duyarlilik)
        if not math.isfinite(duyarlilik):
            raise ValueError("Reseptör duyarlılığı sonlu olmalı.")
        self.reseptor_duyarliliklari[tur] = duyarlilik

    def kimyasal_yanit(self, kimyasal_alan, zaman):
        toplam = 0.0
        for tur, duyarlilik in self.reseptor_duyarliliklari.items():
            yogunluk = kimyasal_alan.yogunluk(tur, self.konum, zaman)
            toplam += duyarlilik * (yogunluk / (1.0 + yogunluk))
        if not math.isfinite(toplam):
            raise ValueError("Kimyasal reseptör yanıtı sonlu olmalı.")
        return toplam


    def buyume_uygunlugu(self, kimyasal_alan, zaman):
        """Dendritin yerel büyüme sinyaline reseptör yanıtı."""
        duyarlilik = self.reseptor_duyarliliklari.get("buyume", 0.0)
        if kimyasal_alan is None or duyarlilik <= 0.0:
            return 0.0
        yogunluk = kimyasal_alan.yogunluk("buyume", self.konum, zaman)
        return duyarlilik * (yogunluk / (1.0 + yogunluk))

    def girdi_al(self, etki, kaynak_sinaps=None):
        etki = float(etki)
        if not math.isfinite(etki):
            raise ValueError("Dendrit girdisi sonlu olmalı.")
        self.girdiler.append(etki)
        if kaynak_sinaps is not None:
            self.bekleyen_kaynak_sinapslari.append(kaynak_sinaps)

    def girdi_var_mi(self):
        return bool(self.girdiler)

    def sinyali_hazirla(self, zaman, kimyasal_alan=None):
        self.son_girdi_kaynak_sinapslari = tuple(
            self.bekleyen_kaynak_sinapslari
        )
        self.bekleyen_kaynak_sinapslari.clear()
        if not self.girdiler:
            return 0.0, 0.0

        elektriksel_toplam = sum(self.girdiler)
        if not math.isfinite(elektriksel_toplam):
            raise ValueError("Dendritik girdi toplamı sonlu olmalı.")
        self.girdiler.clear()

        kimyasal_modulasyon = 0.0
        if kimyasal_alan is not None and self.reseptor_duyarliliklari:
            kimyasal_modulasyon = self.kimyasal_yanit(kimyasal_alan, zaman)

        u = math.tanh(
            elektriksel_toplam / self.sinyal_olcegi + kimyasal_modulasyon
        )
        return elektriksel_toplam, u

    def firsat_sonucu_ogren(self, aktif_sinapslar, zaman, adim=0.01):
        """Katkıyı toplamsal günceller; değişim sınırlara yaklaştıkça küçülür."""
        adim = float(adim)
        if not math.isfinite(adim) or adim < 0:
            raise ValueError("Öğrenme adımı sonlu ve negatif olmayan değer olmalı.")

        aralik = self.katki_ust - self.katki_alt
        for sinaps in self.son_islenen_sinapslar:
            mevcut = self.sinaps_katkilari[sinaps]
            if sinaps in aktif_sinapslar:
                delta = adim * (self.katki_ust - mevcut) / aralik
            elif self.sinaps_degerlendirmeleri.get(sinaps, 0) > 0:
                delta = -adim * (mevcut - self.katki_alt) / aralik
            else:
                delta = 0.0

            self.sinaps_katkilari[sinaps] = max(
                self.katki_alt,
                min(self.katki_ust, mevcut + delta)
            )
            self.sinaps_degerlendirmeleri[sinaps] = (
                self.sinaps_degerlendirmeleri.get(sinaps, 0) + 1
            )
        self.son_islenen_sinapslar.clear()

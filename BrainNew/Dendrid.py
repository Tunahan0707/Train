import math


class Dendrid:
    """İşaretli girdiyi toplar ve yerel sinapslar için sinyal üretir."""

    def __init__(self, kimlik, konum=(0.0, 0.0), sinyal_olcegi=10.0):
        if not math.isfinite(float(sinyal_olcegi)) or sinyal_olcegi <= 0:
            raise ValueError("Sinyal ölçeği sonlu ve pozitif olmalı.")
        if len(konum) != 2 or not all(math.isfinite(float(v)) for v in konum):
            raise ValueError("Dendrit konumu sonlu iki boyutlu koordinat olmalı.")
        self.kimlik = kimlik
        self.konum = tuple(float(v) for v in konum)
        self.sinyal_olcegi = float(sinyal_olcegi)
        self.sinaps_katkilari = {}
        self.girdiler = []
        self.reseptor_duyarliliklari = {}
        self.son_islenen_sinapslar = set()
        self.sinaps_degerlendirmeleri = {}

    def sinaps_bagla(self, sinaps, katki):
        katki = float(katki)
        if not math.isfinite(katki):
            raise ValueError("Sinaps katkısı sonlu olmalı.")
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
        return toplam

    def girdi_al(self, etki):
        etki = float(etki)
        if not math.isfinite(etki):
            raise ValueError("Dendrit girdisi sonlu olmalı.")
        self.girdiler.append(etki)

    def girdi_var_mi(self):
        return bool(self.girdiler)

    def sinyali_hazirla(self, zaman, kimyasal_alan=None):
        if not self.girdiler:
            return 0.0, 0.0

        elektriksel_toplam = sum(self.girdiler)
        self.girdiler.clear()

        kimyasal_modulasyon = 0.0
        if kimyasal_alan is not None and self.reseptor_duyarliliklari:
            kimyasal_modulasyon = self.kimyasal_yanit(kimyasal_alan, zaman)

        u = math.tanh(
            elektriksel_toplam / self.sinyal_olcegi + kimyasal_modulasyon
        )
        return elektriksel_toplam, u

    def firsat_sonucu_ogren(self, aktif_sinapslar, zaman, adim=0.01):
        """Yalnızca bu dendritin gerçekten katkı yüklediği çiftleri günceller."""
        for sinaps in self.son_islenen_sinapslar:
            if sinaps in aktif_sinapslar:
                self.sinaps_katkilari[sinaps] += adim
            elif self.sinaps_degerlendirmeleri.get(sinaps, 0) > 0:
                self.sinaps_katkilari[sinaps] -= adim
            self.sinaps_degerlendirmeleri[sinaps] = (
                self.sinaps_degerlendirmeleri.get(sinaps, 0) + 1
            )
        self.son_islenen_sinapslar.clear()

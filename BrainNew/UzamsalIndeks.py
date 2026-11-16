import math


class UzamsalIndeks:
    """2B sabit hücreli uzamsal indeks; yalnızca aday sorgular, karar vermez."""

    def __init__(self, hucre_boyu=10.0):
        hucre_boyu = float(hucre_boyu)
        if not math.isfinite(hucre_boyu) or hucre_boyu <= 0:
            raise ValueError("Hücre boyu sonlu ve pozitif olmalı.")
        self.hucre_boyu = hucre_boyu
        self._hucreler = {}
        self._konumlar = {}
        self._kimlikler = {}

    def _hucre_anahtari(self, konum):
        if len(konum) != 2:
            raise ValueError("Konum iki boyutlu olmalı.")
        x, y = (float(v) for v in konum)
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("Konum koordinatları sonlu olmalı.")
        return math.floor(x / self.hucre_boyu), math.floor(y / self.hucre_boyu)

    def ekle(self, noron):
        kimlik = noron.kimlik
        mevcut = self._kimlikler.get(kimlik)
        if mevcut is not None:
            if mevcut is noron:
                return False
            raise ValueError(f"Uzamsal indekste yinelenen nöron kimliği: {kimlik}")
        anahtar = self._hucre_anahtari(noron.konum)
        self._hucreler.setdefault(anahtar, {})[kimlik] = noron
        self._konumlar[kimlik] = tuple(float(v) for v in noron.konum)
        self._kimlikler[kimlik] = noron
        return True

    def cikar(self, noron):
        mevcut = self._kimlikler.get(noron.kimlik)
        if mevcut is None:
            return False
        if mevcut is not noron:
            raise ValueError("İndeksten yalnızca kayıtlı nöron nesnesi çıkarılabilir.")
        anahtar = self._hucre_anahtari(self._konumlar[noron.kimlik])
        hucre = self._hucreler[anahtar]
        del hucre[noron.kimlik]
        if not hucre:
            del self._hucreler[anahtar]
        del self._konumlar[noron.kimlik]
        del self._kimlikler[noron.kimlik]
        return True

    def konumu_guncelle(self, noron, yeni_konum):
        if self._kimlikler.get(noron.kimlik) is not noron:
            raise ValueError("Konumu güncellenecek nöron indekste kayıtlı olmalı.")
        yeni_anahtar = self._hucre_anahtari(yeni_konum)
        eski_anahtar = self._hucre_anahtari(self._konumlar[noron.kimlik])
        if yeni_anahtar != eski_anahtar:
            eski_hucre = self._hucreler[eski_anahtar]
            del eski_hucre[noron.kimlik]
            if not eski_hucre:
                del self._hucreler[eski_anahtar]
            self._hucreler.setdefault(yeni_anahtar, {})[noron.kimlik] = noron
        konum = tuple(float(v) for v in yeni_konum)
        self._konumlar[noron.kimlik] = konum
        noron.konum = konum

    def yakinindakileri_bul(self, konum, yaricap, haric=None):
        yaricap = float(yaricap)
        if not math.isfinite(yaricap) or yaricap < 0:
            raise ValueError("Arama yarıçapı sonlu ve negatif olmayan değer olmalı.")
        merkez = tuple(float(v) for v in konum)
        merkez_hucre = self._hucre_anahtari(merkez)
        x, y = merkez
        r2 = yaricap * yaricap
        adim = math.ceil(yaricap / self.hucre_boyu)
        adaylar = []
        for hx in range(merkez_hucre[0] - adim, merkez_hucre[0] + adim + 1):
            for hy in range(merkez_hucre[1] - adim, merkez_hucre[1] + adim + 1):
                for noron in self._hucreler.get((hx, hy), {}).values():
                    if noron is haric:
                        continue
                    nx, ny = self._konumlar[noron.kimlik]
                    dx, dy = nx - x, ny - y
                    uzaklik2 = dx * dx + dy * dy
                    if uzaklik2 <= r2:
                        adaylar.append((uzaklik2, str(noron.kimlik), noron))
        adaylar.sort(key=lambda oge: (oge[0], oge[1]))
        return [noron for _, _, noron in adaylar]

    def __len__(self):
        return len(self._kimlikler)

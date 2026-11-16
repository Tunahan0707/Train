class DeneyKaydi:
    """Simülasyon olaylarını öğrenmeye müdahale etmeden sıralı kaydeder."""

    def __init__(self):
        self.olaylar = []

    @staticmethod
    def _dondur(deger):
        if deger is None or isinstance(deger, (str, int, bool)):
            return deger
        if isinstance(deger, float):
            return deger
        if isinstance(deger, tuple):
            return tuple(DeneyKaydi._dondur(x) for x in deger)
        if isinstance(deger, list):
            return tuple(DeneyKaydi._dondur(x) for x in deger)
        if isinstance(deger, dict):
            return tuple(
                (key, DeneyKaydi._dondur(value))
                for key, value in sorted(deger.items(), key=lambda item: str(item[0]))
            )
        kimlik = getattr(deger, "kimlik", None)
        if kimlik is not None:
            return ("kimlik", str(kimlik))
        raise TypeError(
            f"Deney kaydı desteklenmeyen veri türünü alamaz: {type(deger).__name__}"
        )

    def olay_kaydet(self, zaman, olay_id, tur, hedef_id, veri=None):
        self.olaylar.append((
            float(zaman),
            int(olay_id),
            str(tur),
            str(hedef_id),
            self._dondur(veri),
        ))

    def temizle(self):
        self.olaylar.clear()

    def olay_sayisi(self):
        return len(self.olaylar)

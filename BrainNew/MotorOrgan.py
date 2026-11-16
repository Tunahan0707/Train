class MotorOrgan:
    """Ağın ateşlenme çıktısını görev ortamı için okur."""

    @staticmethod
    def ateslenme_sayilari_oku(beyin, onceki_ateslenmeler=None):
        """Nöronların episode içindeki spike sayılarını döndürür."""
        onceki_ateslenmeler = onceki_ateslenmeler or {}
        return {
            kimlik: max(
                0, noron.ateslenme_sayisi - onceki_ateslenmeler.get(kimlik, 0)
            )
            for kimlik, noron in beyin.noronlar.items()
        }

    @staticmethod
    def oku(beyin, onceki_ateslenmeler=None):
        sayilar = MotorOrgan.ateslenme_sayilari_oku(
            beyin, onceki_ateslenmeler
        )
        return frozenset(kimlik for kimlik, miktar in sayilar.items() if miktar > 0)

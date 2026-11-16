class MotorOrgan:
    """Ağın ateşlenme çıktısını görev ortamı için okur."""

    @staticmethod
    def oku(beyin, onceki_ateslenmeler=None):
        onceki_ateslenmeler = onceki_ateslenmeler or {}
        return frozenset(
            kimlik
            for kimlik, noron in beyin.noronlar.items()
            if noron.ateslenme_sayisi > onceki_ateslenmeler.get(kimlik, 0)
        )

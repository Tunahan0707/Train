
class Baglanti:
    def __init__(
        self,
        kaynak,
        hedef,
        etki_mv=2.0,
        gecikme_ms=1
    ):
        if gecikme_ms < 1:
            raise ValueError("Gecikme en az 1 ms olmalıdır.")

        self.kaynak = kaynak
        self.hedef = hedef

        self.etki_mv = float(etki_mv)
        self.gecikme_ms = int(gecikme_ms)

        self.aktif = True
        self.aktarim_sayisi = 0

        self.uygunluk_izi = 0.0

    def aktar(self, zaman, trace=None):
        if not self.aktif:
            return

        self.hedef.uyari_al(self.etki_mv)

        self.aktarim_sayisi += 1

        if trace is not None:
            trace.aktarim_kaydet(
                zaman,
                self.kaynak,
                self.hedef,
                self.etki_mv
            )

    def izi_azalt(self, oran=0.95):
        self.uygunluk_izi *= oran

    def geri_bildirim(self, deger, ogrenme_orani=0.5):
        if not self.aktif or self.uygunluk_izi <= 0:
            return

        degisim = (
            deger
            * self.uygunluk_izi
            * ogrenme_orani
        )

        self.etki_mv += degisim

        self.etki_mv = max(
            -10.0,
            min(10.0, self.etki_mv)
        )

    def isaret_degistir(self):
        self.etki_mv *= -1

    def guclendir(self, miktar):
        if miktar < 0:
            raise ValueError("Miktar negatif olamaz.")

        if self.etki_mv >= 0:
            self.etki_mv += miktar
        else:
            self.etki_mv -= miktar

        self.etki_mv = max(
            -10.0,
            min(10.0, self.etki_mv)
        )

    def zayiflat(self, miktar):
        if miktar < 0:
            raise ValueError("Miktar negatif olamaz.")

        if self.etki_mv > 0:
            self.etki_mv = max(
                0.0,
                self.etki_mv - miktar
            )
        else:
            self.etki_mv = min(
                0.0,
                self.etki_mv + miktar
            )

    def sil(self):
        if not self.aktif:
            return

        self.aktif = False

        if self in self.kaynak.baglantilar:
            self.kaynak.baglantilar.remove(self)

        if self in self.hedef.gelen_baglantilar:
            self.hedef.gelen_baglantilar.remove(self)

    def uygunluk_izini_artir(self, miktar=1.0):
        self.uygunluk_izi = min(
            5.0,
            self.uygunluk_izi + miktar
        )

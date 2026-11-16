class EgitimSurucusu:
    """Aynı BrainNew ağını ardışık episode'larda koruyan yürütücü.

    Bu sınıf öğrenme hesabı yapmaz ve ağırlıklara dokunmaz. Girdi/çıktı
    organlarını koordine eder; görev ortamı feedback'i ayrı bir callback
    üzerinden kimyasal alana bırakabilir.
    """

    def __init__(self, beyin, reseptor=None, motor=None, feedback_uretici=None):
        from BrainNew.ReseptorOrgan import ReseptorOrgan
        from BrainNew.MotorOrgan import MotorOrgan

        if not hasattr(beyin, "episode_baslat"):
            raise TypeError("EgitimSurucusu bir BrainNew Beyin örneği bekler.")
        self.beyin = beyin
        self.reseptor = reseptor or ReseptorOrgan()
        self.motor = motor or MotorOrgan()
        self.feedback_uretici = feedback_uretici
        self.episode_sayisi = 0
        self.sonuclar = []

    def episode_calistir(self, ornek, feedback=True, olay_limiti=100000):
        """Tek örneği aynı ağda çalıştırır; kalıcı öğrenilmiş durum korunur."""
        self.beyin.episode_baslat()
        onceki = {
            kimlik: noron.ateslenme_sayisi
            for kimlik, noron in self.beyin.noronlar.items()
        }
        self.reseptor.kodla(self.beyin, ornek.girdiler)
        islenen = self.beyin.calistir(olay_limiti=olay_limiti)
        gerceklesen = self.motor.oku(self.beyin, onceki)
        beklenen = frozenset(ornek.beklenen_ciktilar)
        sonuc = {
            "episode": self.episode_sayisi,
            "ornek": ornek.kimlik,
            "beklenen": tuple(sorted(beklenen)),
            "gerceklesen": tuple(sorted(gerceklesen)),
            "dogru": gerceklesen == beklenen,
            "islenen_olay": islenen,
            "simulasyon_zamani": self.beyin.zaman,
        }
        self.episode_sayisi += 1
        self.sonuclar.append(sonuc)
        if feedback and self.feedback_uretici is not None:
            # Callback yalnızca görev ortamı/kimyasal alan etkileşimini yapar;
            # sinaptik parametrelere doğrudan erişim verilmez.
            self.feedback_uretici(self.beyin, sonuc)
        return sonuc

    def egit(self, ornekler, feedback=True, olay_limiti=100000):
        return tuple(
            self.episode_calistir(
                ornek, feedback=feedback, olay_limiti=olay_limiti
            )
            for ornek in ornekler
        )

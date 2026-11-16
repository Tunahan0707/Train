class Noron:
    DINLENME = "dinlenme"
    DEPOLARIZASYON = "depolarizasyon"
    REPOLARIZASYON = "repolarizasyon"
    HIPERPOLARIZASYON = "hiperpolarizasyon"

    def __init__(
        self, kimlik, konum=(0.0, 0.0), dinlenme=-70.0, esik=-55.0,
        sizinti=0.05, depolarizasyon=30.0, repolarizasyon=-40.0,
        hiperpolarizasyon=-80.0
    ):
        self.kimlik = kimlik
        self.konum = tuple(konum)
        self.dinlenme_degeri = float(dinlenme)
        self.esik = float(esik)
        self.sizinti = float(sizinti)
        self.depolarizasyon_degeri = float(depolarizasyon)
        self.repolarizasyon_degeri = float(repolarizasyon)
        self.hiperpolarizasyon_degeri = float(hiperpolarizasyon)
        self.membran = self.dinlenme_degeri
        self.durum = self.DINLENME
        self.dendritler = {}
        self.cikis_sinapslari = []
        self.ateslenme_sayisi = 0
        self._entegrasyon_zamani = None
        self._entegrasyon_planlandi = False

    def dendrit_ekle(self, dendrit):
        self.dendritler[dendrit.kimlik] = dendrit

    def cikis_sinapsi_ekle(self, sinaps):
        self.cikis_sinapslari.append(sinaps)

    def girdi_al(self, dendrit_id, etki):
        self.dendritler[dendrit_id].girdi_al(etki)

    def girdileri_birlestir(self, zaman, kimyasal_alan=None):
        toplam = 0.0
        for dendrit in self.dendritler.values():
            toplam += dendrit.sinyali_isle(zaman, kimyasal_alan)
        return toplam

    def membrani_guncelle(self, toplam_etki):
        if self.durum != self.DINLENME:
            return False
        self.membran += toplam_etki
        self.membran += (self.dinlenme_degeri - self.membran) * self.sizinti
        if self.membran >= self.esik:
            return True
        return False

    def aksiyon_potansiyeli_baslat(self):
        if self.durum != self.DINLENME or self.membran < self.esik:
            return False
        self.durum = self.DEPOLARIZASYON
        self.membran = self.depolarizasyon_degeri
        self.ateslenme_sayisi += 1
        return True

    def faz_degistir(self):
        if self.durum == self.DEPOLARIZASYON:
            self.durum = self.REPOLARIZASYON
            self.membran = self.repolarizasyon_degeri
        elif self.durum == self.REPOLARIZASYON:
            self.durum = self.HIPERPOLARIZASYON
            self.membran = self.hiperpolarizasyon_degeri
        elif self.durum == self.HIPERPOLARIZASYON:
            self.durum = self.DINLENME
            self.membran = self.dinlenme_degeri

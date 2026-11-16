import heapq
import itertools


class Beyin:
    """Yalnızca simülasyon saatini ve olayların dağıtımını yönetir."""

    def __init__(self, kimyasal_alan=None):
        self.zaman = 0.0
        self.noronlar = {}
        self.kimyasal_alan = kimyasal_alan
        self._olaylar = []
        self._olay_sayaci = itertools.count()

    def noron_ekle(self, noron):
        self.noronlar[noron.kimlik] = noron

    def olay_planla(self, gecikme, tur, hedef_id, veri=None):
        if gecikme <= 0:
            raise ValueError("Olay gecikmesi sıfırdan büyük olmalı.")
        olay_zamani = self.zaman + float(gecikme)
        olay_id = next(self._olay_sayaci)
        heapq.heappush(
            self._olaylar,
            (olay_zamani, olay_id, tur, hedef_id, veri)
        )
        return olay_id

    def sinyal_gonder(self, sinaps, zaman):
        gecikme = sinaps.aktive_et(zaman)
        if sinaps.hedef is not None:
            self.olay_planla(gecikme, "sinaptik_girdi", sinaps.hedef.kimlik,
                             (sinaps.kimlik, sinaps.hedef_dendrit_id, sinaps.etki))

    def adim(self):
        if not self._olaylar:
            return False
        zaman, olay_id, tur, hedef_id, veri = heapq.heappop(self._olaylar)
        self.zaman = zaman

        if tur == "sinaptik_girdi":
            noron = self.noronlar[hedef_id]
            _, dendrit_id, etki = veri
            noron.girdi_al(dendrit_id, etki)
            self.olay_planla(1e-6, "entegrasyon", hedef_id)
        elif tur == "entegrasyon":
            noron = self.noronlar[hedef_id]
            if noron.durum == noron.DINLENME:
                toplam = noron.girdileri_birlestir(self.zaman, self.kimyasal_alan)
                if noron.membrani_guncelle(toplam) and noron.aksiyon_potansiyeli_baslat():
                    aktif = []
                    for sinaps in noron.cikis_sinapslari:
                        if sinaps.aktive_olabilir_mi(self.zaman):
                            aktif.append(sinaps)
                    for dendrit in noron.dendritler.values():
                        dendrit.firsat_sonucu_ogren(aktif, self.zaman)
                    for sinaps in aktif:
                        self.sinyal_gonder(sinaps, self.zaman)
                    self.olay_planla(1.0, "faz", hedef_id)
        elif tur == "faz":
            noron = self.noronlar[hedef_id]
            noron.faz_degistir()
            if noron.durum == noron.DEPOLARIZASYON:
                self.olay_planla(1.0, "faz", hedef_id)
            elif noron.durum == noron.REPOLARIZASYON:
                self.olay_planla(1.0, "faz", hedef_id)
            elif noron.durum == noron.HIPERPOLARIZASYON:
                self.olay_planla(2.0, "faz", hedef_id)
        return True

    def calistir(self, olay_limiti=100000):
        islenen = 0
        while self._olaylar and islenen < olay_limiti:
            self.adim()
            islenen += 1
        if self._olaylar and islenen >= olay_limiti:
            raise RuntimeError("Olay limiti aşıldı; olası sonsuz olay zinciri.")
        return islenen

import math


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
        sayisal_degerler = (
            dinlenme, esik, sizinti, depolarizasyon,
            repolarizasyon, hiperpolarizasyon
        )
        if not all(math.isfinite(float(v)) for v in sayisal_degerler):
            raise ValueError("Nöron parametreleri sonlu sayılar olmalı.")
        if not 0.0 <= sizinti < 1.0:
            raise ValueError("Sızıntı oranı [0, 1) aralığında olmalı.")
        if len(konum) != 2 or not all(math.isfinite(float(v)) for v in konum):
            raise ValueError("Nöron konumu sonlu iki boyutlu koordinat olmalı.")

        self.kimlik = kimlik
        self.konum = tuple(float(v) for v in konum)
        self.dinlenme_degeri = float(dinlenme)
        self.esik = float(esik)
        self.sizinti = float(sizinti)
        self.depolarizasyon_degeri = float(depolarizasyon)
        self.repolarizasyon_degeri = float(repolarizasyon)
        self.hiperpolarizasyon_degeri = float(hiperpolarizasyon)
        self.membran = self.dinlenme_degeri
        self.son_membran_guncelleme = 0.0
        self.son_entegrasyon_zamani = None
        self.son_girdi_zamani = None
        self.durum = self.DINLENME
        self.dendritler = {}
        self.cikis_sinapslari = []
        self.ateslenme_sayisi = 0
        self._sinaps_dendritik_sinyalleri = {}

    def dendrit_ekle(self, dendrit):
        mevcut = self.dendritler.get(dendrit.kimlik)
        if mevcut is not None and mevcut is not dendrit:
            raise ValueError(f"Aynı kimlikle ikinci bir dendrit eklenemez: {dendrit.kimlik}")
        self.dendritler[dendrit.kimlik] = dendrit

    def cikis_sinapsi_ekle(self, sinaps):
        if sinaps.kaynak is not self:
            raise ValueError("Çıkış sinapsının kaynak nöronu bu nöron olmalı.")
        if sinaps not in self.cikis_sinapslari:
            self.cikis_sinapslari.append(sinaps)

    def girdi_al(self, dendrit_id, etki, zaman=None):
        if dendrit_id not in self.dendritler:
            raise ValueError(f"Nöronda bulunmayan dendrit: {dendrit_id}")
        self.dendritler[dendrit_id].girdi_al(etki)
        if zaman is not None:
            zaman = float(zaman)
            if not math.isfinite(zaman) or zaman < 0:
                raise ValueError("Girdi zamanı sonlu ve negatif olmayan değer olmalı.")
            self.son_girdi_zamani = zaman

    def bekleyen_girdi_var_mi(self):
        return any(dendrit.girdi_var_mi() for dendrit in self.dendritler.values())

    def girdileri_birlestir(self, zaman, kimyasal_alan=None):
        toplam_membran_etkisi = 0.0
        sinaps_katkilari = {}
        self._sinaps_dendritik_sinyalleri = {}

        for dendrit in self.dendritler.values():
            dendrit.son_islenen_sinapslar.clear()

        for dendrit in self.dendritler.values():
            elektriksel_toplam, yerel_sinyal = dendrit.sinyali_hazirla(
                zaman, kimyasal_alan
            )
            toplam_membran_etkisi += elektriksel_toplam
            if not math.isfinite(toplam_membran_etkisi):
                raise ValueError("Nöron membranına gelen toplam etki sonlu olmalı.")
            if yerel_sinyal == 0.0:
                continue

            for sinaps, katki in dendrit.sinaps_katkilari.items():
                etki = katki * yerel_sinyal
                if etki == 0.0:
                    continue
                sinaps_katkilari.setdefault(sinaps, []).append((dendrit, etki))
                dendrit.son_islenen_sinapslar.add(sinaps)

        for sinaps, katkilar in sinaps_katkilari.items():
            toplam = sum(deger for _, deger in katkilar)
            normalizasyon = math.sqrt(max(1, len(katkilar)))
            sinaps_etkisi = toplam / normalizasyon
            sinaps.etki_uygula(sinaps_etkisi, zaman)
            self._sinaps_dendritik_sinyalleri[sinaps] = max(
                -1.0, min(1.0, sinaps_etkisi)
            )

        return toplam_membran_etkisi

    def membrani_guncelle(self, toplam_etki, zaman):
        if self.durum != self.DINLENME:
            return False
        toplam_etki = float(toplam_etki)
        zaman = float(zaman)
        if not math.isfinite(toplam_etki) or not math.isfinite(zaman):
            raise ValueError("Membran etkisi ve simülasyon zamanı sonlu olmalı.")
        if zaman < self.son_membran_guncelleme:
            raise ValueError("Simülasyon zamanı geriye gidemez.")

        gecen = zaman - self.son_membran_guncelleme
        if gecen and self.sizinti:
            carp = (1.0 - self.sizinti) ** gecen
            self.membran = (
                self.dinlenme_degeri
                + (self.membran - self.dinlenme_degeri) * carp
            )
        self.son_membran_guncelleme = zaman
        self.membran += toplam_etki
        return self.membran >= self.esik

    def aksiyon_potansiyeli_baslat(self):
        if self.durum != self.DINLENME or self.membran < self.esik:
            return False
        self.durum = self.DEPOLARIZASYON
        self.membran = self.depolarizasyon_degeri
        self.ateslenme_sayisi += 1
        return True

    def ateslenme_sonucunu_isle(self, zaman, kimyasal_alan=None):
        """Yerel bakım, sinaps seçimi, aktivasyon ve transmitter salımı."""
        for sinaps in tuple(self.cikis_sinapslari):
            sinaps.yerel_bakim(kimyasal_alan, zaman)
            if sinaps.kopuk:
                self.cikis_sinapslari.remove(sinaps)
                for dendrit in self.dendritler.values():
                    dendrit.sinaps_katkilari.pop(sinaps, None)
                    dendrit.sinaps_degerlendirmeleri.pop(sinaps, None)
                    dendrit.son_islenen_sinapslar.discard(sinaps)

        aktif = []
        for sinaps in self.cikis_sinapslari:
            if not sinaps.aktive_olabilir_mi(zaman):
                continue
            gecikme = sinaps.aktive_et(zaman)
            sinaps.kimyasal_sal(
                kimyasal_alan, zaman,
                self._sinaps_dendritik_sinyalleri.get(sinaps, 0.0)
            )
            aktif.append((sinaps, gecikme))

        aktif_sinapslar = [sinaps for sinaps, _ in aktif]
        for dendrit in self.dendritler.values():
            dendrit.firsat_sonucu_ogren(aktif_sinapslar, zaman)
        return aktif

    def entegrasyonu_isle(self, zaman, kimyasal_alan=None):
        if self.durum != self.DINLENME:
            return False, []

        toplam = self.girdileri_birlestir(zaman, kimyasal_alan)
        self.son_entegrasyon_zamani = float(zaman)
        if not self.membrani_guncelle(toplam, zaman):
            return False, []
        if not self.aksiyon_potansiyeli_baslat():
            return False, []

        return True, self.ateslenme_sonucunu_isle(zaman, kimyasal_alan)

    def faz_gecisi_gecikmesi(self):
        if self.durum == self.DEPOLARIZASYON:
            return 1.0
        if self.durum == self.REPOLARIZASYON:
            return 1.0
        if self.durum == self.HIPERPOLARIZASYON:
            return 2.0
        raise RuntimeError("Dinlenme durumundaki nöronun faz süresi yoktur.")

    def faz_degistir(self):
        if self.durum == self.DEPOLARIZASYON:
            self.durum = self.REPOLARIZASYON
            self.membran = self.repolarizasyon_degeri
            return 1.0
        if self.durum == self.REPOLARIZASYON:
            self.durum = self.HIPERPOLARIZASYON
            self.membran = self.hiperpolarizasyon_degeri
            return 2.0
        if self.durum == self.HIPERPOLARIZASYON:
            self.durum = self.DINLENME
            self.membran = self.dinlenme_degeri
            return None
        raise RuntimeError("Dinlenme durumundaki nörona faz geçişi uygulanamaz.")

    def faz_olayini_isle(self):
        return self.faz_degistir()

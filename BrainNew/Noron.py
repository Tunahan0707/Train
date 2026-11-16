import math


class Noron:
    DINLENME = "dinlenme"
    DEPOLARIZASYON = "depolarizasyon"
    REPOLARIZASYON = "repolarizasyon"
    HIPERPOLARIZASYON = "hiperpolarizasyon"

    def __init__(
        self, kimlik, konum=(0.0, 0.0), dinlenme=-70.0, esik=-55.0,
        sizinti=0.05, depolarizasyon=30.0, repolarizasyon=-40.0,
        hiperpolarizasyon=-80.0, homeostatik_hedef_oran=0.02,
        homeostatik_tau=100.0, homeostatik_oran=0.01,
        homeostatik_esik_alt=-10.0, homeostatik_esik_ust=10.0
    ):
        sayisal_degerler = (
            dinlenme, esik, sizinti, depolarizasyon,
            repolarizasyon, hiperpolarizasyon, homeostatik_hedef_oran,
            homeostatik_tau, homeostatik_oran,
            homeostatik_esik_alt, homeostatik_esik_ust
        )
        if not all(math.isfinite(float(v)) for v in sayisal_degerler):
            raise ValueError("Nöron parametreleri sonlu sayılar olmalı.")
        if not 0.0 <= sizinti < 1.0:
            raise ValueError("Sızıntı oranı [0, 1) aralığında olmalı.")
        if homeostatik_hedef_oran < 0 or homeostatik_tau <= 0 or homeostatik_oran < 0:
            raise ValueError("Homeostatik hedef, zaman sabiti veya öğrenme oranı geçersiz.")
        if homeostatik_esik_alt > 0 or homeostatik_esik_ust < 0 or homeostatik_esik_alt > homeostatik_esik_ust:
            raise ValueError("Homeostatik eşik kayması sınırları sıfırı kapsamalı.")
        if len(konum) != 2 or not all(math.isfinite(float(v)) for v in konum):
            raise ValueError("Nöron konumu sonlu iki boyutlu koordinat olmalı.")

        self.kimlik = kimlik
        self.konum = tuple(float(v) for v in konum)
        self.dinlenme_degeri = float(dinlenme)
        self.esik_temel = float(esik)
        self.esik = self.esik_temel
        self.sizinti = float(sizinti)

        # Nöron-yerel homeostaz: etkinlik izi ve eşik kayması.
        self.homeostatik_hedef_oran = float(homeostatik_hedef_oran)
        self.homeostatik_tau = float(homeostatik_tau)
        self.homeostatik_oran = float(homeostatik_oran)
        self.homeostatik_esik_alt = float(homeostatik_esik_alt)
        self.homeostatik_esik_ust = float(homeostatik_esik_ust)
        self.homeostatik_aktivite_izi = 0.0
        self.homeostatik_esik_kaymasi = 0.0
        self.son_homeostatik_guncelleme = 0.0
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
        self.gelen_sinapslari = []
        self.ateslenme_sayisi = 0
        self._sinaps_dendritik_sinyalleri = {}
        self._entegrasyon_girdi_sinapslari = set()

    def dendrit_ekle(self, dendrit):
        mevcut = self.dendritler.get(dendrit.kimlik)
        if mevcut is not None and mevcut is not dendrit:
            raise ValueError(f"Aynı kimlikle ikinci bir dendrit eklenemez: {dendrit.kimlik}")
        self.dendritler[dendrit.kimlik] = dendrit

    def gelen_sinapsi_ekle(self, sinaps):
        if sinaps.hedef is not self:
            raise ValueError("Gelen sinapsın hedef nöronu bu nöron olmalı.")
        if sinaps not in self.gelen_sinapslari:
            self.gelen_sinapslari.append(sinaps)

    def cikis_sinapsi_ekle(self, sinaps):
        if sinaps.kaynak is not self:
            raise ValueError("Çıkış sinapsının kaynak nöronu bu nöron olmalı.")
        if sinaps not in self.cikis_sinapslari:
            self.cikis_sinapslari.append(sinaps)

    def girdi_al(self, dendrit_id, etki, zaman=None, kaynak_sinaps=None):
        if dendrit_id not in self.dendritler:
            raise ValueError(f"Nöronda bulunmayan dendrit: {dendrit_id}")
        self.dendritler[dendrit_id].girdi_al(etki, kaynak_sinaps)
        if zaman is not None:
            zaman = float(zaman)
            if not math.isfinite(zaman) or zaman < 0:
                raise ValueError("Girdi zamanı sonlu ve negatif olmayan değer olmalı.")
            self.son_girdi_zamani = zaman

    def girdi_kaynagini_isaretle(self, dendrit_id, kaynak_sinaps):
        """İşlenmekte olan girdinin kaynak bağlantısını yerel dendrite iliştirir."""
        if dendrit_id not in self.dendritler:
            raise ValueError(f"Nöronda bulunmayan dendrit: {dendrit_id}")
        if kaynak_sinaps.hedef is not self:
            raise ValueError("Kaynak sinapsın hedefi bu nöron olmalı.")
        if kaynak_sinaps.hedef_dendrit_id != dendrit_id:
            raise ValueError("Kaynak sinaps farklı bir hedef dendrite bağlı.")
        self.dendritler[dendrit_id].bekleyen_kaynak_sinapslari.append(
            kaynak_sinaps
        )

    def bekleyen_girdi_var_mi(self):
        return any(dendrit.girdi_var_mi() for dendrit in self.dendritler.values())

    def girdileri_birlestir(self, zaman, kimyasal_alan=None):
        toplam_membran_etkisi = 0.0
        sinaps_katkilari = {}
        self._entegrasyon_girdi_sinapslari.clear()
        self._sinaps_dendritik_sinyalleri = {}

        for dendrit in self.dendritler.values():
            dendrit.son_islenen_sinapslar.clear()

        for dendrit in self.dendritler.values():
            elektriksel_toplam, yerel_sinyal = dendrit.sinyali_hazirla(
                zaman, kimyasal_alan
            )
            self._entegrasyon_girdi_sinapslari.update(
                dendrit.son_girdi_kaynak_sinapslari
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

    def homeostatik_durumu_guncelle(self, zaman, yeni_ateslenme=False):
        """Uzun dönem etkinlik hatasını yerel eşik ayarına dönüştürür.

        Aktivite izi ateşlenmeleri üstel olarak toplar. Eşik kayması,
        hedef ve gözlenen etkinlik arasındaki zaman-integralli hataya göre
        yavaşça değişir. Beyin bu hesabın hiçbir parçasını yönetmez.
        """
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < self.son_homeostatik_guncelleme:
            raise ValueError("Homeostatik güncelleme zamanı sonlu olmalı ve geriye gitmemeli.")

        gecen = zaman - self.son_homeostatik_guncelleme
        if gecen:
            carp = math.exp(-gecen / self.homeostatik_tau)
            gerceklesen_etkinlik = self.homeostatik_aktivite_izi * (1.0 - carp)
            hedeflenen_etkinlik = self.homeostatik_hedef_oran * gecen
            self.homeostatik_esik_kaymasi += self.homeostatik_oran * (
                gerceklesen_etkinlik - hedeflenen_etkinlik
            )
            self.homeostatik_esik_kaymasi = max(
                self.homeostatik_esik_alt,
                min(self.homeostatik_esik_ust, self.homeostatik_esik_kaymasi)
            )
            self.homeostatik_aktivite_izi *= carp
            self.son_homeostatik_guncelleme = zaman

        if yeni_ateslenme:
            self.homeostatik_aktivite_izi += 1.0

        self.esik = self.esik_temel + self.homeostatik_esik_kaymasi
        return self.esik
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

    def baglantilari_bakimdan_gecir(self, zaman, kimyasal_alan=None):
        """Sinapsların gecikmiş modülatör izlerini yerel olarak işler.

        Fiziksel bakım ve budama bağımsız Mikroglia ajanlarına aittir.
        """
        for sinaps in tuple(self.cikis_sinapslari):
            if not sinaps.kopuk:
                sinaps.gecikmis_modulatoru_isle(kimyasal_alan, zaman)
            if sinaps.kopuk:
                self.cikis_sinapslari.remove(sinaps)
                if sinaps.hedef is not None and sinaps in sinaps.hedef.gelen_sinapslari:
                    sinaps.hedef.gelen_sinapslari.remove(sinaps)
                for dendrit in self.dendritler.values():
                    dendrit.sinaps_katkilari.pop(sinaps, None)
                    dendrit.sinaps_degerlendirmeleri.pop(sinaps, None)
                    dendrit.son_islenen_sinapslar.discard(sinaps)

    def ateslenme_sonucunu_isle(self, zaman, kimyasal_alan=None):
        """Post ateşlenme izini tüm gelen sinapslara yerel olarak dağıtır."""
        # Daha sonra gelecek bir pre olayı, mevcut post izine göre LTD yapabilmelidir.
        for sinaps in tuple(self.gelen_sinapslari):
            if sinaps.hedef is self and not sinaps.kopuk:
                sinaps.stdp_postsinaptik_olayi_isle(zaman)
        self._entegrasyon_girdi_sinapslari.clear()

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
        self.baglantilari_bakimdan_gecir(zaman, kimyasal_alan)
        self.son_entegrasyon_zamani = float(zaman)
        self.homeostatik_durumu_guncelle(zaman)
        if not self.membrani_guncelle(toplam, zaman):
            return False, []
        if not self.aksiyon_potansiyeli_baslat():
            return False, []

        self.homeostatik_durumu_guncelle(zaman, yeni_ateslenme=True)
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

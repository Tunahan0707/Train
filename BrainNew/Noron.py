import math
import random

from BrainNew.Baglanti import Baglanti


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
        homeostatik_esik_alt=-10.0, homeostatik_esik_ust=10.0,
        buyume_esigi=0.01, yeni_baglanti_agirligi=0.1,
        sinaps_iliski_ogrenme_orani=0.01,
        sinaps_iliski_sonum_tau=100.0,
        sinaps_iliski_etki_olcegi=0.1,
        noron_iliski_ogrenme_orani=0.01,
        noron_iliski_sonum_tau=100.0,
        noron_iliski_zaman_penceresi=5.0,
        noron_iliski_arama_yaricapi=10.0,
        noron_iliski_aktivite_esigi=0.05,
        noron_iliski_buyume_etkisi=0.25
    ):
        sayisal_degerler = (
            dinlenme, esik, sizinti, depolarizasyon,
            repolarizasyon, hiperpolarizasyon, homeostatik_hedef_oran,
            homeostatik_tau, homeostatik_oran,
            homeostatik_esik_alt, homeostatik_esik_ust,
            buyume_esigi, yeni_baglanti_agirligi,
            sinaps_iliski_ogrenme_orani, sinaps_iliski_sonum_tau,
            sinaps_iliski_etki_olcegi, noron_iliski_ogrenme_orani,
            noron_iliski_sonum_tau, noron_iliski_zaman_penceresi,
            noron_iliski_arama_yaricapi, noron_iliski_aktivite_esigi,
            noron_iliski_buyume_etkisi
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
        if buyume_esigi < 0 or not 0.0 <= yeni_baglanti_agirligi <= 2.0:
            raise ValueError("Yapısal büyüme parametreleri geçersiz.")
        self.buyume_esigi = float(buyume_esigi)
        self.yeni_baglanti_agirligi = float(yeni_baglanti_agirligi)
        self._yeni_baglanti_sayaci = 0
        self._rastgele = random.Random(f"BrainNew:{kimlik}")
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
        # Son ateşlenmenin yerel nedensel izi: geriye dönük feedback
        # yalnızca bu ateşlenmeye gerçekten girdi taşıyan bağlantıları izler.
        self._son_nedensel_girdi_sinapslari = set()
        self._son_aktif_cikis_sinapslari = set()

        # Aynı nöronun çıkış sinapsları arasındaki seyrek, yönlü ilişkiler.
        if not 0.0 <= sinaps_iliski_ogrenme_orani <= 1.0:
            raise ValueError("Sinaps ilişki öğrenme oranı [0, 1] aralığında olmalı.")
        if sinaps_iliski_sonum_tau <= 0 or sinaps_iliski_etki_olcegi < 0:
            raise ValueError("Sinaps ilişki zaman sabiti ve etki ölçeği geçersiz.")
        self.sinaps_iliski_ogrenme_orani = float(sinaps_iliski_ogrenme_orani)
        self.sinaps_iliski_sonum_tau = float(sinaps_iliski_sonum_tau)
        self.sinaps_iliski_etki_olcegi = float(sinaps_iliski_etki_olcegi)
        self.sinaps_iliski_agirliklari = {}

        # Yakın nöronların zamansal birlikte etkinliğine ait seyrek ilişkiler.
        if not 0.0 <= noron_iliski_ogrenme_orani <= 1.0:
            raise ValueError("Nöron ilişki öğrenme oranı [0, 1] aralığında olmalı.")
        if (
            noron_iliski_sonum_tau <= 0
            or noron_iliski_zaman_penceresi <= 0
            or noron_iliski_arama_yaricapi < 0
            or not 0.0 <= noron_iliski_aktivite_esigi <= 1.0
            or not 0.0 <= noron_iliski_buyume_etkisi <= 1.0
        ):
            raise ValueError("Nöron ilişki parametreleri geçersiz.")
        self.noron_iliski_ogrenme_orani = float(noron_iliski_ogrenme_orani)
        self.noron_iliski_sonum_tau = float(noron_iliski_sonum_tau)
        self.noron_iliski_zaman_penceresi = float(noron_iliski_zaman_penceresi)
        self.noron_iliski_arama_yaricapi = float(noron_iliski_arama_yaricapi)
        self.noron_iliski_aktivite_esigi = float(noron_iliski_aktivite_esigi)
        self.noron_iliski_buyume_etkisi = float(noron_iliski_buyume_etkisi)
        self.noron_iliski_agirliklari = {}
        self.yerel_aktivite_izi = 0.0
        self.son_yerel_aktivite_guncelleme = 0.0
        self.son_ateslenme_zamani = None

        # Pasif episode tanilamasi: ag davranisini degistirmez.
        self.tanilama_entegre_sayisi = 0
        self.tanilama_toplam_membran_girdisi = 0.0
        self.tanilama_mutlak_membran_girdisi = 0.0
        self.tanilama_maksimum_membran_girdisi = 0.0
        self.tanilama_maksimum_membran = self.dinlenme_degeri
        self.tanilama_maksimum_esik_marji = self.dinlenme_degeri - self.esik

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
        self.tanilama_maksimum_membran = max(
            self.tanilama_maksimum_membran, self.membran
        )
        self.tanilama_maksimum_esik_marji = max(
            self.tanilama_maksimum_esik_marji,
            self.membran - self.esik
        )
        return self.membran >= self.esik

    def aksiyon_potansiyeli_baslat(self):
        if self.durum != self.DINLENME or self.membran < self.esik:
            return False
        self.durum = self.DEPOLARIZASYON
        self.membran = self.depolarizasyon_degeri
        self.ateslenme_sayisi += 1
        return True


    def geri_bildirim_uygula(self, aktif_sinapslar, pozitif=True, miktar=0.01):
        """Feedback'i yalnızca bu nöronun çıkış sinapslarına yerel uygular.

        Beyin feedback'in anlamını veya değişecek sinapsları belirlemez.
        Aktiflik kümesi, nöronun kendi ateşlenme/terminal değerlendirmesinden
        gelir. Pozitif ve negatif feedback kullanıcının eşik kuralını izler.
        """
        miktar = float(miktar)
        if not math.isfinite(miktar) or miktar < 0:
            raise ValueError("Feedback miktarı sonlu ve negatif olmayan değer olmalı.")
        yon = 1 if pozitif else -1
        aktifler = set(aktif_sinapslar)
        degisimler = {}
        for sinaps in self.cikis_sinapslari:
            if sinaps.kopuk:
                continue
            etkin = sinaps in aktifler
            # Pozitif: aktif eşik aşağı, pasif eşik yukarı.
            # Negatif: bunun tersi.
            yon_esik = -yon if etkin else yon
            onceki = sinaps.esik
            sinaps.esik = sinaps.esik_geri_bildirim_uygula(yon_esik, miktar)
            degisimler[sinaps.kimlik] = sinaps.esik - onceki
        return degisimler

    def yerel_aktivite_izini_guncelle(self, zaman, yeni_ateslenme=False):
        """Nöronun yakın geçmişteki ateşlenme etkinliğini tembel olarak sönümler."""
        zaman = float(zaman)
        if (
            not math.isfinite(zaman)
            or zaman < self.son_yerel_aktivite_guncelleme
        ):
            raise ValueError("Yerel aktivite zamanı sonlu olmalı ve geriye gitmemeli.")
        gecen = zaman - self.son_yerel_aktivite_guncelleme
        if gecen:
            self.yerel_aktivite_izi *= math.exp(
                -gecen / self.noron_iliski_sonum_tau
            )
            self.son_yerel_aktivite_guncelleme = zaman
        if yeni_ateslenme:
            self.yerel_aktivite_izi = min(1.0, self.yerel_aktivite_izi + 1.0)
            self.son_ateslenme_zamani = zaman
        return self.yerel_aktivite_izi

    def noron_iliski_oku(self, hedef, zaman):
        """Bu nörondan hedef nörona giden yönlü ilişkiyi okur."""
        if hedef is self:
            return 0.0
        kayit = self.noron_iliski_agirliklari.get(hedef)
        if kayit is None:
            return 0.0
        agirlik, son_zaman = kayit
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < son_zaman:
            raise ValueError("Nöron ilişki zamanı sonlu olmalı ve geriye gitmemeli.")
        if zaman > son_zaman:
            agirlik *= math.exp(
                -(zaman - son_zaman) / self.noron_iliski_sonum_tau
            )
        if abs(agirlik) < 1e-8:
            self.noron_iliski_agirliklari.pop(hedef, None)
            return 0.0
        self.noron_iliski_agirliklari[hedef] = (agirlik, zaman)
        return agirlik

    def noron_iliski_guncelle(self, hedef, zaman, birlikte=True):
        """Yakın iki nöron arasındaki tek yönlü ilişkiyi yerel olarak günceller."""
        if hedef is self:
            return 0.0
        dx = hedef.konum[0] - self.konum[0]
        dy = hedef.konum[1] - self.konum[1]
        if dx * dx + dy * dy > self.noron_iliski_arama_yaricapi ** 2:
            return 0.0
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < 0:
            raise ValueError("Nöron ilişki zamanı sonlu ve negatif olmayan olmalı.")
        onceki = self.noron_iliski_oku(hedef, zaman)
        oran = self.noron_iliski_ogrenme_orani
        if birlikte:
            yeni = onceki + oran * (1.0 - onceki)
        else:
            yeni = onceki - oran * (1.0 + onceki)
        yeni = max(-1.0, min(1.0, yeni))
        if abs(yeni) < 1e-8:
            self.noron_iliski_agirliklari.pop(hedef, None)
        else:
            self.noron_iliski_agirliklari[hedef] = (yeni, zaman)
        return yeni

    def yakin_noron_ateslenmelerini_isle(self, aday_noronlar, zaman):
        """Son ateşlenmeye yakın zamanda etkinleşen komşularla yönlü ilişki öğrenir."""
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < 0:
            raise ValueError("Nöron ilişki zamanı sonlu ve negatif olmayan olmalı.")
        for onceki in sorted(aday_noronlar, key=lambda oge: str(oge.kimlik)):
            if onceki.son_ateslenme_zamani is None:
                continue
            gecen = zaman - onceki.son_ateslenme_zamani
            if gecen < 0 or gecen > self.noron_iliski_zaman_penceresi:
                continue
            iz = onceki.yerel_aktivite_izini_guncelle(zaman)
            if iz < self.noron_iliski_aktivite_esigi:
                continue
            # Önce ateşlenen nöron, sonraki nörona doğru ilişkiyi kendi
            # yerel belleğinde güçlendirir. Aynı zaman damgasındaki eşzamanlı
            # ateşlenmede ise yapay bir sıra dayatmamak için iki yön de öğrenir.
            onceki.noron_iliski_guncelle(self, zaman, birlikte=True)
            if gecen == 0.0:
                self.noron_iliski_guncelle(onceki, zaman, birlikte=True)

    def sinaps_iliski_oku(self, kaynak, hedef, zaman):
        """Yönlü ilişkiyi tembel zamansal sönümle okuyup döndürür."""
        if kaynak is hedef:
            return 0.0
        anahtar = (kaynak, hedef)
        kayit = self.sinaps_iliski_agirliklari.get(anahtar)
        if kayit is None:
            return 0.0
        agirlik, son_zaman = kayit
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < son_zaman:
            raise ValueError("Sinaps ilişki zamanı sonlu olmalı ve geriye gitmemeli.")
        if zaman > son_zaman:
            agirlik *= math.exp(
                -(zaman - son_zaman) / self.sinaps_iliski_sonum_tau
            )
        if abs(agirlik) < 1e-8:
            self.sinaps_iliski_agirliklari.pop(anahtar, None)
            return 0.0
        self.sinaps_iliski_agirliklari[anahtar] = (agirlik, zaman)
        return agirlik

    def sinaps_iliski_guncelle(self, kaynak, hedef, zaman, birlikte):
        """Tek bir yönlü sinaps ilişkisini yerel birliktelik kuralıyla günceller."""
        if kaynak is hedef or kaynak.kopuk or hedef.kopuk:
            return 0.0
        if kaynak.kaynak is not self or hedef.kaynak is not self:
            raise ValueError("Sinaps ilişkisi aynı nöronun çıkış terminalleri arasında olmalı.")
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < 0:
            raise ValueError("Sinaps ilişki zamanı sonlu ve negatif olmayan olmalı.")
        onceki = self.sinaps_iliski_oku(kaynak, hedef, zaman)
        oran = self.sinaps_iliski_ogrenme_orani
        if birlikte:
            yeni = onceki + oran * (1.0 - onceki)
        else:
            yeni = onceki - oran * (1.0 + onceki)
        yeni = max(-1.0, min(1.0, yeni))
        if abs(yeni) < 1e-8:
            self.sinaps_iliski_agirliklari.pop((kaynak, hedef), None)
        else:
            self.sinaps_iliski_agirliklari[(kaynak, hedef)] = (yeni, zaman)
        return yeni

    def sinaps_iliski_etkilesimini_uygula(self, aktif_sinapslar, zaman):
        """Etkin terminalin öğrendiği yönlü ilişkiyi diğer terminal potansiyeline uygular."""
        aktifler = sorted(
            set(aktif_sinapslar), key=lambda oge: str(oge.kimlik)
        )
        for kaynak in aktifler:
            if kaynak.kopuk:
                continue
            for hedef in self.cikis_sinapslari:
                if hedef is kaynak or hedef.kopuk:
                    continue
                iliski = self.sinaps_iliski_oku(kaynak, hedef, zaman)
                if iliski:
                    hedef.etki_uygula(
                        iliski * self.sinaps_iliski_etki_olcegi, zaman
                    )

    def sinaps_iliskilerini_temizle(self, sinaps):
        """Kopmuş terminale bağlı yerel ilişki kayıtlarını kaldırır."""
        for anahtar in tuple(self.sinaps_iliski_agirliklari):
            if sinaps in anahtar:
                self.sinaps_iliski_agirliklari.pop(anahtar, None)

    def geri_bildirim_dali_isle(
        self, zaman, pozitif, miktar, iz_esigi, dallanma_sonum,
        ziyaret_edilen
    ):
        """Bir feedback dalını yerel olarak işler ve nedensel öncüllere dallandırır.

        Nöron kendi son ateşlenmesindeki çıkış etkinliğini değerlendirir.
        Geriye yalnızca o ateşlenmeye girdi taşımış, hâlâ bağlı sinapslardan
        geçilir. Her dal kendi presinaptik izine göre ayrı sönümlenir.
        """
        zaman = float(zaman)
        miktar = float(miktar)
        iz_esigi = float(iz_esigi)
        dallanma_sonum = float(dallanma_sonum)
        if not all(math.isfinite(v) for v in (
            zaman, miktar, iz_esigi, dallanma_sonum
        )):
            raise ValueError("Feedback dalı parametreleri sonlu olmalı.")
        if zaman < 0 or not 0.0 < miktar <= 1.0:
            raise ValueError("Feedback zamanı veya miktarı geçersiz.")
        if not 0.0 <= iz_esigi <= 1.0:
            raise ValueError("Feedback iz eşiği [0, 1] aralığında olmalı.")
        if not 0.0 < dallanma_sonum < 1.0:
            raise ValueError("Feedback dallanma sönümü (0, 1) aralığında olmalı.")

        self.geri_bildirim_uygula(
            self._son_aktif_cikis_sinapslari,
            pozitif=pozitif,
            miktar=miktar
        )

        ziyaret = set(ziyaret_edilen)
        dallar = []
        for sinaps in sorted(
            self._son_nedensel_girdi_sinapslari,
            key=lambda oge: str(oge.kimlik)
        ):
            if sinaps.kopuk or sinaps.hedef is not self or sinaps.kaynak is None:
                continue
            kaynak_id = sinaps.kaynak.kimlik
            if kaynak_id in ziyaret:
                continue

            sinaps.izleri_guncelle(zaman)
            yerel_iz = max(0.0, min(1.0, sinaps.pre_iz))
            dal_miktari = miktar * yerel_iz * dallanma_sonum
            if dal_miktari <= 0.0 or dal_miktari < iz_esigi:
                continue

            dal_ziyareti = set(ziyaret)
            dal_ziyareti.add(kaynak_id)
            gecikme = max(
                sinaps.MINIMUM_GECIKME,
                sinaps.uzunluk / sinaps.iletim_hizi
            )
            dallar.append((
                kaynak_id, dal_miktari, frozenset(dal_ziyareti), gecikme
            ))
        return dallar

    def episode_sifirla(self, zaman):
        """Geçici elektriksel/iz durumlarını sıfırlar; öğrenilmiş yapıyı korur."""
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < 0:
            raise ValueError("Episode zamanı sonlu ve negatif olmayan değer olmalı.")
        self.membran = self.dinlenme_degeri
        self.tanilama_entegre_sayisi = 0
        self.tanilama_toplam_membran_girdisi = 0.0
        self.tanilama_mutlak_membran_girdisi = 0.0
        self.tanilama_maksimum_membran_girdisi = 0.0
        self.tanilama_maksimum_membran = self.dinlenme_degeri
        self.tanilama_maksimum_esik_marji = self.dinlenme_degeri - self.esik
        self.son_membran_guncelleme = zaman
        self.son_entegrasyon_zamani = None
        self.son_girdi_zamani = None
        self.durum = self.DINLENME
        self._sinaps_dendritik_sinyalleri.clear()
        self._entegrasyon_girdi_sinapslari.clear()
        self._son_nedensel_girdi_sinapslari.clear()
        self._son_aktif_cikis_sinapslari.clear()
        # Homeostatik etkinlik izi uzun dönem durumdur; episode sınırında
        # silinmez. Yalnızca geçen zaman kadar doğal biçimde sönümlenir.
        self.homeostatik_durumu_guncelle(zaman)
        self.yerel_aktivite_izi = 0.0
        self.son_yerel_aktivite_guncelleme = zaman
        self.son_ateslenme_zamani = None
        for dendrit in self.dendritler.values():
            dendrit.girdiler.clear()
            dendrit.bekleyen_kaynak_sinapslari.clear()
            dendrit.son_girdi_kaynak_sinapslari = ()
            dendrit.son_islenen_sinapslar.clear()
        for sinaps in set(self.cikis_sinapslari + self.gelen_sinapslari):
            sinaps.potansiyel = 0.0
            sinaps.son_guncelleme = zaman
            sinaps.iz = 0.0
            sinaps.pre_iz = 0.0
            sinaps.post_iz = 0.0
            sinaps.son_iz_guncelleme = zaman
            sinaps.son_aktivasyon = None
            sinaps.uygunluk_izini_guncelle(zaman)
            sinaps.son_modulator_zamani = zaman
            sinaps.son_modulator_degeri = 0.0
            sinaps.son_modulator_uygunluk_izi = sinaps.uygunluk_izi
            sinaps._uygunluk_olaylari.clear()

    def yeni_baglanti_adayi_degerlendir(
        self, aday_noronlar, kimyasal_alan, zaman, arama_yaricapi
    ):
        """Yerel büyüme sinyaliyle tek bir uygun hedef dendrit seçip bağlanır.

        Beyin yalnızca uzamsal adayları sağlar. Büyüme uygunluğu, hedef seçimi,
        bağlantı kurulması ve başlangıç katkıları bu nöronun yerel sürecidir.
        """
        if kimyasal_alan is None or not self.dendritler:
            return None
        zaman = float(zaman)
        arama_yaricapi = float(arama_yaricapi)
        if not math.isfinite(zaman) or zaman < 0:
            raise ValueError("Büyüme zamanı sonlu ve negatif olmayan değer olmalı.")
        if not math.isfinite(arama_yaricapi) or arama_yaricapi < 0:
            raise ValueError("Büyüme arama yarıçapı sonlu ve negatif olmayan değer olmalı.")

        kaynak_buyume = kimyasal_alan.yogunluk("buyume", self.konum, zaman)
        if kaynak_buyume <= self.buyume_esigi:
            return None

        secenekler = []
        for hedef in aday_noronlar:
            if hedef is self:
                continue
            for dendrit in hedef.dendritler.values():
                dx = dendrit.konum[0] - self.konum[0]
                dy = dendrit.konum[1] - self.konum[1]
                uzaklik2 = dx * dx + dy * dy
                if uzaklik2 > arama_yaricapi * arama_yaricapi:
                    continue
                uygunluk = dendrit.buyume_uygunlugu(kimyasal_alan, zaman)
                iliski = self.noron_iliski_oku(hedef, zaman)
                uygunluk *= 1.0 + self.noron_iliski_buyume_etkisi * iliski
                if uygunluk <= self.buyume_esigi:
                    continue
                zaten_var = any(
                    not sinaps.kopuk
                    and sinaps.hedef is hedef
                    and sinaps.hedef_dendrit_id == dendrit.kimlik
                    for sinaps in self.cikis_sinapslari
                )
                if not zaten_var:
                    secenekler.append((
                        -uygunluk, uzaklik2, str(hedef.kimlik),
                        str(dendrit.kimlik), hedef, dendrit
                    ))

        if not secenekler:
            return None
        secenekler.sort(key=lambda oge: oge[:4])
        _, uzaklik2, _, _, hedef, hedef_dendrit = secenekler[0]

        self._yeni_baglanti_sayaci += 1
        kimlik = (
            f"{self.kimlik}::{hedef.kimlik}::{hedef_dendrit.kimlik}"
            f"::{self._yeni_baglanti_sayaci}"
        )
        sinaps = Baglanti(
            kimlik, self, hedef,
            uzunluk=math.sqrt(uzaklik2),
            hedef_dendrit_id=hedef_dendrit.kimlik,
            terminal_konumu=self.konum,
            sinaptik_agirlik=self.yeni_baglanti_agirligi,
            baslangic_yapisal_butunluk=0.25,
            baslangic_yapisal_olgunluk=0.25
        )
        for dendrit in self.dendritler.values():
            dendrit.sinaps_bagla(
                sinaps, self._rastgele.uniform(-0.1, 0.1)
            )
        self.cikis_sinapsi_ekle(sinaps)
        return sinaps

    def baglantilari_bakimdan_gecir(self, zaman, kimyasal_alan=None):
        """Sinapsların gecikmiş modülatör izlerini yerel olarak işler.

        Fiziksel bakım ve budama bağımsız Mikroglia ajanlarına aittir.
        """
        for sinaps in tuple(self.cikis_sinapslari):
            if not sinaps.kopuk:
                sinaps.gecikmis_modulatoru_isle(kimyasal_alan, zaman)
            if sinaps.kopuk:
                self.sinaps_iliskilerini_temizle(sinaps)
                self.cikis_sinapslari.remove(sinaps)
                if sinaps.hedef is not None and sinaps in sinaps.hedef.gelen_sinapslari:
                    sinaps.hedef.gelen_sinapslari.remove(sinaps)
                for dendrit in self.dendritler.values():
                    dendrit.sinaps_katkilari.pop(sinaps, None)
                    dendrit.sinaps_degerlendirmeleri.pop(sinaps, None)
                    dendrit.son_islenen_sinapslar.discard(sinaps)

    def ateslenme_sonucunu_isle(self, zaman, kimyasal_alan=None):
        """Ateşlenme sonrası yerel plastisiteyi ve terminal etkinliğini işler."""
        # STDP'nin postsinaptik olayı tüm gelen sinapslarda iz bırakabilir.
        # Feedback nedenselliği ise yalnızca bu ateşlenmeye gerçekten girdi
        # taşıyan sinapsların ayrı bir anlık görüntüsünü kullanır.
        self._son_nedensel_girdi_sinapslari = {
            sinaps for sinaps in self._entegrasyon_girdi_sinapslari
            if sinaps.hedef is self and not sinaps.kopuk
        }
        for sinaps in tuple(self.gelen_sinapslari):
            if sinaps.hedef is self and not sinaps.kopuk:
                sinaps.stdp_postsinaptik_olayi_isle(zaman)
        self._entegrasyon_girdi_sinapslari.clear()

        aktif = []
        degerlendirilen = [
            sinaps for sinaps in self.cikis_sinapslari if not sinaps.kopuk
        ]
        for sinaps in degerlendirilen:
            if not sinaps.aktive_olabilir_mi(zaman):
                continue
            gecikme = sinaps.aktive_et(zaman)
            sinaps.kimyasal_sal(
                kimyasal_alan, zaman,
                self._sinaps_dendritik_sinyalleri.get(sinaps, 0.0)
            )
            aktif.append((sinaps, gecikme))

        aktif_sinapslar = [sinaps for sinaps, _ in aktif]
        self._son_aktif_cikis_sinapslari = set(aktif_sinapslar)

        # Önce eski yönlü ilişkiler geçici terminal potansiyellerini etkiler.
        self.sinaps_iliski_etkilesimini_uygula(aktif_sinapslar, zaman)

        # Sonra bu ateşlenmenin birliktelik örüntüsü ilişkileri öğrenir.
        aktif_kumesi = set(aktif_sinapslar)
        for kaynak in aktif_sinapslar:
            for hedef in degerlendirilen:
                if hedef is kaynak:
                    continue
                self.sinaps_iliski_guncelle(
                    kaynak, hedef, zaman, birlikte=(hedef in aktif_kumesi)
                )
        for dendrit in self.dendritler.values():
            dendrit.firsat_sonucu_ogren(aktif_sinapslar, zaman)
        return aktif

    def entegrasyonu_isle(self, zaman, kimyasal_alan=None):
        if self.durum != self.DINLENME:
            return False, []

        self.tanilama_entegre_sayisi += 1
        toplam = self.girdileri_birlestir(zaman, kimyasal_alan)
        self.tanilama_toplam_membran_girdisi += toplam
        self.tanilama_mutlak_membran_girdisi += abs(toplam)
        self.tanilama_maksimum_membran_girdisi = max(
            self.tanilama_maksimum_membran_girdisi, abs(toplam)
        )
        self.baglantilari_bakimdan_gecir(zaman, kimyasal_alan)
        self.son_entegrasyon_zamani = float(zaman)
        self.homeostatik_durumu_guncelle(zaman)
        if not self.membrani_guncelle(toplam, zaman):
            return False, []
        if not self.aksiyon_potansiyeli_baslat():
            return False, []

        self.homeostatik_durumu_guncelle(zaman, yeni_ateslenme=True)
        self.yerel_aktivite_izini_guncelle(zaman, yeni_ateslenme=True)
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

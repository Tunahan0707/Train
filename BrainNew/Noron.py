from .Dendrid import Dendrid
from .AksonUcu import AksonUcu


class Noron:
    DINLENME = "dinlenme"
    DEPOLARIZASYON = "depolarizasyon"
    REPOLARIZASYON = "repolarizasyon"
    HIPERPOLARIZASYON = "hiperpolarizasyon"

    GERI_BILDIRIM_IZ_ESIGI = 0.01
    BAGLANTI_BUDAMA_ESIGI = 0.1
    KATKI_ESIGI = 0.001

    def __init__(
        self,
        dendrit_sayisi=8,
        akson_sayisi=7,
        esik_mv=-55.0,
        dinlenme_mv=-70.0,
        sizinti_orani=0.05
    ):
        if not 0.0 <= sizinti_orani <= 1.0:
            raise ValueError("Sızıntı oranı 0 ile 1 arasında olmalıdır.")

        self.dinlenme_mv = dinlenme_mv
        self.membran_potansiyeli = dinlenme_mv
        self.esik_mv = esik_mv
        self.sizinti_orani = sizinti_orani

        self.durum = self.DINLENME
        self.hiperpolarizasyon_kalan = 0
        self.birikmis_sinaptik_katkilar = {}

        self.dendritler = [
            Dendrid(self)
            for _ in range(dendrit_sayisi)
        ]
        self.aksonlar = [
            AksonUcu(self)
            for _ in range(akson_sayisi)
        ]
        self.ateslenme_sayisi = 0

    @property
    def refrakter_mi(self):
        return self.durum != self.DINLENME

    def dis_girdi_al(self, etki_mv):
        if self.durum == self.DINLENME:
            self.membran_potansiyeli += etki_mv

    def _sinaptik_katkilari_guncelle(self, yeni_katkilar):
        koruma_katsayisi = 1.0 - self.sizinti_orani

        # Membran potansiyelindeki sızıntı, geçmiş sinaptik
        # katkıların da zamanla azalmasına yansıtılır.
        for baglanti in tuple(self.birikmis_sinaptik_katkilar):
            katki = (
                self.birikmis_sinaptik_katkilar[baglanti]
                * koruma_katsayisi
            )

            if abs(katki) < self.KATKI_ESIGI:
                del self.birikmis_sinaptik_katkilar[baglanti]
            else:
                self.birikmis_sinaptik_katkilar[baglanti] = katki

        for baglanti, etki_mv in yeni_katkilar:
            if not baglanti.aktif:
                continue

            katki = self.birikmis_sinaptik_katkilar.get(
                baglanti, 0.0
            )
            self.birikmis_sinaptik_katkilar[baglanti] = (
                katki + etki_mv * koruma_katsayisi
            )

    def _katkida_bulunan_baglantilari_isaretle(self):
        for baglanti, katki in tuple(
            self.birikmis_sinaptik_katkilar.items()
        ):
            # Ateşlenme anında hem uyarıcı hem baskılayıcı
            # girdiler nedensel geçmişin parçasıdır. Geri bildirim
            # işareti, ağırlığın hangi yönde değişeceğini belirler.
            if baglanti.aktif and abs(katki) > self.KATKI_ESIGI:
                baglanti.uygunluk_izini_artir()

        self.birikmis_sinaptik_katkilar.clear()

    def guncelle(self):
        if self.durum == self.DEPOLARIZASYON:
            self.membran_potansiyeli = -40.0
            self.durum = self.REPOLARIZASYON
            return False

        if self.durum == self.REPOLARIZASYON:
            self.membran_potansiyeli = -80.0
            self.durum = self.HIPERPOLARIZASYON
            self.hiperpolarizasyon_kalan = 2
            return False

        if self.durum == self.HIPERPOLARIZASYON:
            self.hiperpolarizasyon_kalan -= 1
            if self.hiperpolarizasyon_kalan <= 0:
                self.durum = self.DINLENME
                self.membran_potansiyeli = self.dinlenme_mv
            return False

        toplam_etki = 0.0
        yeni_katkilar = []

        for dendrit in self.dendritler:
            etki, katkilar = dendrit.etkileri_al()
            toplam_etki += etki
            yeni_katkilar.extend(katkilar)

        self.membran_potansiyeli += toplam_etki
        self._sinaptik_katkilari_guncelle(yeni_katkilar)

        fark = self.dinlenme_mv - self.membran_potansiyeli
        self.membran_potansiyeli += fark * self.sizinti_orani

        if self.membran_potansiyeli >= self.esik_mv:
            self.ateslenme_sayisi += 1
            self.membran_potansiyeli = 30.0
            self.durum = self.DEPOLARIZASYON
            self._katkida_bulunan_baglantilari_isaretle()
            return True

        return False

    def geri_bildirim(self, deger):
        """
        Bu nöron kendi gelen bağlantılarını değerlendirir.
        Geri bildirim zincirinin bir önceki aşamasındaki
        nöronları döndürür.

        Ateşlenme izi bulunmayan bir nöron, yalnızca kendi
        sönümlenmekte olan sinaptik katkılarından yerel bir iz
        çıkarabilir. Böylece eşik altında kalan hedef girdileri
        için dışarıdan özel bir öğrenme modu gerekmez.
        """
        if deger not in (-1.0, 0.0, 1.0):
            raise ValueError(
                "Geri bildirim -1, 0 veya +1 olmalıdır."
            )

        if deger == 0:
            return []

        etkin_baglantilar = [
            baglanti
            for dendrit in self.dendritler
            for baglanti in tuple(dendrit.gelen_baglantilar)
            if (
                baglanti.aktif
                and baglanti.uygunluk_izi > self.GERI_BILDIRIM_IZ_ESIGI
            )
        ]

        # Ateşlenmiş nöronlar katkılarını ateşlenme anında zaten
        # uygunluk izine çevirmiştir. Yalnızca henüz böyle bir izi
        # olmayan nöron, kendi kalan katkılarından iz oluşturabilir.
        if not etkin_baglantilar:
            self._katkida_bulunan_baglantilari_isaretle()
            etkin_baglantilar = [
                baglanti
                for dendrit in self.dendritler
                for baglanti in tuple(dendrit.gelen_baglantilar)
                if (
                    baglanti.aktif
                    and baglanti.uygunluk_izi > self.GERI_BILDIRIM_IZ_ESIGI
                )
            ]

        if not etkin_baglantilar:
            return []

        onceki_noronlar = []

        for baglanti in etkin_baglantilar:
            onceki_noronlar.append(baglanti.kaynak.noron)
            baglanti.geri_bildirim(deger)

            if abs(baglanti.etki_mv) < self.BAGLANTI_BUDAMA_ESIGI:
                baglanti.sil()

        if deger > 0:
            self._yeni_baglanti_olustur(etkin_baglantilar)

        return onceki_noronlar

    def _yeni_baglanti_olustur(self, kaynak_baglantilar):
        """
        Geri bildirim alan nöron, kendisine sinyal gönderen
        nöronlardan biriyle yeni bir bağlantı oluşturabilir.
        Her geri bildirim dalgasında en fazla bir yeni bağlantı.
        """
        for kaynak_baglantisi in kaynak_baglantilar:
            akson = kaynak_baglantisi.kaynak

            if not kaynak_baglantisi.aktif:
                continue

            # İlk yapısal büyüme kuralı yalnızca uyarıcı
            # bağlantılardan yeni dallanma üretir. İnhibitör
            # bağlantılar ağırlık öğrenmesine katılır; yeni
            # inhibitör dallanma için ayrı bir kural gerekir.
            if kaynak_baglantisi.etki_mv <= 0:
                continue

            for dendrit in self.dendritler:
                zaten_bagli = any(
                    b.aktif and b.kaynak is akson
                    for b in dendrit.gelen_baglantilar
                )
                if zaten_bagli:
                    continue

                isaret = (
                    1.0 if kaynak_baglantisi.etki_mv >= 0 else -1.0
                )
                akson.baglan(
                    dendrit,
                    etki_mv=isaret,
                    gecikme_ms=kaynak_baglantisi.gecikme_ms
                )
                return

    def fizyolojik_durumu_sifirla(self):
        self.membran_potansiyeli = self.dinlenme_mv
        self.durum = self.DINLENME
        self.hiperpolarizasyon_kalan = 0
        self.birikmis_sinaptik_katkilar.clear()

        for dendrit in self.dendritler:
            dendrit.temizle()

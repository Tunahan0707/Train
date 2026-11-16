import math


class SayisalTemsil:
    """Pozitif tam sayıları örtüşen, log-Gauss ayarlı popülasyonlarla kodlar.

    Bu sınıf görev arayüzüdür; ağın içinde aritmetik işlem yapmaz.
    Her tercih edilen sayı bir nöronun en yüksek yanıt verdiği değerdir.
    Yanıt genliği, sabit aralıklı duyusal darbelerin sayısına dönüştürülür.
    """

    def __init__(
        self,
        en_kucuk=1,
        en_buyuk=9,
        log_sigma=0.25,
        azami_darbe=12,
        darbe_araligi=5.0,
        darbe_etkisi=100.0,
    ):
        try:
            log_sigma = float(log_sigma)
            darbe_araligi = float(darbe_araligi)
            darbe_etkisi = float(darbe_etkisi)
        except (TypeError, ValueError):
            raise ValueError("Sayısal temsil parametreleri sayısal olmalı.") from None
        sayisal = (log_sigma, darbe_araligi, darbe_etkisi)
        if not all(math.isfinite(x) for x in sayisal):
            raise ValueError("Sayısal temsil parametreleri sonlu olmalı.")
        if (
            isinstance(en_kucuk, bool)
            or isinstance(en_buyuk, bool)
            or not isinstance(en_kucuk, int)
            or not isinstance(en_buyuk, int)
            or en_kucuk < 1
            or en_buyuk < en_kucuk
        ):
            raise ValueError("Sayı aralığı pozitif tam sayılardan oluşmalı.")
        if log_sigma <= 0:
            raise ValueError("Logaritmik ayar genişliği pozitif olmalı.")
        if isinstance(azami_darbe, bool) or not isinstance(azami_darbe, int) or azami_darbe < 1:
            raise ValueError("Azami darbe sayısı pozitif tam sayı olmalı.")
        if darbe_araligi <= 0 or darbe_etkisi <= 0:
            raise ValueError("Darbe aralığı ve etkisi pozitif olmalı.")

        self.tercih_edilen_sayilar = tuple(range(en_kucuk, en_buyuk + 1))
        self.log_sigma = float(log_sigma)
        self.azami_darbe = azami_darbe
        self.darbe_araligi = float(darbe_araligi)
        self.darbe_etkisi = float(darbe_etkisi)

        kodlar = {
            self.darbe_sayilari(sayi)
            for sayi in self.tercih_edilen_sayilar
        }
        if len(kodlar) != len(self.tercih_edilen_sayilar):
            raise ValueError(
                "Seçilen ayarlar sayı aralığında birbirinden farklı kodlar üretmiyor."
            )

    def _sayiyi_dogrula(self, sayi):
        if isinstance(sayi, bool) or not isinstance(sayi, int):
            raise TypeError("Kodlanacak değer tam sayı olmalı.")
        if sayi not in self.tercih_edilen_sayilar:
            raise ValueError(
                f"Sayı {self.tercih_edilen_sayilar[0]} ile "
                f"{self.tercih_edilen_sayilar[-1]} arasında olmalı."
            )

    def aktivasyon_vektoru(self, sayi):
        """Sayıya karşı her popülasyon biriminin ideal yanıtını döndürür."""
        self._sayiyi_dogrula(sayi)
        log_sayi = math.log(sayi)
        return tuple(
            math.exp(
                -0.5 * ((log_sayi - math.log(tercih)) / self.log_sigma) ** 2
            )
            for tercih in self.tercih_edilen_sayilar
        )

    def darbe_sayilari(self, sayi):
        """İdeal yanıtları sonlu çözünürlüklü spike/darbe sayılarına çevirir."""
        return tuple(
            int(round(self.azami_darbe * yanit))
            for yanit in self.aktivasyon_vektoru(sayi)
        )

    @staticmethod
    def _kimlikleri_dogrula(kimlikler, beklenen, alan):
        kimlikler = tuple(kimlikler)
        if len(kimlikler) != beklenen:
            raise ValueError(f"{alan} sayısı tercih edilen sayı adediyle eşleşmeli.")
        if any(not isinstance(x, str) or not x for x in kimlikler):
            raise ValueError(f"{alan} boş olmayan metin kimliklerinden oluşmalı.")
        if len(set(kimlikler)) != len(kimlikler):
            raise ValueError(f"{alan} benzersiz olmalı.")
        return kimlikler

    def kodla(
        self,
        sayi,
        noron_kimlikleri,
        dendrit_kimlikleri,
        baslangic_gecikmesi=1e-6,
    ):
        """Sayıyı ReseptorOrgan'ın gönderebileceği duyusal olaylara dönüştürür.

        Dönüş biçimi: (noron_id, dendrit_id, etki, gecikme).
        Aynı popülasyon biriminin darbeleri, nöronun refrakter döngüsünden
        ayrı işlenebilecek biçimde zamana yayılır.
        """
        self._sayiyi_dogrula(sayi)
        noronlar = self._kimlikleri_dogrula(
            noron_kimlikleri, len(self.tercih_edilen_sayilar), "Nöron kimlikleri"
        )
        dendritler = self._kimlikleri_dogrula(
            dendrit_kimlikleri, len(self.tercih_edilen_sayilar), "Dendrit kimlikleri"
        )
        baslangic_gecikmesi = float(baslangic_gecikmesi)
        if not math.isfinite(baslangic_gecikmesi) or baslangic_gecikmesi <= 0:
            raise ValueError("Başlangıç gecikmesi sonlu ve pozitif olmalı.")

        olaylar = []
        for noron_id, dendrit_id, darbe_sayisi in zip(
            noronlar, dendritler, self.darbe_sayilari(sayi)
        ):
            for darbe in range(darbe_sayisi):
                gecikme = baslangic_gecikmesi + darbe * self.darbe_araligi
                olaylar.append(
                    (noron_id, dendrit_id, self.darbe_etkisi, gecikme)
                )
        return tuple(olaylar)

    def coz(self, ateslenme_sayilari, noron_kimlikleri):
        """Popülasyon spike sayılarını en yakın kod kitabı örüntüsüne çözer.

        Bu bir görev hesabı değildir; yalnızca motor popülasyonun hangi
        sayısal örüntüye en çok benzediğini okur. Çıktı yoksa None döner.
        """
        noronlar = self._kimlikleri_dogrula(
            noron_kimlikleri, len(self.tercih_edilen_sayilar), "Nöron kimlikleri"
        )
        gozlenen = []
        for noron_id in noronlar:
            miktar = ateslenme_sayilari.get(noron_id, 0)
            if (
                isinstance(miktar, bool)
                or not isinstance(miktar, int)
                or miktar < 0
            ):
                raise ValueError("Ateşlenme sayıları negatif olmayan tam sayılar olmalı.")
            gozlenen.append(miktar)

        en_yuksek = max(gozlenen, default=0)
        if en_yuksek == 0:
            return None
        normalize_gozlenen = tuple(x / en_yuksek for x in gozlenen)

        en_iyi_sayi = None
        en_iyi_hata = math.inf
        for aday in self.tercih_edilen_sayilar:
            sablon = self.darbe_sayilari(aday)
            sablon_en_yuksek = max(sablon)
            normalize_sablon = tuple(x / sablon_en_yuksek for x in sablon)
            hata = sum(
                (gozlenen_degeri - sablon_degeri) ** 2
                for gozlenen_degeri, sablon_degeri in zip(
                    normalize_gozlenen, normalize_sablon
                )
            )
            if hata < en_iyi_hata:
                en_iyi_sayi = aday
                en_iyi_hata = hata
        return en_iyi_sayi

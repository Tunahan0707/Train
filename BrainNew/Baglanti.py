import math


class Baglanti:
    """Yerel sinaps, transmitter terminali ve yapısal durum."""

    MINIMUM_GECIKME = 1e-6

    def __init__(
        self, kimlik, kaynak, hedef, uzunluk=1.0, iletim_hizi=1.0,
        esik=0.2, sonum_tau=5.0, baslangic_potansiyeli=0.0,
        hedef_dendrit_id=None, etki=1.0, terminal_konumu=None,
        transmitter_profili=None, kimyasal_yayilim=1.0,
        kimyasal_temizlenme=0.1, transmitter_salimi_duyarliliklari=None,
        yapisal_yaslanma_tau=1000.0, bakim_kazanci=0.01,
        budama_kazanci=0.02, budama_esigi=0.1,
        kullanim_izi_esigi=0.1, kopma_esigi=0.1, sinaptik_agirlik=1.0,
        hebbian_oran=0.01, stdp_depresyon_oran=0.01,
        uygunluk_tau=100.0, modulator_ogrenme_orani=0.01,
        baslangic_yapisal_butunluk=1.0
    ):
        sayisal = (
            uzunluk, iletim_hizi, esik, sonum_tau,
            baslangic_potansiyeli, etki, kimyasal_yayilim,
            kimyasal_temizlenme, yapisal_yaslanma_tau,
            bakim_kazanci, budama_kazanci, budama_esigi,
            kullanim_izi_esigi, kopma_esigi, sinaptik_agirlik,
            hebbian_oran, stdp_depresyon_oran,
            uygunluk_tau, modulator_ogrenme_orani,
            baslangic_yapisal_butunluk
        )
        if not all(math.isfinite(float(v)) for v in sayisal):
            raise ValueError("Bağlantı parametreleri sonlu sayılar olmalı.")
        if uzunluk < 0 or iletim_hizi <= 0 or sonum_tau <= 0:
            raise ValueError("Bağlantı parametreleri geçersiz.")
        if not -1.0 <= esik <= 1.0:
            raise ValueError("Sinaps eşiği [-1, 1] potansiyel aralığında olmalı.")
        if not -1.0 <= baslangic_potansiyeli <= 1.0:
            raise ValueError("Başlangıç potansiyeli [-1, 1] aralığında olmalı.")
        if kimyasal_yayilim <= 0 or kimyasal_temizlenme < 0:
            raise ValueError("Kimyasal yayılım parametreleri geçersiz.")
        if not 0.0 <= baslangic_yapisal_butunluk <= 1.0:
            raise ValueError("Başlangıç yapısal bütünlüğü [0, 1] aralığında olmalı.")
        if yapisal_yaslanma_tau <= 0 or bakim_kazanci < 0 or budama_kazanci < 0:
            raise ValueError("Yapısal bakım parametreleri geçersiz.")
        if not 0.0 <= budama_esigi or not 0.0 <= kullanim_izi_esigi:
            raise ValueError("Budama ve kullanım eşikleri negatif olamaz.")
        if not 0.0 <= kopma_esigi <= 1.0:
            raise ValueError("Kopma eşiği [0, 1] aralığında olmalı.")

        self.kimlik = kimlik
        self.kaynak = kaynak
        self.hedef = hedef
        if hedef is not None and hedef_dendrit_id is None:
            raise ValueError("Hedef nöron için dendrit kimliği zorunlu.")
        self.hedef_dendrit_id = hedef_dendrit_id
        self.etki = float(etki)
        self.sinaptik_agirlik_alt = -2.0
        self.sinaptik_agirlik_ust = 2.0
        if not -2.0 <= sinaptik_agirlik <= 2.0:
            raise ValueError("İşaretli sinaptik ağırlık [-2, 2] aralığında olmalı.")
        self.sinaptik_agirlik = float(sinaptik_agirlik)
        if hebbian_oran < 0:
            raise ValueError("Hebbian öğrenme oranı negatif olamaz.")
        self.hebbian_oran = float(hebbian_oran)
        self.hebbian_guncelleme_sayisi = 0
        self.toplam_hebbian_degisim = 0.0
        if stdp_depresyon_oran < 0:
            raise ValueError("STDP depresyon oranı negatif olamaz.")
        self.stdp_depresyon_oran = float(stdp_depresyon_oran)
        self.stdp_depresyon_sayisi = 0
        self.toplam_stdp_depresyon = 0.0
        if uygunluk_tau <= 0 or modulator_ogrenme_orani < 0:
            raise ValueError("Uygunluk izi ve modülatör öğrenme parametreleri geçersiz.")
        self.uygunluk_tau = float(uygunluk_tau)
        self.modulator_ogrenme_orani = float(modulator_ogrenme_orani)
        self.uygunluk_izi = 0.0
        self.son_uygunluk_guncelleme = 0.0
        self.son_modulator_zamani = 0.0
        self.son_modulator_degeri = 0.0
        self.son_modulator_uygunluk_izi = 0.0
        self._uygunluk_olaylari = []
        self.modulator_guncelleme_sayisi = 0
        self.toplam_modulator_agirlik_degisim = 0.0
        self.uzunluk = float(uzunluk)
        self.iletim_hizi = float(iletim_hizi)
        self.esik = float(esik)
        self.sonum_tau = float(sonum_tau)
        self.potansiyel = float(baslangic_potansiyeli)
        self.son_guncelleme = 0.0
        self.son_aktivasyon = None
        self.aktivasyon_sayisi = 0
        self.iz = 0.0

        if terminal_konumu is None:
            terminal_konumu = getattr(kaynak, "konum", (0.0, 0.0))
        if len(terminal_konumu) != 2 or not all(
            math.isfinite(float(v)) for v in terminal_konumu
        ):
            raise ValueError("Terminal konumu sonlu iki boyutlu koordinat olmalı.")
        self.terminal_konumu = tuple(float(v) for v in terminal_konumu)
        self.konum = self.terminal_konumu

        self.transmitter_profili = dict(transmitter_profili or {})
        if any(
            not math.isfinite(float(miktar)) or miktar < 0
            for miktar in self.transmitter_profili.values()
        ):
            raise ValueError("Transmitter salım miktarları sonlu ve negatif olmayan değerler olmalı.")
        self.transmitter_profili = {
            tur: float(miktar) for tur, miktar in self.transmitter_profili.items()
        }
        self.transmitter_salimi_duyarliliklari = dict(
            transmitter_salimi_duyarliliklari or {}
        )
        if any(
            not math.isfinite(float(deger))
            for deger in self.transmitter_salimi_duyarliliklari.values()
        ):
            raise ValueError("Transmitter salım duyarlılıkları sonlu olmalı.")
        if not set(self.transmitter_salimi_duyarliliklari).issubset(
            self.transmitter_profili
        ):
            raise ValueError("Salım duyarlılığı yalnızca terminal repertuvarındaki türlere verilebilir.")

        self.kimyasal_yayilim = float(kimyasal_yayilim)
        self.kimyasal_temizlenme = float(kimyasal_temizlenme)

        # Bağlantı-yerel mikroglia-benzeri yapısal durum.
        self.yapisal_butunluk = float(baslangic_yapisal_butunluk)
        self.son_bakim_zamani = 0.0
        self.yapisal_yaslanma_tau = float(yapisal_yaslanma_tau)
        self.bakim_kazanci = float(bakim_kazanci)
        self.budama_kazanci = float(budama_kazanci)
        self.budama_esigi = float(budama_esigi)
        self.kullanim_izi_esigi = float(kullanim_izi_esigi)
        self.kopma_esigi = float(kopma_esigi)
        self.kopuk = False
        self.son_yapisal_sinyaller = {
            "buyume": 0.0, "stabilizasyon": 0.0, "budama": 0.0
        }

        # Kısa ömürlü etkinlik izleri; kalıcı sinaptik ağırlık değildir.
        self.pre_iz_tau = 20.0
        self.post_iz_tau = 20.0
        self.pre_iz = 0.0
        self.post_iz = 0.0
        self.son_iz_guncelleme = 0.0

        if self.hedef is not None:
            self.hedef.gelen_sinapsi_ekle(self)

    def izleri_guncelle(self, zaman):
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < self.son_iz_guncelleme:
            raise ValueError("Etkinlik izi zamanı sonlu olmalı ve geriye gitmemeli.")
        gecen = zaman - self.son_iz_guncelleme
        if gecen:
            self.pre_iz *= math.exp(-gecen / self.pre_iz_tau)
            self.post_iz *= math.exp(-gecen / self.post_iz_tau)
            self.son_iz_guncelleme = zaman

    def presinaptik_iz_arttir(self, zaman, miktar=1.0):
        miktar = float(miktar)
        if not math.isfinite(miktar) or miktar < 0:
            raise ValueError("Presinaptik iz artışı sonlu ve negatif olmayan değer olmalı.")
        self.izleri_guncelle(zaman)
        self.pre_iz += miktar

    def postsinaptik_iz_arttir(self, zaman, miktar=1.0):
        miktar = float(miktar)
        if not math.isfinite(miktar) or miktar < 0:
            raise ValueError("Postsinaptik iz artışı sonlu ve negatif olmayan değer olmalı.")
        self.izleri_guncelle(zaman)
        self.post_iz += miktar

    def potansiyeli_guncelle(self, zaman):
        zaman = float(zaman)
        if not math.isfinite(zaman):
            raise ValueError("Simülasyon zamanı sonlu olmalı.")
        if zaman < self.son_guncelleme:
            raise ValueError("Simülasyon zamanı geriye gidemez.")
        gecen = zaman - self.son_guncelleme
        if gecen:
            carp = math.exp(-gecen / self.sonum_tau)
            self.potansiyel *= carp
            self.iz *= carp
            self.son_guncelleme = zaman

    def iletim_etkisi(self):
        return self.etki * self.sinaptik_agirlik

    def esik_geri_bildirim_uygula(self, yon, miktar):
        """Yerel feedback'in sinaps aktivasyon eşiğine etkisini uygular.

        yon=+1: etkin sinapsın eşiği düşer, etkin olmayanın yükselir.
        yon=-1: bu yönler tersine döner. Kararı çağıran nöron verir.
        """
        yon = int(yon)
        miktar = float(miktar)
        if yon not in (-1, 1):
            raise ValueError("Feedback yönü +1 veya -1 olmalı.")
        if not math.isfinite(miktar) or miktar < 0:
            raise ValueError("Feedback miktarı sonlu ve negatif olmayan değer olmalı.")
        return max(-1.0, min(1.0, self.esik + yon * miktar))

    def sinaptik_agirligi_ayarla(self, yeni_deger):
        yeni_deger = float(yeni_deger)
        if not math.isfinite(yeni_deger):
            raise ValueError("Sinaptik ağırlık sonlu olmalı.")
        self.sinaptik_agirlik = max(
            self.sinaptik_agirlik_alt,
            min(self.sinaptik_agirlik_ust, yeni_deger)
        )
        return self.sinaptik_agirlik

    def hebbian_ogren(self, zaman):
        """Yerel pre/post birlikteliğini kalıcı elektriksel ağırlığa işler.

        Yalnızca hedefin gerçek bir postsinaptik ateşlenmesi sırasında çağrılır.
        Önceden oluşmuş presinaptik iz zaman farkını taşır; güncelleme
        ağırlık üst sınırına yaklaştıkça doğal olarak küçülür.
        """
        if self.kopuk or self.hebbian_oran == 0.0:
            return 0.0
        self.izleri_guncelle(zaman)
        if self.pre_iz <= 0.0:
            return 0.0

        onceki = self.sinaptik_agirlik
        ust_buyukluk = max(
            abs(self.sinaptik_agirlik_alt),
            abs(self.sinaptik_agirlik_ust)
        )
        buyukluk = abs(onceki)
        kalan_pay = (ust_buyukluk - buyukluk) / ust_buyukluk
        delta = self.hebbian_oran * self.pre_iz * kalan_pay
        # Ağırlık çarpanının nötr başlangıç işareti pozitiftir;
        # uyarıcı/baskılayıcı baz işaret zaten self.etki içinde taşınır.
        isaret = math.copysign(1.0, onceki) if onceki != 0.0 else 1.0
        yeni = self.sinaptik_agirligi_ayarla(
            isaret * (buyukluk + delta)
        )
        gercek_delta = yeni - onceki
        self.hebbian_guncelleme_sayisi += 1
        self.toplam_hebbian_degisim += gercek_delta
        return gercek_delta

    def stdp_presinaptik_olayi_isle(self, zaman):
        """Pre olayı: önce eski post izine göre LTD, sonra pre izini yenile."""
        if self.kopuk:
            return 0.0
        self.izleri_guncelle(zaman)
        self.uygunluk_izini_guncelle(zaman, -min(1.0, self.post_iz))
        onceki = self.sinaptik_agirlik
        if self.post_iz > 0.0 and self.stdp_depresyon_oran > 0.0:
            ust_buyukluk = max(
                abs(self.sinaptik_agirlik_alt),
                abs(self.sinaptik_agirlik_ust)
            )
            buyukluk = abs(onceki)
            delta = (
                self.stdp_depresyon_oran * self.post_iz
                * buyukluk / ust_buyukluk
            )
            isaret = (
                math.copysign(1.0, onceki)
                if onceki != 0.0
                else math.copysign(1.0, self.etki if self.etki != 0.0 else 1.0)
            )
            self.sinaptik_agirligi_ayarla(
                isaret * max(0.0, buyukluk - delta)
            )
            gercek_zayiflama = (
                abs(onceki) - abs(self.sinaptik_agirlik)
            )
            if gercek_zayiflama > 0.0:
                self.stdp_depresyon_sayisi += 1
                self.toplam_stdp_depresyon += gercek_zayiflama
        else:
            gercek_zayiflama = 0.0
        self.presinaptik_iz_arttir(zaman)
        return gercek_zayiflama

    def stdp_postsinaptik_olayi_isle(self, zaman):
        """Post olayı: pre izine göre LTP, ardından post izini yenile."""
        if self.kopuk:
            return 0.0
        degisim = self.hebbian_ogren(zaman)
        self.uygunluk_izini_guncelle(zaman, min(1.0, self.pre_iz))
        self.postsinaptik_iz_arttir(zaman)
        return degisim

    def uygunluk_izini_guncelle(self, zaman, degisim=0.0):
        """Yerel pre/post eşleşmesini gecikmiş geri bildirim için saklar."""
        zaman = float(zaman)
        degisim = float(degisim)
        if not math.isfinite(zaman) or zaman < self.son_uygunluk_guncelleme:
            raise ValueError("Uygunluk izi zamanı sonlu olmalı ve geriye gitmemeli.")
        if not math.isfinite(degisim):
            raise ValueError("Uygunluk izi değişimi sonlu olmalı.")
        gecen = zaman - self.son_uygunluk_guncelleme
        if gecen:
            self.uygunluk_izi *= math.exp(-gecen / self.uygunluk_tau)
            self.son_uygunluk_guncelleme = zaman
        self.uygunluk_izi = max(-1.0, min(1.0, self.uygunluk_izi + degisim))
        if degisim != 0.0:
            self._uygunluk_olaylari.append((zaman, degisim))
        return self.uygunluk_izi

    def gecikmis_modulatoru_isle(self, kimyasal_alan, zaman):
        """Ödül/ceza ile uygunluk izinin zaman-integralini ağırlığa işler.

        Sabit örnekleme anındaki yoğunluğu kullanmak yerine, iki güncelleme
        arasındaki kimyasal alan × uygunluk izi çarpımını Gauss-Legendre
        kuadratürüyle entegre eder. Böylece kısa kimyasal darbeler, arada
        nöron ateşlenmesi olmasa da sonraki bakımda hesaba katılır.
        """
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < self.son_modulator_zamani:
            raise ValueError("Modülatör zamanı sonlu olmalı ve geriye gitmemeli.")

        baslangic = self.son_modulator_zamani
        self.uygunluk_izini_guncelle(zaman)
        if kimyasal_alan is None or self.kopuk:
            self.son_modulator_zamani = zaman
            self.son_modulator_degeri = 0.0
            self.son_modulator_uygunluk_izi = self.uygunluk_izi
            self._uygunluk_olaylari.clear()
            return 0.0

        odul = kimyasal_alan.yogunluk(
            "odul", self.terminal_konumu, zaman
        )
        ceza = kimyasal_alan.yogunluk(
            "ceza", self.terminal_konumu, zaman
        )
        deger = odul - ceza

        olaylar = [
            (olay_zamani, delta)
            for olay_zamani, delta in self._uygunluk_olaylari
            if baslangic <= olay_zamani <= zaman
        ]
        olaylar.sort(key=lambda oge: oge[0])
        baslangic_izi = self.son_modulator_uygunluk_izi

        dugumler = (
            -0.9602898564975363, -0.7966664774136267,
            -0.5255324099163290, -0.1834346424956498,
             0.1834346424956498,  0.5255324099163290,
             0.7966664774136267,  0.9602898564975363
        )
        agirliklar = (
            0.1012285362903763, 0.2223810344533745,
            0.3137066458778873, 0.3626837833783620,
            0.3626837833783620, 0.3137066458778873,
            0.2223810344533745, 0.1012285362903763
        )

        def iz_degeri(olcum_zamani):
            iz = baslangic_izi
            son_olay = baslangic
            for olay_zamani, delta in olaylar:
                if olay_zamani > olcum_zamani:
                    break
                gecen = olay_zamani - son_olay
                if gecen > 0:
                    iz *= math.exp(-gecen / self.uygunluk_tau)
                iz = max(-1.0, min(1.0, iz + delta))
                son_olay = olay_zamani
            kalan = olcum_zamani - son_olay
            if kalan > 0:
                iz *= math.exp(-kalan / self.uygunluk_tau)
            return iz

        integral = 0.0
        kaynaklar = getattr(kimyasal_alan, "kaynaklar", None)
        tek_kaynak_yogunlugu = getattr(
            kimyasal_alan, "kaynak_yogunlugu", None
        )
        if kaynaklar is not None and callable(tek_kaynak_yogunlugu):
            # Her kaynak ayrı entegre edilir. Böylece her quadrature noktasında
            # bütün kaynakları yeniden toplamak yerine maliyet O(kaynak × iz).
            for kaynak in kaynaklar:
                if kaynak.tur not in ("odul", "ceza"):
                    continue
                sol_baslangic = max(baslangic, kaynak.zaman)
                if zaman <= sol_baslangic:
                    continue
                sinirlar = {sol_baslangic, zaman}
                for olay_zamani, _ in olaylar:
                    if sol_baslangic < olay_zamani < zaman:
                        sinirlar.add(olay_zamani)
                kirilma = kaynak.zaman + kaynak.baslangic_yasi
                if sol_baslangic < kirilma < zaman:
                    sinirlar.add(kirilma)
                # Nokta kaynakta ilk yaş çevresindeki 1/t davranışını
                # çözebilmek için kaynak yaşını geometrik aralıklara böl.
                yas = max(
                    sol_baslangic - kaynak.zaman,
                    kaynak.baslangic_yasi
                )
                while True:
                    sonraki_yas = yas * 2.0
                    sonraki_zaman = kaynak.zaman + sonraki_yas
                    if sonraki_zaman <= sol_baslangic or sonraki_zaman >= zaman:
                        break
                    sinirlar.add(sonraki_zaman)
                    yas = sonraki_yas
                sirali_sinirlar = sorted(sinirlar)
                yon = 1.0 if kaynak.tur == "odul" else -1.0
                for sol, sag in zip(sirali_sinirlar, sirali_sinirlar[1:]):
                    if sag <= sol:
                        continue
                    orta = 0.5 * (sol + sag)
                    yari = 0.5 * (sag - sol)
                    for dugum, agirlik in zip(dugumler, agirliklar):
                        t = orta + yari * dugum
                        iz = iz_degeri(t)
                        kimyasal = tek_kaynak_yogunlugu(
                            kaynak, self.terminal_konumu, t
                        )
                        integral += yari * agirlik * iz * kimyasal * yon
        else:
            # Genel KimyasalAlan arayüzü için güvenli geri dönüş.
            sinirlar = {baslangic, zaman}
            for olay_zamani, _ in olaylar:
                sinirlar.add(olay_zamani)
            for sol, sag in zip(sorted(sinirlar), sorted(sinirlar)[1:]):
                if sag <= sol:
                    continue
                orta = 0.5 * (sol + sag)
                yari = 0.5 * (sag - sol)
                for dugum, agirlik in zip(dugumler, agirliklar):
                    t = orta + yari * dugum
                    iz = iz_degeri(t)
                    kimyasal = (
                        kimyasal_alan.yogunluk("odul", self.terminal_konumu, t)
                        - kimyasal_alan.yogunluk("ceza", self.terminal_konumu, t)
                    )
                    integral += yari * agirlik * iz * kimyasal

        self.son_modulator_zamani = zaman
        self.son_modulator_degeri = deger
        self.son_modulator_uygunluk_izi = self.uygunluk_izi
        self._uygunluk_olaylari.clear()

        if self.modulator_ogrenme_orani == 0.0 or integral == 0.0:
            return 0.0

        onceki = self.sinaptik_agirlik
        delta = self.modulator_ogrenme_orani * integral
        self.sinaptik_agirligi_ayarla(onceki + delta)
        gercek_delta = self.sinaptik_agirlik - onceki
        if gercek_delta != 0.0:
            self.modulator_guncelleme_sayisi += 1
            self.toplam_modulator_agirlik_degisim += gercek_delta
        return gercek_delta

    def etki_uygula(self, etki, zaman):
        if self.kopuk:
            return
        etki = float(etki)
        if not math.isfinite(etki):
            raise ValueError("Sinaptik etki sonlu olmalı.")
        self.potansiyeli_guncelle(zaman)
        r = abs(etki) / (1.0 + abs(etki))
        if etki >= 0:
            self.potansiyel += (1.0 - self.potansiyel) * r
        else:
            self.potansiyel -= (1.0 + self.potansiyel) * r
        self.potansiyel = max(-1.0, min(1.0, self.potansiyel))

    def aktive_olabilir_mi(self, zaman):
        if self.kopuk:
            return False
        self.potansiyeli_guncelle(zaman)
        return self.potansiyel >= self.esik

    def aktive_et(self, zaman):
        if self.kopuk:
            raise RuntimeError("Kopmuş bağlantı aktive edilemez.")
        self.potansiyeli_guncelle(zaman)
        self.son_aktivasyon = float(zaman)
        self.aktivasyon_sayisi += 1
        self.iz += 1.0
        self.stdp_presinaptik_olayi_isle(zaman)
        return max(self.MINIMUM_GECIKME, self.uzunluk / self.iletim_hizi)

    def kimyasal_sal(self, kimyasal_alan, zaman, dendritik_sinyal=0.0):
        """Terminal repertuvarını, yerel dendritik sinyalle transmitter bazında modüle eder."""
        if kimyasal_alan is None or self.kopuk:
            return
        dendritik_sinyal = float(dendritik_sinyal)
        if not math.isfinite(dendritik_sinyal):
            raise ValueError("Dendritik salım sinyali sonlu olmalı.")
        for tur, temel_miktar in self.transmitter_profili.items():
            duyarlilik = self.transmitter_salimi_duyarliliklari.get(tur, 0.0)
            miktar = max(0.0, temel_miktar + duyarlilik * dendritik_sinyal)
            if miktar == 0.0:
                continue
            kimyasal_alan.sal(
                tur, self.terminal_konumu, miktar, zaman,
                yayilim=self.kimyasal_yayilim,
                temizlenme=self.kimyasal_temizlenme
            )


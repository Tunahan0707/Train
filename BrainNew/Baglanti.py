import math


class Baglanti:
    """Yerel sinaps, transmitter terminali ve mikroglia-benzeri bakım durumu."""

    MINIMUM_GECIKME = 1e-6

    def __init__(
        self, kimlik, kaynak, hedef, uzunluk=1.0, iletim_hizi=1.0,
        esik=0.2, sonum_tau=5.0, baslangic_potansiyeli=0.0,
        hedef_dendrit_id=None, etki=1.0, terminal_konumu=None,
        transmitter_profili=None, kimyasal_yayilim=1.0,
        kimyasal_temizlenme=0.1, transmitter_salimi_duyarliliklari=None,
        yapisal_yaslanma_tau=1000.0, bakim_kazanci=0.01,
        budama_kazanci=0.02, budama_esigi=0.1,
        kullanim_izi_esigi=0.1, kopma_esigi=0.1, sinaptik_agirlik=1.0
    ):
        sayisal = (
            uzunluk, iletim_hizi, esik, sonum_tau,
            baslangic_potansiyeli, etki, kimyasal_yayilim,
            kimyasal_temizlenme, yapisal_yaslanma_tau,
            bakim_kazanci, budama_kazanci, budama_esigi,
            kullanim_izi_esigi, kopma_esigi, sinaptik_agirlik
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
        self.sinaptik_agirlik_alt = 0.0
        self.sinaptik_agirlik_ust = 2.0
        if not 0.0 <= sinaptik_agirlik <= 2.0:
            raise ValueError("Sinaptik ağırlık [0, 2] aralığında olmalı.")
        self.sinaptik_agirlik = float(sinaptik_agirlik)
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
        self.yapisal_butunluk = 1.0
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

    def sinaptik_agirligi_ayarla(self, yeni_deger):
        yeni_deger = float(yeni_deger)
        if not math.isfinite(yeni_deger):
            raise ValueError("Sinaptik ağırlık sonlu olmalı.")
        self.sinaptik_agirlik = max(0.0, min(2.0, yeni_deger))
        return self.sinaptik_agirlik

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
        self.presinaptik_iz_arttir(zaman)
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

    def yerel_bakim(self, kimyasal_alan, zaman):
        """Bağlantı-yerel bakım/budama; Beyin veya küresel yönetici karar vermez."""
        zaman = float(zaman)
        if not math.isfinite(zaman) or zaman < self.son_bakim_zamani:
            raise ValueError("Yapısal bakım zamanı sonlu olmalı ve geriye gitmemeli.")
        if self.kopuk:
            return False

        self.potansiyeli_guncelle(zaman)
        gecen = zaman - self.son_bakim_zamani
        if gecen:
            self.yapisal_butunluk *= math.exp(
                -gecen / self.yapisal_yaslanma_tau
            )

        sinyaller = {"buyume": 0.0, "stabilizasyon": 0.0, "budama": 0.0}
        if kimyasal_alan is not None:
            for tur in sinyaller:
                sinyaller[tur] = kimyasal_alan.yogunluk(
                    tur, self.terminal_konumu, zaman
                )
        self.son_yapisal_sinyaller = sinyaller

        # Büyüme/stabilizasyon sinyalleri mevcut bağlantıyı korur veya
        # güçlendirir. Budama, yalnızca düşük kullanım iziyle birlikte etkilidir.
        koruma = sinyaller["buyume"] + sinyaller["stabilizasyon"]
        self.yapisal_butunluk += self.bakim_kazanci * koruma
        if self.iz < self.kullanim_izi_esigi:
            self.yapisal_butunluk -= (
                self.budama_kazanci * sinyaller["budama"]
            )
        self.yapisal_butunluk = max(0.0, min(1.0, self.yapisal_butunluk))
        self.son_bakim_zamani = zaman

        if (
            self.iz < self.kullanim_izi_esigi
            and sinyaller["budama"] >= self.budama_esigi
            and self.yapisal_butunluk <= self.kopma_esigi
        ):
            self.kopuk = True
        return not self.kopuk

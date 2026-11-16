import heapq
import itertools
import math


class Beyin:
    """Simülasyon saatini ve olayların bileşenlere dağıtımını yönetir."""

    ENTEGRASYON_GECIKMESI = 1e-6
    _OLAY_ONCELIGI = {
        "duyusal_girdi": 0,
        "sinaptik_girdi": 0,
        "faz": 1,
        "entegrasyon": 2,
    }

    def __init__(self, kimyasal_alan=None):
        self.zaman = 0.0
        self.noronlar = {}
        self.kimyasal_alan = kimyasal_alan
        self._olaylar = []
        self._olay_sayaci = itertools.count()
        self._entegrasyon_planlari = set()

    def noron_ekle(self, noron):
        mevcut = self.noronlar.get(noron.kimlik)
        if mevcut is not None and mevcut is not noron:
            raise ValueError(f"Aynı kimlikle ikinci bir nöron eklenemez: {noron.kimlik}")
        self.noronlar[noron.kimlik] = noron

    def olay_planla(self, gecikme, tur, hedef_id, veri=None):
        try:
            gecikme = float(gecikme)
        except (TypeError, ValueError):
            raise ValueError("Olay gecikmesi sonlu ve sıfırdan büyük olmalı.") from None
        if not math.isfinite(gecikme) or gecikme <= 0:
            raise ValueError("Olay gecikmesi sonlu ve sıfırdan büyük olmalı.")

        olay_zamani = self.zaman + gecikme
        olay_id = next(self._olay_sayaci)
        oncelik = self._OLAY_ONCELIGI.get(tur, 99)
        heapq.heappush(
            self._olaylar,
            (olay_zamani, oncelik, olay_id, tur, hedef_id, veri)
        )
        return olay_id

    def _entegrasyon_planla(self, noron_id):
        olay_zamani = self.zaman + self.ENTEGRASYON_GECIKMESI
        anahtar = (noron_id, olay_zamani)
        if anahtar in self._entegrasyon_planlari:
            return None
        self._entegrasyon_planlari.add(anahtar)
        return self.olay_planla(
            self.ENTEGRASYON_GECIKMESI, "entegrasyon", noron_id
        )

    def duyusal_girdi(self, noron_id, dendrit_id, etki, gecikme=1e-6):
        if noron_id not in self.noronlar:
            raise ValueError(f"Bilinmeyen nöron: {noron_id}")
        self.olay_planla(
            gecikme, "duyusal_girdi", noron_id, (dendrit_id, float(etki))
        )

    def sinyal_gonder(self, sinaps, zaman):
        if zaman != self.zaman:
            raise ValueError("Sinaps aktivasyonu mevcut simülasyon zamanında yapılmalı.")
        if sinaps.hedef is not None:
            hedef_id = sinaps.hedef.kimlik
            if self.noronlar.get(hedef_id) is not sinaps.hedef:
                raise ValueError("Hedef nöron bu Beyin'e kayıtlı değil.")
            if sinaps.hedef_dendrit_id not in sinaps.hedef.dendritler:
                raise ValueError("Hedef dendrit, hedef nöronda bulunamadı.")

        # Aktivasyon eşiğini sinapsın kendisi doğrular ve yerel salımı başlatır.
        gecikme = sinaps.aktive_et(zaman)
        sinaps.kimyasal_sal(self.kimyasal_alan, zaman)
        if sinaps.hedef is not None:
            self.olay_planla(
                gecikme, "sinaptik_girdi", sinaps.hedef.kimlik,
                (sinaps.kimlik, sinaps.hedef_dendrit_id, sinaps.etki)
            )

    def _girdi_olayini_isle(self, noron, veri):
        if len(veri) == 2:
            dendrit_id, etki = veri
        else:
            _, dendrit_id, etki = veri
        noron.girdi_al(dendrit_id, etki, zaman=self.zaman)
        self._entegrasyon_planla(noron.kimlik)

    def adim(self):
        if not self._olaylar:
            return False

        zaman, _, _, tur, hedef_id, veri = heapq.heappop(self._olaylar)
        self.zaman = zaman

        if tur in ("duyusal_girdi", "sinaptik_girdi"):
            self._girdi_olayini_isle(self.noronlar[hedef_id], veri)

        elif tur == "entegrasyon":
            self._entegrasyon_planlari.discard((hedef_id, zaman))
            noron = self.noronlar[hedef_id]
            ateslendi, aktif_sinapslar = noron.entegrasyonu_isle(
                self.zaman, self.kimyasal_alan
            )
            if ateslendi:
                for sinaps in aktif_sinapslar:
                    self.sinyal_gonder(sinaps, self.zaman)
                self.olay_planla(1.0, "faz", hedef_id)

        elif tur == "faz":
            noron = self.noronlar[hedef_id]
            sonraki_gecikme = noron.faz_olayini_isle()
            if sonraki_gecikme is not None:
                self.olay_planla(sonraki_gecikme, "faz", hedef_id)
            elif noron.bekleyen_girdi_var_mi():
                # Refrakter dönemde tamponda tutulan girdiler kaybolmaz.
                self._entegrasyon_planla(noron.kimlik)

        else:
            raise ValueError(f"Bilinmeyen olay türü: {tur}")

        return True

    def calistir(self, olay_limiti=100000):
        if not isinstance(olay_limiti, int) or olay_limiti < 0:
            raise ValueError("Olay limiti negatif olmayan bir tam sayı olmalı.")
        islenen = 0
        while self._olaylar and islenen < olay_limiti:
            self.adim()
            islenen += 1
        if self._olaylar and islenen >= olay_limiti:
            raise RuntimeError("Olay limiti aşıldı; olası sonsuz olay zinciri.")
        return islenen

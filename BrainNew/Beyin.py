import heapq
import itertools
import math

from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.Mikroglia import Mikroglia
from BrainNew.UzamsalIndeks import UzamsalIndeks


class Beyin:
    """Simülasyon saatini ve olayların bileşenlere dağıtımını yönetir."""

    ENTEGRASYON_GECIKMESI = 1e-6
    _OLAY_ONCELIGI = {
        "duyusal_girdi": 0,
        "sinaptik_girdi": 0,
        "faz": 1,
        "entegrasyon": 2,
    }

    def __init__(self, kimyasal_alan=None, deney_kaydi=None):
        self.zaman = 0.0
        self.noronlar = {}
        self.baglanti_indeksi = UzamsalIndeks()
        self.mikroglialar = {}
        self.kimyasal_alan = kimyasal_alan if kimyasal_alan is not None else KimyasalAlan()
        self.deney_kaydi = deney_kaydi
        self._olaylar = []
        self._olay_sayaci = itertools.count()
        self._entegrasyon_planlari = set()

    def noron_ekle(self, noron):
        mevcut = self.noronlar.get(noron.kimlik)
        if mevcut is not None and mevcut is not noron:
            raise ValueError(f"Aynı kimlikle ikinci bir nöron eklenemez: {noron.kimlik}")
        self.noronlar[noron.kimlik] = noron
        for sinaps in noron.cikis_sinapslari:
            self.baglanti_ekle(sinaps)

    def baglanti_ekle(self, sinaps):
        """Sinaps terminalini mikroglia için uzamsal indekse kaydeder."""
        if sinaps.kopuk:
            return False
        return self.baglanti_indeksi.ekle(sinaps)

    def mikroglia_ekle(self, mikroglia):
        if not isinstance(mikroglia, Mikroglia):
            raise TypeError("mikroglia_ekle bir Mikroglia nesnesi bekler.")
        mevcut = self.mikroglialar.get(mikroglia.kimlik)
        if mevcut is not None and mevcut is not mikroglia:
            raise ValueError("Aynı kimlikle ikinci bir mikroglia eklenemez.")
        self.mikroglialar[mikroglia.kimlik] = mikroglia
        return mikroglia

    def mikroglia_bakim_planla(self, mikroglia_id, gecikme):
        if mikroglia_id not in self.mikroglialar:
            raise ValueError(f"Bilinmeyen mikroglia: {mikroglia_id}")
        return self.olay_planla(gecikme, "mikroglia_bakim", mikroglia_id)

    def _kopuk_baglantiyi_temizle(self, sinaps):
        if sinaps.kaynak is not None and sinaps in sinaps.kaynak.cikis_sinapslari:
            sinaps.kaynak.cikis_sinapslari.remove(sinaps)
            for dendrit in sinaps.kaynak.dendritler.values():
                dendrit.sinaps_katkilari.pop(sinaps, None)
                dendrit.sinaps_degerlendirmeleri.pop(sinaps, None)
                dendrit.son_islenen_sinapslar.discard(sinaps)
        if sinaps.hedef is not None and sinaps in sinaps.hedef.gelen_sinapslari:
            sinaps.hedef.gelen_sinapslari.remove(sinaps)
        self.baglanti_indeksi.cikar(sinaps)

    def olay_planla(self, gecikme, tur, hedef_id, veri=None):
        try:
            gecikme = float(gecikme)
        except (TypeError, ValueError):
            raise ValueError("Olay gecikmesi sonlu ve sıfırdan büyük olmalı.") from None
        if not math.isfinite(gecikme) or gecikme <= 0:
            raise ValueError("Olay gecikmesi sonlu ve sıfırdan büyük olmalı.")

        olay_zamani = self.zaman + gecikme
        if not math.isfinite(olay_zamani):
            raise ValueError("Planlanan olay zamanı sonlu olmalı.")
        if olay_zamani <= self.zaman:
            raise ValueError("Gecikme, mevcut simülasyon zamanında temsil edilemeyecek kadar küçük.")
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
        olay_id = self.olay_planla(
            self.ENTEGRASYON_GECIKMESI, "entegrasyon", noron_id
        )
        self._entegrasyon_planlari.add(anahtar)
        return olay_id

    def duyusal_girdi(self, noron_id, dendrit_id, etki, gecikme=1e-6):
        if noron_id not in self.noronlar:
            raise ValueError(f"Bilinmeyen nöron: {noron_id}")
        self.olay_planla(
            gecikme, "duyusal_girdi", noron_id, (dendrit_id, float(etki))
        )

    def _iletim_olayini_planla(self, sinaps, gecikme):
        """Önceden yerel olarak aktive edilmiş sinapsın iletimini zamanlar."""
        if sinaps.hedef is None:
            return
        hedef_id = sinaps.hedef.kimlik
        if self.noronlar.get(hedef_id) is not sinaps.hedef:
            raise ValueError("Hedef nöron bu Beyin'e kayıtlı değil.")
        if sinaps.hedef_dendrit_id not in sinaps.hedef.dendritler:
            raise ValueError("Hedef dendrit, hedef nöronda bulunamadı.")
        self.olay_planla(
            gecikme, "sinaptik_girdi", hedef_id,
            (sinaps, sinaps.hedef_dendrit_id, sinaps.iletim_etkisi())
        )

    def sinyal_gonder(self, sinaps, zaman):
        """Tekil/dış kullanım için sinaps aktivasyonunu ve iletimini başlatır.

        Normal ağ akışında aktivasyon kararını Noron verir; bu yardımcı metot
        yalnızca açıkça istenen doğrudan sinaps aktivasyonu içindir.
        """
        if zaman != self.zaman:
            raise ValueError("Sinaps aktivasyonu mevcut simülasyon zamanında yapılmalı.")
        if sinaps.hedef is not None:
            hedef_id = sinaps.hedef.kimlik
            if self.noronlar.get(hedef_id) is not sinaps.hedef:
                raise ValueError("Hedef nöron bu Beyin'e kayıtlı değil.")
            if sinaps.hedef_dendrit_id not in sinaps.hedef.dendritler:
                raise ValueError("Hedef dendrit, hedef nöronda bulunamadı.")
        if not sinaps.aktive_olabilir_mi(zaman):
            return False
        gecikme = sinaps.aktive_et(zaman)
        sinaps.kimyasal_sal(self.kimyasal_alan, zaman)
        self._iletim_olayini_planla(sinaps, gecikme)
        return True

    def _girdi_olayini_isle(self, noron, veri):
        kaynak_sinaps = None
        if len(veri) == 2:
            dendrit_id, etki = veri
        else:
            kaynak_sinaps, dendrit_id, etki = veri
        # Eski Noron alt sınıflarıyla uyumluluk için mevcut girdi imzasını koru.
        noron.girdi_al(dendrit_id, etki, zaman=self.zaman)
        if kaynak_sinaps is not None:
            noron.girdi_kaynagini_isaretle(dendrit_id, kaynak_sinaps)
        self._entegrasyon_planla(noron.kimlik)

    def adim(self):
        if not self._olaylar:
            return False

        zaman, _, olay_id, tur, hedef_id, veri = heapq.heappop(self._olaylar)
        self.zaman = zaman

        # Pasif gözlem: kayıt olay akışına ve öğrenme kararlarına müdahale etmez.
        if self.deney_kaydi is not None:
            self.deney_kaydi.olay_kaydet(zaman, olay_id, tur, hedef_id, veri)

        if tur in ("duyusal_girdi", "sinaptik_girdi"):
            self._girdi_olayini_isle(self.noronlar[hedef_id], veri)

        elif tur == "entegrasyon":
            self._entegrasyon_planlari.discard((hedef_id, zaman))
            noron = self.noronlar[hedef_id]
            ateslendi, aktif_sinapslar = noron.entegrasyonu_isle(
                self.zaman, self.kimyasal_alan
            )
            if ateslendi:
                for sinaps, gecikme in aktif_sinapslar:
                    self._iletim_olayini_planla(sinaps, gecikme)
                self.olay_planla(
                    noron.faz_gecisi_gecikmesi(), "faz", hedef_id
                )

        elif tur == "faz":
            noron = self.noronlar[hedef_id]
            sonraki_gecikme = noron.faz_olayini_isle()
            if sonraki_gecikme is not None:
                self.olay_planla(sonraki_gecikme, "faz", hedef_id)
            elif noron.bekleyen_girdi_var_mi():
                # Refrakter dönemde tamponda tutulan girdiler kaybolmaz.
                self._entegrasyon_planla(noron.kimlik)

        elif tur == "mikroglia_bakim":
            mikroglia = self.mikroglialar[hedef_id]
            kopanlar = mikroglia.bakim_yap(
                self.baglanti_indeksi, self.kimyasal_alan, self.zaman
            )
            for sinaps in kopanlar:
                self._kopuk_baglantiyi_temizle(sinaps)

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

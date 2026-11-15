
import heapq
import random
from collections import deque

from Noron import Noron
from ReseptorOrgan import ReseptorOrgan
from MotorOrgan import MotorOrgan


class Beyin:
    def __init__(
        self,
        girdi_sayisi,
        cikti_sayisi,
        ara_noron_sayisi=50,
        seed=None,
        trace=None
    ):
        self.rng = random.Random(seed)
        self.trace = trace

        self.zaman = 0
        self._olay_sirasi = 0
        self._olay_kuyrugu = []

        self.etkin_baglantilar = set()

        self.reseptor_noronlari = [
            Noron(
                dendrit_sayisi=self.rng.randint(6, 12),
                akson_sayisi=self.rng.randint(5, 10)
            )
            for _ in range(girdi_sayisi)
        ]

        self.ara_noronlar = [
            Noron(
                dendrit_sayisi=self.rng.randint(6, 12),
                akson_sayisi=self.rng.randint(5, 10)
            )
            for _ in range(ara_noron_sayisi)
        ]

        self.motor_noronlari = [
            Noron(
                dendrit_sayisi=self.rng.randint(6, 12),
                akson_sayisi=self.rng.randint(5, 10)
            )
            for _ in range(cikti_sayisi)
        ]

        self.noronlar = (
            self.reseptor_noronlari
            + self.ara_noronlar
            + self.motor_noronlari
        )

        self.reseptor_organ = ReseptorOrgan(
            self.reseptor_noronlari
        )

        self.motor_organ = MotorOrgan(cikti_sayisi)

        self._rastgele_baglantilari_olustur()

    def _rastgele_baglantilari_olustur(self):
        tum_dendritler = [
            dendrit
            for noron in self.noronlar
            for dendrit in noron.dendritler
        ]

        for noron in self.noronlar:
            for akson in noron.aksonlar:
                baglanti_sayisi = self.rng.randint(0, 2)

                if not tum_dendritler:
                    continue

                hedefler = self.rng.sample(
                    tum_dendritler,
                    min(baglanti_sayisi, len(tum_dendritler))
                )

                for hedef in hedefler:
                    isaret = self.rng.choice((-1, 1))

                    akson.baglan(
                        hedef,
                        etki_mv=isaret * 2.0,
                        gecikme_ms=self.rng.randint(1, 5)
                    )

    def _iletim_planla(self, baglanti):
        teslim_zamani = self.zaman + baglanti.gecikme_ms

        self._olay_sirasi += 1

        heapq.heappush(
            self._olay_kuyrugu,
            (
                teslim_zamani,
                self._olay_sirasi,
                baglanti
            )
        )

    def deneme_sonu_sifirla(self):
        """
        Geçici fizyolojik durumu sıfırlar.
        Öğrenilmiş sinaptik durumları korur.
        """

        for noron in self.noronlar:
            noron.fizyolojik_durumu_sifirla()

        # Önceki denemeden kalan sinyaller yeni denemeye taşınmasın.
        self._olay_kuyrugu.clear()

    def _olaylari_ilet(self):
        while (
            self._olay_kuyrugu
            and self._olay_kuyrugu[0][0] <= self.zaman
        ):
            _, _, baglanti = heapq.heappop(
                self._olay_kuyrugu
            )

            if not baglanti.aktif:
                continue

            baglanti.aktar(self.zaman, self.trace)

            if baglanti.aktif:
                self.etkin_baglantilar.add(baglanti)

    def adim(self):
        self._olaylari_ilet()

        ateslenenler = []

        for noron in self.noronlar:
            if noron.guncelle():
                ateslenenler.append(noron)

        for noron in ateslenenler:

            if self.trace is not None:
                self.trace.ateslenme_kaydet(
                    self.zaman,
                    noron
                )

            if noron in self.motor_noronlari:
                indeks = self.motor_noronlari.index(noron)
                self.motor_organ.noron_ateslendi(indeks)

            for akson in noron.aksonlar:
                for baglanti in akson.baglantilar:
                    self._iletim_planla(baglanti)

        self.uygunluk_izlerini_guncelle()

        self.zaman += 1

        return ateslenenler

    def girdi_al(self, veri):
        self.motor_organ.reset()
        self.reseptor_organ.girdi_al(veri)

    def calistir(self, adim_sayisi=100):
        for _ in range(adim_sayisi):
            self.adim()

        return self.motor_organ.ciktilar.copy()

    def isle(self, veri, adim_sayisi=100):
        self.girdi_al(veri)
        return self.calistir(adim_sayisi)

    def geri_bildirim(self, deger):
        """
        Geri bildirim motor nöronlarından başlar.

        Beyin bağlantıları değiştirmez.
        Yalnızca geri bildirim dalgasını koordine eder.
        """

        if deger not in (-1.0, 0.0, 1.0):
            raise ValueError(
                "Geri bildirim -1, 0 veya +1 olmalıdır."
            )

        if deger == 0:
            return

        kuyruk = deque(
            noron
            for indeks, noron in enumerate(
                self.motor_noronlari
            )
            if self.motor_organ.ciktilar[indeks] == 1
        )

        ziyaret_edilen = set()

        while kuyruk:
            noron = kuyruk.popleft()

            if noron in ziyaret_edilen:
                continue

            ziyaret_edilen.add(noron)

            # Nöron kendi yerel bağlantılarını değerlendirir.
            onceki_noronlar = noron.geri_bildirim(deger)

            # Beyin yalnızca geri bildirim dalgasını taşır.
            for onceki_noron in onceki_noronlar:
                if onceki_noron not in ziyaret_edilen:
                    kuyruk.append(onceki_noron)

    def uygunluk_izlerini_guncelle(self):
        for baglanti in tuple(self.etkin_baglantilar):

            if not baglanti.aktif:
                self.etkin_baglantilar.discard(baglanti)
                continue

            baglanti.izi_azalt()

            if baglanti.uygunluk_izi < 0.01:
                self.etkin_baglantilar.discard(baglanti)

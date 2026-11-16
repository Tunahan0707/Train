import heapq
import math
import random
from collections import deque

from .Noron import Noron
from .ReseptorOrgan import ReseptorOrgan
from .MotorOrgan import MotorOrgan


class Beyin:
    # 100 ara noronda %25 fan-out ve %75 fan-in, ortalama %18.75 kesişim verir.
    GIRDI_ARA_FANOUT_ORANI = 0.25
    ARA_MOTOR_FANIN_ORANI = 0.75

    # Uc eszamanli 5.6 mV sinaps: 3 * 5.6 * 0.95 = 15.96 mV.
    MOTOR_ESZAMANLI_SINAPSAYISI = 3
    ILK_SINAPTIK_ETKI_MV = 5.6

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

        self.reseptor_organ = ReseptorOrgan(self.reseptor_noronlari)
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

        self._sinyal_omurgasini_olustur()

    def _sinyal_omurgasini_olustur(self):
        """
        Rastgele arka plan agina seyrek bir ileri-iletim omurgasi ekler.
        Girdi-cikti eslesmesini kodlamaz; yalnizca sinyalin ara ve motor
        noronlara ulasabilecegi baslangic yollarini kurar.
        """
        if not self.ara_noronlar:
            return

        # Reseptorlerin rastgele cikislarini kaldirip ileri projeksiyonu kur.
        for reseptor in self.reseptor_noronlari:
            for akson in reseptor.aksonlar:
                for baglanti in tuple(akson.baglantilar):
                    baglanti.sil()

        # Ara noronlardan motorlara giden rastgele yollarin yerine,
        # kontrollu ve eszamanli baslangic projeksiyonlari kur.
        motor_kumesi = set(self.motor_noronlari)
        for ara_noron in self.ara_noronlar:
            for akson in ara_noron.aksonlar:
                for baglanti in tuple(akson.baglantilar):
                    if baglanti.hedef.noron in motor_kumesi:
                        baglanti.sil()

        ara_sayisi = len(self.ara_noronlar)
        girdi_fanout = min(
            ara_sayisi,
            max(1, math.ceil(
                ara_sayisi * self.GIRDI_ARA_FANOUT_ORANI
            ))
        )
        motor_fanin = min(
            ara_sayisi,
            max(1, math.ceil(
                ara_sayisi * self.ARA_MOTOR_FANIN_ORANI
            ))
        )

        girdi_hedefleri = [
            self.rng.sample(self.ara_noronlar, girdi_fanout)
            for _ in self.reseptor_noronlari
        ]
        motor_kaynaklari = [
            self.rng.sample(self.ara_noronlar, motor_fanin)
            for _ in self.motor_noronlari
        ]

        etki = self.ILK_SINAPTIK_ETKI_MV

        for reseptor, hedefler in zip(
            self.reseptor_noronlari, girdi_hedefleri
        ):
            for hedef_noron in hedefler:
                akson = self.rng.choice(reseptor.aksonlar)
                dendrit = self.rng.choice(hedef_noron.dendritler)
                akson.baglan(
                    dendrit,
                    etki_mv=etki,
                    gecikme_ms=self.rng.randint(1, 5)
                )

        for motor, kaynaklar in zip(
            self.motor_noronlari, motor_kaynaklari
        ):
            for kaynak_noron in kaynaklar:
                gecikme = self.rng.randint(1, 5)
                aksonlar = self.rng.sample(
                    kaynak_noron.aksonlar,
                    self.MOTOR_ESZAMANLI_SINAPSAYISI
                )
                dendritler = self.rng.sample(
                    motor.dendritler,
                    self.MOTOR_ESZAMANLI_SINAPSAYISI
                )

                for akson, dendrit in zip(aksonlar, dendritler):
                    akson.baglan(
                        dendrit,
                        etki_mv=etki,
                        gecikme_ms=gecikme
                    )

    def _iletim_planla(self, baglanti):
        teslim_zamani = self.zaman + baglanti.gecikme_ms
        self._olay_sirasi += 1
        heapq.heappush(
            self._olay_kuyrugu,
            (teslim_zamani, self._olay_sirasi, baglanti)
        )

    def deneme_sonu_sifirla(self):
        """Geçici fizyolojik durumu sıfırlar; öğrenilmiş bağlantıları korur."""
        for noron in self.noronlar:
            noron.fizyolojik_durumu_sifirla()

        # Uygunluk izleri yalnızca mevcut denemeye ait geçici
        # nedensel bilgidir; denemeler arasında taşınmamalıdır.
        for baglanti in tuple(self.etkin_baglantilar):
            baglanti.uygunluk_izi = 0.0
        self.etkin_baglantilar.clear()
        self._olay_kuyrugu.clear()
        self.motor_organ.reset()
        self.reseptor_organ.sifirla()

    def _olaylari_ilet(self):
        while (
            self._olay_kuyrugu
            and self._olay_kuyrugu[0][0] <= self.zaman
        ):
            _, _, baglanti = heapq.heappop(self._olay_kuyrugu)
            if not baglanti.aktif:
                continue

            baglanti.aktar(self.zaman, self.trace)
            if baglanti.aktif:
                self.etkin_baglantilar.add(baglanti)

    def adim(self):
        # Aktif duyusal uyaran her biyolojik zaman adiminda uygulanir.
        self.reseptor_organ.uyarim_uygula()

        # Önce önceki zaman adımından kalan izleri azalt.
        # Bu adımda oluşan yeni izler bir sonraki adımda azalmaya başlar.
        self.uygunluk_izlerini_guncelle()
        self._olaylari_ilet()
        ateslenenler = []

        for noron in self.noronlar:
            if noron.guncelle():
                ateslenenler.append(noron)

        for noron in ateslenenler:
            if self.trace is not None:
                self.trace.ateslenme_kaydet(self.zaman, noron)

            if noron in self.motor_noronlari:
                indeks = self.motor_noronlari.index(noron)
                self.motor_organ.noron_ateslendi(indeks)

            for akson in noron.aksonlar:
                for baglanti in akson.baglantilar:
                    self._iletim_planla(baglanti)

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

    def geri_bildirim(self, deger, baslangic_noronlari=None):
        """
        Geri bildirim dalgasını verilen başlangıç nöronlarından
        geriye doğru koordine eder.

        Başlangıç nöronları belirtilmezse ateşlenmiş motor nöronları
        kullanılır. Öğretici sinyalin hedefi ateşlenmemiş bir motor
        nöronuyse deney katmanı onu açıkça başlangıç olarak verebilir.

        Beklenen çıktıyı belirlemek veya hata hesaplamak bu sınıfın
        görevi değildir; bunlar deney/eğitim katmanına aittir.
        """
        if deger not in (-1.0, 0.0, 1.0):
            raise ValueError("Geri bildirim -1, 0 veya +1 olmalıdır.")
        if deger == 0:
            return

        if baslangic_noronlari is None:
            baslangic_noronlari = [
                noron
                for indeks, noron in enumerate(self.motor_noronlari)
                if self.motor_organ.ciktilar[indeks] == 1
            ]
        else:
            baslangic_noronlari = list(baslangic_noronlari)

        motor_kumesi = set(self.motor_noronlari)
        if any(noron not in motor_kumesi for noron in baslangic_noronlari):
            raise ValueError("Geri bildirim başlangıçları motor nöronları olmalıdır.")

        kuyruk = deque(baslangic_noronlari)
        ziyaret_edilen = set()

        while kuyruk:
            noron = kuyruk.popleft()
            if noron in ziyaret_edilen:
                continue

            ziyaret_edilen.add(noron)
            onceki_noronlar = noron.geri_bildirim(deger)

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

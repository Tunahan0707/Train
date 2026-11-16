import random

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.MotorOrgan import MotorOrgan
from BrainNew.Noron import Noron
from BrainNew.ReseptorOrgan import ReseptorOrgan
from BrainNew.SayisalTemsil import SayisalTemsil


class BuyuklukKarsilastirmaDeneyi:
    """Rastgele başlangıçlı bir ağda ödül-modülatörlü büyüklük karşılaştırması.

    Sol/sağ sayı popülasyonları iki ayrı duyusal kanaldır. Her duyusal
    nöronun iki karar nöronuna da başlangıçta rastgele işaretli bağlantısı
    bulunur. Karşılaştırma kuralı bağlantı topolojisine yerleştirilmez.

    Görev ortamı yalnızca ağ çıktısını değerlendirip odul/ceza kimyasalı
    salar. Sinaptik ağırlık güncellemesi Baglanti'nin yerel uygunluk izi ve
    modülatör integrali üzerinden gerçekleşir.
    """

    SOL = "SOL_BUYUK"
    SAG = "SAG_BUYUK"
    KARAR_NORONLARI = (SOL, SAG)

    def __init__(
        self,
        seed=20261120,
        test_orani=0.2,
        odul_miktari=100.0,
        ceza_miktari=100.0,
        modulator_ogrenme_orani=0.01,
        geri_bildirim_araligi=0.25,
    ):
        if not 0.0 < float(test_orani) < 1.0:
            raise ValueError("Test oranı 0 ile 1 arasında olmalı.")
        if odul_miktari <= 0 or ceza_miktari <= 0:
            raise ValueError("Ödül ve ceza miktarları pozitif olmalı.")
        if modulator_ogrenme_orani < 0 or geri_bildirim_araligi <= 0:
            raise ValueError("Öğrenme oranı ve feedback aralığı geçersiz.")

        self.seed = seed
        self.test_orani = float(test_orani)
        self.odul_miktari = float(odul_miktari)
        self.ceza_miktari = float(ceza_miktari)
        self.modulator_ogrenme_orani = float(modulator_ogrenme_orani)
        self.geri_bildirim_araligi = float(geri_bildirim_araligi)
        self.temsil = SayisalTemsil()
        self.sol_noronlari = tuple(f"SL{i}" for i in range(1, 10))
        self.sag_noronlari = tuple(f"SR{i}" for i in range(1, 10))
        self.sol_dendritleri = tuple(f"SLD{i}" for i in range(1, 10))
        self.sag_dendritleri = tuple(f"SRD{i}" for i in range(1, 10))
        self.beyin = self._ag_kur()
        self.reseptor = ReseptorOrgan()
        self.motor = MotorOrgan()
        self.sinapslar = tuple(
            sinaps
            for noron in self.beyin.noronlar.values()
            for sinaps in noron.cikis_sinapslari
            if sinaps.hedef is not None
            and sinaps.hedef.kimlik in self.KARAR_NORONLARI
        )
        self.egitim_ornekleri, self.test_ornekleri = self.ornekleri_ayir(
            seed=seed, test_orani=self.test_orani
        )
        self.episode_sayisi = 0

    @staticmethod
    def ornekleri_ayir(seed=0, test_orani=0.2):
        """Aynı sayı çiftinin ters sırası eğitim/test arasında bölünmez."""
        if not 0.0 < float(test_orani) < 1.0:
            raise ValueError("Test oranı 0 ile 1 arasında olmalı.")
        ciftler = [
            (sol, sag)
            for sol in range(1, 10)
            for sag in range(sol + 1, 10)
        ]
        random.Random(seed).shuffle(ciftler)
        test_adedi = max(1, min(len(ciftler) - 1, round(
            len(ciftler) * float(test_orani)
        )))
        test_ciftleri = set(ciftler[:test_adedi])
        egitim = []
        test = []
        for sol, sag in ciftler:
            hedef = test if (sol, sag) in test_ciftleri else egitim
            hedef.extend(((sol, sag), (sag, sol)))
        return tuple(egitim), tuple(test)

    def _ag_kur(self):
        rng = random.Random(self.seed)
        alan = KimyasalAlan()
        beyin = Beyin(kimyasal_alan=alan)
        noronlar = {}

        for i, kimlik in enumerate(self.sol_noronlari):
            noron = Noron(kimlik, konum=(0.0, float(i)))
            noron.dendrit_ekle(Dendrid(self.sol_dendritleri[i]))
            noronlar[kimlik] = noron

        for i, kimlik in enumerate(self.sag_noronlari):
            noron = Noron(kimlik, konum=(10.0, float(i)))
            noron.dendrit_ekle(Dendrid(self.sag_dendritleri[i]))
            noronlar[kimlik] = noron

        karar_konumlari = {
            self.SOL: (5.0, 2.0),
            self.SAG: (5.0, 6.0),
        }
        for kimlik, konum in karar_konumlari.items():
            noron = Noron(kimlik, konum=konum)
            noron.dendrit_ekle(Dendrid(f"{kimlik}:D"))
            noronlar[kimlik] = noron

        # İki duyusal kanal da iki karar nöronuna rastgele işaretli
        # projeksiyon yapar. Bağlantıların yönü/sayısı sayısal etikete bağlı
        # değildir; yalnızca seed ile belirlenen başlangıç rastlantısıdır.
        for kaynak_id in self.sol_noronlari + self.sag_noronlari:
            kaynak = noronlar[kaynak_id]
            dendrit_id = (
                self.sol_dendritleri[int(kaynak_id[2:]) - 1]
                if kaynak_id.startswith("SL")
                else self.sag_dendritleri[int(kaynak_id[2:]) - 1]
            )
            kaynak_dendriti = kaynak.dendritler[dendrit_id]
            for hedef_id in self.KARAR_NORONLARI:
                hedef = noronlar[hedef_id]
                isaret = 1.0 if rng.random() < 0.5 else -1.0
                sinaps = Baglanti(
                    f"{kaynak_id}->{hedef_id}",
                    kaynak,
                    hedef,
                    uzunluk=1.0,
                    hedef_dendrit_id=f"{hedef_id}:D",
                    etki=15.0 * isaret,
                    esik=0.15,
                    sinaptik_agirlik=rng.uniform(0.8, 1.2),
                    hebbian_oran=0.0,
                    stdp_depresyon_oran=0.0,
                    uygunluk_tau=100.0,
                    modulator_ogrenme_orani=self.modulator_ogrenme_orani,
                    terminal_konumu=hedef.konum,
                )
                kaynak_dendriti.sinaps_bagla(sinaps, rng.uniform(0.3, 0.8))
                kaynak.cikis_sinapsi_ekle(sinaps)

        # Karar nöronları arasında genel rekabet: biri ateşlenince diğerini
        # baskılayan sabit karşılıklı inhibisyon. Bu, büyüklük kuralını kodlamaz.
        for kaynak_id, hedef_id in (
            (self.SOL, self.SAG),
            (self.SAG, self.SOL),
        ):
            kaynak = noronlar[kaynak_id]
            sinaps = Baglanti(
                f"{kaynak_id}->{hedef_id}:WTA",
                kaynak,
                noronlar[hedef_id],
                uzunluk=1.0,
                hedef_dendrit_id=f"{hedef_id}:D",
                etki=-20.0,
                esik=0.15,
                hebbian_oran=0.0,
                stdp_depresyon_oran=0.0,
                modulator_ogrenme_orani=0.0,
                terminal_konumu=kaynak.konum,
            )
            kaynak.dendritler[f"{kaynak_id}:D"].sinaps_bagla(sinaps, 0.5)
            kaynak.cikis_sinapsi_ekle(sinaps)

        for noron in noronlar.values():
            beyin.noron_ekle(noron)
        beyin.ag_ozeti = {
            "seed": self.seed,
            "duyusal_noron": 18,
            "karar_noron": 2,
            "rastgele_duyusal_projeksiyon": 36,
            "rekabet_baglantisi": 2,
        }
        return beyin

    @staticmethod
    def _beklenen(sol_sayi, sag_sayi):
        if sol_sayi == sag_sayi:
            raise ValueError("İlk deney yalnızca eşit olmayan sayıları karşılaştırır.")
        return BuyuklukKarsilastirmaDeneyi.SOL if sol_sayi > sag_sayi else BuyuklukKarsilastirmaDeneyi.SAG

    @staticmethod
    def _karar_ver(sol_ates, sag_ates):
        if sol_ates > sag_ates:
            return BuyuklukKarsilastirmaDeneyi.SOL
        if sag_ates > sol_ates:
            return BuyuklukKarsilastirmaDeneyi.SAG
        return None

    def _geri_bildirim_sal(self, dogru, zaman, beklenen, gerceklesen):
        """Görev ortamı, ilgili karar bölgesine yerel kimyasal sinyal bırakır.

        Doğru kararda ödül doğru çıktı bölgesine; yanlış kararda ceza ateşlenen
        yanlış çıktı bölgesine salınır. Böylece modülatör bütün bağlantılara
        eşit dağılmaz; terminal konumundaki yerel alanı Baglanti değerlendirir.
        Karar çıkmadıysa yanlış bir yolu cezalandırmak için kanıt yoktur.
        """
        if gerceklesen is None:
            return None
        hedef = beklenen if dogru else gerceklesen
        tur = "odul" if dogru else "ceza"
        miktar = self.odul_miktari if dogru else self.ceza_miktari
        return self.beyin.kimyasal_alan.sal(
            tur,
            self.beyin.noronlar[hedef].konum,
            miktar,
            zaman,
            yayilim=1.0,
            temizlenme=100.0,
        )

    def episode_calistir(self, sol_sayi, sag_sayi, feedback=True):
        beklenen = self._beklenen(sol_sayi, sag_sayi)
        self.beyin.episode_baslat()
        onceki = {
            kimlik: self.beyin.noronlar[kimlik].ateslenme_sayisi
            for kimlik in self.KARAR_NORONLARI
        }

        girdiler = self.temsil.kodla(
            sol_sayi, self.sol_noronlari, self.sol_dendritleri
        ) + self.temsil.kodla(
            sag_sayi, self.sag_noronlari, self.sag_dendritleri
        )
        self.reseptor.kodla(self.beyin, girdiler)
        islenen = self.beyin.calistir()

        sayilar = self.motor.ateslenme_sayilari_oku(self.beyin, onceki)
        sol_ates = sayilar[self.SOL]
        sag_ates = sayilar[self.SAG]
        gerceklesen = self._karar_ver(sol_ates, sag_ates)

        dogru = gerceklesen == beklenen
        sonuc = {
            "episode": self.episode_sayisi,
            "sol_sayi": sol_sayi,
            "sag_sayi": sag_sayi,
            "beklenen": beklenen,
            "gerceklesen": gerceklesen,
            "sol_ateslenme": sol_ates,
            "sag_ateslenme": sag_ates,
            "dogru": dogru,
            "islenen_olay": islenen,
            "simulasyon_zamani": self.beyin.zaman,
        }
        self.episode_sayisi += 1

        if feedback:
            self._geri_bildirim_sal(
                dogru, self.beyin.zaman, beklenen, gerceklesen
            )
            # Modülatörün aynı örneğin uygunluk izine uygulanmasını sağlar;
            # bir sonraki örneğin etkinlik izleriyle karışmasını önler.
            self.beyin.calistir(
                son_zaman=self.beyin.zaman + self.geri_bildirim_araligi
            )
        return sonuc

    def egit(self, ornekler=None):
        ornekler = self.egitim_ornekleri if ornekler is None else tuple(ornekler)
        return tuple(
            self.episode_calistir(sol, sag, feedback=True)
            for sol, sag in ornekler
        )

    def test_et(self, ornekler=None):
        ornekler = self.test_ornekleri if ornekler is None else tuple(ornekler)
        return tuple(
            self.episode_calistir(sol, sag, feedback=False)
            for sol, sag in ornekler
        )

    @staticmethod
    def ozetle(sonuclar):
        sonuclar = tuple(sonuclar)
        if not sonuclar:
            raise ValueError("Özetlenecek en az bir sonuç gerekli.")
        dogru = sum(sonuc["dogru"] for sonuc in sonuclar)
        return {
            "ornek_sayisi": len(sonuclar),
            "dogru": dogru,
            "yanlis": len(sonuclar) - dogru,
            "dogruluk": dogru / len(sonuclar),
            "iki_cikis_ateslendi": sum(
                sonuc["sol_ateslenme"] > 0 and sonuc["sag_ateslenme"] > 0
                for sonuc in sonuclar
            ),
            "hicbir_cikis_ateslenmedi": sum(
                sonuc["sol_ateslenme"] == 0 and sonuc["sag_ateslenme"] == 0
                for sonuc in sonuclar
            ),
            "karar_olusmadi": sum(
                sonuc["gerceklesen"] is None for sonuc in sonuclar
            ),
        }

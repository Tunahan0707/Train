import copy
import random

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.MotorOrgan import MotorOrgan
from BrainNew.Noron import Noron
from BrainNew.ReseptorOrgan import ReseptorOrgan


class BinaryBuyuklukKarsilastirmaDeneyi:
    """Binary duyusal kodlama ve ara nöron katmanıyla büyüklük karşılaştırması.

    1-9 sayıları dört bit olarak kodlanır. BrainOld'daki gibi sol ve sağ
    operandın her biri dört dendritli bir reseptör nöronuna sunulur. Böylece
    sekiz bit kanalı iki nöronun dendritlerinde temsil edilir. Reseptör
    nöronları doğrudan karar nöronlarına bağlanmaz; 20 ara nörona projekte olur.
    Ara nöronlar iki karar nöronuna projekte olur.

    Duyusal->ara bağlantılar yerel Hebbian/STDP plastisitesine açıktır.
    Ara->karar bağlantıları gecikmiş yerel ödül/ceza modülatörüyle öğrenir.
    Görev ortamı sinaptik parametreleri doğrudan değiştirmez.
    """

    SOL = "SOL_BUYUK"
    SAG = "SAG_BUYUK"
    KARAR_NORONLARI = (SOL, SAG)
    BIT_SAYISI = 4
    ARA_NORON_SAYISI = 20
    ARA_GIRDI_SAYISI = 2

    def __init__(
        self,
        seed=20261121,
        test_orani=0.2,
        odul_miktari=1.0,
        ceza_miktari=1.0,
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

        self.sol_girdi_noronu = "SOL_GIRDI"
        self.sag_girdi_noronu = "SAG_GIRDI"
        self.duyusal_noronlari = (
            self.sol_girdi_noronu, self.sag_girdi_noronu
        )
        self.ara_noronlari = tuple(
            f"ARA{i}" for i in range(self.ARA_NORON_SAYISI)
        )

        self.beyin = self._ag_kur()
        self.reseptor = ReseptorOrgan()
        self.motor = MotorOrgan()
        self.duyusal_ara_sinapslari = tuple(
            sinaps
            for kimlik in self.duyusal_noronlari
            for sinaps in self.beyin.noronlar[kimlik].cikis_sinapslari
        )
        self.ara_karar_sinapslari = tuple(
            sinaps
            for kimlik in self.ara_noronlari
            for sinaps in self.beyin.noronlar[kimlik].cikis_sinapslari
        )
        self.sinapslar = (
            self.duyusal_ara_sinapslari + self.ara_karar_sinapslari
        )
        self.egitim_ornekleri, self.test_ornekleri = self.ornekleri_ayir(
            seed=seed, test_orani=self.test_orani
        )
        self.episode_sayisi = 0

    @staticmethod
    def binary_kodla(sayi):
        """1-9 aralığındaki sayıyı baştaki sıfırları koruyarak dört bite çevirir."""
        if isinstance(sayi, bool) or not isinstance(sayi, int):
            raise TypeError("Sayı tam sayı olmalı.")
        if not 1 <= sayi <= 9:
            raise ValueError("Binary deneyinde sayı 1 ile 9 arasında olmalı.")
        return format(sayi, "04b")

    @classmethod
    def girdi_olaylari_uret(cls, sol_sayi, sag_sayi):
        sol_kod = cls.binary_kodla(sol_sayi)
        sag_kod = cls.binary_kodla(sag_sayi)
        olaylar = []
        for kod, noron_id in (
            (sol_kod, "SOL_GIRDI"),
            (sag_kod, "SAG_GIRDI"),
        ):
            for bit_indeksi, bit in enumerate(kod):
                if bit == "1":
                    olaylar.append(
                        (
                            noron_id,
                            f"{noron_id}:D{bit_indeksi}",
                            100.0,
                            1e-6,
                        )
                    )
        return tuple(olaylar)

    @staticmethod
    def ornekleri_ayir(seed=0, test_orani=0.2):
        """Ters sıralı sayı çiftlerini aynı eğitim/test bölümünde tutar."""
        if not 0.0 < float(test_orani) < 1.0:
            raise ValueError("Test oranı 0 ile 1 arasında olmalı.")
        ciftler = [
            (sol, sag)
            for sol in range(1, 10)
            for sag in range(sol + 1, 10)
        ]
        random.Random(seed).shuffle(ciftler)
        test_adedi = max(
            1,
            min(
                len(ciftler) - 1,
                round(len(ciftler) * float(test_orani)),
            ),
        )
        test_ciftleri = set(ciftler[:test_adedi])
        egitim, test = [], []
        for sol, sag in ciftler:
            hedef = test if (sol, sag) in test_ciftleri else egitim
            hedef.extend(((sol, sag), (sag, sol)))
        return tuple(egitim), tuple(test)

    def _ag_kur(self):
        rng = random.Random(self.seed)
        beyin = Beyin(kimyasal_alan=KimyasalAlan())
        noronlar = {}

        # BrainOld düzeni: iki reseptör nöronu, her birinde dört bit dendriti.
        for i, kimlik in enumerate(self.duyusal_noronlari):
            noron = Noron(kimlik, konum=(0.0, float(i * 5)))
            for bit_indeksi in range(self.BIT_SAYISI):
                noron.dendrit_ekle(
                    Dendrid(f"{kimlik}:D{bit_indeksi}")
                )
            noronlar[kimlik] = noron

        # BrainOld'daki 20 ara nöron fikrini koruyoruz; her biri sol ve sağ
        # reseptörden birer dendritik giriş alır.
        ara_konumlari = {}
        for i, kimlik in enumerate(self.ara_noronlari):
            konum = (5.0, float(i))
            ara_konumlari[kimlik] = konum
            noron = Noron(kimlik, konum=konum)
            for j in range(self.ARA_GIRDI_SAYISI):
                noron.dendrit_ekle(Dendrid(f"{kimlik}:D{j}"))
            noronlar[kimlik] = noron

        karar_konumlari = {
            self.SOL: (10.0, 4.0),
            self.SAG: (10.0, 15.0),
        }
        for kimlik, konum in karar_konumlari.items():
            noron = Noron(kimlik, konum=konum)
            for i in range(self.ARA_NORON_SAYISI):
                noron.dendrit_ekle(Dendrid(f"{kimlik}:D{i}"))
            noronlar[kimlik] = noron

        # Her reseptör nöronundan her ara nörona bir terminal gider.
        # Terminalin potansiyelini dört bit dendritinin ayrı, işaretli
        # katkıları belirler; dolayısıyla bit konumları ayırt edilebilir.
        for kaynak_id in self.duyusal_noronlari:
            kaynak = noronlar[kaynak_id]
            for ara_id in self.ara_noronlari:
                ara = noronlar[ara_id]
                dendrit_indeksi = self.duyusal_noronlari.index(kaynak_id)
                dendrit_id = f"{ara_id}:D{dendrit_indeksi}"
                isaret = 1.0 if rng.random() < 0.5 else -1.0
                sinaps = Baglanti(
                    f"{kaynak_id}->{ara_id}",
                    kaynak,
                    ara,
                    uzunluk=1.0,
                    hedef_dendrit_id=dendrit_id,
                    etki=15.0 * isaret,
                    esik=0.15,
                    sinaptik_agirlik=rng.uniform(0.8, 1.2),
                    hebbian_oran=0.005,
                    stdp_depresyon_oran=0.001,
                    uygunluk_tau=100.0,
                    modulator_ogrenme_orani=0.0,
                    terminal_konumu=ara.konum,
                )
                for dendrit in kaynak.dendritler.values():
                    dendrit.sinaps_bagla(sinaps, rng.uniform(-0.8, 0.8))
                kaynak.cikis_sinapsi_ekle(sinaps)

        # Ara nöronların iki karar popülasyonuna çıkışları rastgele işaretlidir.
        # Her çıkış sinapsı dört dendritin tümünden yerel katkı alır.
        for ara_id in self.ara_noronlari:
            ara = noronlar[ara_id]
            for karar_id in self.KARAR_NORONLARI:
                karar = noronlar[karar_id]
                isaret = 1.0 if rng.random() < 0.5 else -1.0
                sinaps = Baglanti(
                    f"{ara_id}->{karar_id}",
                    ara,
                    karar,
                    uzunluk=1.0,
                    hedef_dendrit_id=f"{karar_id}:D{self.ara_noronlari.index(ara_id)}",
                    etki=15.0 * isaret,
                    esik=0.15,
                    sinaptik_agirlik=rng.uniform(0.8, 1.2),
                    hebbian_oran=0.0,
                    stdp_depresyon_oran=0.0,
                    uygunluk_tau=100.0,
                    modulator_ogrenme_orani=self.modulator_ogrenme_orani,
                    terminal_konumu=karar.konum,
                )
                for dendrit in ara.dendritler.values():
                    dendrit.sinaps_bagla(sinaps, rng.uniform(-0.8, 0.8))
                ara.cikis_sinapsi_ekle(sinaps)

        for noron in noronlar.values():
            beyin.noron_ekle(noron)

        beyin.ag_ozeti = {
            "seed": self.seed,
            "duyusal_noron": len(self.duyusal_noronlari),
            "duyusal_dendrit": len(self.duyusal_noronlari) * self.BIT_SAYISI,
            "ara_noron": len(self.ara_noronlari),
            "karar_noron": len(self.KARAR_NORONLARI),
            "duyusal_ara_baglantisi": len(self.ara_noronlari) * self.ARA_GIRDI_SAYISI,
            "ara_karar_baglantisi": len(self.ara_noronlari) * len(self.KARAR_NORONLARI),
            "dogrudan_duyusal_karar_baglantisi": 0,
        }
        return beyin

    @staticmethod
    def _beklenen(sol_sayi, sag_sayi):
        if sol_sayi == sag_sayi:
            raise ValueError("Deney yalnızca eşit olmayan sayıları karşılaştırır.")
        return (
            BinaryBuyuklukKarsilastirmaDeneyi.SOL
            if sol_sayi > sag_sayi
            else BinaryBuyuklukKarsilastirmaDeneyi.SAG
        )

    @staticmethod
    def _karar_ver(sol_ates, sag_ates):
        if sol_ates > sag_ates:
            return BinaryBuyuklukKarsilastirmaDeneyi.SOL
        if sag_ates > sol_ates:
            return BinaryBuyuklukKarsilastirmaDeneyi.SAG
        return None

    def _geri_bildirim_sal(self, dogru, zaman, beklenen, gerceklesen):
        """Görev ortamı yalnızca ilgili karar bölgesine kimyasal sinyal bırakır."""
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
        sol_kod = self.binary_kodla(sol_sayi)
        sag_kod = self.binary_kodla(sag_sayi)
        self.beyin.episode_baslat()
        onceki = {
            kimlik: self.beyin.noronlar[kimlik].ateslenme_sayisi
            for kimlik in self.KARAR_NORONLARI
        }

        self.reseptor.kodla(
            self.beyin,
            self.girdi_olaylari_uret(sol_sayi, sag_sayi),
        )
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
            "sol_kod": sol_kod,
            "sag_kod": sag_kod,
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
        """Her test örneğini eğitilmiş ağın bağımsız kopyasında değerlendirir.

        Test girdileri birbirlerinin ağırlıklarını değiştiremez. Eğitim sırasında
        kalmış ödül/ceza kaynakları da test kopyasından temizlenir.
        """
        ornekler = self.test_ornekleri if ornekler is None else tuple(ornekler)
        egitilmis_beyin = self.beyin
        sonuclar = []
        try:
            for sol, sag in ornekler:
                self.beyin = copy.deepcopy(egitilmis_beyin)
                self.beyin.kimyasal_alan.kaynaklar.clear()
                sonuclar.append(
                    self.episode_calistir(sol, sag, feedback=False)
                )
        finally:
            self.beyin = egitilmis_beyin
        return tuple(sonuclar)

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

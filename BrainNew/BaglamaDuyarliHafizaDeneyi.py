"""Aynı ipucunun bağlama göre farklı anıları çağırmasını sınar.

A+X -> B,C
A+Y -> D,E

Aynı A ipucu iki bağlam kapısına da düşük şiddetle ulaşır. X yalnızca
Gx kapısına, Y yalnızca Gy kapısına ulaşır. Her iki katkı tek başına
nöron eşiğini aşamaz; birlikte geldiklerinde yerel membran toplamı
kapıyı ateşler. Gx ve Gy'nin çıkış bağlantıları ayrı hedef örüntülerine
önceden kuruludur ve eğitim sırasında yerel Hebbian mekanizmayla güçlenir.

Bu kontrollü deney bağlam seçiciliğini sınar; bağlam kapılarının veya
duyusal bağlantı topolojisinin kendiliğinden öğrenildiğini iddia etmez.
"""

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.DeneySurucusu import DeneyOrnegi
from BrainNew.EgitimSurucusu import EgitimSurucusu
from BrainNew.Noron import Noron


class BaglamaDuyarliHafizaDeneyi:
    BASLANGIC_AGIRLIGI = 0.05
    IPUCU_GECIKMESI = 1e-6
    BAGLAM_GECIKMESI = 2e-6
    OGRETIM_GECIKMESI = 5.0
    ALT_ESIK_GIRDISI = 8.0

    ORUNTU_X = ("Gx", ("B", "C"), "X")
    ORUNTU_Y = ("Gy", ("D", "E"), "Y")

    @classmethod
    def _ag_kur(cls):
        beyin = Beyin()
        noronlar = {
            kimlik: Noron(
                kimlik,
                konum=konum,
                noron_iliski_arama_yaricapi=0.0,
            )
            for kimlik, konum in (
                ("Gx", (0.0, 0.0)),
                ("Gy", (0.0, 2.0)),
                ("B", (2.0, 0.0)),
                ("C", (3.0, 0.0)),
                ("D", (2.0, 2.0)),
                ("E", (3.0, 2.0)),
            )
        }

        dendritler = {}
        for kimlik, noron in noronlar.items():
            dendrit = Dendrid(f"{kimlik}:D")
            noron.dendrit_ekle(dendrit)
            dendritler[kimlik] = dendrit

        sinapslar = {}
        for kapı_id, hedefler, _ in (cls.ORUNTU_X, cls.ORUNTU_Y):
            for hedef_id in hedefler:
                sinaps = Baglanti(
                    f"{kapı_id}->{hedef_id}",
                    noronlar[kapı_id],
                    noronlar[hedef_id],
                    uzunluk=1.0,
                    iletim_hizi=1.0,
                    esik=0.2,
                    etki=100.0,
                    sinaptik_agirlik=cls.BASLANGIC_AGIRLIGI,
                    hebbian_oran=0.5,
                    hedef_dendrit_id=f"{hedef_id}:D",
                    terminal_konumu=noronlar[kapı_id].konum,
                    baslangic_yapisal_olgunluk=1.0,
                )
                dendritler[kapı_id].sinaps_bagla(sinaps, 1.0)
                noronlar[kapı_id].cikis_sinapsi_ekle(sinaps)
                sinapslar[f"{kapı_id}->{hedef_id}"] = sinaps

        for noron in noronlar.values():
            beyin.noron_ekle(noron)

        return beyin, EgitimSurucusu(beyin), sinapslar

    @classmethod
    def _girdiler(cls, baglam=None, tam_oruntu=None, ipucu=True, olcek=1.0, ipucu_olcegi=None, baglam_olcegi=None):
        girdiler = []
        ipucu_olcegi = olcek if ipucu_olcegi is None else ipucu_olcegi
        baglam_olcegi = olcek if baglam_olcegi is None else baglam_olcegi
        if ipucu:
            girdiler.extend((
                ("Gx", "Gx:D", cls.ALT_ESIK_GIRDISI * ipucu_olcegi, cls.IPUCU_GECIKMESI),
                ("Gy", "Gy:D", cls.ALT_ESIK_GIRDISI * ipucu_olcegi, cls.IPUCU_GECIKMESI),
            ))
        if baglam == "X":
            girdiler.append(
                ("Gx", "Gx:D", cls.ALT_ESIK_GIRDISI * baglam_olcegi, cls.BAGLAM_GECIKMESI)
            )
        elif baglam == "Y":
            girdiler.append(
                ("Gy", "Gy:D", cls.ALT_ESIK_GIRDISI * baglam_olcegi, cls.BAGLAM_GECIKMESI)
            )

        if tam_oruntu is not None:
            kapı_id, hedefler, _ = (
                cls.ORUNTU_X if tam_oruntu == "X" else cls.ORUNTU_Y
            )
            girdiler.extend(
                (hedef, f"{hedef}:D", 100.0, cls.OGRETIM_GECIKMESI)
                for hedef in hedefler
            )
        return girdiler

    @classmethod
    def _ornek(cls, kimlik, baglam=None, tam_oruntu=None, ipucu=True, olcek=1.0, ipucu_olcegi=None, baglam_olcegi=None):
        if tam_oruntu is not None:
            secilen_oruntu = tam_oruntu
        elif ipucu and baglam in ("X", "Y"):
            secilen_oruntu = baglam
        else:
            secilen_oruntu = None

        if secilen_oruntu is None:
            beklenen = set()
        else:
            kapı_id, hedefler, _ = (
                cls.ORUNTU_X if secilen_oruntu == "X" else cls.ORUNTU_Y
            )
            beklenen = {kapı_id, *hedefler}
        return DeneyOrnegi(
            kimlik,
            cls._girdiler(
                baglam=baglam, tam_oruntu=tam_oruntu,
                ipucu=ipucu, olcek=olcek,
                ipucu_olcegi=ipucu_olcegi,
                baglam_olcegi=baglam_olcegi,
            ),
            beklenen,
        )

    @classmethod
    def _bozulmus_ornek(cls, kimlik, baglam, rng, gurultu_orani=0.0, eksik_kanal=None):
        """Yalnızca geri çağırma girdilerine gürültü veya kanal kaybı uygular."""
        import math

        if not math.isfinite(gurultu_orani) or gurultu_orani < 0.0:
            raise ValueError("Gürültü oranı sonlu ve negatif olmayan bir sayı olmalı.")
        if eksik_kanal not in (None, "ipucu", "baglam"):
            raise ValueError("Eksik kanal 'ipucu', 'baglam' veya None olmalı.")

        temel = cls._ornek(kimlik, baglam=baglam)
        girdiler = []
        for noron_id, dendrit_id, etki, gecikme in temel.girdiler:
            kanal = (
                "ipucu" if gecikme == cls.IPUCU_GECIKMESI else "baglam"
            )
            if kanal == eksik_kanal:
                continue
            if gurultu_orani:
                etki *= max(0.0, 1.0 + rng.gauss(0.0, gurultu_orani))
            girdiler.append((noron_id, dendrit_id, etki, gecikme))

        beklenen = temel.beklenen_ciktilar if eksik_kanal is None else set()
        return DeneyOrnegi(kimlik, girdiler, beklenen)

    def rastgele_gurultu_taramasi(
        self, gurultu_oranlari=(0.05, 0.10, 0.20), tekrar=20, seed=20261116
    ):
        """Temiz eğitimden sonra duyusal genliklere bağımsız Gauss gürültüsü ekler.

        Gürültü yalnızca geri çağırma ipucu/bağlam girdilerine uygulanır.
        Her tekrar aynı temiz eğitimden başlar; sonuçlar iki bağlam için
        ayrı ayrı tam eşleşme ve yanlış-pozitif sayısıyla raporlanır.
        """
        import math
        import random

        if not isinstance(tekrar, int) or tekrar < 1:
            raise ValueError("Tekrar sayısı pozitif tam sayı olmalı.")
        oranlar = tuple(float(x) for x in gurultu_oranlari)
        if any(not math.isfinite(x) or x < 0.0 for x in oranlar):
            raise ValueError("Gürültü oranları sonlu ve negatif olmayan olmalı.")

        rng = random.Random(seed)
        rapor = {}
        for oran in oranlar:
            baglam_raporu = {}
            for baglam in ("X", "Y"):
                dogru = yanlis_pozitif = toplam_olay = 0
                ornek_sonuclari = []
                for sira in range(tekrar):
                    _, surucu, _ = self._ag_kur()
                    surucu.episode_calistir(
                        self._ornek("gurultu-egitim-X", baglam="X", tam_oruntu="X"),
                        feedback=False,
                    )
                    surucu.episode_calistir(
                        self._ornek("gurultu-egitim-Y", baglam="Y", tam_oruntu="Y"),
                        feedback=False,
                    )
                    ornek = self._bozulmus_ornek(
                        f"gurultulu-geri-cagirma-{baglam}-{oran}-{sira}",
                        baglam, rng, gurultu_orani=oran,
                    )
                    sonuc = surucu.episode_calistir(ornek, feedback=False)
                    dogru += bool(sonuc["dogru"])
                    beklenen = set(sonuc["beklenen"])
                    gerceklesen = set(sonuc["gerceklesen"])
                    yanlis_pozitif += len(gerceklesen - beklenen)
                    toplam_olay += sonuc["islenen_olay"]
                    ornek_sonuclari.append(sonuc)
                baglam_raporu[baglam] = {
                    "dogru": dogru,
                    "toplam": tekrar,
                    "tam_eslesme_orani": dogru / tekrar,
                    "yanlis_pozitif": yanlis_pozitif,
                    "ortalama_islenen_olay": toplam_olay / tekrar,
                    "ornekler": tuple(ornek_sonuclari),
                }
            rapor[oran] = baglam_raporu
        return rapor

    def eksik_kanal_taramasi(self, kanallar=("ipucu", "baglam")):
        """İpucu veya bağlam kanalı tamamen yokken geri çağırmayı ölçer."""
        import random

        rapor = {}
        for kanal in kanallar:
            if kanal not in ("ipucu", "baglam"):
                raise ValueError("Kanal 'ipucu' veya 'baglam' olmalı.")
            baglam_raporu = {}
            for baglam in ("X", "Y"):
                _, surucu, _ = self._ag_kur()
                surucu.episode_calistir(
                    self._ornek("eksik-kanal-egitim-X", baglam="X", tam_oruntu="X"),
                    feedback=False,
                )
                surucu.episode_calistir(
                    self._ornek("eksik-kanal-egitim-Y", baglam="Y", tam_oruntu="Y"),
                    feedback=False,
                )
                ornek = self._bozulmus_ornek(
                    f"eksik-{kanal}-geri-cagirma-{baglam}",
                    baglam, random.Random(0), eksik_kanal=kanal,
                )
                baglam_raporu[baglam] = surucu.episode_calistir(
                    ornek, feedback=False
                )
            rapor[kanal] = baglam_raporu
        return rapor

    def calistir(self):
        """Tek ağda iki bağlamı öğretir ve aynı ipucuyla ayrı ayrı çağırır."""
        _, baseline_surucu, _ = self._ag_kur()
        baseline = {
            "A": baseline_surucu.episode_calistir(
                self._ornek("baseline-A-tek", baglam=None),
                feedback=False,
            ),
            "X": baseline_surucu.episode_calistir(
                self._ornek("baseline-X-tek", baglam="X", ipucu=False),
                feedback=False,
            ),
            "Y": baseline_surucu.episode_calistir(
                self._ornek("baseline-Y-tek", baglam="Y", ipucu=False),
                feedback=False,
            ),
        }

        _, surucu, sinapslar = self._ag_kur()
        baslangic_agirliklari = {
            kimlik: sinaps.sinaptik_agirlik
            for kimlik, sinaps in sinapslar.items()
        }

        egitim_X = surucu.episode_calistir(
            self._ornek("A-arti-X-egitimi", baglam="X", tam_oruntu="X"),
            feedback=False,
        )
        egitim_Y = surucu.episode_calistir(
            self._ornek("A-arti-Y-egitimi", baglam="Y", tam_oruntu="Y"),
            feedback=False,
        )

        geri_cagirma_X = surucu.episode_calistir(
            self._ornek("A-arti-X-geri-cagirma", baglam="X"),
            feedback=False,
        )
        geri_cagirma_Y = surucu.episode_calistir(
            self._ornek("A-arti-Y-geri-cagirma", baglam="Y"),
            feedback=False,
        )

        ogrenilmis_agirliklar = {
            kimlik: sinaps.sinaptik_agirlik
            for kimlik, sinaps in sinapslar.items()
        }
        return {
            "baseline": baseline,
            "egitim_X": egitim_X,
            "egitim_Y": egitim_Y,
            "geri_cagirma_X": geri_cagirma_X,
            "geri_cagirma_Y": geri_cagirma_Y,
            "baslangic_agirliklari": baslangic_agirliklari,
            "ogrenilmis_agirliklar": ogrenilmis_agirliklar,
        }


    def gurultu_taramasi(self, olcekler=(0.90, 0.95, 1.0, 1.05, 1.10)):
        """Eğitimden sonra ipucu/bağlam genliğine duyarlılığı ölçer.

        Her ölçek ve bağlam için ağ baştan kurulur ve aynı iki örüntüyle
        eğitilir. Böylece bir test koşusunun yerel plastisitesi diğer test
        koşusunu etkilemez. Ölçek yalnızca A ipucu ve X/Y bağlam girdilerine
        uygulanır; eğitimdeki hedef nöronların doğrudan öğretim girdileri
        değiştirilmez.
        """
        import math

        rapor = {}
        for olcek in olcekler:
            olcek = float(olcek)
            if not math.isfinite(olcek) or olcek <= 0.0:
                raise ValueError("Gürültü ölçeği sonlu ve pozitif olmalı.")
            baglam_sonuclari = {}
            for baglam in ("X", "Y"):
                _, surucu, _ = self._ag_kur()
                surucu.episode_calistir(
                    self._ornek(
                        f"gurultu-egitim-X-{olcek}",
                        baglam="X", tam_oruntu="X"
                    ),
                    feedback=False,
                )
                surucu.episode_calistir(
                    self._ornek(
                        f"gurultu-egitim-Y-{olcek}",
                        baglam="Y", tam_oruntu="Y"
                    ),
                    feedback=False,
                )
                baglam_sonuclari[baglam] = surucu.episode_calistir(
                    self._ornek(
                        f"gurultu-geri-cagirma-{baglam}-{olcek}",
                        baglam=baglam, olcek=olcek
                    ),
                    feedback=False,
                )
            rapor[olcek] = baglam_sonuclari
        return rapor

    def bagimsiz_genlik_taramasi(
        self,
        olcek_ciftleri=((0.90, 1.0), (1.0, 0.90), (0.90, 0.90), (0.80, 1.0), (1.0, 0.80)),
    ):
        """İpucu ve bağlam kanallarının genlik duyarlılığını ayrı ayrı ölçer.

        Her çift (ipucu ölçeği, bağlam ölçeği) için tek ağ kurulur,
        iki bağlam da aynı ağda eğitilir ve ardından ayrı ayrı geri çağrılır.
        Bu deney rastgele gürültü değil, kanallara bağımsız genlik
        bozulması uygular.
        """
        import math

        rapor = {}
        for ipucu_olcegi, baglam_olcegi in olcek_ciftleri:
            ipucu_olcegi = float(ipucu_olcegi)
            baglam_olcegi = float(baglam_olcegi)
            if (
                not math.isfinite(ipucu_olcegi)
                or not math.isfinite(baglam_olcegi)
                or ipucu_olcegi <= 0.0
                or baglam_olcegi <= 0.0
            ):
                raise ValueError("Genlik ölçekleri sonlu ve pozitif olmalı.")

            _, surucu, _ = self._ag_kur()
            surucu.episode_calistir(
                self._ornek(
                    f"bagimsiz-egitim-X-{ipucu_olcegi}-{baglam_olcegi}",
                    baglam="X", tam_oruntu="X",
                ),
                feedback=False,
            )
            surucu.episode_calistir(
                self._ornek(
                    f"bagimsiz-egitim-Y-{ipucu_olcegi}-{baglam_olcegi}",
                    baglam="Y", tam_oruntu="Y",
                ),
                feedback=False,
            )

            baglam_sonuclari = {}
            for baglam in ("X", "Y"):
                baglam_sonuclari[baglam] = surucu.episode_calistir(
                    self._ornek(
                        f"bagimsiz-geri-cagirma-{baglam}-{ipucu_olcegi}-{baglam_olcegi}",
                        baglam=baglam,
                        ipucu_olcegi=ipucu_olcegi,
                        baglam_olcegi=baglam_olcegi,
                    ),
                    feedback=False,
                )
            rapor[(ipucu_olcegi, baglam_olcegi)] = baglam_sonuclari
        return rapor


if __name__ == "__main__":
    sonuc = BaglamaDuyarliHafizaDeneyi().calistir()
    for ad, kayit in sonuc["baseline"].items():
        print(
            f"baseline_{ad}: dogru={kayit['dogru']} "
            f"beklenen={kayit['beklenen']} "
            f"gerceklesen={kayit['gerceklesen']}"
        )
    for ad in ("egitim_X", "egitim_Y", "geri_cagirma_X", "geri_cagirma_Y"):
        kayit = sonuc[ad]
        print(
            f"{ad}: dogru={kayit['dogru']} "
            f"beklenen={kayit['beklenen']} "
            f"gerceklesen={kayit['gerceklesen']}"
        )
    print("Öğrenilmiş sinaptik ağırlıklar:", sonuc["ogrenilmis_agirliklar"])

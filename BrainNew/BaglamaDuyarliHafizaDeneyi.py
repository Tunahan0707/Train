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
    def _girdiler(cls, baglam=None, tam_oruntu=None):
        girdiler = [
            ("Gx", "Gx:D", cls.ALT_ESIK_GIRDISI, cls.IPUCU_GECIKMESI),
            ("Gy", "Gy:D", cls.ALT_ESIK_GIRDISI, cls.IPUCU_GECIKMESI),
        ]
        if baglam == "X":
            girdiler.append(
                ("Gx", "Gx:D", cls.ALT_ESIK_GIRDISI, cls.BAGLAM_GECIKMESI)
            )
        elif baglam == "Y":
            girdiler.append(
                ("Gy", "Gy:D", cls.ALT_ESIK_GIRDISI, cls.BAGLAM_GECIKMESI)
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
    def _ornek(cls, kimlik, baglam=None, tam_oruntu=None):
        if tam_oruntu is None:
            beklenen = set()
        else:
            kapı_id, hedefler, _ = (
                cls.ORUNTU_X if tam_oruntu == "X" else cls.ORUNTU_Y
            )
            beklenen = {kapı_id, *hedefler}
        return DeneyOrnegi(
            kimlik,
            cls._girdiler(baglam=baglam, tam_oruntu=tam_oruntu),
            beklenen,
        )

    def calistir(self):
        """Tek ağda iki bağlamı öğretir ve aynı ipucuyla ayrı ayrı çağırır."""
        _, baseline_surucu, _ = self._ag_kur()
        baseline = {
            "A": baseline_surucu.episode_calistir(
                self._ornek("baseline-A-tek", baglam=None),
                feedback=False,
            ),
            "X": baseline_surucu.episode_calistir(
                self._ornek("baseline-X-tek", baglam="X"),
                feedback=False,
            ),
            "Y": baseline_surucu.episode_calistir(
                self._ornek("baseline-Y-tek", baglam="Y"),
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

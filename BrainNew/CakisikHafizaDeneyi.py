"""Ortak eleman içeren iki örüntüde geri çağırma ve karışma deneyi.

Öğrenilen örüntüler:
    A -> B, C
    D -> B, E

B iki örüntünün ortak elemanıdır. Deney, A ve D ipuçlarının kendi
özel elemanlarını geri çağırırken diğer örüntünün özel elemanlarını
yanlışlıkla etkinleştirip etkinleştirmediğini ölçer.

Geri çağırma algoritması veya özel örüntü seçici içermez; mevcut yerel
sinaptik öğrenme ve iletim mekanizmalarını kullanır.
"""

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.DeneySurucusu import DeneyOrnegi
from BrainNew.EgitimSurucusu import EgitimSurucusu
from BrainNew.Noron import Noron


class CakisikHafizaDeneyi:
    BASLANGIC_AGIRLIGI = 0.05
    IPUCU_GECIKMESI = 1e-6
    HEDEF_GECIKMESI = 5.0

    ORUNTU_A = ("A", ("B", "C"))
    ORUNTU_D = ("D", ("B", "E"))

    @classmethod
    def _ag_kur(cls):
        beyin = Beyin()
        konumlar = {
            "A": (0.0, 0.0),
            "B": (1.0, 0.0),
            "C": (2.0, 0.0),
            "D": (0.0, 2.0),
            "E": (1.0, 2.0),
        }
        noronlar = {
            kimlik: Noron(
                kimlik,
                konum=konum,
                noron_iliski_arama_yaricapi=0.0,
            )
            for kimlik, konum in konumlar.items()
        }
        dendritler = {}
        for kimlik, noron in noronlar.items():
            dendrit = Dendrid(f"{kimlik}:D")
            noron.dendrit_ekle(dendrit)
            dendritler[kimlik] = dendrit

        sinapslar = {}
        for kaynak_id, hedefler in (
            cls.ORUNTU_A,
            cls.ORUNTU_D,
        ):
            for hedef_id in hedefler:
                sinaps = Baglanti(
                    f"{kaynak_id}->{hedef_id}",
                    noronlar[kaynak_id],
                    noronlar[hedef_id],
                    uzunluk=1.0,
                    iletim_hizi=1.0,
                    esik=0.2,
                    etki=100.0,
                    sinaptik_agirlik=cls.BASLANGIC_AGIRLIGI,
                    hebbian_oran=0.5,
                    hedef_dendrit_id=f"{hedef_id}:D",
                    terminal_konumu=noronlar[kaynak_id].konum,
                    baslangic_yapisal_olgunluk=1.0,
                )
                dendritler[kaynak_id].sinaps_bagla(sinaps, 1.0)
                noronlar[kaynak_id].cikis_sinapsi_ekle(sinaps)
                sinapslar[f"{kaynak_id}->{hedef_id}"] = sinaps

        for noron in noronlar.values():
            beyin.noron_ekle(noron)

        return beyin, EgitimSurucusu(beyin), sinapslar

    @classmethod
    def _oruntu_ornegi(cls, ipucu, hedefler, kimlik):
        girdiler = [
            (ipucu, f"{ipucu}:D", 100.0, cls.IPUCU_GECIKMESI)
        ]
        girdiler.extend(
            (hedef, f"{hedef}:D", 100.0, cls.HEDEF_GECIKMESI)
            for hedef in hedefler
        )
        return DeneyOrnegi(kimlik, girdiler, {ipucu, *hedefler})

    @classmethod
    def _kismi_ipucu(cls, ipucu, hedefler, kimlik):
        return DeneyOrnegi(
            kimlik,
            [(ipucu, f"{ipucu}:D", 100.0, cls.IPUCU_GECIKMESI)],
            {ipucu, *hedefler},
        )

    @classmethod
    def _baseline_olc(cls, ipucu, hedefler):
        _, surucu, _ = cls._ag_kur()
        sonuc = surucu.episode_calistir(
            cls._kismi_ipucu(
                ipucu, hedefler, f"baseline-{ipucu}"
            ),
            feedback=False,
        )
        return sonuc

    def calistir(self):
        """İki örüntüyü aynı ağda öğretir ve ayrı ayrı geri çağırır."""
        baseline_a = self._baseline_olc("A", ("B", "C"))
        baseline_d = self._baseline_olc("D", ("B", "E"))

        beyin, surucu, sinapslar = self._ag_kur()
        baslangic_agirliklari = {
            kimlik: sinaps.sinaptik_agirlik
            for kimlik, sinaps in sinapslar.items()
        }

        egitim_a = surucu.episode_calistir(
            self._oruntu_ornegi("A", ("B", "C"), "oruntu-A-egitimi"),
            feedback=False,
        )
        egitim_d = surucu.episode_calistir(
            self._oruntu_ornegi("D", ("B", "E"), "oruntu-D-egitimi"),
            feedback=False,
        )

        geri_cagirma_a = surucu.episode_calistir(
            self._kismi_ipucu("A", ("B", "C"), "oruntu-A-geri-cagirma"),
            feedback=False,
        )
        geri_cagirma_d = surucu.episode_calistir(
            self._kismi_ipucu("D", ("B", "E"), "oruntu-D-geri-cagirma"),
            feedback=False,
        )

        ogrenilmis_agirliklar = {
            kimlik: sinaps.sinaptik_agirlik
            for kimlik, sinaps in sinapslar.items()
        }
        return {
            "baseline_A": baseline_a,
            "baseline_D": baseline_d,
            "egitim_A": egitim_a,
            "egitim_D": egitim_d,
            "geri_cagirma_A": geri_cagirma_a,
            "geri_cagirma_D": geri_cagirma_d,
            "baslangic_agirliklari": baslangic_agirliklari,
            "ogrenilmis_agirliklar": ogrenilmis_agirliklar,
            "beyin": beyin,
        }


if __name__ == "__main__":
    sonuc = CakisikHafizaDeneyi().calistir()
    for ad in (
        "baseline_A", "baseline_D", "egitim_A", "egitim_D",
        "geri_cagirma_A", "geri_cagirma_D",
    ):
        kayit = sonuc[ad]
        print(
            f"{ad}: dogru={kayit['dogru']} "
            f"beklenen={kayit['beklenen']} "
            f"gerceklesen={kayit['gerceklesen']}"
        )
    print("Öğrenilmiş sinaptik ağırlıklar:", sonuc["ogrenilmis_agirliklar"])

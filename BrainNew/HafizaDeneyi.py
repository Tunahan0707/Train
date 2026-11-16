"""Kısmi ipucuyla yerel ilişkisel geri çağırma için kontrollü deney.

Bu modül örüntü tamamlama algoritması içermez. Zayıf bağlantıların
Hebbian mekanizmayla güçlenmesini ve sonraki episode'da kısmi ipucunun
önceden birlikte sunulmuş nöronları etkinleştirip etkinleştirmediğini ölçer.
"""

from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.DeneySurucusu import DeneyOrnegi
from BrainNew.EgitimSurucusu import EgitimSurucusu
from BrainNew.Noron import Noron


class HafizaDeneyi:
    """Tek ilişkisel örüntü üzerinde baseline, eğitim ve geri çağırma."""

    BASLANGIC_AGIRLIGI = 0.05
    GERI_CAGIRMA_GECIKMESI = 1e-6
    OGRETIM_GECIKMESI = 5.0

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
                ("A", (0.0, 0.0)),
                ("B", (1.0, 0.0)),
                ("C", (0.0, 1.0)),
            )
        }
        dendritler = {}
        for kimlik, noron in noronlar.items():
            dendrit = Dendrid(f"{kimlik}:D")
            noron.dendrit_ekle(dendrit)
            dendritler[kimlik] = dendrit

        sinapslar = {}
        for hedef_id in ("B", "C"):
            sinaps = Baglanti(
                f"A->{hedef_id}",
                noronlar["A"],
                noronlar[hedef_id],
                uzunluk=1.0,
                iletim_hizi=1.0,
                esik=0.2,
                etki=100.0,
                sinaptik_agirlik=cls.BASLANGIC_AGIRLIGI,
                hebbian_oran=0.5,
                hedef_dendrit_id=f"{hedef_id}:D",
                terminal_konumu=noronlar["A"].konum,
                baslangic_yapisal_olgunluk=1.0,
            )
            # A'nın aynı duyusal dendriti iki zayıf çıkış terminalini
            # yerel olarak etkinleştirir. Hedef dendritler yalnızca
            # gerçek sinaptik iletimi alır.
            dendritler["A"].sinaps_bagla(sinaps, 1.0)
            noronlar["A"].cikis_sinapsi_ekle(sinaps)
            sinapslar[hedef_id] = sinaps

        for noron in noronlar.values():
            beyin.noron_ekle(noron)

        return beyin, EgitimSurucusu(beyin), sinapslar

    @classmethod
    def _kismi_ipucu(cls, kimlik):
        return DeneyOrnegi(
            kimlik,
            [("A", "A:D", 100.0, cls.GERI_CAGIRMA_GECIKMESI)],
            {"A", "B", "C"},
        )

    def calistir(self):
        """Aynı öğrenilmiş ağda tam örüntüyü öğretip A ipucuyla geri çağırır.

        Baseline ayrı ve eğitilmemiş bir ağda ölçülür; böylece baseline
        sunumu eğitim ağının izlerini veya parametrelerini değiştiremez.
        """
        baseline_beyin, baseline_surucu, baseline_sinapslar = self._ag_kur()
        baseline = baseline_surucu.episode_calistir(
            self._kismi_ipucu("baseline-kismi-ipucu"),
            feedback=False,
        )

        beyin, surucu, sinapslar = self._ag_kur()
        baslangic_agirliklari = {
            hedef: sinaps.sinaptik_agirlik
            for hedef, sinaps in sinapslar.items()
        }

        tam_oruntu = DeneyOrnegi(
            "tam-oruntu-egitimi",
            [
                ("A", "A:D", 100.0, self.GERI_CAGIRMA_GECIKMESI),
                ("B", "B:D", 100.0, self.OGRETIM_GECIKMESI),
                ("C", "C:D", 100.0, self.OGRETIM_GECIKMESI),
            ],
            {"A", "B", "C"},
        )
        egitim = surucu.episode_calistir(tam_oruntu, feedback=False)

        geri_cagirma = surucu.episode_calistir(
            self._kismi_ipucu("egitim-sonrasi-kismi-ipucu"),
            feedback=False,
        )
        ogrenilmis_agirliklar = {
            hedef: sinaps.sinaptik_agirlik
            for hedef, sinaps in sinapslar.items()
        }

        return {
            "baseline": baseline,
            "egitim": egitim,
            "geri_cagirma": geri_cagirma,
            "baslangic_agirliklari": baslangic_agirliklari,
            "ogrenilmis_agirliklar": ogrenilmis_agirliklar,
            "baseline_agirliklari": {
                hedef: sinaps.sinaptik_agirlik
                for hedef, sinaps in baseline_sinapslar.items()
            },
            "baseline_beyin": baseline_beyin,
            "egitim_beyin": beyin,
        }


if __name__ == "__main__":
    sonuc = HafizaDeneyi().calistir()
    for ad in ("baseline", "egitim", "geri_cagirma"):
        kayit = sonuc[ad]
        print(
            f"{ad}: dogru={kayit['dogru']} "
            f"beklenen={kayit['beklenen']} "
            f"gerceklesen={kayit['gerceklesen']}"
        )
    print("Öğrenilmiş sinaptik ağırlıklar:", sonuc["ogrenilmis_agirliklar"])

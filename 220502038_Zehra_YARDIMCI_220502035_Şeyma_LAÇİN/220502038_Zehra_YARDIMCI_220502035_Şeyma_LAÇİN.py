import csv

# Olaylar dosyasını oku
with open('C:/Users/LENOVO/OneDrive/Masaüstü/Lab 2.Ödev açıklama/olaylar.csv', 'r') as olaylar_file:
    olaylar_reader = csv.DictReader(olaylar_file)
    olaylar_list = list(olaylar_reader)

# Gemiler dosyasını oku
with open('C:/Users/LENOVO/OneDrive/Masaüstü/Lab 2.Ödev açıklama/gemiler.csv', 'r') as gemiler_file:
    gemiler_reader = csv.DictReader(gemiler_file)
    gemiler_list = list(gemiler_reader)


class Liman:
    def __init__(self):
        self.istif_alani_1 = Stack(750)  # İstif Alanı 1
        self.istif_alani_2 = Stack(750)  # İstif Alanı 2
        self.gemi_listesi = []  # Gemilerin tutulacağı liste
        self.tir_listesi = []  # TIR'ların tutulacağı liste
        self.zaman = 0
        self.aktif_gemi = None  # Şu anda yüklenmekte olan gemi

    def limana_tir_ekle(self, tir):
        if tir.ulke in ["Mordor", "Neverland", "Lilliputa", "Oceania"]:
            self.tir_listesi.append(tir)
            self.tir_listesi.sort(key=lambda x: x.plaka)  # Plaka numarasına göre sırala
            print(f"{tir.plaka} plakalı TIR limana eklendi.")
        else:
            print(f"{tir.plaka} plakalı TIR, geçerli bir ülkeden gelmediği için limana eklenemedi.")

    def limana_gemi_ekle(self, gemi):
        if gemi.ulke in ["Mordor", "Neverland", "Lilliputa", "Oceania"]:
            self.gemi_listesi.append(gemi)
            self.gemi_listesi.sort(key=lambda x: x.numara)  # Gemi numarasına göre sırala
            print(f"{gemi.numara} numaralı gemi limana eklendi.")
            self.gemi_listesi.sort(key=lambda x: x.numara)  # Numaraya göre sırala
            self.kontrol_et_ve_isle_gemi_yukleme()

    def tirlari_yukleri_indir(self):
        # TIR'ların yüklerini indir
        tirler_to_unload = sorted(self.tir_listesi, key=lambda x: x.plaka)
        for tir in tirler_to_unload:
            yuk = tir.get_yuk_bilgileri()
            self.istif_alani_1.push(yuk)
            print(f"Geliş Zamanı: {self.zaman}, Tırlar İndiriliyor:")
            print(f"Tır Plakası: {tir.plaka}, İstif Alanı: 1, İndirilen Yük: {yuk['yuk_miktari']} ton")
            print(f"Yüklerin Üstüne {yuk['yuk_miktari']} Ton Yük Eklendi")

            # Yük gemiye yüklenemediyse istif alanında beklet
            if not self.gemilere_yuk_yukle():
                print(f"{tir.plaka} isimli yük uygun gemi bulunmadığından istif alanında bekletiliyor.")

        # TIR listesini temizle
        self.tir_listesi.clear()

        # İndirilen yükleri 1 numaralı istif alanına üst üste yerleştir
        self.istif_alani_1_yerlestir()

    def istif_alani_1_yerlestir(self):
        # İstif Alanı 1'deki yükleri üst üste yerleştir
        temp_stack = Stack(self.istif_alani_1.capacity)
        while not self.istif_alani_1.is_empty():
            yuk = self.istif_alani_1.pop()
            temp_stack.push(yuk)

        while not temp_stack.is_empty():
            yuk = temp_stack.pop()
            self.istif_alani_1.push(yuk)
            self.istif_alani_1.push(yuk)  # Üst üste yerleştirme işlemi

        self.istif_alani_1.is_empty_message()

    def gemilere_yuk_yukle(self):
        if self.aktif_gemi and not self.aktif_gemi.yuk_kapasite_dolu() and not self.istif_alani_1.is_empty():
            gemi = self.aktif_gemi
            while not gemi.yuk_kapasite_dolu() and not self.istif_alani_1.is_empty():
                yuk = self.istif_alani_1.pop()
                # Kontrol: Yük miktarı ve geminin taşıma kapasitesi kontrol ediliyor
                if yuk['yuk_miktari'] <= gemi.kapasite - gemi.yuk_miktari:
                    gemi.gemilere_yuk_yukle(yuk)
                    print(f"{gemi.numara} isimli gemiye {yuk['yuk_miktari']} tonluk yük yüklendi.")
                else:
                    print(f"{gemi.numara} isimli gemiye {yuk['yuk_miktari']} tonluk yük yüklenemedi. Gemi kapasitesi dolu.")
            if gemi.yuk_kapasite_dolu() or self.istif_alani_1.is_empty():
                print(f"{gemi.numara} numaralı gemi yükleme işlemini tamamladı.")
                self.aktif_gemi = None
                self.kontrol_et_ve_isle_gemi_yukleme()

    def kontrol_et_ve_isle(self):
        # İstif alanları, gemi yükleme, bekleme süreleri gibi diğer özel durumları ele al
        self.kontrol_et_ve_isle_istif_alanlari()
        self.kontrol_et_ve_isle_gemi_yukleme()

    def kontrol_et_ve_isle_istif_alanlari(self):
        # İstif alanlarını kontrol et ve gerekirse işlemleri uygula
        if self.istif_alani_1_is_empty():
            print("İstif Alanı 1 boş.")
        elif self.istif_alani_1_is_full():
            print("İstif Alanı 1 dolu. İstif alanı 2'ye yönlendirme yapılabilir.")
            self.yonlendirme_yap()

    def kontrol_et_ve_isle_gemi_yukleme(self):
        # Gemi yükleme özel durumları kontrol et ve gerekirse işlemleri uygula
        if self.gemi_listesi and not self.istif_alani_1.is_empty() and not self.aktif_gemi:
            # Yükleme sırası limandaki en küçük numaralı gemiye geçer
            self.aktif_gemi = self.gemi_listesi.pop(0)
            print(f"Yükleme sırası {self.aktif_gemi.numara} numaralı gemiye geçti.")
            self.gemilere_yuk_yukle()
        else:
            if self.gemi_listesi:
                print("Gemi bekleniyor...")
            if self.istif_alani_1.is_full():
                print("İstif Alanı Dolu. TIR'lar bekleniyor...")

    def yonlendirme_yap(self):
        # İstif alanı 1 doluysa, istif alanı 2'ye yönlendirme yap
        if not self.istif_alani_1_is_empty():
            while not self.istif_alani_1_is_empty():
                yuk = self.istif_alani_1.pop()
                self.istif_alani_2.push(yuk)
                print("İstif Alanı 1'den İstif Alanı 2'ye yönlendirme yapıldı.")

            self.istif_alani_1.is_empty_message()
        else:
            print("İstif Alanı 1 boş, yönlendirme yapılmadı.")
            self.istif_alani_1.is_empty_message()

    def istif_alani_1_is_empty(self):
        return self.istif_alani_1.is_empty()

    def istif_alani_1_is_full(self):
        return self.istif_alani_1.is_full()

    def limani_simule_et(self):
        while self.tir_listesi or self.gemi_listesi:
            # Zamanı ilerlet
            self.zaman += 1

            # Diğer gerekli işlemleri kontrol et ve uygula
            self.kontrol_et_ve_isle()

            # TIR'ları yüklerini indir
            self.tirlari_yukleri_indir()

            # Gemilere yük yüklemeyi kontrol et
            self.gemilere_yuk_yukle()

            # Zaman ilerlet
            self.zaman += 1
            print(f"\nZaman: {self.zaman}")

    def liman_olustur_gemi(self, gemi_row):
        # 'kapasite', '20_ton_adet', '30_ton_adet' ve 'yük_miktarı' değerlerini integer'a çevir
        kapasite = int(gemi_row['kapasite'])
        konteyner_20 = int(gemi_row['20_ton_adet'])
        konteyner_30 = int(gemi_row['30_ton_adet'])
        yuk_miktari = int(gemi_row['yük_miktarı'])

        # Gemilerin kapasitesi kontrol ediliyor
        if kapasite not in [250, 300, 300, 500]:
            raise ValueError("Gemi kapasitesi uygun değil.")

        return Gemi(
            gemi_row['gemi_adi'],
            kapasite,
            gemi_row['gidecek_ülke'],
            konteyner_20,
            konteyner_30,
            yuk_miktari,
            gemi_row['maliyet']
        )

    def liman_olustur_tir(self, tir_row):
        # '20_ton_adet' ve '30_ton_adet' değerlerini integer'a çevir
        konteyner_20 = int(tir_row['20_ton_adet'])
        konteyner_30 = int(tir_row['30_ton_adet'])

        # 'yük_miktarı' değerini integer'a çevir
        yuk_miktari = int(tir_row['yük_miktarı'])

        # TIR'ın kapasitesi kontrol ediliyor
        if konteyner_20 not in [0, 1] or konteyner_30 not in [0, 1]:
            raise ValueError("TIR'ın konteyner kapasitesi uygun değil.")

        # Yuk miktarı uygun mu kontrol et
        if yuk_miktari != 20 * konteyner_20 + 30 * konteyner_30:
            raise ValueError("TIR'ın yük miktarı konteyner kapasiteleri ile uyuşmuyor.")

        return TIR(
            tir_row['maliyet'],
            tir_row['tır_plakası'],
            tir_row['ülke'],
            konteyner_20,
            konteyner_30,
            yuk_miktari
        )

class TIR:
    plaka_sayaci = 1  # TIR plaka sayacı

    def __init__(self, maliyet, tir_plakasi, ulke, konteyner_20, konteyner_30, yuk_miktari):
        # Konteyner kapasiteleri sadece 20 veya 30 ton olabilir
        if konteyner_20 not in [0, 1] or konteyner_30 not in [0, 1]:
            raise ValueError("TIR'ın konteyner kapasitesi uygun değil.")

        # Yuk miktarı uygun mu kontrol et
        if yuk_miktari != 20 * konteyner_20 + 30 * konteyner_30:
            raise ValueError("TIR'ın yük miktarı konteyner kapasiteleri ile uyuşmuyor.")

        self.plaka = f"{str(TIR.plaka_sayaci).zfill(3)}_kostu_{str(TIR.plaka_sayaci).zfill(3)}"
        TIR.plaka_sayaci += 1
        self.ulke = ulke
        self.yuk_miktari = yuk_miktari
        self.maliyet = maliyet
        self.konteyner_20 = konteyner_20
        self.konteyner_30 = konteyner_30

    def get_yuk_bilgileri(self):
        return {
            'plaka': self.plaka,
            'ulke': self.ulke,
            'konteyner_20': self.konteyner_20,
            'konteyner_30': self.konteyner_30,
            'yuk_miktari': self.yuk_miktari,
            'maliyet': self.maliyet
        }


class Gemi:
    def __init__(self, numara, kapasite, ulke, konteyner_20, konteyner_30, yuk_miktari, maliyet):
        self.numara = numara
        self.kapasite = kapasite
        self.ulke = ulke
        self.konteyner_20 = konteyner_20
        self.konteyner_30 = konteyner_30
        self.yuk_miktari = yuk_miktari
        self.maliyet = maliyet

    def get_yuk_bilgileri(self):
        return {
            'numara': self.numara,
            'kapasite': self.kapasite,
            'ulke': self.ulke,
            'konteyner_20': self.konteyner_20,
            'konteyner_30': self.konteyner_30,
            'yuk_miktari': self.yuk_miktari,
            'maliyet': self.maliyet
        }

    def yuk_kapasite_dolu(self):
        return self.yuk_miktari >= self.kapasite

class Stack:
    def __init__(self, capacity):
        self.items = []
        self.capacity = capacity

    def is_empty(self):
        return len(self.items) == 0

    def is_full(self):
        return len(self.items) == self.capacity

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def peek(self):
        if not self.is_empty():
            return self.items[-1]

    def size(self):
        return len(self.items)

    def is_full_message(self):
        if self.is_full():
            print("İstif Alanı Dolu!")

    def is_empty_message(self):
        if self.is_empty():
            print("İstif Alanı Boş!")


# Liman nesnesi oluştur
liman = Liman()

# Limanı simule et
liman.limani_simule_et()


# Liman işlemleri
def liman_islemleri(olay, liman):
    if 'geliş_zamanı' in olay:
        if 'gemi_adi' in olay:
            # Gemi verisi varsa gemi ekleyin
            gemi = liman.liman_olustur_gemi(olay)
            liman.limana_gemi_ekle(gemi)
            print(f"{gemi.numara} numaralı gemi limana geldi.")
        elif 'tır_plakası' in olay:
            # TIR verisi varsa TIR ekleyin
            tir = liman.liman_olustur_tir(olay)
            liman.limana_tir_ekle(tir)
            print(f"{tir.plaka} plakalı TIR limana geldi.")
    else:
        print("Geçersiz olay verisi.")


# Liman sınıfını oluşturma
liman = Liman()

# Ana işlem döngüsü
for index, olay in enumerate(olaylar_list):
    # Liman işlemleri
    liman_islemleri(olay, liman)

    # Limanı simule et
    liman.limani_simule_et()

    # Zaman ilerlemesi
    liman.zaman += 1
    print(f"\nZaman: {liman.zaman}")
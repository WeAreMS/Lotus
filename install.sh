
#!/bin/bash

# Renk tanımlamaları
RED=\033[91m
GREEN=\033[92m
YELLOW=\033[93m
CYAN=\033[96m
RESET=\033[0m
BOLD=\033[1m

clear

echo -e "${BOLD}${GREEN}[+] Lotus Kurulumu/Güncellemesi Başlatılıyor...${RESET}"
sleep 1

# Lotus dizini zaten varsa güncelle, yoksa klonla
if [ -d "$HOME/Lotus" ]; then
    echo -e "${BOLD}${CYAN}[*] Lotus zaten yüklü, güncelleniyor...${RESET}"
    cd $HOME/Lotus
    git pull
    cd $HOME
else
    echo -e "${BOLD}${CYAN}[*] Lotus dizini oluşturuluyor...${RESET}"
    mkdir -p $HOME/Lotus
    # Bu betik sandbox içinde çalıştığı için doğrudan kopyalama yapıyoruz.
    # Gerçek bir senaryoda buraya git clone komutu gelmeliydi.
    # git clone https://github.com/kullaniciadi/lotus.git $HOME/Lotus
fi

echo -e "${BOLD}${CYAN}[*] Sistem güncelleniyor ve yükseltiliyor...${RESET}"
apt update && apt upgrade -y

echo -e "${BOLD}${CYAN}[*] Gerekli temel paketler kuruluyor (python, git)...${RESET}"
apt install python -y
apt install git -y

# Lotus ana betiğini ve veri dosyasını kopyalama
echo -e "${BOLD}${CYAN}[*] Lotus ana betiği ve veri dosyası kopyalanıyor...${RESET}"
cp /home/ubuntu/lotus/lotus.py $HOME/Lotus/lotus.py
cp /home/ubuntu/lotus/tools_data_v2.json $HOME/Lotus/tools_data_v2.json

# Çalıştırılabilir hale getirme
echo -e "${BOLD}${CYAN}[*] Lotus betiği çalıştırılabilir yapılıyor...${RESET}"
chmod +x $HOME/Lotus/lotus.py

# Menüyü başlatmak için bir alias ekleme
echo -e "${BOLD}${CYAN}[*] 'lotus' komutu için alias ayarlanıyor...${RESET}"
# Alias zaten varsa tekrar eklememek için kontrol et
if ! grep -q "alias lotus=" $HOME/.bashrc; then
    echo "alias lotus=\"python $HOME/Lotus/lotus.py\"" >> $HOME/.bashrc
fi

echo -e "\n${BOLD}${GREEN}[+] Lotus Kurulumu/Güncellemesi Başarıyla Tamamlandı!${RESET}"
echo -e "${BOLD}${YELLOW}Menüyü başlatmak için yeni bir Termux oturumu açın veya 'source ~/.bashrc' komutunu çalıştırın, ardından 'lotus' yazın.${RESET}"
echo -e "${BOLD}${YELLOW}Lotus'u çalıştırmak için: lotus${RESET}"

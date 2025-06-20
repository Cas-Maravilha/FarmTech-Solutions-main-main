#!/bin/bash

# FarmTech Solutions - Script de Instalação do Ambiente R
# Este script instala o R e as dependências necessárias para os scripts do módulo climático

# Definir cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

echo -e "${GREEN}=========================================================${NC}"
echo -e "${GREEN}    FarmTech Solutions - Instalação do Ambiente R    ${NC}"
echo -e "${GREEN}=========================================================${NC}"
echo

# Verificar se o script está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Este script precisa ser executado como root (sudo).${NC}"
  echo -e "${YELLOW}Use: sudo $0${NC}"
  exit 1
fi

# Verificar o sistema operacional
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    OS=$(uname -s)
    VER=$(uname -r)
fi

echo -e "${YELLOW}Detectado sistema operacional: $OS $VER${NC}"
echo

# Função para instalar no Ubuntu/Debian
install_ubuntu() {
    echo -e "${GREEN}Atualizando listas de pacotes...${NC}"
    apt-get update

    echo -e "${GREEN}Instalando dependências do sistema...${NC}"
    apt-get install -y --no-install-recommends \
        software-properties-common \
        dirmngr \
        gnupg \
        apt-transport-https \
        ca-certificates

    # Adicionar repositório do R
    echo -e "${GREEN}Adicionando repositório do R...${NC}"
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
    add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"

    # Atualizar novamente
    apt-get update

    # Instalar R
    echo -e "${GREEN}Instalando R...${NC}"
    apt-get install -y r-base r-base-dev

    # Instalar outros pacotes necessários
    echo -e "${GREEN}Instalando dependências adicionais...${NC}"
    apt-get install -y \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        libfontconfig1-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libfreetype6-dev \
        libpng-dev \
        libtiff5-dev \
        libjpeg-dev
}

# Função para instalar no CentOS/RHEL/Fedora
install_redhat() {
    echo -e "${GREEN}Instalando repositórios necessários...${NC}"

    # Verificar se é CentOS/RHEL 8+ ou Fedora
    if [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        if [[ "$VER" == "8"* ]] || [[ "$VER" == "9"* ]]; then
            dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
            dnf config-manager --set-enabled PowerTools || dnf config-manager --set-enabled powertools || :
        else
            yum install -y epel-release
        fi
    elif [[ "$OS" == *"Fedora"* ]]; then
        dnf install -y dnf-plugins-core
    fi

    # Instalar R
    echo -e "${GREEN}Instalando R...${NC}"
    if [[ "$OS" == *"Fedora"* ]]; then
        dnf install -y R
    else
        yum install -y R
    fi

    # Instalar dependências
    echo -e "${GREEN}Instalando dependências adicionais...${NC}"
    if [[ "$OS" == *"Fedora"* ]] || [[ "$VER" == "8"* ]] || [[ "$VER" == "9"* ]]; then
        dnf install -y libcurl-devel openssl-devel libxml2-devel
    else
        yum install -y libcurl-devel openssl-devel libxml2-devel
    fi
}

# Função para instalar em sistemas baseados em Arch
install_arch() {
    echo -e "${GREEN}Atualizando sistema...${NC}"
    pacman -Syu --noconfirm

    echo -e "${GREEN}Instalando R e dependências...${NC}"
    pacman -S --noconfirm r gcc-fortran
}

# Função para instalar em macOS
install_macos() {
    echo -e "${GREEN}Instalando Homebrew (se necessário)...${NC}"
    which brew > /dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    echo -e "${GREEN}Instalando R...${NC}"
    brew install r
}

# Baseado no OS, chamar a função de instalação apropriada
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]] || [[ "$OS" == *"Mint"* ]]; then
    install_ubuntu
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Fedora"* ]]; then
    install_redhat
elif [[ "$OS" == *"Arch"* ]] || [[ "$OS" == *"Manjaro"* ]]; then
    install_arch
elif [[ "$OS" == *"Darwin"* ]] || [[ $(uname -s) == "Darwin" ]]; then
    install_macos
else
    echo -e "${RED}Sistema operacional não suportado: $OS${NC}"
    echo -e "${YELLOW}Por favor, instale o R manualmente:${NC}"
    echo -e "${YELLOW}https://www.r-project.org/about.html${NC}"
    exit 1
fi

# Instalar pacotes R necessários
echo -e "${GREEN}Instalando pacotes R necessários...${NC}"
R --vanilla -e "install.packages(c('httr', 'jsonlite', 'dplyr', 'lubridate', 'crayon'), repos='https://cloud.r-project.org/')"

# Verificar instalação
echo -e "${GREEN}Verificando instalação do R...${NC}"
R --version

# Verificar se o diretório para relatórios climáticos existe
if [ ! -d "relatorios_clima" ]; then
    echo -e "${GREEN}Criando diretório para relatórios climáticos...${NC}"
    mkdir -p relatorios_clima
fi

# Dar permissão de execução aos scripts R
echo -e "${GREEN}Configurando permissões para scripts R...${NC}"
chmod +x clima_api.R
chmod +x integrar_clima_agricultura.R

echo
echo -e "${GREEN}=========================================================${NC}"
echo -e "${GREEN}    Instalação concluída com sucesso!    ${NC}"
echo -e "${GREEN}=========================================================${NC}"
echo
echo -e "${YELLOW}Agora você pode executar os scripts R:${NC}"
echo -e "  ./clima_api.R - Para obter dados meteorológicos"
echo -e "  ./integrar_clima_agricultura.R - Para integrar dados climáticos com dados agrícolas"
echo

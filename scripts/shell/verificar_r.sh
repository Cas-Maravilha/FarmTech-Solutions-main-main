#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Verificando instalação do R...${NC}"

# Verificar se R está instalado
if command -v R &> /dev/null; then
    R_VERSION=$(R --version | head -n 1 | awk '{print $3}')
    echo -e "${GREEN}R encontrado! Versão: ${R_VERSION}${NC}"
else
    echo -e "${RED}R não encontrado no sistema.${NC}"
    echo -e "${YELLOW}Para instalar o R, execute o script de instalação:${NC}"
    echo -e "    sudo ./instalar_ambiente_r.sh"
    exit 1
fi

# Verificar pacotes necessários
echo -e "${YELLOW}Verificando pacotes R necessários...${NC}"

# Criar um script R temporário para verificar pacotes
cat > /tmp/check_packages.R << 'EOF'
required_packages <- c("httr", "jsonlite", "dplyr", "lubridate", "crayon")
installed_packages <- rownames(installed.packages())
missing_packages <- required_packages[!required_packages %in% installed_packages]

if (length(missing_packages) == 0) {
  cat("Todos os pacotes necessários estão instalados!\n")

  # Verificar versões
  for (pkg in required_packages) {
    version <- packageVersion(pkg)
    cat(sprintf("%s: versão %s\n", pkg, version))
  }

  quit(status = 0)
} else {
  cat("Pacotes faltando:\n")
  cat(paste(" -", missing_packages), sep = "\n")
  quit(status = 1)
}
EOF

# Executar o script R
if R --vanilla -q -f /tmp/check_packages.R; then
    echo -e "${GREEN}Verificação de pacotes concluída com sucesso!${NC}"
else
    echo -e "${RED}Alguns pacotes estão faltando.${NC}"
    echo -e "${YELLOW}Para instalar os pacotes necessários, execute:${NC}"
    echo -e "    R -e \"install.packages(c('httr', 'jsonlite', 'dplyr', 'lubridate', 'crayon'))\""
fi

# Verificar arquivos de script R
echo -e "\n${YELLOW}Verificando scripts R...${NC}"
for script in "clima_api.R" "integrar_clima_agricultura.R"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo -e "${GREEN}✓ $script encontrado e executável${NC}"
        else
            echo -e "${YELLOW}✓ $script encontrado, mas não é executável${NC}"
            echo -e "   Para tornar executável: chmod +x $script"
        fi
    else
        echo -e "${RED}✗ $script não encontrado${NC}"
    fi
done

# Verificar diretórios necessários
echo -e "\n${YELLOW}Verificando diretórios necessários...${NC}"
for dir in "relatorios" "relatorios_clima"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ Diretório $dir existe${NC}"
    else
        echo -e "${RED}✗ Diretório $dir não existe${NC}"
        echo -e "   Para criar: mkdir -p $dir"
    fi
done

# Verificar arquivos de dados
echo -e "\n${YELLOW}Verificando arquivos de dados...${NC}"
if [ -f "dados_fazenda.csv" ]; then
    NUM_LINHAS=$(wc -l < dados_fazenda.csv)
    echo -e "${GREEN}✓ dados_fazenda.csv encontrado ($NUM_LINHAS linhas)${NC}"
elif [ -f "dados_fazenda.json" ]; then
    echo -e "${GREEN}✓ dados_fazenda.json encontrado${NC}"
else
    echo -e "${RED}✗ Nenhum arquivo de dados encontrado${NC}"
    echo -e "   O sistema necessita de dados_fazenda.csv ou dados_fazenda.json"
fi

echo -e "\n${GREEN}Verificação concluída!${NC}"

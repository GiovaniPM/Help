#!/bin/bash
# Autor: Hugo Constantinopolos <hugo.constantinopolos@gruporbs.com.br>
# 
# Esse script tem com dependência os seguintes pacotes
#   - curl
#   - jq
# sudo apt-get install curl jq

# Verifica Dependências
echo "Verificando dependências"
# Verifica versão do curl
curl -V | head -n 1 | cut -d' ' -f1-3
if (( $? )); # $? É o retorno de curl -V, qualquer valor diferente de 0 indica um erro
then
	echo "curl não encontrado."
	echo "tente instalar com:"
	echo "Linux:	apt install curl"
	echo "Windows:  choco install curl"
	echo "build abortado."
	exit
fi
# Verifica versão do jq
jq -V
	if (( $? )); # $? É o retorno de jq -V, qualquer valor diferente de 0 indica um erro
then
	echo "jq não encontrado."
	echo "tente instalar com:"
	echo "Linux:	apt install jq"
	echo "Windows:  choco install jq"
	echo "build abortado."
	exit
fi
# Dependências encontradas.
echo "ok"

# Define o job a ser executado
JOB_JENKINS=http://jenkins.corp-app-hlg.rbs.com.br/job/JDE_consulta_web_Deploy
AUTH_TOKEN=build-hlg

# Variaveis de autenticação, podem ser definidas por variaveis de
# ambiente ou diretamente no código
USER=${RBS_USERNAME-$USERNAME}
API_TOKEN=${JENKINS_HLG_API_TOKEN-$API_TOKEN}

echo "Job será executado como $USER"
#echo $API_TOKEN

if [ ! "$API_TOKEN" ] ;
then
	echo "Variavel API_TOKEN não definida."
	echo "build abortado."
	exit
fi

# Executa o build remoto
echo "Iniciando o Job"
curl -sf -o /dev/null -u ${USER}:${API_TOKEN} $JOB_JENKINS/buildWithParameters?token=${AUTH_TOKEN}

if (( $? )); # $? É o retorno de curl, qualquer valor diferente de 0 indica um erro
then
	echo "Erro ao iniciar o JOB!"
	echo "Verifique se o job está configurado para aceitar builds remotos."
	exit
fi
echo -n "Build em execucao"

#Inicia a variavel RUNNING 
RUNNING=$(curl -s -u \
${USER}:${API_TOKEN} $JOB_JENKINS/lastBuild/api/json \
| jq '.building')

# Aguarda a execução do job iniciar
while [ $RUNNING = 'false' ];
do
    echo -n "."
    RUNNING=$(curl -s -u \
    ${USER}:${API_TOKEN} $JOB_JENKINS/lastBuild/api/json \
    | jq '.building')
    sleep 1
done   

# Aguarda o fim da execução do job
while [ $RUNNING = 'true' ];
do
    echo -n "."
    RUNNING=$(curl -s -u \
    ${USER}:${API_TOKEN} $JOB_JENKINS/lastBuild/api/json \
    | jq '.building')
    sleep 1
done
echo "."
echo "Job Encerrado"

# Exibe o Log do Job
curl -s -u ${USER}:${API_TOKEN} $JOB_JENKINS/lastBuild/consoleText

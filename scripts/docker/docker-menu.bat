@echo off
setlocal enabledelayedexpansion
set LOGFILE=%~dp0docker-manutencao.log
set BACKUPDIR=%~dp0backup_docker

:MENU
cls
echo ========================================
echo 🐳 MENU ULTRA TURBINADO DE MANUTENCAO DO DOCKER
echo ========================================
echo.
echo [1] Atualizar todas as imagens Docker
echo [2] Atualizar imagem Docker especifica
echo [3] Backup dos volumes
echo [4] Exportar container para .tar
echo [5] Exibir log de manutencao
echo [6] Exibir logs recentes de containers
echo [7] Limpeza geral do sistema
echo [8] Remocao seletiva por nome
echo [9] Remover containers parados
echo [10] Remover imagens nao utilizadas
echo [11] Remover redes nao utilizadas
echo [12] Remover volumes nao utilizados
echo [13] Ver uso de CPU/memoria em tempo real
echo [14] Verificar uso de disco
echo [15] Sair
echo.
set /p opcao=Escolha uma opcao [1-15]:

if "%opcao%"=="1" goto ATUALIZAR
if "%opcao%"=="2" goto ATUALIZAR_ESPECIFICA
if "%opcao%"=="3" goto BACKUP
if "%opcao%"=="4" goto EXPORTAR
if "%opcao%"=="5" goto LOG
if "%opcao%"=="6" goto LOGSCONTAINER
if "%opcao%"=="7" goto COMPLETO
if "%opcao%"=="8" goto SELETIVO
if "%opcao%"=="9" goto CONTAINERS
if "%opcao%"=="10" goto IMAGENS
if "%opcao%"=="11" goto REDES
if "%opcao%"=="12" goto VOLUMES
if "%opcao%"=="13" goto ESTATISTICAS
if "%opcao%"=="14" goto DISCO
if "%opcao%"=="15" exit
goto MENU

:DISCO
cls
docker system df
pause
goto MENU

:CONTAINERS
cls
docker container prune -f >> %LOGFILE%
powershell -command "&{[System.Windows.Forms.MessageBox]::Show('Containers parados removidos!', 'Alerta Docker')}"
pause
goto MENU

:IMAGENS
cls
docker image prune -f >> %LOGFILE%
pause
goto MENU

:VOLUMES
cls
set /p confirm="Tem certeza que deseja remover volumes nao utilizados? (s/n): "
if /i "%confirm%"=="s" docker volume prune -f >> %LOGFILE%
pause
goto MENU

:COMPLETO
cls
docker system prune -a -f >> %LOGFILE%
powershell -c (New-Object Media.SoundPlayer 'C:\Windows\Media\notify.wav').PlaySync()
pause
goto MENU

:BACKUP
cls
if not exist "%BACKUPDIR%" mkdir "%BACKUPDIR%"
for /f "tokens=*" %%v in ('docker volume ls -q') do (
    docker run --rm -v %%v:/volume -v "%BACKUPDIR%:/backup" alpine tar czf /backup/%%v.tar.gz -C /volume .
    echo Backup do volume %%v concluido >> %LOGFILE%
)
pause
goto MENU

:LOG
cls
type %LOGFILE%
pause
goto MENU

:ATUALIZAR
cls
for /f %%i in ('docker images --format "{{.Repository}}"') do (
    echo Atualizando imagem %%i...
    docker pull %%i >> %LOGFILE%
)
pause
goto MENU

:ESTATISTICAS
cls
docker stats --no-stream
pause
goto MENU

:REDES
cls
docker network prune -f >> %LOGFILE%
pause
goto MENU

:LOGSCONTAINER
cls
for /f %%c in ('docker ps -a -q') do (
    echo --- LOGS do container %%c ---
    docker logs --tail 10 %%c
)
pause
goto MENU

:EXPORTAR
cls
echo 🔍 LISTA DE CONTAINERS DISPONIVEIS PARA EXPORTACAO:
echo -----------------------------------------
docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
echo -----------------------------------------
set /p cid="Informe o ID ou nome do container a exportar: "
docker export %cid% > %cid%-backup.tar
echo Container exportado para %cid%-backup.tar >> %LOGFILE%
pause
goto MENU

:SELETIVO
cls
set /p alvo="Informe o nome do container/imagem/volume a remover: "
echo [1] Remover Container
echo [2] Remover Imagem
echo [3] Remover Volume
set /p tipo="Escolha o tipo [1-3]: "
if "%tipo%"=="1" docker rm -f %alvo% >> %LOGFILE%
if "%tipo%"=="2" docker rmi %alvo% >> %LOGFILE%
if "%tipo%"=="3" docker volume rm %alvo% >> %LOGFILE%
pause
goto MENU

:ATUALIZAR_ESPECIFICA
cls
echo 🔍 IMAGENS DISPONIVEIS PARA ATUALIZACAO:
echo -----------------------------------------
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"
echo -----------------------------------------
set /p imagem="Informe o nome da imagem que deseja atualizar (ex: nginx, ubuntu): "
docker pull %imagem% >> %LOGFILE%
echo Imagem %imagem% atualizada com sucesso! >> %LOGFILE%
pause
goto MENU
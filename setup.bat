@echo off
title DocIntellect RPA - Setup
echo ============================================
echo  DocIntellect RPA - Instalacao
echo ============================================
echo.

:: Checa Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.12+ em python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado

:: Instala dependencias do projeto
echo.
echo Instalando dependencias...
python -m pip install -e ".[dev,ocr,nlp,ui]" -q
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

:: Cria .env se nao existir
if not exist .env (
    copy .env.example .env >nul
    echo [OK] .env criado a partir de .env.example
)

:: Cria pastas necessarias
if not exist data mkdir data >nul
if not exist logs mkdir logs >nul

:: Tenta baixar dados de idioma do Tesseract
echo.
set /p INSTALL_TESSDATA="Deseja baixar o idioma 'por' para o Tesseract? (S/N) [S]: "
if /i "%INSTALL_TESSDATA%" neq "N" (
    echo Baixando idioma portugues do Tesseract...
    if not exist "%USERPROFILE%\tessdata" mkdir "%USERPROFILE%\tessdata"
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata' -OutFile \"$env:USERPROFILE\tessdata\por.traineddata\" -UseBasicParsing"
    if exist "%USERPROFILE%\tessdata\por.traineddata" (
        echo [OK] Idioma 'por' baixado para %USERPROFILE%\tessdata
        echo Lembre-se de ajustar TESSDATA_PREFIX no .env
    ) else (
        echo [AVISO] Nao foi possivel baixar. Execute manualmente ou configure TESSDATA_PREFIX
    )
)

:: Tenta instalar Tesseract OCR via winget
echo.
set /p INSTALL_TESSERACT="Deseja instalar Tesseract OCR via winget? (S/N) [S]: "
if /i "%INSTALL_TESSERACT%" neq "N" (
    echo Instalando Tesseract OCR...
    winget install --id UB-Mannheim.TesseractOCR -e --silent >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Tesseract OCR instalado
    ) else (
        echo [AVISO] Falha ao instalar via winget. Baixe manualmente de github.com/UB-Mannheim/tesseract/wiki
    )
)

echo.
echo ============================================
echo  Instalacao concluida!
echo ============================================
echo.
echo  Para iniciar o projeto:
echo    python run.py
echo.
echo  Ou separadamente:
echo    python run.py --no-ui    (só a API)
echo    python run.py --no-api   (só a UI)
echo.
echo  Documentacao da API: http://127.0.0.1:8000/docs
echo  Interface grafica:   http://127.0.0.1:8501
echo.
pause

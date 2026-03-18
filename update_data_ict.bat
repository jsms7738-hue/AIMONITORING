@echo off
chcp 65001 > nul
echo ============================================
3: echo  ICT 데이터 및 대시보드 업데이트 시작
echo ============================================
echo.

cd /d "c:\Users\yoonh\Desktop\AI\ICT데이타"

echo [1/2] Excel 데이터 읽는 중 (CREATE_TIME 기준 분류)...
python extract_data.py
if %errorlevel% neq 0 (
    echo.
    echo [오류] 데이터 추출에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo [2/2] 대시보드 HTML 파일 생성 중...
python build_dashboard.py
if %errorlevel% neq 0 (
    echo.
    echo [오류] 대시보드 생성에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  업데이트 완료! 브라우저에서 새로고침하세요.
echo ============================================
echo.
timeout /t 3

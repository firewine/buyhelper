# 11번가 구매 도우미 스크립트

개인 사용자를 위한 **반자동 구매 도우미**입니다.

- 구매 버튼 오픈 감지 후 즉시 클릭
- 용도 선택(아무거나), 11pay, 롯데카드, 20개월 할부 클릭 시도
- 기본값은 **최종 결제 직전에서 멈춤** (`--auto-submit` 없을 때)

> 주의: 사이트 약관/법을 준수해서 사용하세요. 본 스크립트는 로그인/보안문자 우회 기능이 없습니다.

## 1) 설치 (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install playwright
playwright install chromium
```

## 2) 실행 예시

### Edge 권장
```powershell
python purchase_helper.py --url "https://www.11st.co.kr/products/8237180966" --browser edge
```

### Chrome 사용
```powershell
python purchase_helper.py --url "https://www.11st.co.kr/products/8237180966" --browser chrome
```

### 최종 결제까지 자동 클릭
```powershell
python purchase_helper.py --url "https://www.11st.co.kr/products/8237180966" --browser edge --auto-submit
```

## 3) 옵션

- `--poll-ms` : 구매 버튼 재확인 주기 (기본 150ms)
- `--timeout-ms` : 클릭/탐색 타임아웃 (기본 3000ms)
- `--user-data-dir` : 브라우저 프로필 경로 (로그인 유지)

## 4) 셀렉터 커스터마이징

11번가 UI 변경 시 `purchase_helper.py`의 `Selectors` 값을 조정하세요.


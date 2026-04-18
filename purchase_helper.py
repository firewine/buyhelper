#!/usr/bin/env python3
"""11번가 구매 도우미 (Windows/Chromium).

주의:
- 본 스크립트는 개인 사용의 '도우미' 용도입니다.
- 로그인 우회, CAPTCHA 우회, 대량 계정/대량 구매 등의 기능은 포함하지 않습니다.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


@dataclass
class Selectors:
    buy_button: str = 'button:has-text("구매"), button:has-text("바로구매")'
    purpose_any: str = 'text=개인사용, text=기타, [data-purpose="personal"]'
    pay_11: str = 'text=11pay, text=11번가페이'
    card_lotte: str = 'text=롯데카드, text=롯데'
    installment_dropdown: str = '[aria-label*="할부"], select[name*="install"]'
    installment_20: str = 'text=20개월'
    final_submit: str = 'button:has-text("결제하기"), button:has-text("주문하기")'


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="11번가 구매 도우미")
    parser.add_argument("--url", required=True, help="상품 URL")
    parser.add_argument("--browser", choices=["chrome", "edge"], default="edge")
    parser.add_argument(
        "--poll-ms", type=int, default=150, help="구매 버튼 재확인 간격(ms)"
    )
    parser.add_argument(
        "--timeout-ms", type=int, default=3000, help="클릭/탐색 타임아웃(ms)"
    )
    parser.add_argument(
        "--auto-submit",
        action="store_true",
        help="최종 결제 버튼까지 자동 클릭 (기본: 직전에서 멈춤)",
    )
    parser.add_argument(
        "--user-data-dir",
        default=os.path.join(os.getcwd(), "pw-user-data"),
        help="브라우저 프로필 경로 (로그인 유지용)",
    )
    return parser


def wait_and_click(page, selector: str, timeout_ms: int, name: str) -> bool:
    try:
        locator = page.locator(selector).first
        locator.wait_for(state="visible", timeout=timeout_ms)
        locator.click(timeout=timeout_ms)
        logging.info("클릭 성공: %s", name)
        return True
    except PlaywrightTimeoutError:
        logging.warning("클릭 실패(타임아웃): %s", name)
        return False


def wait_buy_open(page, selector: str, poll_ms: int, timeout_ms: int) -> None:
    start = time.time()
    while True:
        btn = page.locator(selector).first
        try:
            if btn.is_visible(timeout=300):
                disabled = btn.is_disabled()
                if not disabled:
                    elapsed = int((time.time() - start) * 1000)
                    logging.info("구매 가능 감지: %sms", elapsed)
                    btn.click(timeout=timeout_ms)
                    logging.info("구매 버튼 클릭 완료")
                    return
        except PlaywrightTimeoutError:
            pass

        page.wait_for_timeout(poll_ms)
        try:
            page.reload(wait_until="domcontentloaded", timeout=timeout_ms)
        except PlaywrightTimeoutError:
            logging.warning("페이지 reload 타임아웃, 다음 루프로 진행")


def select_installment_20(page, selectors: Selectors, timeout_ms: int) -> bool:
    dropdown = page.locator(selectors.installment_dropdown).first
    try:
        dropdown.wait_for(state="visible", timeout=timeout_ms)
        dropdown.click(timeout=timeout_ms)
    except PlaywrightTimeoutError:
        logging.warning("할부 드롭다운 미노출")
        return False

    return wait_and_click(page, selectors.installment_20, timeout_ms, "20개월 할부")


def run(args: argparse.Namespace) -> int:
    selectors = Selectors()

    channel = "msedge" if args.browser == "edge" else "chrome"
    logging.info("브라우저: %s", channel)
    logging.info("프로필: %s", args.user_data_dir)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=args.user_data_dir,
            channel=channel,
            headless=False,
            viewport={"width": 1380, "height": 900},
        )
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout_ms)

        logging.info("로그인 상태/결제 인증수단은 미리 준비해두세요.")

        wait_buy_open(
            page,
            selectors.buy_button,
            poll_ms=args.poll_ms,
            timeout_ms=args.timeout_ms,
        )

        wait_and_click(page, selectors.purpose_any, args.timeout_ms, "용도 선택")
        wait_and_click(page, selectors.pay_11, args.timeout_ms, "11pay 선택")
        wait_and_click(page, selectors.card_lotte, args.timeout_ms, "롯데카드 선택")
        select_installment_20(page, selectors, args.timeout_ms)

        if args.auto_submit:
            wait_and_click(page, selectors.final_submit, args.timeout_ms, "최종 결제")
            logging.info("auto-submit=true: 최종 결제 클릭 시도 완료")
        else:
            logging.info("auto-submit=false: 최종 결제 직전에서 멈춤")

        logging.info("종료하려면 브라우저를 닫거나 Ctrl+C를 누르세요.")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            context.close()

    return 0


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = build_parser()
    args = parser.parse_args()

    if args.poll_ms < 50:
        logging.warning("poll-ms 50 미만은 차단/오탐 가능성이 있어 권장하지 않습니다.")

    if not args.url.startswith("http"):
        logging.error("--url 은 http(s) URL 이어야 합니다.")
        return 2

    return run(args)


if __name__ == "__main__":
    sys.exit(main())

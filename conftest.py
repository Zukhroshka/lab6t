import os
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def _create_chrome_driver():
    chrome_options = Options()

    # переключатель headless через переменную окружения или флаг pytest
    if os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes"):
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # отключаем уведомления и прочее
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.implicitly_wait(10)
    return driver


@pytest.fixture(scope="function")
def browser(request):
    driver = _create_chrome_driver()
    yield driver

    # если тест упал — можно сохранить скриншот (pytest hook ниже тоже доступен)
    try:
        driver.quit()
    except Exception:
        pass


# hook: attach screenshot on failure
def pytest_exception_interact(node, call, report):
    # не всегда вызывается; оставляем для совместимости
    pass


# альтернативный способ — использовать встроенный hook для каждого теста:
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # выполняем тест и получаем результат
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        # пытаемся получить fixture 'browser'
        browser = item.funcargs.get("browser")
        if browser:
            try:
                png = browser.get_screenshot_as_png()
                allure.attach(png, name="screenshot_on_failure", attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass


@pytest.fixture
def base_url():
    return "https://ya.ru"

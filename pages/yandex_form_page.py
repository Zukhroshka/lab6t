from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


class YandexFormPage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # локаторы
    SEARCH_INPUT = (By.ID, "text")
    SUGGEST_LIST = (By.CSS_SELECTOR, ".mini-suggest__popup-content")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SEARCH_RESULTS = (By.CSS_SELECTOR, "#search-result .serp-item")
    RESULT_LINKS = (By.CSS_SELECTOR, "#search-result .serp-item a")

    def open_page(self, url):
        """Открыть указанный URL"""
        self.driver.get(url)
        return self

    def enter_search_text(self, text):
        """Ввести текст в поисковую строку"""
        search_input = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        search_input.clear()
        search_input.send_keys(text)
        return self

    def wait_for_suggest(self):
        """Дождаться появления списка подсказок"""
        self.wait.until(EC.visibility_of_element_located(self.SUGGEST_LIST))
        return self

    def click_search_button(self):
        """Нажать кнопку поиска"""
        btn = self.wait.until(EC.element_to_be_clickable(self.SEARCH_BUTTON))
        btn.click()
        return self

    def wait_for_search_results(self):
        """Дождаться появления результатов поиска"""
        self.wait.until(EC.presence_of_all_elements_located(self.SEARCH_RESULTS))
        return self

    def get_first_result_text(self):
        """
        Найти первый нормальный результат (не блок Алисы и не быстрый ответ).
        Возвращает текст ссылки первого подходящего результата.
        """
        try:
            results = self.wait.until(EC.presence_of_all_elements_located(self.SEARCH_RESULTS))
        except TimeoutException:
            return None

        for res in results:
            try:
                text = res.text.strip()
            except StaleElementReferenceException:
                continue

            if not text:
                continue

            low = text.lower()
            # Пропускаем "Алису" и инфоблоки
            if low.startswith("алиса") or "на основе источников" in low:
                continue

            # Пытаемся взять заголовок ссылки (если есть)
            try:
                link_el = res.find_element(By.CSS_SELECTOR, "a")
                link_text = link_el.text.strip()
                if link_text:
                    return link_text
            except Exception:
                pass

            # Если ссылки нет — возвращаем весь текст
            return text

        # fallback — ничего не нашли
        return None

    def perform_search(self, search_text):
        """Полный цикл поиска"""
        (
            self.enter_search_text(search_text)
                .wait_for_suggest()
                .click_search_button()
                .wait_for_search_results()
        )
        return self

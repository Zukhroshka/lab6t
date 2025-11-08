import pytest
import allure
import re
from selenium.common.exceptions import TimeoutException
from pages.yandex_form_page import YandexFormPage


@allure.suite("Тестирование поиска Яндекс")
class TestYandexSearch:

    @allure.title("Тест поиска и проверки результатов")
    @allure.description("Этот тест проверяет, что поиск на Яндексе возвращает корректные результаты.")
    @pytest.mark.parametrize("search_query,expected_text", [
        ("Selenium WebDriver", "Selenium"),
        ("Python автоматизация тестирования", "Python"),
        ("Тестирование программного обеспечения", "тестирование"),
    ])
    def test_yandex_search_functionality(self, browser, base_url, search_query, expected_text):
        """Проверяет, что первый результат поиска содержит ожидаемое слово"""
        form_page = YandexFormPage(browser)

        with allure.step("Открыть главную страницу Яндекс"):
            form_page.open_page(base_url)

        with allure.step(f"Выполнить поиск запроса: {search_query}"):
            form_page.perform_search(search_query)

        with allure.step("Проверить наличие результатов поиска"):
            try:
                first_result = form_page.get_first_result_text()
            except TimeoutException:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="timeout_error_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
                pytest.fail("Не удалось дождаться результатов поиска (TimeoutException)")

            assert first_result, "Результаты поиска не отобразились"

            result_lower = first_result.lower()
            expected_lower = expected_text.lower()

            # --- Проверка по корню слова, чтобы избежать проблем с окончаниями ---
            min_len = max(4, len(expected_lower) // 2)
            pattern = rf"{re.escape(expected_lower[:min_len])}\w*"
            match = re.search(pattern, result_lower)

            if not match:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="failed_result_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
                allure.attach(first_result, name="Текст результата", attachment_type=allure.attachment_type.TEXT)
                pytest.fail(f"Ожидаемый текст '{expected_text}' не найден в результате: '{first_result}'")

    @allure.title("Тест отображения подсказок при вводе")
    def test_suggest_display(self, browser, base_url):
        """Проверяет появление списка подсказок при вводе текста"""
        form_page = YandexFormPage(browser)

        with allure.step("Открыть главную страницу Яндекс"):
            form_page.open_page(base_url)

        with allure.step("Ввести текст в поисковую строку"):
            form_page.enter_search_text("автоматизация тестирования")

        with allure.step("Проверить, что подсказки отображаются"):
            form_page.wait_for_suggest()

    @allure.title("Тест очистки поисковой строки")
    def test_search_input_clear(self, browser, base_url):
        """Проверяет, что поле поиска можно очистить"""
        form_page = YandexFormPage(browser)

        with allure.step("Открыть главную страницу Яндекс"):
            form_page.open_page(base_url)

        with allure.step("Ввести текст и очистить поле"):
            form_page.enter_search_text("текст для очистки")
            search_input = browser.find_element(*form_page.SEARCH_INPUT)
            search_input.clear()
            value_after_clear = search_input.get_attribute("value")

        with allure.step("Проверить, что поле очищено"):
            assert value_after_clear == "", f"Поле не очищено, значение: '{value_after_clear}'"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])

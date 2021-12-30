import pytest
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time


@pytest.fixture(scope="class")
def browser():
    browser = Chrome()
    browser.implicitly_wait(10)
    yield browser
    browser.quit()


class YandexSearchPage:
    URL = "https://yandex.ru"

    def __init__(self, browser):
        self.browser = browser

    def load(self):
        self.browser.get(self.URL)

    def is_element_present(self, how, what):
        try:
            self.browser.find_element(how, what)
        except NoSuchElementException:
            return False
        return True

    def select(self, how, what):
        return self.browser.find_element(how, what)

    def enter_request(self, request):
        search_panel = self.browser.find_element(By.ID, 'text')
        search_panel.send_keys(request)

    def press_key(self, key):
        actions = ActionChains(self.browser)
        actions.send_keys(key)
        actions.perform()


class TestSearchInYandex:

    def test_is_search_panel_present(self, browser):
        search_page = YandexSearchPage(browser)
        search_page.load()
        assert search_page.is_element_present(By.ID, 'text'), 'Панели поиска нет на странице'

    def test_is_suggest_bar_visible(self, browser):
        search_page = YandexSearchPage(browser)
        search_page.enter_request('тензор')
        time.sleep(0.5)
        suggest_popup = search_page.select(By.CSS_SELECTOR, 'div.mini-suggest__popup')
        assert suggest_popup.is_displayed(), 'Таблица с подсказками не отображается'

    def test_is_table_of_results_loaded(self, browser):
        search_page = YandexSearchPage(browser)
        search_page.press_key(Keys.ENTER)
        assert 'тензор' in browser.title, 'Страница с результатами поиска не загрузилась'

    def test_is_five_first_links_lead_to_tensor_ru(self, browser):
        results = browser.find_elements_by_xpath('//div[contains(@class,"Path")]/a')
        for i in range(5):
            url = results[i].get_attribute('href')
            assert 'tensor.ru' in url, f"В первых пяти результатах поиска есть ссылка, не ведущая на tensor.ru. \
            Это результат номер {i + 1}, ссылка ведёт на {url}"


class TestImagesInYandex:

    def test_is_images_button_present(self, browser):
        search_page = YandexSearchPage(browser)
        search_page.load()
        assert search_page.is_element_present(By.CSS_SELECTOR,
                                              '[data-id="images"]'), 'Кнопка "Картинки" не отображается'

    def test_is_yandex_ru_images_loaded(self, browser):
        search_page = YandexSearchPage(browser)
        images_button = search_page.select(By.CSS_SELECTOR, '[data-id="images"]')
        images_button.click()
        browser.switch_to.window(browser.window_handles[1])
        current_url = browser.current_url
        assert 'https://yandex.ru/images/' in current_url, 'Страница Яндекс.Картинки не открылась'

    def test_is_first_category_loaded(self, browser):
        search_page = YandexSearchPage(browser)
        first_category = search_page.select(By.CSS_SELECTOR, 'div.PopularRequestList div:first-child')
        first_category_text = first_category.text
        first_category.click()
        first_image = search_page.select(By.CSS_SELECTOR, '[class="serp-item__thumb justifier__thumb"]')
        global first_image_url
        first_image_url = first_image.get_attribute('src')
        first_image.click()
        assert first_category_text in browser.title, 'Заголовок открытой страницы не совпадает с названием категории'

    def test_is_second_image_not_coincides_with_the_first_image(self, browser):
        search_page = YandexSearchPage(browser)
        search_page.press_key(Keys.ARROW_RIGHT)
        second_image = search_page.select(By.CSS_SELECTOR, '[class="serp-item__thumb justifier__thumb"]')
        second_image_url = second_image.get_attribute('src')
        assert first_image_url == second_image_url, 'Первая картинка совпадает со второй'

    def test_is_first_image_coincides_with_previous_to_the_second_image(self, browser):
        search_page = YandexSearchPage(browser)
        search_page.press_key(Keys.ARROW_LEFT)
        new_image = search_page.select(By.CSS_SELECTOR, '[class="serp-item__thumb justifier__thumb"]')
        new_image_url = new_image.get_attribute('src')
        assert first_image_url == new_image_url, 'Первая картинка отличается от предыдущей для второй картинки'

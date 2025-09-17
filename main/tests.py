from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from .models import News


class FootballNewsFunctionalTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()
        cls.browser.implicitly_wait(5)  # wait global

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        # create user for testing
        self.test_user = User.objects.create_user(
            username="testadmin",
            password="testpassword"
        )

    def tearDown(self):
        # bersihkan state browser
        self.browser.delete_all_cookies()
        self.browser.execute_script("window.localStorage.clear();")
        self.browser.execute_script("window.sessionStorage.clear();")
        self.browser.get("about:blank")

    def login_user(self):
        """Helper untuk login"""
        self.browser.get(f"{self.live_server_url}/login/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("testadmin")
        password_input.send_keys("testpassword")
        password_input.submit()

        # tunggu homepage muncul
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Football News")
        )

    def test_login_page(self):
        self.login_user()

        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Football News")

        # cek logout button/link
        logout_btn = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
        self.assertTrue(logout_btn.is_displayed())

    def test_register_page(self):
        self.browser.get(f"{self.live_server_url}/register/")

        # pastikan register page terbuka
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Register")

        # isi form register
        username_input = self.browser.find_element(By.NAME, "username")
        password1_input = self.browser.find_element(By.NAME, "password1")
        password2_input = self.browser.find_element(By.NAME, "password2")

        username_input.send_keys("newuser")
        password1_input.send_keys("complexpass123")
        password2_input.send_keys("complexpass123")
        password2_input.submit()

        # tunggu redirect ke login
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login")
        )
        login_h1 = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(login_h1.text, "Login")

    def test_create_news(self):
        self.login_user()

        # klik Add News
        add_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Add News"))
        )
        add_button.click()

        # isi form
        title_input = self.browser.find_element(By.NAME, "title")
        content_input = self.browser.find_element(By.NAME, "content")
        category_select = Select(self.browser.find_element(By.NAME, "category"))
        thumbnail_input = self.browser.find_element(By.NAME, "thumbnail")
        is_featured_checkbox = self.browser.find_element(By.NAME, "is_featured")

        title_input.send_keys("Test News Title")
        content_input.send_keys("Test news content for selenium testing")
        thumbnail_input.send_keys("https://example.com/image.jpg")
        category_select.select_by_value("match")
        is_featured_checkbox.click()

        # submit
        title_input.submit()

        # cek kembali ke homepage
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Football News")
        )
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Football News")

        # cek berita tampil
        news_title = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Test News Title"))
        )
        self.assertTrue(news_title.is_displayed())

    def test_news_detail(self):
        self.login_user()

        # buat news manual
        news = News.objects.create(
            title="Detail Test News",
            content="Content for detail testing",
            user=self.test_user
        )

        # buka halaman detail
        self.browser.get(f"{self.live_server_url}/news/{news.id}/")

        # cek konten tampil
        self.assertIn("Detail Test News", self.browser.page_source)
        self.assertIn("Content for detail testing", self.browser.page_source)

    def test_logout(self):
        self.login_user()

        logout_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
        logout_button.click()

        # cek redirect ke login
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login")
        )
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Login")

    def test_filter_main_page(self):
        # buat 2 berita
        News.objects.create(
            title="My Test News",
            content="My news content",
            user=self.test_user
        )
        News.objects.create(
            title="Other User News",
            content="Other content",
            user=self.test_user
        )

        self.login_user()

        # klik All Articles
        all_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "All Articles"))
        )
        all_button.click()
        self.assertIn("My Test News", self.browser.page_source)
        self.assertIn("Other User News", self.browser.page_source)

        # klik My Articles
        my_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "My Articles")
        my_button.click()
        self.assertIn("My Test News", self.browser.page_source)

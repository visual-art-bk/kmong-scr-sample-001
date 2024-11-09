import sys
import traceback
from PyQt5 import QtWidgets, QtGui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


class CrawlerUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.results = []
        self.error_occurred = False

    def initUI(self):
        self.setWindowTitle("Tistory Blog Crawler")
        layout = QtWidgets.QVBoxLayout()

        # URL 입력창
        self.url_label = QtWidgets.QLabel("크롤링할 티스토리 블로그 URL 입력:")
        layout.addWidget(self.url_label)
        self.url_input = QtWidgets.QLineEdit(self)
        layout.addWidget(self.url_input)

        # 상태 및 결과 창
        self.status_label = QtWidgets.QTextEdit("현재 상태: 대기 중")
        self.status_label.setReadOnly(True)
        layout.addWidget(self.status_label)

        self.start_button = QtWidgets.QPushButton("크롤링 시작")
        self.start_button.clicked.connect(self.start_crawling)
        layout.addWidget(self.start_button)

        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def log_status(self, message):
        self.status_label.append(message)

    def start_crawling(self):
        url = self.url_input.text()
        if not url:
            self.display_error("URL이 입력되지 않았습니다.")
            return
        self.log_status(f"크롤링 시작합니다 - {url}")

        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(service=service, options=options)

            driver.get(url)
            self.log_status("페이지 로딩 완료, 크롤링 시작 중...")

            posts = driver.find_elements(By.CSS_SELECTOR, "h2.post-title")[:3]
            dates = driver.find_elements(By.CSS_SELECTOR, "span.post-date")[:3]

            for i in range(3):
                post_title = posts[i].text
                post_date = dates[i].text
                self.results.append({"title": post_title, "date": post_date})
                self.result_text.append(
                    f"제목: {post_title}\n생성일자: {post_date}\n\n"
                )
                self.log_status(f"{i+1}번째 게시글 크롤링 완료")

            driver.quit()
            self.log_status("크롤링 완료!")

        except NoSuchElementException as e:
            self.display_error("크롤링 요소를 찾을 수 없습니다.", e)
        except WebDriverException as e:
            self.display_error("웹 드라이버 오류 발생.", e)
        except Exception as e:
            self.display_error("알 수 없는 오류 발생.", e)

    def display_error(self, message, exception):
        self.error_occurred = True
        self.log_status("오류 발생!")
        self.result_text.append("\n오류 메시지:")
        self.result_text.setTextColor(QtGui.QColor("red"))
        self.result_text.append(f"{message}\n\n세부 정보:\n{traceback.format_exc()}")
        self.result_text.setTextColor(QtGui.QColor("black"))


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = CrawlerUI()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

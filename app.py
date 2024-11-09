import sys
import traceback
from PyQt5 import QtWidgets, QtGui, QtCore
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class CrawlerThread(QtCore.QThread):
    update_status = QtCore.pyqtSignal(str)
    update_result = QtCore.pyqtSignal(str)
    error_occurred = QtCore.pyqtSignal(str, str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.results = []

    def run(self):
        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(service=service, options=options)

            self.update_status.emit("페이지 로딩 완료, 크롤링 시작 중...")
            driver.get(self.url)

            titles = driver.find_elements(By.XPATH, "//span[@class='title']")[:10]
            
            for i, title in enumerate(titles):
                title_text = title.text
                self.results.append(title_text)
                self.update_result.emit(f"제목 {i + 1}: {title_text}\n")
                self.update_status.emit(f"{i + 1}번째 제목 크롤링 완료")

            self.update_status.emit("크롤링 완료! 저장 버튼을 사용하여 파일에 저장할 수 있습니다.")
            driver.quit()

        except NoSuchElementException as e:
            error_trace = traceback.format_exc()
            self.error_occurred.emit("크롤링 요소를 찾을 수 없습니다.", error_trace)
        except WebDriverException as e:
            error_trace = traceback.format_exc()
            self.error_occurred.emit("웹 드라이버 오류 발생.", error_trace)
        except Exception as e:
            error_trace = traceback.format_exc()
            self.error_occurred.emit("알 수 없는 오류 발생.", error_trace)

class CrawlerUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.crawler_thread = None

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

        # 결과물 저장 버튼
        self.save_button = QtWidgets.QPushButton("메모장으로 결과물 저장")
        self.save_button.setEnabled(False)  # 초기에는 비활성화
        self.save_button.clicked.connect(self.save_results_to_file)
        layout.addWidget(self.save_button)

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

        # 스레드 시작
        self.crawler_thread = CrawlerThread(url)
        self.crawler_thread.update_status.connect(self.log_status)
        self.crawler_thread.update_result.connect(self.result_text.append)
        self.crawler_thread.error_occurred.connect(self.display_error)
        self.crawler_thread.finished.connect(self.enable_save_button)
        self.crawler_thread.start()

    def enable_save_button(self):
        # 버튼 활성화 및 색상 변경
        self.save_button.setEnabled(True)
        self.save_button.setStyleSheet("background-color: lightgreen;")

    def save_results_to_file(self):
        # 파일 저장 창 열기
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "메모장으로 결과물 저장", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_path:
            # 결과를 파일에 저장
            with open(file_path, "w", encoding="utf-8") as f:
                for title in self.crawler_thread.results:
                    f.write(f"{title}\n")
            self.log_status(f"결과물이 {file_path}에 저장되었습니다.")

    def display_error(self, message, error_trace=""):
        self.log_status("오류 발생!")
        self.result_text.append("\n오류 메시지:")
        self.result_text.setTextColor(QtGui.QColor("red"))
        error_message = f"{message}\n\n세부 정보:\n{error_trace}"
        self.result_text.append(error_message)
        self.result_text.setTextColor(QtGui.QColor("black"))

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = CrawlerUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

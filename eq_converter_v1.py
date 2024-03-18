import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QMessageBox, QStatusBar
from PyQt6.QtGui import QClipboard
from latex2mathml.converter import convert

class Latex2MathMLConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('LaTeX to MathML Converter by maxwang967@gmail.com')
        self.statusBar().showMessage('Ready.') 

        # 设置中心窗口和布局
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # LaTeX输入组件
        self.latexInput = QLineEdit()
        self.latexInput.setPlaceholderText('Enter LaTeX code here...')
        layout.addWidget(self.latexInput)

        # 显示MathML转换结果的组件，设置为只读以禁止编辑但允许选中
        self.mathmlOutput = QTextEdit()
        self.mathmlOutput.setPlaceholderText('MathML result will be shown here...')
        self.mathmlOutput.setAcceptRichText(False)
        self.mathmlOutput.setReadOnly(True)  # 禁止编辑但允许选中和复制
        layout.addWidget(self.mathmlOutput)

        # 转换按钮
        self.convertButton = QPushButton('Convert')
        self.convertButton.clicked.connect(self.convertLatexToMathML)
        layout.addWidget(self.convertButton)
        
        # 复制到剪贴板按钮
        self.copyButton = QPushButton('Copy to Clipboard')
        self.copyButton.clicked.connect(self.copyToClipboard)
        layout.addWidget(self.copyButton)
    
    def convertLatexToMathML(self):
        self.statusBar().showMessage('Converting...')  # 更新状态栏
        try:
            # 获取LaTeX字符串
            latex_str = self.latexInput.text()
            # 转换为MathML
            mathml_result = convert(latex_str)
            # 显示转换结果
            self.mathmlOutput.setPlainText(mathml_result)
            self.statusBar().showMessage('Conversion Completed!')  # 转换完成更新状态栏
        except Exception as e:
            # 异常处理，显示错误信息
            QMessageBox.critical(self, "Conversion Error", "Please input the legal latex codes.")
            self.mathmlOutput.setPlainText("")
            self.statusBar().showMessage('Conversion Failed!')  # 更新状态栏为失败状态
    
    def copyToClipboard(self):
        # 获取MathML结果
        mathml_result = self.mathmlOutput.toPlainText()
        # 将结果复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(mathml_result, QClipboard.Mode.Clipboard)
        self.statusBar().showMessage('Copied to Clipboard!')  # 更新状态栏消息

def main():
    app = QApplication(sys.argv)
    converter = Latex2MathMLConverter()
    converter.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QMessageBox, QGroupBox, QHBoxLayout, QRadioButton, QTextBrowser
from PyQt6.QtGui import QClipboard
from latex2mathml.converter import convert
import re

if getattr(sys, 'frozen', False):
    # 如果应用被打包
    application_path = sys._MEIPASS
else:
    # 在开发环境中
    application_path = os.path.dirname(__file__)

unimathsymbols_path = os.path.join(application_path, 'latex2mathml', 'unimathsymbols.txt')

class Latex2MathMLConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.part_texts = []  # 用于保存每个部分的实际文本内容
    
    def initUI(self):
        self.setWindowTitle('LaTeX to MathML Converter by maxwang967@gmail.com')
        self.statusBar().showMessage('Ready.') 
        self.setFixedSize(1024, 768)
        # 设置中心窗口和布局
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # LaTeX输入组件
        self.latexInput = QTextEdit()
        self.latexInput.setPlaceholderText('Enter LaTeX code here...')
        self.latexInput.setAcceptRichText(False)
        self.latexInput.textChanged.connect(self.onAutoConvert)
        layout.addWidget(self.latexInput)

        self.mathmlOutput = QTextBrowser()
        self.mathmlOutput.setOpenExternalLinks(False)
        self.mathmlOutput.anchorClicked.connect(self.onTextPartClicked)
        self.mathmlOutput.setReadOnly(True)  # 禁止编辑但允许选中和复制
        layout.addWidget(self.mathmlOutput)

                # 创建选项组
        self.optionGroup = QGroupBox("Conversion Options")
        optionLayout = QHBoxLayout()

        # 单选按钮：仅方程式
        self.equationOnlyRadio = QRadioButton("Equation Only")
        optionLayout.addWidget(self.equationOnlyRadio)

        # 单选按钮：文本和方程式混合
        self.textEquationMixRadio = QRadioButton("Text & Equation Mix")
        optionLayout.addWidget(self.textEquationMixRadio)

        # 默认选择
        self.textEquationMixRadio.setChecked(True)
        # 连接单选按钮的clicked信号
        self.equationOnlyRadio.clicked.connect(self.onAutoConvert)
        self.textEquationMixRadio.clicked.connect(self.onAutoConvert)
        self.optionGroup.setLayout(optionLayout)
        layout.addWidget(self.optionGroup)


        # 复制到剪贴板按钮
        self.copyButton = QPushButton('Copy to Clipboard')
        self.copyButton.clicked.connect(self.copyToClipboard)
        layout.addWidget(self.copyButton)
    

    def convertLatexToMathML(self, latex_str):
        self.statusBar().showMessage('Converting...')  # 更新状态栏
        try:
            if self.equationOnlyRadio.isChecked():
                # "Equation Only"模式：直接转换整个字符串
                mathml_result = ""
                if latex_str != "":
                    mathml_result = convert(latex_str)
                self.mathmlOutput.setPlainText(mathml_result)
            elif self.textEquationMixRadio.isChecked():
                self.part_texts.clear()  # 清除旧的内容
                parts = self.split_text_and_formulas(latex_str)
                formatted_text = ""
                for i, part in enumerate(parts):
                    clean_part = part.strip("$")  # 假设我们直接将$...$内的内容当做公式
                      # 保存实际的文本内容
                    # if part.startswith("$") and part.endswith("$"):
                    if re.match(r'^\$(?:\\.|[^\$\\])*\$$', part) or re.match(r'^\$\$(?:\\.|[^\$\\])*\$\$$', part) or re.match(r'^\\begin\{equation\*?\}(?:\\.|[^\$\\])*?\\end\{equation\*?\}$', part, flags=re.DOTALL):
                        # 公式部分
                        formatted_text += f"<span><a href='#part_{i}' style='text-decoration:none; color:blue;'>{clean_part}</a></span>"
                        self.part_texts.append(convert(clean_part.replace("\\\\", "").replace("&", "")))
                    else:
                        # 文本部分
                        formatted_text += f"<span><a href='#part_{i}' style='text-decoration:none; color:black;'>{clean_part}</a></span>"
                        self.part_texts.append(clean_part)
                        # print("text part:", clean_part)
                self.mathmlOutput.setHtml(formatted_text)
                # self.mathmlOutput.setPlainText(result_text)
            
            self.statusBar().showMessage('Conversion Completed!')  # 转换完成更新状态栏
        except Exception as e:
            # 异常处理，显示错误信息
            QMessageBox.critical(self, "Conversion Error", f"Please input the legal latex codes. Detailed error: {str(e)}")
            self.mathmlOutput.setPlainText("")
            self.statusBar().showMessage('Conversion Failed!')  # 更新状态栏为失败状态

    
    def copyToClipboard(self):
        # 获取MathML结果
        mathml_result = self.mathmlOutput.toPlainText()
        # 将结果复制到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(mathml_result, QClipboard.Mode.Clipboard)
        self.statusBar().showMessage('Copied to Clipboard!')  # 更新状态栏消息


    def onAutoConvert(self):
        # 当单选按钮被点击时调用，触发转换流程
        latex_str = self.latexInput.toPlainText()
        self.convertLatexToMathML(latex_str)


    def onTextPartClicked(self, link):
        # 从链接中提取ID
        part_id = link.fragment()
        if part_id.startswith('part_'):
            part_index = int(part_id.split('_')[1])
            actual_text = self.part_texts[part_index]
            clipboard = QApplication.clipboard()
            clipboard.setText(actual_text)  # 复制实际文本内容到剪贴板
            # print(f"Text Copied: {actual_text}")
            self.statusBar().showMessage(f'Copied: {actual_text}')

    def split_text_and_formulas(self, latex_str):
        """
        分割文本和公式。支持$...$、$$...$$、\begin{equation}...\end{equation}和\begin{equation*}...\end{equation*}
        """
        # 定义正则表达式来匹配不同类型的公式
        pattern = r'(\$(?:\\.|[^\$\\])*\$|\$\$(?:\\.|[^\$\\])*\$\$|\\begin\{equation\*?\}(?:\\.|[^\$\\])*?\\end\{equation\*?\})'
        parts = re.split(pattern, latex_str, flags=re.DOTALL)
        return parts

def main():
    app = QApplication(sys.argv)
    converter = Latex2MathMLConverter()
    converter.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QMessageBox, QGroupBox, QHBoxLayout, QRadioButton, QTextBrowser, QLabel
from PyQt6.QtGui import QClipboard
from latex2mathml.converter import convert
from latex2mathml.exceptions import MissingEndError
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
        self.explanationVisible = True  # 追踪说明文本的显示状态
    
    def initUI(self):
        self.setWindowTitle('Latex2Word Full Converter')
        self.statusBar().showMessage('Ready.') 
        self.setFixedSize(1024, 768)
        # 设置中心窗口和布局
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # 创建一个 QGroupBox 用于包含说明文本
        self.explanationGroupBox = QGroupBox("")
        explanationLayout = QVBoxLayout()

        explanationLabel = QLabel("<b>Welcome to Latex2Word Full Converter!</b><br>"
                                  "<p>Enter your LaTeX code below and see the converted output.</p>"
                                  "<ul>"
                                  "<li>In the 'Equation Only' mode, just input the equation in latex with/without '$','$$' or '\\begin{equation}', etc.</li>"
                                  "<li>In the 'Text Equation Mix' mode, just input the mixed latex codes, and the converted results will show in two colors (i.e., black for normal text, and blue for equations).</li>"
                                  "<li>You can click on the 'black' part or 'blue' part to put them in your clipboard, and just paste in Microsoft Word with 'Unformatted Text' mode to display just as you see in the latex codes.</li>"
                                  "<li>Note that Microsoft Word does not support to copy mixed text (i.e., normal text and equation) together, and thus you need to click on each part of the results and copy them in sequence.</li>"
                                  "<li>Please feel free to create issues in <a href='https://github.com/maxwang967/Latex2WordFullConverter'>link<a/>.</li>"
                                  "</ul>")
        explanationLabel.setWordWrap(True)
        explanationLabel.setOpenExternalLinks(True)
        # explanationLabel.setHidden(True)
        # 将说明文本添加到 QGroupBox 的布局中
        explanationLayout.addWidget(explanationLabel)
        self.explanationGroupBox.setLayout(explanationLayout)

        # 将 QGroupBox 添加到主布局中
        layout.addWidget(self.explanationGroupBox)

        # 添加一个箭头按钮用于显示或隐藏说明文本
        self.toggleButton = QPushButton()
        self.toggleButton.setText("Hide") 
        self.toggleButton.clicked.connect(self.toggleExplanation)
        layout.addWidget(self.toggleButton)

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
        self.copyButton = QPushButton('Copy All')
        self.copyButton.clicked.connect(self.copyToClipboard)
        layout.addWidget(self.copyButton)

        # add clear button
        self.clearButton = QPushButton('Clear')
        self.clearButton.clicked.connect(self.clearAll)
        layout.addWidget(self.clearButton)
    

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
                    if (clean_part != "") and (re.match(r'^\$(?:\\.|[^\$\\])*\$$', part) or re.match(r'^\$\$(?:\\.|[^\$\\])*\$\$$', part) or re.match(r'^\\begin\{equation\*?\}(?:\\.|[^\$\\])*?\\end\{equation\*?\}$', part, flags=re.DOTALL)):
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
        except MissingEndError:
            QMessageBox.critical(self, "Conversion Error", f"Missing end tag for the equations, at: {clean_part.replace("\\\\", "").replace("&", "")}")
            self.statusBar().showMessage('Conversion Failed!')  # 更新状态栏为失败状态
        except Exception:
            QMessageBox.critical(self, "Conversion Error", f"Fatal error, at: {clean_part.replace("\\\\", "").replace("&", "")}")
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

    def clearAll(self):
        self.latexInput.clear()
        self.mathmlOutput.clear()
        self.statusBar().showMessage('Ready.')


    def toggleExplanation(self):
        # 切换说明文本的可见性
        self.explanationVisible = not self.explanationVisible
        self.explanationGroupBox.setVisible(self.explanationVisible)
        # 根据当前状态更新箭头方向
        if self.explanationVisible:
            self.toggleButton.setText("Hide")
        else:
            self.toggleButton.setText("Show")

def main():
    app = QApplication(sys.argv)
    converter = Latex2MathMLConverter()
    converter.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

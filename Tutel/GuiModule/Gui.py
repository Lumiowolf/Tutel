import logging
import os
import sys
from io import StringIO

import qdarktheme
from PySide6.QtCore import QPointF, QThread, QObject, Signal
from PySide6.QtGui import QAction, QFont, QPainter, Qt, QPaintEvent, QTextOption, QWheelEvent, QMouseEvent, QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QGridLayout, QSplitter, QFileDialog, \
    QMessageBox, QInputDialog

from Tutel.ErrorHandlerModule.ErrorHandler import ErrorHandler
from Tutel.ErrorHandlerModule.ErrorType import LexerException, ParserException, InterpreterException, Exit
from Tutel.InterpreterModuler.Interpreter import Interpreter
from Tutel.InterpreterModuler.TutelBuiltins import Turtle
from Tutel.LexerModule.Lexer import Lexer
from Tutel.ParserModule.Parser import Parser


class Worker(QObject):
    finished = Signal()
    exception = Signal(str)
    get_start = Signal(list)

    add_turtle = Signal(int, object, QPointF, int)
    set_color = Signal(int, object)
    set_position = Signal(int, QPointF)
    set_orientation = Signal(int, int)
    add_point = Signal(int, QPointF)

    def __init__(self, code):
        super().__init__()
        self.code = code
        self.lexer = None
        self.parser = None
        self.program = None
        self.interpreter = None
        self.error_handler = ErrorHandler(logging.CRITICAL)
        Turtle.set_up(self.add_turtle, self.set_color, self.set_position, self.set_orientation, self.add_point)

    def parse(self):
        try:
            self.lexer = Lexer(StringIO(self.code), self.error_handler)
            self.parser = Parser(self.error_handler)
            self.program = self.parser.parse(self.lexer)
            self.get_start.emit(list(self.program.functions.keys()))
        except LexerException as e:
            self.finished.disconnect()
            self.exception.emit(str(e))
        except ParserException as e:
            self.finished.disconnect()
            self.exception.emit(str(e))
        except Exit:
            pass
        except Exception as e:
            self.finished.disconnect()
            self.exception.emit(f"Unhandled exception: {e}")

    def execute(self, start):
        if start != "":
            try:
                self.interpreter = Interpreter(self.error_handler)
                self.interpreter.execute(self.program, start)
            except InterpreterException as e:
                self.finished.disconnect()
                self.exception.emit(str(e))
            except Exit:
                pass
            except Exception as e:
                self.finished.disconnect()
                self.exception.emit(f"Unhandled exception: {e}")
        self.finished.emit()

    def stop(self):
        if self.interpreter is not None:
            self.interpreter.stop()
        else:
            self.finished.emit()


class Gui:
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler

        self.app = QApplication(sys.argv)
        font = QFont()
        font.setPointSize(12)
        self.app.setFont(font)

        self.mainWindow = MainWindow()

        # Apply dark theme to Qt application
        self.app.setStyleSheet(qdarktheme.load_stylesheet())

    def run(self):
        sys.exit(self.app.exec())


class MainWindow(QMainWindow):
    execute = Signal(str)

    def __init__(self):
        super().__init__()
        self.path = None
        self.draw_area = DrawArea()
        self.code_area = CodeArea()

        self.execute_thread = QThread()
        self.execute_worker = Worker(self.code_area.toPlainText())

        self.initUI()

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path
        if path:
            self.filename = os.path.split(path)[1]
        else:
            self.filename = None

    def run_code(self):
        if self.execute_thread.isRunning():
            if self.dialog_rerun():
                self.execute_worker.finished.connect(self.__run_code)
                self.stop_code_worker()
            return
        self.__run_code()

    def __run_code(self):
        self.execute_thread = QThread()
        self.execute_worker = Worker(self.code_area.toPlainText())
        self.draw_area.setDisabled(True)

        self.execute_thread.started.connect(self.draw_area.set_up)
        self.execute_thread.started.connect(self.execute_worker.parse)
        self.execute_worker.finished.connect(self.stop_code_thread)
        self.execute_worker.finished.connect(self.dialog_info)
        self.execute_worker.finished.connect(lambda: self.draw_area.setEnabled(True))
        self.execute_worker.exception.connect(self.stop_code_thread)
        self.execute_worker.exception.connect(self.dialog_critical)
        self.execute_worker.exception.connect(lambda: self.draw_area.setEnabled(True))
        self.execute_worker.get_start.connect(self.dialog_get_start)
        self.execute.connect(self.execute_worker.execute)
        self.execute_worker.add_turtle.connect(self.draw_area.add_turtle)
        self.execute_worker.set_color.connect(self.draw_area.set_color)
        self.execute_worker.set_position.connect(self.draw_area.set_position)
        self.execute_worker.set_orientation.connect(self.draw_area.set_orientation)
        self.execute_worker.add_point.connect(self.draw_area.add_point)
        self.execute_worker.moveToThread(self.execute_thread)

        self.execute_thread.start()

    def stop_code_worker(self):
        print("Terminating...\n")
        self.execute_worker.stop()

    def stop_code_thread(self):
        self.execute_thread.quit()
        self.execute_thread.wait()
        print("Program finished")

    def initUI(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')

        new_action = QAction('&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('Open file')
        new_action.triggered.connect(self.file_new)
        file_menu.addAction(new_action)

        open_action = QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open file')
        open_action.triggered.connect(self.file_open)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save file')
        save_action.triggered.connect(self.file_save)
        file_menu.addAction(save_action)

        save_as_action = QAction('Save &As', self)
        save_as_action.setStatusTip('Save file as')
        save_as_action.triggered.connect(self.file_save_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction('&Exit', self)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.exit)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu('&Edit')

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.code_area.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.setStatusTip("Redo last undone change")
        redo_action.triggered.connect(self.code_area.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("&Cut", self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.setStatusTip("Cut selected text")
        cut_action.triggered.connect(self.code_area.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("C&opy", self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(self.code_area.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.triggered.connect(self.code_area.paste)
        edit_menu.addAction(paste_action)

        select_action = QAction("&Select All", self)
        select_action.setShortcut('Ctrl+A')
        select_action.setStatusTip("Select all text")
        select_action.triggered.connect(self.code_area.selectAll)
        edit_menu.addAction(select_action)

        run_menu = menubar.addMenu('&Run')
        run_action = QAction("Run &Code", self)
        run_action.setShortcut('Ctrl+R')
        run_action.setStatusTip("Run code from editor")
        run_action.triggered.connect(self.run_code)
        run_menu.addAction(run_action)

        stop_action = QAction("Stop Code", self)
        stop_action.setStatusTip("Stop execution of code")
        stop_action.triggered.connect(self.stop_code_worker)
        run_menu.addAction(stop_action)

        self.statusBar()

        splitter = QSplitter()
        splitter.addWidget(self.draw_area)
        splitter.addWidget(self.code_area)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)

        layout = QGridLayout()
        layout.addWidget(splitter)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.setWindowTitle('Tutel')
        self.showMaximized()

    def file_new(self):
        if self._has_changed():
            new, save = self.dialog_unsaved()
            if new:
                if save:
                    saved = self.file_save()
                    if saved:
                        self._clear_code_area()
                self._clear_code_area()
        else:
            self._clear_code_area()

    def _clear_code_area(self):
        self.code_area.setPlainText("")
        self.path = None

    def _has_changed(self) -> bool:
        if not self.path:
            if self.code_area.toPlainText():
                return True
            else:
                return False

        try:
            with open(self.path, 'r') as f:
                text = f.read()

        except Exception as e:
            self.dialog_critical(str(e))
            return True

        else:
            return text != self.code_area.toPlainText()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "Tutel source code (*.tut);;Text documents (*.txt);;All files (*.*)")

        if path:
            try:
                if self._has_changed():
                    _open, save = self.dialog_unsaved()
                    if _open:
                        if save:
                            saved = self.file_save()
                            if saved:
                                self._file_open(path)
                        else:
                            self._file_open(path)
                else:
                    self._file_open(path)
            except Exception as e:
                self.dialog_critical(str(e))

    def _file_open(self, path):
        with open(path, 'r') as f:
            text = f.read()
        self.path = path
        self.code_area.setPlainText(text)
        self.update_title(self.filename)

    def file_save(self):
        if self.path is None:
            return self.file_save_as()

        return self._save_to_path(self.path)

    def file_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "",
                                              "Tutel source code (*.tut);;Text documents (*.txt);;All files (*.*)")

        if not path:
            return False

        return self._save_to_path(path)

    def _save_to_path(self, path):
        text = self.code_area.toPlainText()
        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))
            return False

        else:
            self.path = path
            self.update_title(self.filename)
            return True

    def update_title(self, filename):
        self.setWindowTitle(f"Tutel • {filename}")

    def closeEvent(self, event: QCloseEvent) -> None:
        self.exit()
        event.ignore()

    def exit(self):
        if (not self.path and self.code_area.toPlainText()) or self._has_changed():
            _exit, _save = self.dialog_unsaved()
            if _exit:
                if _save:
                    _saved = self.file_save()
                    if _saved:
                        self.__exit()
                else:
                    self.__exit()
        else:
            self.__exit()

    def __exit(self):
        if self.execute_thread.isRunning():
            if self.dialog_in_progress_close():
                self.hide()
                self.stop_code_worker()
                self.execute_thread.finished.connect(QApplication.instance().quit)
        else:
            self.hide()
            QApplication.instance().quit()

    def dialog_unsaved(self):
        qm = QMessageBox

        ret = qm.question(self, 'Saving', f"Do you want to save file {self.filename}?", qm.Yes | qm.No | qm.Cancel)

        if ret == qm.Yes:
            return True, True
        elif ret == qm.No:
            return True, False
        else:
            return False, False

    def dialog_critical(self, error):
        qm = QMessageBox

        qm.critical(self, 'Error', f'Something wrong happened. Error message:\n\n{error}')

    def dialog_info(self):
        qm = QMessageBox

        qm.information(self, 'Finished', 'Execution finished!')

    def dialog_rerun(self):
        qm = QMessageBox

        ret = qm.question(self, 'Stopping', "Code is currently executed. Do you want to stop it and run again?",
                          qm.Yes | qm.No)

        if ret == qm.Yes:
            return True
        else:
            return False

    def dialog_in_progress_close(self):
        qm = QMessageBox

        ret = qm.question(self, 'Stopping', "Code is currently executed. Do you want to stop it and exit?",
                          qm.Yes | qm.No)

        if ret == qm.Yes:
            return True
        else:
            return False

    def dialog_get_start(self, functions):
        function, ok = QInputDialog.getItem(self, "Start function", "Choose start function", functions, 0)
        if ok:
            self.execute.emit(function)
        else:
            self.execute.emit("")


class DrawArea(QWidget):
    def __init__(self):
        super().__init__()
        self.turtles = {}
        self.lines = []
        self.factor = 1
        self.drag = False
        self.shift = QPointF(0.0, 0.0)
        self.focus_point = QPointF(0.0, 0.0)
        self.start_pos = QPointF(0.0, 0.0)
        self.setMouseTracking(True)
        self.initUI()

    def initUI(self):
        self.show()

    def set_up(self):
        self.turtles = {}

    def add_turtle(self, turtle_id, color, position, orientation):
        self.turtles[turtle_id] = {"position": position, "orientation": orientation,
                                   "lines": [{"color": color, "points": []}]}

    def set_color(self, turtle_id, color):
        if len(self.turtles[turtle_id]["lines"][-1]["points"]) > 0:
            start_point = self.turtles[turtle_id]["lines"][-1]["points"][-1]
            self.turtles[turtle_id]["lines"].append({"color": color, "points": [start_point]})
        else:
            self.turtles[turtle_id]["lines"].append({"color": color, "points": []})

    def set_position(self, turtle_id, position):
        self.turtles[turtle_id]["position"] = position
        color = self.turtles[turtle_id]["lines"][-1]["color"]
        self.turtles[turtle_id]["lines"].append({"color": color, "points": []})
        self.update()

    def set_orientation(self, turtle_id, orientation):
        self.turtles[turtle_id]["orientation"] = orientation

    def add_point(self, turtle_id, point):
        self.turtles[turtle_id]["position"] = point
        self.turtles[turtle_id]["lines"][-1]["points"].append(point)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        rect = event.rect()
        qp = QPainter(self)
        qp.eraseRect(rect)
        qp.setRenderHint(QPainter.Antialiasing)
        lines = self._get_lines()
        for line in lines:
            qp.setPen(line["color"])
            qp.drawPolyline(line["points"])
        self.factor = 1
        qp.end()

    def _get_lines(self):
        # result = [self.turtles[turtle_id]["lines"] for turtle_id in self.turtles.keys()]
        # for turtle_id in self.turtles.keys():
        #     lines = []
        #     for line in self.turtles[turtle_id]["lines"]:
        #         line["points"] = [(point - self.focus_point) * self.factor + self.focus_point - self.shift for point in
        #                           line["points"]]
        #         lines.append(line)
        #     self.turtles[turtle_id]["lines"] = lines
        #     result += lines
        result = []
        for turtle_id in self.turtles.keys():
            result += self.turtles[turtle_id]["lines"]
        return result

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            self.factor = 1.1
        if event.angleDelta().y() < 0:
            self.factor = 0.9
        self.adjust()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPosition()
            self.drag = True

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drag:
            self.shift = self.start_pos - event.globalPosition()
            self.start_pos = event.globalPosition()
            self.adjust()
            self.update()
        self.focus_point = event.globalPosition()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.drag = False
        self.shift = QPointF(0.0, 0.0)

    def adjust(self):
        for turtle_id in self.turtles:
            for i in range(len(self.turtles[turtle_id]["lines"])):
                self.turtles[turtle_id]["lines"][i]["points"] = [
                    (point - self.focus_point) * self.factor + self.focus_point - self.shift for point in
                    self.turtles[turtle_id]["lines"][i]["points"]]


class CodeArea(QTextEdit):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        font = QFont()
        font.setPointSize(16)
        font.setFamily("Courier New")
        self.setFont(font)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setAcceptRichText(False)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() == Qt.ShiftModifier:
            QApplication.sendEvent(self.horizontalScrollBar(), event)
        elif event.modifiers() == Qt.CTRL:
            font = self.font()
            if event.angleDelta().y() > 0:
                font.setPointSize(font.pointSize() + 1)
            elif event.angleDelta().y() < 0:
                font.setPointSize(font.pointSize() - 1)
            self.setFont(font)
        else:
            QTextEdit.wheelEvent(self, event)

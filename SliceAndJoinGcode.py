# ===================================================================
# Verzija: 51
# Datum: 12.01.2026
# Opis: Plugin SliceAndJoinGcode pripravo G-code tako, da se
# prvi layser tiska na način Outside → Inside, ostali pa layerji
# pa na način Inside → Outside. Postopek izdelave take G-code:
#  - Če model na postelji ne obstaja, ne naredi nič
#  - Nastavi Wall Orderning na Outside → Inside
#  - Slice #1: Outside → Inside (shrani prvi layer)
#  - Nastavi Wall Orderning na Inside → Outside
#  - Slice #2: Inside → Outside (shrani drugi in ostale layerje)
#  - Združi G-code #1 + #2
#  - Prikaže zdrženo G-code v oknu.
#  - V oknu mogoči: Search, Replace ter Save G-code.
#  - Search & Replace = case-insensitive
#  - Temna tema, barvanje G-code
#  - Cura 5.11.x kompatibilno
#  - Ime datoteke z G-code = 6 črk imena tikalnika in ime modela
# ===================================================================

from PyQt6.QtWidgets import (
    QMessageBox,
    QApplication,
    QDialog,
    QVBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from UM.Extension import Extension
from cura.CuraApplication import CuraApplication
import re


def getMetaData():
    return {}


def register(app):
    return {"extension": SliceAndJoinGcode()}


# -------------------------------------------------------------
# Napredni syntax highlighter za G-code (barve po vrstah)
# -------------------------------------------------------------
class GcodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)

        # ====== BARVE PO TOKENIH ======
        self.token_formats = {
            "G": self._fmt("#F42828"),  # G ukazi
            "M": self._fmt("#A62CF7"),  # M ukazi
            "X": self._fmt("#00AB72"),  # koordinate
            "Y": self._fmt("#E2D700"),
            "Z": self._fmt("#08EFFF"),
            "E": self._fmt("#FF00F2"),  # ekstruder
            "F": self._fmt("#FFA303"),  # feedrate
            "S": self._fmt("#FF830F"),  # temperature
        }

        self.comment_format = self._fmt("#3F9CFF")
        self.layer_format = self._fmt("#929292")

        # ====== ROBUSTEN TOKEN REGEX ======
        self.token_regex = re.compile(r"([GMXYZESF])([-+]?(?:\d+\.?\d*|\.\d+))")

    def _fmt(self, color):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    def highlightBlock(self, text):
        # --------------------------------------------------
        # KOMENTAR
        # --------------------------------------------------
        comment_start = text.find(";")
        if comment_start != -1:
            self.setFormat(
                comment_start, len(text) - comment_start, self.comment_format
            )

            # ;LAYER:x
            layer_match = re.search(r";LAYER:\d+", text)
            if layer_match:
                self.setFormat(
                    layer_match.start(), len(layer_match.group()), self.layer_format
                )

            code_part = text[:comment_start]
        else:
            code_part = text

        # --------------------------------------------------
        # TOKENI (EN FORMAT NA CELOTEN SKLOP)
        # --------------------------------------------------
        for match in self.token_regex.finditer(code_part):
            letter = match.group(1)
            fmt = self.token_formats.get(letter)
            if fmt:
                self.setFormat(match.start(), len(match.group()), fmt)


# -------------------------------------------------------------
# Glavna razširitev
# -------------------------------------------------------------
class SliceAndJoinGcode(Extension):

    VERSION = "51"
    DATE = "13.01.2026"

    def __init__(self):
        super().__init__()
        self.setMenuName("Slice First Layer Outside-In")
        self.addMenuItem("Run", self.startProcess)

        self._original_inset_direction = "inside_out"
        self._original_auto_slice = None
        self._phase = 0

        self._gcode_first_layer = []
        self._gcode_rest = []
        self._final_gcode = ""
        self._last_search_pos = 0  # za funkcijo search

    # ---------------------------------------------------------
    # Glavni vstop
    # ---------------------------------------------------------
    def startProcess(self):
        self._disableAutoSlice()

        if not self._hasModelsOnBed():
            self._restoreAutoSlice()
            return

        self._saveOriginalInsetDirection()
        self._phase = 1
        QTimer.singleShot(0, self._sliceOutsideIn)

    # ---------------------------------------------------------
    # Auto Slice OFF
    # ---------------------------------------------------------
    def _disableAutoSlice(self):
        prefs = CuraApplication.getInstance().getPreferences()
        try:
            self._original_auto_slice = prefs.getValue("general/auto_slice")
            if self._original_auto_slice:
                prefs.setValue("general/auto_slice", False)
        except Exception as e:
            print("AutoSlice error:", e)

    # ---------------------------------------------------------
    # Auto Slice RESTORE
    # ---------------------------------------------------------
    def _restoreAutoSlice(self):
        if self._original_auto_slice:
            CuraApplication.getInstance().getPreferences().setValue(
                "general/auto_slice", True
            )

    # ---------------------------------------------------------
    # Shrani originalno nastavitev
    # ---------------------------------------------------------
    def _saveOriginalInsetDirection(self):
        app = CuraApplication.getInstance()
        try:
            stack = app.getGlobalContainerStack()
            if stack and stack.userChanges:
                val = stack.userChanges.getProperty("inset_direction", "value")
                if val:
                    self._original_inset_direction = val
        except:
            self._original_inset_direction = "inside_out"

    # ---------------------------------------------------------
    # Slice 1 – Outside → Inside
    # ---------------------------------------------------------
    def _sliceOutsideIn(self):
        self._setInsetDirection("outside_in")
        QTimer.singleShot(100, self._executeSlice)

    # ---------------------------------------------------------
    # Slice 2 – Inside → Outside
    # ---------------------------------------------------------
    def _sliceInsideOut(self):
        self._setInsetDirection("inside_out")
        QTimer.singleShot(100, self._executeSlice)

    # ---------------------------------------------------------
    # Nastavitev wall ordering
    # ---------------------------------------------------------
    def _setInsetDirection(self, value):
        app = CuraApplication.getInstance()
        try:
            stack = app.getGlobalContainerStack()
            if stack and stack.userChanges:
                stack.userChanges.setProperty("inset_direction", "value", value)
                app.globalContainerStackChanged.emit()
                QApplication.processEvents()
        except Exception as e:
            print(e)

    # ---------------------------------------------------------
    # Slice
    # ---------------------------------------------------------
    def _executeSlice(self):
        app = CuraApplication.getInstance()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        app.getBackend().slice()
        QTimer.singleShot(300, self._waitForSlice)

    # ---------------------------------------------------------
    # Čakanje na CuraEngine
    # ---------------------------------------------------------
    def _waitForSlice(self):
        backend = CuraApplication.getInstance().getBackend()
        try:
            if backend._process and backend._process.poll() is None:
                QTimer.singleShot(500, self._waitForSlice)
                return
        except:
            pass

        QApplication.restoreOverrideCursor()
        self._processSliceResult()

    # ---------------------------------------------------------
    # Obdelava rezultata slica
    # ---------------------------------------------------------
    def _processSliceResult(self):
        app = CuraApplication.getInstance()
        scene = app.getController().getScene()
        plate = app.getMultiBuildPlateModel().activeBuildPlate

        if not hasattr(scene, "gcode_dict") or plate not in scene.gcode_dict:
            QMessageBox.critical(None, "Error", "G-code not exists")
            self._restoreOriginalInsetDirection()
            self._restoreAutoSlice()
            return

        lines = scene.gcode_dict[plate]

        if self._phase == 1:
            self._extractFirstLayer(lines)
            self._phase = 2
            QTimer.singleShot(0, self._sliceInsideOut)

        elif self._phase == 2:
            self._extractRestLayers(lines)
            self._mergeGcode()
            self._restoreOriginalInsetDirection()
            self._showFinalDialog()

    # ---------------------------------------------------------
    # Izlušči prvi layer (do ;LAYER:1)
    # ---------------------------------------------------------
    def _extractFirstLayer(self, lines):
        result = []
        for line in lines:
            if line.startswith(";LAYER:1"):
                break
            result.append(line)
        self._gcode_first_layer = result

    # ---------------------------------------------------------
    # Izlušči layerje od ;LAYER:1 dalje
    # ---------------------------------------------------------
    def _extractRestLayers(self, lines):
        start = False
        result = []
        for line in lines:
            if line.startswith(";LAYER:1"):
                start = True
            if start:
                result.append(line)
        self._gcode_rest = result

    # ---------------------------------------------------------
    # Združi G-code
    # ---------------------------------------------------------
    def _mergeGcode(self):
        merged = []
        merged.extend(self._gcode_first_layer)
        merged.extend(self._gcode_rest)
        self._final_gcode = "\n".join(merged)

    # ---------------------------------------------------------
    # Dialog + Save g-code + Search & Replace + temna tema
    # ---------------------------------------------------------
    def _showFinalDialog(self):
        dialog = QDialog()
        dialog.setWindowTitle(
            f" G-CODE – First layer Outside-In    (v. {self.VERSION} – {self.DATE})  -  (c) Julijan Zavernik"
        )
        dialog.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dialog.setModal(True)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        # prepreč ESC
        def ignoreEsc(event):
            if event.key() != Qt.Key.Key_Escape:
                QDialog.keyPressEvent(dialog, event)

        dialog.keyPressEvent = ignoreEsc

        # temna tema za celoten dialog
        dialog.setStyleSheet(
            """
            QDialog { background-color: #1e1e1e; }
            QLabel { color: #FFFFFF; font-size: 10pt; }
            QPushButton { background-color: #0078d7; color: #FFFFFF; font-size: 10pt; min-height: 21px; }
            QLineEdit { background-color: #333333; color: #FFFFFF; border: 1px solid #555555; font-size: 10pt}
        """
        )

        layout = QVBoxLayout(dialog)

        # G-code editor - začni s "loading" sporočilom
        edit = QPlainTextEdit()
        edit.setPlainText(
            "⏳ PLEASE WAIT...\n\nLoading G-code...\n\nThis may take a moment for large models."
        )
        edit.setReadOnly(True)
        edit.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 11pt;
            }
        """
        )
        layout.addWidget(edit)

        # Syntax highlighter
        self.highlighter = GcodeHighlighter(edit.document())

        # Search panel (onemogoči na začetku)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_label = QLabel("Search:")
        search_label.setFixedWidth(60)
        self.search_input = QLineEdit()
        self.search_input.setDisabled(True)  # Onemogoči na začetku
        search_btn = QPushButton("Search")
        search_btn.setDisabled(True)  # Onemogoči na začetku
        search_btn.setFixedWidth(100)
        search_btn.clicked.connect(lambda: self._searchGcode(edit))
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # Replace panel (onemogoči na začetku)
        replace_layout = QHBoxLayout()
        replace_layout.setContentsMargins(10, 0, 10, 0)
        replace_label = QLabel("Replace:")
        replace_label.setFixedWidth(60)
        self.replace_input = QLineEdit()
        self.replace_input.setDisabled(True)  # Onemogoči na začetku
        replace_btn = QPushButton("Replace")
        replace_btn.setDisabled(True)  # Onemogoči na začetku
        replace_btn.setFixedWidth(100)
        replace_btn.clicked.connect(lambda: self._searchAndReplaceGcode(edit))
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(replace_btn)
        layout.addLayout(replace_layout)

        # Gumbi Information | Save | Close desno (onemogoči na začetku)
        info_btn = QPushButton(" Information ")
        info_btn.setDisabled(True)  # Onemogoči na začetku

        save_btn = QPushButton(" Save G-code ")
        save_btn.setDisabled(True)  # Onemogoči na začetku

        close_btn = QPushButton("Close")
        close_btn.setDisabled(True)  # Onemogoči na začetku

        info_btn.clicked.connect(self._showInfo)
        save_btn.clicked.connect(self._saveGcodeToFile)
        close_btn.clicked.connect(dialog.accept)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_layout.addStretch()
        button_layout.addWidget(info_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.resize(900, 600)

        # Ko se dialog zapre – obnovi Auto Slice
        dialog.finished.connect(self._restoreAutoSlice)

        # Prikaži dialog
        dialog.show()

        # Prisilno osveži UI
        QApplication.processEvents()

        # Funkcija, ki se pokliče ko je G-code pripravljen
        def load_and_enable_gcode():
            # 1. Naloži G-code (to lahko traja)
            edit.setPlainText(self._final_gcode)

            # 2. Spremeni cursor nazaj na normalen
            QApplication.restoreOverrideCursor()

            # 3. Omogoči vse widgete
            self.search_input.setDisabled(False)
            search_btn.setDisabled(False)
            self.replace_input.setDisabled(False)
            replace_btn.setDisabled(False)
            info_btn.setDisabled(False)
            save_btn.setDisabled(False)
            close_btn.setDisabled(False)

            # 4. Osveži UI
            QApplication.processEvents()

        # Po 100ms začni z nalaganjem
        QTimer.singleShot(100, load_and_enable_gcode)

        dialog.exec()

    # ---------------------------------------------------------
    # Funkcija Search (case-insensitive)
    # ---------------------------------------------------------
    def _searchGcode(self, edit_widget):
        search_text = self.search_input.text()
        if not search_text:
            return

        document = edit_widget.document()
        cursor = QTextCursor(document)
        cursor.setPosition(self._last_search_pos)
        found = document.find(search_text, cursor)
        if found.isNull():
            cursor.setPosition(0)
            found = document.find(search_text, cursor)
            if found.isNull():
                QMessageBox.information(None, "Search", "Text not found.")
                return

        edit_widget.setTextCursor(found)
        edit_widget.setFocus()
        self._last_search_pos = found.selectionEnd()

    # ---------------------------------------------------------
    # Funkcija Search & Replace (case-insensitive)
    # ---------------------------------------------------------
    def _searchAndReplaceGcode(self, edit_widget):
        search = self.search_input.text()
        replace = self.replace_input.text()
        if search:
            self._final_gcode = re.sub(
                search, replace, self._final_gcode, flags=re.IGNORECASE
            )
            edit_widget.setPlainText(self._final_gcode)
            self._last_search_pos = 0

    # ---------------------------------------------------------
    # Pridobitev imena aktivnega tiskalnika iz Cure
    # ---------------------------------------------------------
    def getActivePrinterNameSimple(self):
        """Vrni prvih 6 znakov očiščenega imena tiskalnika."""
        from cura.CuraApplication import CuraApplication
        import re

        app = CuraApplication.getInstance()

        # Poskusi vse metode dokler ne najdeš imena
        for method in [
            lambda: app.getMachineManager().activeMachineName,
            lambda: (
                app.getMachineManager().activeMachine.name
                if hasattr(app.getMachineManager().activeMachine, "name")
                else None
            ),
            lambda: (
                app.getGlobalContainerStack().definition.getName()
                if app.getGlobalContainerStack()
                and app.getGlobalContainerStack().definition
                else None
            ),
            lambda: (
                app.getGlobalContainerStack().getMetaDataEntry("name")
                if app.getGlobalContainerStack()
                else None
            ),
        ]:
            try:
                name = method()
                if name:
                    # Očisti, skrajšaj in vrni
                    cleaned = re.sub(r'[<>:"/\\|?*]', "", str(name)).strip()
                    short = cleaned[:6].upper()
                    return short if short else "UNK"
            except:
                continue

        return "UNK"

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------
    def _showInfo(self):
        info_text = (
            "Version: 50      Date: 13.01.2026\n\n"
            "Description:\n"
            "SliceAndJoinGcode plugin prepares G-code so that\n"
            "the first layer is printed Outside → Inside, and all other layers\n"
            "are printed Inside → Outside.\n\n"
            "Procedure to create such G-code:\n"
            "• If the model doesn't exist on the build plate, do nothing\n"
            "• Set Wall Ordering to Outside → Inside\n"
            "• Slice #1: Outside → Inside (save first layer)\n"
            "• Set Wall Ordering to Inside → Outside\n"
            "• Slice #2: Inside → Outside (save second and remaining layers)\n"
            "• Merge G-code #1 + #2\n"
            "• Display merged G-code in the window\n"
            "• Available in window: Search, Replace, and Save G-code\n"
            "• Search & Replace = case-insensitive\n"
            "• Dark theme, G-code syntax highlighting\n"
            "• Cura 5.11.x compatible\n"
            "• G-code filename = 6 letters from printer name + model name\n\n"
            "Enjoy."
        )

        dialog = QDialog(None)
        dialog.setWindowTitle("Information")

        layout = QVBoxLayout()

        label = QLabel(info_text)
        label.setWordWrap(True)
        layout.addWidget(label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.setLayout(layout)
        dialog.exec()

    # ---------------------------------------------------------
    # Save file dialog
    # ---------------------------------------------------------
    def _saveGcodeToFile(self):

        app = CuraApplication.getInstance()
        scene = app.getController().getScene()
        root = scene.getRoot()
        nodes = [c for c in root.getChildren() if type(c).__name__ == "CuraSceneNode"]

        # print("Ime prvega modela:", first_model_name)
        if nodes:
            first_model_name = nodes[0].getName()
        # odstranim .stl
        first_model_name = re.sub(
            r"\.stl\s*$", "", first_model_name, flags=re.IGNORECASE
        )
        # Pridobi ime tiskalnika
        printer_name = self.getActivePrinterNameSimple()
        # priredim ime datoteke: 6 znakov imena printerja_ime prveega modela.code
        default_filename = f"{printer_name}_{first_model_name}.gcode"

        filename, _ = QFileDialog.getSaveFileName(
            None, "Save G-code", default_filename, "G-code (*.gcode)"
        )

        if not filename:
            return

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self._final_gcode)
        except Exception as e:
            QMessageBox.critical(None, "Error", str(e))

    # ---------------------------------------------------------
    # Preveri modele
    # ---------------------------------------------------------
    def _hasModelsOnBed(self):
        app = CuraApplication.getInstance()
        scene = app.getController().getScene()
        root = scene.getRoot()
        nodes = [c for c in root.getChildren() if type(c).__name__ == "CuraSceneNode"]
        if not nodes:
            QMessageBox.warning(None, "Error", "There is no model on the bed !")
            return False
        return True

    # ---------------------------------------------------------
    # Obnovi originalno nastavitev
    # ---------------------------------------------------------
    def _restoreOriginalInsetDirection(self):
        self._setInsetDirection(self._original_inset_direction)

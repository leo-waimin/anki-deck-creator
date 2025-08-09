import os, sys
from PySide6 import QtCore, QtGui, QtWidgets

PURPLE   = "#6a4c93"
LAVENDER = "#f3eaff"
GRAY     = "#dedee6"
DARKER   = "#c9c9d2"
TEXT     = "#1b1b1f"

class DropZone(QtWidgets.QFrame):
    filesAccepted = QtCore.Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setCursor(QtCore.Qt.DragCopyCursor)
        self._highlight = False

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(8)

        self.label = QtWidgets.QLabel("Drop your .json and .py files here")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("dropLabel")
        lay.addWidget(self.label)

    # -- drag events --
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._setHighlight(True)
        else:
            e.ignore()

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragLeaveEvent(self, e: QtGui.QDragLeaveEvent):
        self._setHighlight(False)
        e.accept()

    def dropEvent(self, e: QtGui.QDropEvent):
        self._setHighlight(False)
        urls = e.mimeData().urls()
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        self.filesAccepted.emit(paths)

    def _setHighlight(self, on: bool):
        if self._highlight == on:
            return
        self._highlight = on
        # toggle a thicker border while dragging
        self.setProperty("dragover", "true" if on else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

class ConfirmDialog(QtWidgets.QDialog):
    def __init__(self, subdeck: str, files: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm")
        self.setModal(True)
        self.setMinimumWidth(480)

        v = QtWidgets.QVBoxLayout(self)
        v.setSpacing(16)
        v.setContentsMargins(20, 20, 20, 20)

        title = QtWidgets.QLabel("Create Anki Cards?")
        title.setObjectName("title")
        v.addWidget(title)

        info = QtWidgets.QLabel(
            f"<b>Subdeck</b>: {subdeck}<br>"
            f"<b>Files</b>:<br>&nbsp;&nbsp;• {files[0]}<br>&nbsp;&nbsp;• {files[1]}"
        )
        info.setTextFormat(QtCore.Qt.RichText)
        v.addWidget(info)

        btns = QtWidgets.QHBoxLayout(); btns.addStretch()
        self.btnCancel = QtWidgets.QPushButton("Cancel")
        self.btnCreate = QtWidgets.QPushButton("Proceed")
        btns.addWidget(self.btnCancel); btns.addWidget(self.btnCreate)
        v.addLayout(btns)

        self.btnCancel.clicked.connect(self.reject)
        self.btnCreate.clicked.connect(self.accept)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anki Deck Creator (MVP)")
        self.setMinimumSize(720, 460)

        # central
        cw = QtWidgets.QWidget(); self.setCentralWidget(cw)
        outer = QtWidgets.QVBoxLayout(cw)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(18)

        # Header
        header = QtWidgets.QLabel("ANKI DECK CREATOR")
        header.setObjectName("appTitle")
        header.setAlignment(QtCore.Qt.AlignHCenter)
        outer.addWidget(header)

        # Subdeck row
        row = QtWidgets.QHBoxLayout(); row.setSpacing(12)
        lbl = QtWidgets.QLabel("Choose a subdeck:")
        lbl.setObjectName("label")
        self.combo = QtWidgets.QComboBox(); self.combo.setEditable(True)
        self.combo.setObjectName("combo")
        self.combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)  # we’ll “create” on proceed
        self.combo.setPlaceholderText("Select or type a new subdeck…")
        row.addWidget(lbl)
        row.addWidget(self.combo, 1)
        outer.addLayout(row)

        # Drop zone
        droplbl = QtWidgets.QLabel("Drag & drop your files:")
        droplbl.setObjectName("label")
        outer.addWidget(droplbl)
        self.drop = DropZone()
        outer.addWidget(self.drop)

        # Status + Proceed
        foot = QtWidgets.QHBoxLayout(); foot.setSpacing(12)
        self.status = QtWidgets.QLabel("Waiting for files…")
        self.status.setObjectName("status")
        foot.addWidget(self.status)
        foot.addStretch()
        self.btnProceed = QtWidgets.QPushButton("Validate & Continue")
        self.btnProceed.setEnabled(False)
        foot.addWidget(self.btnProceed)
        outer.addLayout(foot)

        # data
        self.files = []

        # signals
        self.drop.filesAccepted.connect(self.onFilesDropped)
        self.btnProceed.clicked.connect(self.onProceed)

        # populate subdecks (placeholder list; wire to Anki later)
        self.populateSubdecks()

        # style
        self.applyStyle()

    # ---------- behavior ----------
    def populateSubdecks(self):
        defaults = [
            "00 350-401::01 Packet Forwarding"
            "00 350-401::02 Spanning Tree Protocol and 03 Advanced STP Tuning"
            "00 350-401::04 Multiple Spanning Tree Protocol"
            "00 350-401::05 VLAN Trunks and Etherchannel Bundles"
            "00 350-401::06 IP Routing Essentials"
            "00 350-401::07 EIGRP"
            "00 350-401::08 OSPF"
            "00 350-401::09 Advanced OSPF"
            "00 350-401::10 OSPFv3"
            "00 350-401::11 BGP"
            "00 350-401::12 Advanced BGP"
            "00 350-401::13 Multicast"
            "00 350-401::14 Quality of Service"
            "00 350-401::15 IP Services"
            "00 350-401::16 Overlay Tunnels"
            "00 350-401::17 Wireless Signals and Modulation"
            "00 350-401::18 Wireless Infrastructure"
            "00 350-401::19 Understanding Wireless Roaming and Location Services"
            "00 350-401::20 Authenticating Wireless Clients"
            "00 350-401::21 Troubleshooting Wireless Connectivity"
            "00 350-401::22 Enterprise Network Architecture"
        ]
        self.combo.addItems(defaults)

    def onFilesDropped(self, paths: list[str]):
        files = [p for p in paths if os.path.isfile(p)]
        if len(files) > 2:
            files = files[-2:]  # keep the last two if user drops many
        valid, msg = self.validateFiles(files)
        self.status.setText(msg)
        self.files = files if valid else []
        self.btnProceed.setEnabled(valid)

    def validateFiles(self, files: list[str]):
        if len(files) != 2:
            return False, "Drop exactly two files: one .json and one .py"
        exts = {os.path.splitext(f)[1].lower() for f in files}
        if exts == {".json", ".py"}:
            return True, "Looks good ✔  (json + py)"
        return False, "Need one .json and one .py"

    def onProceed(self):
        subdeck = self.combo.currentText().strip()
        if not subdeck:
            QtWidgets.QMessageBox.warning(self, "Missing subdeck", "Please select or type a subdeck name.")
            return
        if len(self.files) != 2:
            QtWidgets.QMessageBox.warning(self, "Missing files", "Please drop one .json and one .py file.")
            return

        dlg = ConfirmDialog(subdeck, self.files, self)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.createCards(subdeck, self.files)

    # ---- stub to replace with real Anki integration ----
    def createCards(self, subdeck: str, files: list[str]):
        """
        TODO (next step):
          - If subdeck doesn't exist, create it (AnkiConnect /createDeck)
          - Parse JSON, run .py generator if needed
          - Build notes and call AnkiConnect /addNotes
        """
        QtWidgets.QMessageBox.information(
            self, "Stub",
            f"This is where we'd create cards in subdeck:\n\n{subdeck}\n\nFiles:\n• {files[0]}\n• {files[1]}"
        )

    # ---------- styling ----------
    def applyStyle(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {LAVENDER};
                color: {TEXT};
                font-size: 14px;
                font-family: Segoe UI, Arial, sans-serif;
            }}
            #appTitle {{
                color: {PURPLE};
                font-weight: 800;
                font-size: 22px;
                letter-spacing: 1px;
                margin-bottom: 8px;
            }}
            #label {{
                color: #444;
                font-weight: 600;
            }}
            #status {{
                color: #444;
                font-style: italic;
            }}
            QComboBox, QLineEdit {{
                background: white;
                border: 1px solid {GRAY};
                border-radius: 8px;
                padding: 8px 10px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 26px;
            }}
            QComboBox::down-arrow {{
                image: none; /* keep it simple */
            }}
            QPushButton {{
                background: {PURPLE};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
            }}
            QPushButton:disabled {{
                background: {DARKER};
                color: #f2f2f2;
            }}
            QPushButton:hover:!disabled {{
                filter: brightness(1.05);
            }}
            QPushButton:pressed:!disabled {{
                transform: translateY(1px);
            }}
            #dropZone {{
                background: {GRAY};
                border-radius: 16px;
                border: 2px dashed #b6b6c4;
            }}
            #dropZone[dragover="true"] {{
                background: #ececff;
                border: 2px solid {PURPLE};
            }}
            #dropLabel {{
                color: #404050;
                font-weight: 600;
            }}
        """)

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

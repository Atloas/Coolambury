from PyQt5.QtWidgets import QApplication

from ..Application.DrawingHistoryWindow import DrawingHistoryWindow

if __name__ == "__main__":
    app = QApplication([])
    drawings = [
        [
            [
                (0, 0),
                (100, 100),
            ],
            [
                (105, 4),
                (2, 99)
            ]
        ],
        [
            [
                (50, 0),
                (100, 100),
                (0, 100)
            ],
            [
                (0, 100),
                (50, 0)
            ]
        ],
        [
            [
                (0, 0),
                (100, 0),
                (100, 100),
                (0, 100)
            ]
        ]
    ]
    drawingHistoryWindow = DrawingHistoryWindow(drawings)
    app.exec()

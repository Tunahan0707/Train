from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QPushButton,
)
from PySide6.QtGui import (
    QPainter,
    QPen,
    QColor,
    QKeySequence,
    QPainterPath,
    QShortcut,
)
from PySide6.QtCore import Qt, QRectF, Signal

from settings import (
    COLOR_WORKSPACE_BACKGROUND,
    COLOR_GRID,
    COLOR_COMPONENT_SELECTED,
    GRID_SIZE,
    ZOOM_FACTOR,
    MIN_ZOOM,
    MAX_ZOOM,
    DELETE_BUTTON_SIZE,
    DELETE_BUTTON_MARGIN,
    COLOR_DELETE_BUTTON_BACKGROUND,
    COLOR_DELETE_BUTTON_HOVER,
    COLOR_DELETE_BUTTON_TEXT,
    SHORTCUT_DELETE,
    SHORTCUT_UNDO,
    SHORTCUT_REDO,
    MOUSE_SELECTION_BUTTON,
    MOUSE_PAN_BUTTON,
    MOUSE_PAN_MODIFIER,
    MOUSE_DELETE_BUTTON,
    MOUSE_DELETE_MODIFIER,
)

from components.resistor import Resistor
from core.history import History
from core.commands import (
    AddItemCommand,
    DeleteItemsCommand,
    MoveItemsCommand,
)


class Workspace(QGraphicsView):
    placement_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Scene
        self.circuit_scene = QGraphicsScene(self)
        self.circuit_scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setScene(self.circuit_scene)

        # Görünüm
        self.setBackgroundBrush(QColor(COLOR_WORKSPACE_BACKGROUND))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.viewport().setMouseTracking(True)

        # History
        self.history = History()

        # Fare ve yerleştirme durumları
        self.panning = False
        self.selecting = False
        self.pan_start = None
        self.selection_start = None
        self.selection_start_scene = None
        self.selection_path = QPainterPath()
        self.drag_start_positions = {}
        self.placement_component = None

        # Çöp kutusu
        self.delete_button = QPushButton("🗑", self)
        self.delete_button.setToolTip("Seçili nesneleri sil")
        self.delete_button.setFixedSize(
            DELETE_BUTTON_SIZE,
            DELETE_BUTTON_SIZE,
        )
        self.delete_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_DELETE_BUTTON_BACKGROUND};
                color: {COLOR_DELETE_BUTTON_TEXT};
                border: none;
                border-radius: 12px;
                font-size: 22px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_DELETE_BUTTON_HOVER};
            }}
        """)
        self.delete_button.clicked.connect(self.delete_selected_items)

        self.update_delete_button_position()
        self.setup_shortcuts()

    # Kısayollar
    def setup_shortcuts(self):
        shortcuts = [
            (SHORTCUT_DELETE, self.delete_selected_items),
            (SHORTCUT_UNDO, self.undo),
            (SHORTCUT_REDO, self.redo),
        ]

        self.shortcuts = []

        for sequence, callback in shortcuts:
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.setContext(
                Qt.ShortcutContext.WidgetWithChildrenShortcut
            )
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

    def undo(self):
        self.history.undo()
        self.viewport().update()

    def redo(self):
        self.history.redo()
        self.viewport().update()

    # Bileşen yerleştirme
    def start_placement(self, component_id):
        if component_id != "resistor":
            return

        self.placement_component = component_id
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()
        self.placement_changed.emit(component_id)

    def cancel_placement(self):
        if self.placement_component is None:
            return

        self.placement_component = None
        self.unsetCursor()
        self.placement_changed.emit("")

    def place_component_at(self, position):
        if self.placement_component == "resistor":
            item = Resistor()
        else:
            return

        command = AddItemCommand(
            self.circuit_scene,
            item,
            position,
        )
        self.history.execute(command)

        self.circuit_scene.clearSelection()
        item.setSelected(True)

    # Silme
    def delete_selected_items(self):
        items = self.circuit_scene.selectedItems()

        if not items:
            return

        command = DeleteItemsCommand(self.circuit_scene, items)
        self.history.execute(command)
        self.setFocus()

    def delete_item_at(self, position):
        item = self.itemAt(position)

        if item is None:
            return

        while item.parentItem() is not None:
            item = item.parentItem()

        if item.scene() != self.circuit_scene:
            return

        command = DeleteItemsCommand(self.circuit_scene, [item])
        self.history.execute(command)

    # Çöp kutusu konumu
    def update_delete_button_position(self):
        margin = DELETE_BUTTON_MARGIN
        size = DELETE_BUTTON_SIZE

        self.delete_button.move(
            self.width() - size - margin,
            self.height() - size - margin,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_delete_button_position()

    # Izgara
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        left = int(rect.left()) - (int(rect.left()) % GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % GRID_SIZE)

        painter.setPen(QPen(QColor(COLOR_GRID), 0))

        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += GRID_SIZE

        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += GRID_SIZE

    # Noktalı, içi boş kutu seçim çerçevesi
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

        if not self.selecting or self.selection_path.isEmpty():
            return

        painter.save()

        pen = QPen(
            QColor(COLOR_COMPONENT_SELECTED),
            1.5,
            Qt.PenStyle.DotLine,
        )
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.selection_path)

        painter.restore()

    # Yakınlaştırma
    def wheelEvent(self, event):
        current_zoom = self.transform().m11()
        factor = (
            ZOOM_FACTOR
            if event.angleDelta().y() > 0
            else 1 / ZOOM_FACTOR
        )

        new_zoom = current_zoom * factor

        if MIN_ZOOM <= new_zoom <= MAX_ZOOM:
            self.scale(factor, factor)

    # Fare kontrol yardımcıları
    def matches_modifier(self, event, modifier):
        if modifier == "Shift":
            return bool(
                event.modifiers()
                & Qt.KeyboardModifier.ShiftModifier
            )

        if modifier == "None":
            blocked = (
                Qt.KeyboardModifier.ShiftModifier
                | Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.AltModifier
            )
            return not bool(event.modifiers() & blocked)

        return False

    def matches_button(self, event, button_name):
        buttons = {
            "Left": Qt.MouseButton.LeftButton,
            "Middle": Qt.MouseButton.MiddleButton,
            "Right": Qt.MouseButton.RightButton,
        }
        return buttons.get(button_name) == event.button()

    # Fare basılması
    def mousePressEvent(self, event):
        # Shift + sağ tık: bileşen sil
        if (
            self.matches_button(event, MOUSE_DELETE_BUTTON)
            and self.matches_modifier(event, MOUSE_DELETE_MODIFIER)
        ):
            self.delete_item_at(event.position().toPoint())
            event.accept()
            return

        # Shift + orta tık: çalışma alanını kaydır
        if (
            self.matches_button(event, MOUSE_PAN_BUTTON)
            and self.matches_modifier(event, MOUSE_PAN_MODIFIER)
        ):
            self.panning = True
            self.pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        # Orta tık: kutu seçimi
        if (
            self.matches_button(event, MOUSE_SELECTION_BUTTON)
            and self.matches_modifier(event, "None")
        ):
            self.selecting = True
            self.selection_start = event.position().toPoint()
            self.selection_start_scene = self.mapToScene(
                self.selection_start
            )
            self.selection_path = QPainterPath()

            self.circuit_scene.clearSelection()
            self.viewport().update()

            event.accept()
            return

        # Kütüphaneden seçilen bileşeni yerleştir
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.placement_component is not None
        ):
            scene_position = self.mapToScene(
                event.position().toPoint()
            )
            self.place_component_at(scene_position)
            event.accept()
            return

        # Normal nesne seçimi ve taşıma başlangıcı
        if event.button() == Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)

            self.drag_start_positions = {
                item: item.pos()
                for item in self.circuit_scene.selectedItems()
            }
            return

        super().mousePressEvent(event)

    # Fare hareketi
    def mouseMoveEvent(self, event):
        current_pos = event.position().toPoint()

        if self.panning:
            delta = current_pos - self.pan_start

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            self.pan_start = current_pos
            return

        if self.selecting:
            current_scene = self.mapToScene(current_pos)
            selection_rect = QRectF(
                self.selection_start_scene,
                current_scene,
            ).normalized()

            self.selection_path = QPainterPath()
            self.selection_path.addRect(selection_rect)
            self.viewport().update()
            return

        super().mouseMoveEvent(event)

    # Fare bırakılması
    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.MiddleButton
            and self.panning
        ):
            self.panning = False
            self.pan_start = None
            self.setCursor(
                Qt.CursorShape.CrossCursor
                if self.placement_component
                else Qt.CursorShape.ArrowCursor
            )
            event.accept()
            return

        if (
            event.button() == Qt.MouseButton.MiddleButton
            and self.selecting
        ):
            release_scene = self.mapToScene(
                event.position().toPoint()
            )
            selection_rect = QRectF(
                self.selection_start_scene,
                release_scene,
            ).normalized()

            selection_path = QPainterPath()
            selection_path.addRect(selection_rect)

            self.circuit_scene.setSelectionArea(
                selection_path,
                Qt.ItemSelectionOperation.ReplaceSelection,
                Qt.ItemSelectionMode.IntersectsItemShape,
            )

            self.selecting = False
            self.selection_path = QPainterPath()
            self.selection_start = None
            self.selection_start_scene = None

            self.viewport().update()
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)

            old_positions = self.drag_start_positions
            new_positions = {
                item: item.pos()
                for item in old_positions
                if item.scene() == self.circuit_scene
            }

            changed_items = {
                item: position
                for item, position in new_positions.items()
                if old_positions[item] != position
            }

            if changed_items:
                old_changed_positions = {
                    item: old_positions[item]
                    for item in changed_items
                }

                self.history.undo_stack.append(
                    MoveItemsCommand(
                        old_changed_positions,
                        changed_items,
                    )
                )
                self.history.redo_stack.clear()

            self.drag_start_positions.clear()
            return

        super().mouseReleaseEvent(event)

    # Yerleştirme modundan çıkış
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.selecting:
                self.selecting = False
                self.selection_path = QPainterPath()
                self.selection_start = None
                self.selection_start_scene = None
                self.viewport().update()

            self.cancel_placement()
            event.accept()
            return

        super().keyPressEvent(event)

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
from PySide6.QtCore import Qt, QRectF, QPointF, Signal

from settings import (
    GRID_SIZE,
    ZOOM_FACTOR,
    MIN_ZOOM,
    MAX_ZOOM,
    DELETE_BUTTON_SIZE,
    DELETE_BUTTON_MARGIN,
    SHORTCUT_DELETE,
    SHORTCUT_UNDO,
    SHORTCUT_REDO,
    SHORTCUT_ROTATE,
    SHORTCUT_DUPLICATE,
    SHORTCUT_RESET_ZOOM,
    GRID_SNAP_ENABLED,
    MOUSE_SELECTION_BUTTON,
    MOUSE_PAN_BUTTON,
    MOUSE_PAN_MODIFIER,
    MOUSE_DELETE_BUTTON,
    MOUSE_DELETE_MODIFIER,
)

from components.resistor import Resistor
from components.basic import BasicComponent
from components.wire import WireItem
from theme import color
from core.history import History
from core.commands import (
    AddItemCommand,
    AddItemsCommand,
    DeleteItemsCommand,
    MoveItemsCommand,
    RotateItemsCommand,
    SetValueCommand,
)


class TrashButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(DELETE_BUTTON_SIZE, DELETE_BUTTON_SIZE)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet("""
            QPushButton {
                background: #873d4b;
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover { background: #a84c58; }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#f4f6fa"), 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        cx, cy = self.width() / 2, self.height() / 2
        painter.drawLine(int(cx - 8), int(cy - 9), int(cx + 8), int(cy - 9))
        painter.drawLine(int(cx - 3), int(cy - 12), int(cx + 3), int(cy - 12))
        painter.drawLine(int(cx - 6), int(cy - 6), int(cx - 5), int(cy + 9))
        painter.drawLine(int(cx + 6), int(cy - 6), int(cx + 5), int(cy + 9))
        painter.drawLine(int(cx - 5), int(cy + 9), int(cx + 5), int(cy + 9))
        painter.drawLine(int(cx - 2), int(cy - 5), int(cx - 2), int(cy + 6))
        painter.drawLine(int(cx + 2), int(cy - 5), int(cx + 2), int(cy + 6))
        painter.end()


class Workspace(QGraphicsView):
    history_changed = Signal()
    component_added = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Scene
        self.circuit_scene = QGraphicsScene(self)
        self.circuit_scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setScene(self.circuit_scene)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        # Görünüm
        self.setBackgroundBrush(QColor(color("workspace")))
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

        # Çöp kutusu
        self.delete_button = TrashButton(self)
        self.delete_button.clicked.connect(self.delete_selected_items)

        self.update_delete_button_position()
        self.setup_shortcuts()

    # Kısayollar
    def setup_shortcuts(self):
        shortcuts = [
            (SHORTCUT_DELETE, self.delete_selected_items),
            (SHORTCUT_UNDO, self.undo),
            (SHORTCUT_REDO, self.redo),
            (SHORTCUT_ROTATE, self.rotate_selected_items),
            (SHORTCUT_DUPLICATE, self.duplicate_selected_items),
            (SHORTCUT_RESET_ZOOM, self.reset_zoom),
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
        self.history_changed.emit()
        self.viewport().update()

    def redo(self):
        self.history.redo()
        self.history_changed.emit()
        self.viewport().update()

    def set_component_value(self, item, new_value):
        if item is None or item.scene() != self.circuit_scene:
            return
        if not hasattr(item, "set_value"):
            return
        old_value = getattr(item, "value", "")
        if str(old_value) == str(new_value):
            return
        self.history.execute(SetValueCommand(item, old_value, str(new_value)))
        self.history_changed.emit()

    def snap_position(self, position):
        return type(position)(
            round(position.x() / GRID_SIZE) * GRID_SIZE,
            round(position.y() / GRID_SIZE) * GRID_SIZE,
        )

    def reset_zoom(self):
        self.resetTransform()
        self.centerOn(0, 0)

    def duplicate_selected_items(self):
        originals = list(self.circuit_scene.selectedItems())
        if not originals:
            return

        duplicates = []
        positions = {}
        offset = GRID_SIZE * 2
        for original in originals:
            component_id = getattr(original, "component_id", None)
            if component_id == "wire":
                duplicate = WireItem(
                    QPointF(original.start_point.x() + offset, original.start_point.y() + offset),
                    QPointF(original.end_point.x() + offset, original.end_point.y() + offset),
                )
                positions[duplicate] = QPointF(0, 0)
            elif component_id == "resistor":
                duplicate = Resistor()
            elif component_id:
                duplicate = BasicComponent(component_id)
            else:
                continue

            if hasattr(duplicate, "set_value"):
                duplicate.set_value(getattr(original, "value", ""))
            if component_id != "wire":
                duplicate.setRotation(original.rotation())
                position = original.pos()
                positions[duplicate] = type(position)(
                    position.x() + offset, position.y() + offset
                )
            duplicates.append(duplicate)

        if not duplicates:
            return
        self.circuit_scene.clearSelection()
        self.history.execute(
            AddItemsCommand(self.circuit_scene, duplicates, positions)
        )
        for item in duplicates:
            item.setSelected(True)
        self.history_changed.emit()
        self.viewport().update()

    def rotate_selected_items(self):
        items = [
            item for item in self.circuit_scene.selectedItems()
            if getattr(item, "component_id", None) != "wire"
        ]
        if not items:
            return
        rotations = {item: item.rotation() for item in items}
        self.history.execute(RotateItemsCommand(rotations))
        self.history_changed.emit()
        self.viewport().update()

    # Silme
    def delete_selected_items(self):
        items = self.circuit_scene.selectedItems()

        if not items:
            return

        command = DeleteItemsCommand(self.circuit_scene, items)
        self.history.execute(command)
        self.history_changed.emit()
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
        self.history_changed.emit()

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

    # Noktalı, içi boş kutu seçim çerçevesi
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

        if not self.selecting:
            return

        painter.save()

        if self.selecting and not self.selection_path.isEmpty():
            pen = QPen(
                QColor(color("selected")),
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

    def apply_theme(self, colors):
        self.setBackgroundBrush(QColor(colors["workspace"]))
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background: {colors["danger"]};
                color: #ffffff;
                border: none;
                border-radius: 18px;
                font-size: 25px;
                font-weight: 400;
            }}
            QPushButton:hover {{ background: {colors["accent"]}; }}
        """)
        self.circuit_scene.update()
        self.viewport().update()

    def add_component(self, component_id, shift=False, stack_index=0):
        center = self.mapToScene(self.viewport().rect().center())
        position = QPointF(center.x(), center.y() + stack_index * GRID_SIZE * 4) if shift else center
        if GRID_SNAP_ENABLED:
            position = self.snap_position(position)
        if component_id == "wire":
            half = GRID_SIZE * 2
            item = WireItem(QPointF(position.x() - half, position.y()), QPointF(position.x() + half, position.y()))
            item_position = QPointF(0, 0)
        elif component_id == "resistor":
            item = Resistor()
            item_position = position
        else:
            try:
                item = BasicComponent(component_id)
            except ValueError:
                return
            item_position = position
        if not shift or stack_index == 0:
            self.circuit_scene.clearSelection()
        self.history.execute(AddItemCommand(self.circuit_scene, item, item_position))
        item.setSelected(True)
        self.history_changed.emit()
        self.component_added.emit()
        self.setFocus()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-physics-component"):
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-physics-component"):
            event.accept()
            return
        event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasFormat("application/x-physics-component"):
            event.ignore()
            return

        component_id = bytes(event.mimeData().data(
            "application/x-physics-component"
        )).decode("utf-8")
        position = self.mapToScene(event.position().toPoint())
        if GRID_SNAP_ENABLED:
            position = self.snap_position(position)

        if component_id == "wire":
            half = GRID_SIZE * 2
            item = WireItem(
                QPointF(position.x() - half, position.y()),
                QPointF(position.x() + half, position.y()),
            )
            item_position = QPointF(0, 0)
        elif component_id == "resistor":
            item = Resistor()
            item_position = position
        else:
            try:
                item = BasicComponent(component_id)
            except ValueError:
                event.ignore()
                return
            item_position = position

        self.history.execute(AddItemCommand(self.circuit_scene, item, item_position))
        self.circuit_scene.clearSelection()
        item.setSelected(True)
        self.history_changed.emit()
        self.component_added.emit()
        self.setFocus()
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()

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
            self.unsetCursor()
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

            viewport_point = event.position().toPoint()
            widget_point = self.mapFromGlobal(self.viewport().mapToGlobal(viewport_point))
            if self.delete_button.geometry().contains(widget_point):
                for item, old_position in self.drag_start_positions.items():
                    if item.scene() == self.circuit_scene:
                        item.setPos(old_position)
                self.delete_selected_items()
                self.drag_start_positions.clear()
                event.accept()
                return

            old_positions = self.drag_start_positions
            if GRID_SNAP_ENABLED:
                for item, old_position in old_positions.items():
                    if item.scene() == self.circuit_scene and item.pos() != old_position:
                        item.setPos(self.snap_position(item.pos()))

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


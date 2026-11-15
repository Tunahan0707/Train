
import ctypes
from . import WinAPI as api


class Window:

    def __init__(
        self,
        title="Renderer",
        width=800,
        height=600,
        x=100,
        y=100,
        resizable=True
    ):
        self.title = title
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.resizable = resizable

        self.hwnd = None
        self.is_running = False
        self.class_name = f"RendererWindow_{id(self)}"
        self._wndproc = None

    def _window_procedure(self, hwnd, msg, wparam, lparam):
        if msg == api.WM_DESTROY:
            api.PostQuitMessage(0)
            return 0

        return api.DefWindowProcW(hwnd, msg, wparam, lparam)

    def open(self):
        hinstance = api.GetModuleHandleW(None)

        self._wndproc = api.WNDPROC(self._window_procedure)

        style = api.WS_OVERLAPPEDWINDOW

        if not self.resizable:
            style &= ~api.WS_THICKFRAME
            style &= ~api.WS_MAXIMIZEBOX

        wc = api.WNDClass()
        wc.lpfnWndProc = self._wndproc
        wc.hInstance = hinstance
        wc.lpszClassName = self.class_name

        if not api.RegisterClassW(ctypes.byref(wc)):
            raise ctypes.WinError(ctypes.get_last_error())

        self.hwnd = api.CreateWindowExW(
            0,
            self.class_name,
            self.title,
            style,
            self.x,
            self.y,
            self.width,
            self.height,
            None,
            None,
            hinstance,
            None
        )

        if not self.hwnd:
            raise ctypes.WinError(ctypes.get_last_error())

        api.ShowWindow(self.hwnd, api.SW_SHOW)

    def run(self):
        if not self.hwnd:
            raise RuntimeError("Önce pencereyi açmalısın.")

        self.is_running = True
        msg = api.MSG()

        while self.is_running:
            result = api.GetMessageW(
                ctypes.byref(msg), None, 0, 0
            )

            if result == -1:
                raise ctypes.WinError(ctypes.get_last_error())

            if result == 0:
                self.is_running = False
                break

            api.TranslateMessage(ctypes.byref(msg))
            api.DispatchMessageW(ctypes.byref(msg))

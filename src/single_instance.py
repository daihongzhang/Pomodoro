"""Single-instance enforcement via QLocalServer / QLocalSocket.

First instance creates a named local server.
Second instance connects, sends "show", then exits.
"""

import sys
from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

SERVER_NAME = "ClaudeProjects-PomodoroTimer"


def try_activate_existing() -> bool:
    """Try to connect to an already-running instance.

    Returns True if a running instance was found and told to show itself.
    The caller should sys.exit(0) after a True return.
    """
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if not socket.waitForConnected(1000):
        return False

    socket.write(b"show")
    socket.waitForBytesWritten(500)
    socket.disconnectFromServer()
    return True


class SingleInstanceServer(QObject):
    """Listens for connections from second-instance processes.

    Emits:
        show_requested — when the second instance asks us to show the window.
    """

    show_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Remove stale pipe in case the previous instance crashed
        QLocalServer.removeServer(SERVER_NAME)

        self._server = QLocalServer(self)
        self._server.newConnection.connect(self._on_new_connection)

        if not self._server.listen(SERVER_NAME):
            print(
                f"[Pomodoro] IPC server failed: {self._server.errorString()}",
                file=sys.stderr,
            )

    def _on_new_connection(self):
        conn = self._server.nextPendingConnection()
        if conn is None:
            return

        def on_ready():
            data = conn.readAll().data().decode("utf-8", errors="replace").strip()
            if data == "show":
                self.show_requested.emit()

        conn.readyRead.connect(on_ready)
        conn.disconnected.connect(conn.deleteLater)

    def cleanup(self):
        """Shut down the server and remove the named pipe."""
        if self._server is not None and self._server.isListening():
            self._server.close()
        QLocalServer.removeServer(SERVER_NAME)

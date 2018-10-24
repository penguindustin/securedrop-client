"""
Check the core Window UI class works as expected.
"""
from PyQt5.QtWidgets import QApplication, QVBoxLayout
from PyQt5.QtCore import QTimer
from securedrop_client.gui.main import Window
from securedrop_client.gui.widgets import LoginDialog
from securedrop_client.resources import load_icon
from unittest import mock


app = QApplication([])


def test_init():
    """
    Ensure the Window instance is setup in the expected manner.
    """
    mock_li = mock.MagicMock(return_value=load_icon('icon.png'))
    mock_lo = mock.MagicMock(return_value=QVBoxLayout())
    mock_lo().addWidget = mock.MagicMock()
    with mock.patch('securedrop_client.gui.main.load_icon', mock_li), \
            mock.patch('securedrop_client.gui.main.ToolBar') as mock_tb, \
            mock.patch('securedrop_client.gui.main.MainView') as mock_mv, \
            mock.patch('securedrop_client.gui.main.QVBoxLayout', mock_lo), \
            mock.patch('securedrop_client.gui.main.QMainWindow') as mock_qmw:
        w = Window()
        mock_li.assert_called_once_with(w.icon)
        mock_tb.assert_called_once_with(w.widget)
        mock_mv.assert_called_once_with(w.widget)
        assert mock_lo().addWidget.call_count == 2


def test_setup():
    """
    Ensure the passed in controller is referenced and the various views are
    instantiated as expected.
    """
    w = Window()
    mock_controller = mock.MagicMock()
    w.setup(mock_controller)
    assert w.controller == mock_controller


def test_autosize_window():
    """
    Check the autosizing fits to the full screen size.
    """
    w = Window()
    w.resize = mock.MagicMock()
    mock_screen = mock.MagicMock()
    mock_screen.width.return_value = 1024
    mock_screen.height.return_value = 768
    mock_sg = mock.MagicMock()
    mock_sg.screenGeometry.return_value = mock_screen
    mock_qdw = mock.MagicMock(return_value=mock_sg)
    with mock.patch('securedrop_client.gui.main.QDesktopWidget', mock_qdw):
        w.autosize_window()
    w.resize.assert_called_once_with(1024, 768)


def test_show_login():
    """
    The login dialog is displayed with a clean state.
    """
    mock_controller = mock.MagicMock()
    w = Window()
    w.setup(mock_controller)
    with mock.patch('securedrop_client.gui.main.LoginDialog') as mock_ld:
        w.show_login()
        mock_ld.assert_called_once_with(w)
    w.login_dialog.reset.assert_called_once_with()
    w.login_dialog.exec.assert_called_once_with()


def test_show_login_error():
    """
    Ensures that an error message is displayed in the login dialog.
    """
    mock_controller = mock.MagicMock()
    w = Window()
    w.setup(mock_controller)
    w.login_dialog = mock.MagicMock()
    w.show_login_error('boom')
    w.login_dialog.error.assert_called_once_with('boom')


def test_hide_login():
    """
    Ensure the login dialog is closed and hidden.
    """
    mock_controller = mock.MagicMock()
    w = Window()
    w.setup(mock_controller)
    ld = mock.MagicMock()
    w.login_dialog = ld
    w.hide_login()
    ld.accept.assert_called_once_with()
    assert w.login_dialog is None


def test_show_sources():
    """
    Ensure the sources list is passed to the source list widget to be updated.
    """
    w = Window()
    w.main_view = mock.MagicMock()
    w.show_sources([1, 2, 3])
    w.main_view.source_list.update.assert_called_once_with([1, 2, 3])


def test_show_sync():
    """
    If there's a value display the result of its "humanize" method.
    """
    w = Window()
    w.main_view = mock.MagicMock()
    updated_on = mock.MagicMock()
    w.show_sync(updated_on)
    w.main_view.status.setText.assert_called_once_with('Last Sync: ' +
                                                       updated_on.humanize())


def test_show_sync_no_sync():
    """
    If there's no value to display, default to a "waiting" message.
    """
    w = Window()
    w.main_view = mock.MagicMock()
    w.show_sync(None)
    w.main_view.status.setText.\
        assert_called_once_with('Waiting to Synchronize')


def test_set_logged_in_as():
    """
    Given a username, the toolbar is appropriately called to update.
    """
    w = Window()
    w.tool_bar = mock.MagicMock()
    w.set_logged_in_as('test')
    w.tool_bar.set_logged_in_as.assert_called_once_with('test')


def test_logout():
    """
    Ensure the toolbar updates to the logged out state.
    """
    w = Window()
    w.tool_bar = mock.MagicMock()
    w.logout()
    w.tool_bar.set_logged_out.assert_called_once_with()


def test_on_source_changed():
    """
    Ensure the event handler for when a source is changed calls the
    show_conversation_for method with the expected source object.
    """
    w = Window()
    w.main_view = mock.MagicMock()
    mock_si = w.main_view.source_list.currentItem()
    mock_sw = w.main_view.source_list.itemWidget()
    w.show_conversation_for = mock.MagicMock()
    w.on_source_changed()
    w.show_conversation_for.assert_called_once_with(mock_sw.source)


def test_conversation_for():
    """
    TODO: Finish this once we have data. Currently checks only the GUI layer
    is called in the expected manner with dummy data.
    """
    w = Window()
    w.main_view = mock.MagicMock()
    mock_conview = mock.MagicMock()
    mock_source = mock.MagicMock()
    mock_source.journalistic_designation = 'Testy McTestface'
    with mock.patch('securedrop_client.gui.main.ConversationView',
                    mock_conview):
        w.show_conversation_for(mock_source)
    conv = mock_conview()
    assert conv.add_message.call_count > 0
    assert conv.add_reply.call_count > 0


def test_set_status():
    """
    Ensure the status bar's text is updated.
    """
    w = Window()
    w.status_bar = mock.MagicMock()
    w.set_status('hello', 100)
    w.status_bar.showMessage.assert_called_once_with('hello', 100)

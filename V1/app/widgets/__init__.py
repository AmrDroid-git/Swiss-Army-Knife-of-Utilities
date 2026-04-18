# FLEXIBLE CUSTOM COMPONENTS

from .base_widget import BaseComponent

# Subfolder modules
from .button import WidgetButton
from .console_window import WidgetConsole, WidgetInteractiveConsole
from .label import WidgetLabel

from .text_widgets import WidgetIText, WidgetOText
from .file_link_widgets import WidgetIFileLink, WidgetOFileLink
from .folder_link_widgets import WidgetIFolderLink, WidgetOFolderLink

__all__ = [
    "BaseComponent",
    "WidgetButton",
    "WidgetConsole",
    "WidgetInteractiveConsole",
    "WidgetLabel",
    "WidgetIText",
    "WidgetOText",
    "WidgetIFileLink",
    "WidgetOFileLink",
    "WidgetIFolderLink",
    "WidgetOFolderLink"
]

from __future__ import (unicode_literals, division, absolute_import, print_function)
from calibre.customize import StoreBase

__license__ = 'GPL 3'
__copyright__ = '2015, Sergey Kuznetsov <clk824@gmail.com>; 2025, Oleksandr Makarenko <makarenko.dev@icloud.com>'
__docformat__ = 'restructuredtext en'

class FlibustaStore(StoreBase):
    """Development environment requirements for the project:
        - Calibre version: >= 8.4.0
        - Python version: >=3.8.5
        """
    name = 'Flibusta'
    title = name
    version = (1, 0, 0)
    author = 'Sergey Kuznetsov, Eduard Ryzhov, Alexander Bykov, Oleksandr Makarenko'
    supported_platforms = ['windows', 'osx', 'linux']
    description = (
        'A fork of Flibusta plugin that allows downloading books from flibusta.is '
        'with additional improvements (Original by: Sergey Kuznetsov et al). '
        '(Calibre version: >= 8.4.0).')
    minimum_calibre_version = (8, 4, 0)
    actual_plugin = 'calibre_plugins.store_flibusta.flibusta:FlibustaStore'


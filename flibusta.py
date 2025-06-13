from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__ = 'GPL 3'
__copyright__ = '2015, Sergey Kuznetsov <clk824@gmail.com>; 2025, Oleksandr Makarenko <makarenko.dev@icloud.com>'
__docformat__ = 'restructuredtext en'

from contextlib import closing
from qt.core import QUrl
from calibre import browser, guess_extension
from calibre.gui2 import open_url
from calibre.utils.xml_parse import safe_xml_fromstring
from calibre.gui2.store import StorePlugin
from calibre.gui2.store.search_result import SearchResult
from calibre.gui2.store.web_store_dialog import WebStoreDialog
from calibre.utils.opensearch.description import Description
from calibre.utils.opensearch.query import Query

class FlibustaStore(StorePlugin):
    open_search_url = 'https://github.com/omcode-ua/flibusta-calibre-opds-store/main/opds-opensearch.xml'
    web_url = 'https://flibusta.site/'

    def open(self, parent=None, detail_item=None, external=False):
        url = detail_item if detail_item else self.web_url

        if external or self.config.get('open_external', False):
            open_url(QUrl(url))
        else:
            dialog = WebStoreDialog(self.gui, self.web_url, parent, detail_item, create_browser=self.create_browser)
            dialog.setWindowTitle(self.name)
            dialog.set_tags(self.config.get('tags', ''))
            dialog.exec()

    def search(self, query, max_results=10, timeout=60):
        if not self.open_search_url:
            return
        yield from self._open_search(self.open_search_url, query, max_results, timeout)

    @staticmethod
    def _open_search(url, query, max_results, timeout):
        description = Description(url)
        url_template = description.get_best_template()
        if not url_template:
            return

        oquery = Query(url_template)
        oquery.searchTerms = query
        oquery.count = max_results
        search_url = oquery.url()

        br = browser()
        with closing(br.open(search_url, timeout=timeout)) as f:
            doc = safe_xml_fromstring(f.read())

        counter = max_results
        for data in doc.xpath('//*[local-name() = "entry"]'):
            if counter <= 0:
                break
            counter -= 1
            yield FlibustaStore._parse_entry(data)

    @staticmethod
    def _parse_entry(data):
        s = SearchResult()
        s.detail_item = ''.join(data.xpath('./*[local-name() = "id"]/text()')).strip()
        s.downloads = {}

        for link in data.xpath('./*[local-name() = "link"]'):
            rel = link.get('rel', '')
            href = link.get('href', '')
            type_ = link.get('type', '')

            if not (rel and href):
                continue

            if 'thumbnail' in rel:
                s.cover_url = href
            elif 'acquisition/buy' in rel:
                s.detail_item = href
            elif 'alternate' in rel:
                s.detail_item = FlibustaStore.web_url + href
            elif 'acquisition' in rel and type_:
                ext = FlibustaStore._custom_guess_extension(type_)
                if ext:
                    s.downloads[ext] = FlibustaStore.web_url + href

        s.formats = ', '.join(s.downloads.keys()).strip()
        s.title = ' '.join(data.xpath('./*[local-name() = "title"]//text()')).strip()
        s.author = ', '.join(data.xpath('./*[local-name() = "author"]//*[local-name() = "name"]//text()')).strip()
        s.price = '$0.00'
        s.drm = SearchResult.DRM_UNLOCKED

        return s

    @staticmethod
    def _custom_guess_extension(type_):
        ext = guess_extension(type_)
        if ext:
            return ext[1:].upper().strip()
        if 'application/fb2' in type_:
            return 'FB2'
        if 'application/epub' in type_:
            return 'EPUB'
        if 'application/mobi' in type_:
            return 'MOBI'
        return None
import asyncio
import re
from decimal import Decimal
from urllib.parse import quote

from app.models import BaseParser, Offer, Seller, tag_strip


class Parser(BaseParser):
    _DOMAIN = "http://angrybottlegnome.ru/"
    _SEARCH = "/shop/search/{}"

    CURRENCY_CODE = "RUB"

    def __parse_offers_from_card_page(self, page):
        offers = []
        card_name = tag_strip(page.select_one('h1'))
        seller = Seller(name="Angrybottlegnome", link=self._DOMAIN)
        for row in page.select(".abg-card-version-instock, .abg-card-version-outofstock"):
            match = re.match( r'(\w+), +([\w\/]+) +(\w*)\s?\((\d+).+: (\d+)\)', tag_strip(row))
            offers.append(
                Offer(
                    card_name=card_name,
                    language=match.group(1).lower(),
                    is_foil=match.group(3) == "Фойл",
                    condition=match.group(2),
                    link=self._get_full_url(self._SEARCH.format(quote(card_name))),
                    price=Decimal(match.group(4)),
                    currency_code=self.CURRENCY_CODE,
                    amount=int(match.group(5)),
                    seller=seller
                )
            )
        return offers

    def __parse_search_table(self, table):
        links = []
        for row in table.select('tbody tr'):
            cols = row.select('td')
            if tag_strip(cols[2]) != 0:
                links.append(cols[0].select_one('a').attrs['href'])
        
        return links

    async def _get_offers_page(self, search):
        return await self._get_page(self._SEARCH.format(quote(search)))

    async def parse_card_offers(self, card):
        offers = []
        page = await self._get_offers_page(card)
        table = page.select_one('#search-results table')
        if table is None:
            return {}
        available_cards = self.__parse_search_table(table)

        pages = await asyncio.gather(*[self._get_page(link) for link in available_cards])

        for page in pages:
            offers += self.__parse_offers_from_card_page(page)
        
        return {card: offers}
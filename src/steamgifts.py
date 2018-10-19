#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
#
# The stlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import contextlib
from typing import NamedTuple, List, Dict, Any, Optional

import aiohttp
import bs4
from stlib import webapi


class UserInfo(NamedTuple):
    points: int
    level: int


class GiveawayInfo(NamedTuple):
    name: str
    copies: int
    points: int
    level: int
    query: str
    id: str


class ConfigureError(Exception): pass


class GiveawayEndedError(Exception): pass


class NoGiveawaysError(Exception): pass


class Main(webapi.SteamWebAPI):
    def __init__(
            self,
            session: aiohttp.ClientSession,
            server: str = 'https://www.steamgifts.com',
            join_script: str = 'ajax.php',
            search_page: str = 'https://www.steamgifts.com/giveaways/search',
            config_page: str = 'https://www.steamgifts.com/account/settings/giveaways',
            login_page: str = 'https://steamgifts.com/?login',
            openid_url: str = 'https://steamcommunity.com/openid',
            headers: Optional[Dict[str, str]] = None,
            *args: Any,
            **kwargs: Any,
    ) -> None:
        super().__init__(session, *args, **kwargs)

        self.session = session
        self.server = server
        self.join_script = join_script
        self.search_page = search_page
        self.config_page = config_page
        self.login_page = login_page
        self.openid_url = openid_url

        if not headers:
            headers = {'User-Agent': 'Unknown/0.0.0'}

        self.headers = headers

    async def do_login(self) -> Dict[str, Any]:
        async with self.session.get(self.login_page, headers=self.headers) as response:
            html = bs4.BeautifulSoup(await response.text(), 'html.parser')
            form = html.find('form')
            data = {}

            if not form:
                if 'Suspensions' in html.find('a', class_='nav__button'):
                    raise webapi.LoginError('Unable to login, user is suspended.')

            for input_ in form.findAll('input'):
                with contextlib.suppress(KeyError):
                    data[input_['name']] = input_['value']

        async with self.session.post(f'{self.openid_url}/login', headers=self.headers, data=data) as response:
            avatar = bs4.BeautifulSoup(await response.text(), 'html.parser').find('a', class_='nav__avatar-outer-wrap')

            if avatar:
                json_data = {'success': True, 'nickname': avatar['href'].split('/')[2]}
            else:
                raise webapi.LoginError('Unable to log-in on steamgifts')

            json_data.update(data)

            return json_data

    async def configure(self) -> None:
        async with self.session.get(self.config_page) as response:
            html = bs4.BeautifulSoup(await response.text(), 'html.parser')

        form = html.find('form')
        data = {}

        for input_ in form.findAll('input'):
            with contextlib.suppress(KeyError):
                data[input_['name']] = input_['value']

        post_data = {
            'xsrf_token': data['xsrf_token'],
            'filter_giveaways_exist_in_account': 1,
            'filter_giveaways_missing_base_game': 1,
            'filter_giveaways_level': 1
        }

        try:
            # if status != 200, session will raise an exception
            await self.session.post(self.config_page, data=post_data)
        except aiohttp.ClientResponseError:
            raise ConfigureError from None

    async def get_user_info(self) -> UserInfo:
        async with self.session.get(self.server) as response:
            html = bs4.BeautifulSoup(await response.text(), 'html.parser')

        points = html.find('span', class_="nav__points")
        level = html.find('span', class_=None)

        return UserInfo(int(points.text), int(''.join(filter(str.isdigit, level.text))))

    async def get_giveaways(self, giveaway_type: str) -> List[GiveawayInfo]:
        if giveaway_type == "main":
            search_query = ''
        else:
            search_query = f"?type={giveaway_type}"

        async with self.session.get(f'{self.search_page}{search_query}') as response:
            html = bs4.BeautifulSoup(await response.text(), 'html.parser')

        container = html.find('div', class_='widget-container')
        head = container.find('div', class_='page__heading')
        giveaways_raw = head.findAllNext('div', class_='giveaway__row-outer-wrap')
        giveaways = []

        with contextlib.suppress(AttributeError):
            pinned = container.find('div', class_='pinned-giveaways__outer-wrap')
            giveaways_raw += pinned.findAll('div', class_='giveaway__row-outer-wrap')

        for giveaway in giveaways_raw:
            if giveaway.find('div', class_='is-faded'):
                continue

            temp_head = giveaway.find('a', class_='giveaway__heading__name')
            name = temp_head.text
            query = temp_head['href']
            id = temp_head['href'].split('/')[2]

            temp_head = giveaway.find('span', class_='giveaway__heading__thin')

            if 'Copies' in temp_head.text:
                copies = int(''.join(filter(str.isdigit, temp_head.text)))
                temp_head = temp_head.findNext('span', class_='giveaway__heading__thin')
                points = int(''.join(filter(str.isdigit, temp_head.text)))
            else:
                copies = 1
                points = int(''.join(filter(str.isdigit, temp_head.text)))

            try:
                level_column = giveaway.find('div', class_='giveaway__column--contributor-level')
                level = int(''.join(filter(str.isdigit, level_column.text)))
            except AttributeError:
                level = 0

            giveaways.append(GiveawayInfo(name, copies, points, level, query, id))

        return giveaways

    async def join(self, giveaway: GiveawayInfo) -> bool:
        async with self.session.get(f'{self.server}{giveaway.query}') as response:
            soup = bs4.BeautifulSoup(await response.text(), 'html.parser')

        if not soup.find('a', class_='nav__avatar-outer-wrap'):
            raise webapi.LoginError("User is not logged in")

        sidebar = soup.find('div', class_='sidebar')
        form = sidebar.find('form')

        if not form:
            raise GiveawayEndedError("Giveaway is already ended.")

        data = {}

        try:
            for input_ in form.findAll('input'):
                with contextlib.suppress(KeyError):
                    data[input_['name']] = input_['value']
        except AttributeError:
            raise NoGiveawaysError("No giveaways available to join.")

        post_data = {
            'xsrf_token': data['xsrf_token'],
            'do': 'entry_insert',
            'code': data['code'],
        }

        async with self.session.post(
                f'{self.server}/{self.join_script}',
                data=post_data,
                headers=self.headers,
        ) as response:
            if 'success' in await response.text():
                return True
            else:
                return False

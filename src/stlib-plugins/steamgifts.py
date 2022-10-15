#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2022
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
import logging
from typing import NamedTuple, List, Dict, Any

import aiohttp
from stlib import login, utils

log = logging.getLogger(__name__)


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


class ConfigureError(Exception):
    pass


class GiveawayEndedError(Exception):
    pass


class NoGiveawaysError(Exception):
    pass


class NoPointsError(Exception):
    pass


class NoLevelError(Exception):
    pass


class UserSuspended(login.LoginError):
    pass


class TooFast(login.LoginError):
    pass


class PrivateProfile(login.LoginError):
    pass


class Main(utils.Base):
    def __init__(
            self,
            *args: Any,
            server: str = 'https://www.steamgifts.com',
            join_script: str = 'ajax.php',
            search_page: str = 'https://www.steamgifts.com/giveaways/search',
            config_page: str = 'https://www.steamgifts.com/account/settings/giveaways',
            login_page: str = 'https://steamgifts.com/?login',
            openid_url: str = 'https://steamcommunity.com/openid',
            **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.server = server
        self.join_script = join_script
        self.search_page = search_page
        self.config_page = config_page
        self.login_page = login_page
        self.openid_url = openid_url
        self.user_info = UserInfo(0, 0)

    async def do_login(self) -> Dict[str, Any]:
        html = await self.request_html(self.login_page)
        form = html.find('form')
        data = {}

        if not form:
            nav_button = html.find('a', class_='nav__button')
            warning = html.find('div', class_='notification--warning')

            if nav_button and 'Suspensions' in nav_button.text:
                raise UserSuspended('Unable to login, user is suspended.')

            if warning and 'Please wait' in warning.text:
                raise TooFast('Wait 15 seconds before try again.')

            if warning and 'public Steam profile' in warning.text:
                raise PrivateProfile('Your profile must be public to use steamgifts.')

            raise login.LoginError('Unable to log-in on steamgifts')

        for input_ in form.findAll('input'):
            with contextlib.suppress(KeyError):
                data[input_['name']] = input_['value']

        html = await self.request_html(f'{self.openid_url}/login', data=data)
        avatar = html.find('a', class_='nav__avatar-outer-wrap')
        nav_button = html.find('a', class_='nav__button')
        warning = html.find('div', class_='notification--warning')

        # For some reason notifications can be displayed before or after login
        # So we must check for it again... not my fault. Don't remove that!
        if avatar:
            if nav_button and 'Suspensions' in nav_button.text:
                raise UserSuspended('Unable to login, user is suspended.')

            json_data = {'success': True, 'nickname': avatar['href'].split('/')[2]}
        else:
            if warning and 'public Steam profile' in warning.text:
                raise PrivateProfile('Your profile must be public to use steamgifts.')

            raise login.LoginError('Unable to log-in on steamgifts')

        json_data.update(data)

        return json_data

    async def configure(self) -> None:
        html = await self.request_html(self.config_page)
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
            await self.request(self.config_page, data=post_data)
        except aiohttp.ClientResponseError:
            raise ConfigureError from None

    async def get_giveaways(
            self,
            giveaway_type: str,
            return_unavailable: bool = False,
            pinned_giveaways: bool = True,
    ) -> List[GiveawayInfo]:
        if giveaway_type == "main":
            search_query = ''
        else:
            search_query = f"?type={giveaway_type}"

        html = await self.request_html(f'{self.search_page}{search_query}')
        user_points = int(html.find('span', class_="nav__points").text)
        user_level = int(''.join(filter(str.isdigit, html.find('span', class_=None).text)))
        self.user_info = UserInfo(user_points, user_level)

        container = html.find('div', class_='widget-container')
        head = container.find('div', class_='page__heading')
        giveaways_raw = head.findAllNext('div', class_='giveaway__row-outer-wrap')
        giveaways = []

        if pinned_giveaways:
            with contextlib.suppress(AttributeError):
                pinned = container.find('div', class_='pinned-giveaways__outer-wrap')
                giveaways_raw += pinned.findAll('div', class_='giveaway__row-outer-wrap')

        for giveaway in giveaways_raw:
            if giveaway.find('div', class_='is-faded'):
                continue

            temp_head = giveaway.find('a', class_='giveaway__heading__name')
            name = temp_head.text[:22] + '...'
            query = temp_head['href']
            id_ = temp_head['href'].split('/')[2]

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

            if not return_unavailable and (user_level < level or user_points < points):
                log.warning("Ignoring %s because user don't have all the requirements to join.", id_)
            else:
                giveaways.append(GiveawayInfo(name, copies, points, level, query, id_))

        return giveaways

    async def join(self, giveaway: GiveawayInfo) -> bool:
        if self.user_info.level < giveaway.level:
            raise NoLevelError(f"User don't have required level to join {giveaway.id}")

        if self.user_info.points < giveaway.points:
            raise NoPointsError(f"User don't have required points to join {giveaway.id}")

        html = await self.request_html(f'{self.server}{giveaway.query}')
        if not html.find('a', class_='nav__avatar-outer-wrap'):
            raise login.LoginError("User is not logged in")

        sidebar = html.find('div', class_='sidebar')
        form = sidebar.find('form')

        if not form:
            raise GiveawayEndedError(f"Giveaway {giveaway.id} is already ended.")

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

        response = await self.request(f'{self.server}/{self.join_script}', data=post_data)

        if 'success' in response.content:
            # noinspection PyProtectedMember
            self.user_info = self.user_info._replace(points=self.user_info.points - giveaway.points)
            return True

        return False

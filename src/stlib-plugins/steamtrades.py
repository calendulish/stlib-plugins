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
import json
import os
from typing import Any, Dict, NamedTuple

from bs4 import BeautifulSoup
from stlib import login, utils


class TradeInfo(NamedTuple):
    id: str
    title: str
    html: BeautifulSoup


class TradeClosedError(Exception):
    def __init__(self, trade_info: TradeInfo, message: str) -> None:
        super().__init__(message)

        self.id = trade_info.id
        self.title = trade_info.title


class TradeNotReadyError(Exception):
    def __init__(self, trade_info: TradeInfo, time_left: int, message: str) -> None:
        super().__init__(message)

        self.time_left = time_left
        self.id = trade_info.id
        self.title = trade_info.title


class NoTradesError(Exception):
    pass


class UserLevelError(login.LoginError):
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
            server: str = 'https://www.steamtrades.com',
            bump_script: str = 'ajax.php',
            login_page: str = 'https://steamtrades.com/?login',
            openid_url: str = 'https://steamcommunity.com/openid',
            **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.server = server
        self.bump_script = bump_script
        self.login_page = login_page
        self.openid_url = openid_url

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
                raise PrivateProfile('Your profile must be public to use steamtrades.')

            raise login.LoginError('Unable to log-in on steamtrades')

        for input_ in form.findAll('input'):
            with contextlib.suppress(KeyError):
                data[input_['name']] = input_['value']

        html = await self.request_html(f'{self.openid_url}/login', data=data)
        avatar = html.find('a', class_='nav_avatar')
        nav_button = html.find('a', class_='nav__button')
        notification = html.find('div', class_='notification')
        warning = html.find('div', class_='notification--warning')

        # For some reason notifications can be displayed before or after login
        # So we must check for it again... not my fault. Don't remove that!
        if avatar:
            if nav_button and 'Suspensions' in nav_button.text:
                raise UserSuspended('Unable to login, user is suspended.')

            json_data = {'success': True, 'steamid': avatar['href'].split('/')[2]}
        else:
            if notification and 'Steam level' in notification.text:
                raise UserLevelError('Steam level must be greater to 1.')

            if warning and 'public Steam profile' in warning.text:
                raise PrivateProfile('Your profile must be public to use steamtrades.')

            raise login.LoginError('Unable to log-in on steamtrades')

        json_data.update(data)

        return json_data

    async def get_trade_info(self, trade_id: str) -> TradeInfo:
        response = await self.request(f'{self.server}/trade/{trade_id}/')
        id_ = response.info.url.path.split('/')[2]
        title = os.path.basename(response.info.url.path).replace('-', ' ')[:22] + '...'
        html = await self.get_html(response)
        return TradeInfo(id_, title, html)

    async def bump(self, trade_info: TradeInfo) -> bool:
        if not trade_info.html.find('a', class_='nav_avatar'):
            raise login.LoginError("User is not logged in")

        if trade_info.html.find('div', class_='js_trade_open'):
            raise TradeClosedError(trade_info, f"Trade {trade_info.id} is closed")

        form = trade_info.html.find('form')
        data = {}

        try:
            for input_ in form.findAll('input'):
                data[input_['name']] = input_['value']
        except AttributeError:
            raise NoTradesError("No trades available to bump")

        payload = {
            'code': data['code'],
            'xsrf_token': data['xsrf_token'],
            'do': 'trade_bump',
        }

        response = await self.request(f'{self.server}/{self.bump_script}', data=payload)

        if 'Please wait another' in response.content:
            error = json.loads(response.content)['popup_heading_h2'][0]
            minutes_left = int(error.split(' ')[3])
            raise TradeNotReadyError(trade_info, minutes_left, f"Trade {trade_info.id} is not ready")

        response = await self.request(f'{self.server}/trades')
        return trade_info.id in response.content

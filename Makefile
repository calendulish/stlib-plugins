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

CC := /usr/bin/gcc
PYTHON := /usr/bin/env python
INSTALL := /usr/bin/install
RM := /bin/rm
PREFIX := /usr/local
DATADIR := $(PREFIX)/share

ifeq ($(OS),Windows_NT)
	current_os := windows
else
	ifeq (patsubst CYGWIN%,Cygwin,$(shell uname))
		current_os := windows
	else ifeq (patsubst MSYS%, MSYS, $(shell uname))
		current_os := windows
	else
		current_os := linux
	endif
endif

all: build

build: clean
	$(PYTHON) -m compileall src/

install: build
ifeq ($(current_os),windows)
	@echo "Please, use install.cmd script to install plugins on Windows."
	@exit 1
endif

	$(INSTALL) -Dm644 src/__pycache__/steamtrades* $(DESTDIR)$(DATADIR)/stlib/plugins/steamtrades.pyc
	$(INSTALL) -Dm644 src/__pycache__/steamgifts* $(DESTDIR)$(DATADIR)/stlib/plugins/steamgifts.pyc

clean:
	$(RM) -rf src/__pycache__


.PHONY: clean build install

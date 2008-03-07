# First Aid Kit - diagnostic and repair tool for Linux
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


NAME := "firstaidkit"
VERSION := $(shell awk '/Version:/ { print $$2 }' firstaidkit.spec)
RELEASE := $(shell awk '/Release:/ { print $$2 }' firstaidkit.spec)

PLUGIN_PATH = plugins
# all the plugins that have a make build to run
PLUGIN_DIRS = plugin_undelete_partitions

tarball:
	git-archive --format=tar --prefix=$(NAME)-$(VERSION)/ HEAD | bzip2 -f > $(NAME)-$(VERSION).tar.bz2

rpm-all: tarball
	rpmbuild -ta $(NAME)-$(VERSION).tar.bz2
	rm -f $(NAME)-$(VERSION).tar.bz2

subdirs:
	for d in $(PLUGIN_DIRS); do make -C $(PLUGIN_PATH)/$$d build; [ $$? == 0 ] || exit 1; done

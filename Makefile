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

tarball:
	git-archive --format=tar --prefix=$(NAME)-$(VERSION)/ HEAD | bzip2 -f > $(NAME)-$(VERSION).tar.bz2

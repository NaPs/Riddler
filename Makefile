# Riddler makefile

deb_version		:= $(shell dpkg-parsechangelog | sed -ne "s/^Version: \(.*\)/\1/p")
upstream_fullname	:= $(shell python setup.py --fullname)
upstream_name		:= $(shell python setup.py --name)
upstream_version	:= $(shell python setup.py --version)
orig			:= $(upstream_name)_$(upstream_version).orig

sdist:
	python setup.py sdist

clean:
	rm -Rf dist build dotconf.egg-info debsource

debsource: sdist
	rm -Rf ./debsource/ && mkdir -p ./debsource/
	cp ./dist/$(upstream_fullname).tar.gz ./debsource/$(orig).tar.gz
	tar xf ./debsource/$(orig).tar.gz -C ./debsource/
	cp -Rf ./debian/ ./debsource/$(upstream_fullname)/
	cd ./debsource/$(upstream_fullname)/ && dpkg-buildpackage -us -uc -S

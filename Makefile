ROOT_DIR=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR=${ROOT_DIR}_build/
BIN_DIR=~/bin/
INSTALL_DIR=~/
WOOF_DIR=.woof/

build: clean
	mkdir -p ${BUILD_DIR}

	cd ${ROOT_DIR}/lib/src/ ; zip -r ${BUILD_DIR}/woof.zip *
	echo '#!/usr/bin/env python' | cat - ${BUILD_DIR}/woof.zip > ${BUILD_DIR}/woof
	chmod +x ${BUILD_DIR}/woof
	#rm ${BUILD_DIR}/woof.zip

	echo "woof built"

install: build
	mkdir -p ${BIN_DIR}
	mkdir -p ${WOOF_DIR}
	mkdir -p ${WOOF_DIR}/log

	cp -v ${ROOT_DIR}/lib/helpers/woof ${BIN_DIR}
	cp -v ${BUILD_DIR}/woof ${INSTALL_DIR}${WOOF_DIR}

uninstall:
	rm ${BIN_DIR}/woof
	rm ${INSTALL_DIR}${WOOF_DIR} -rf

backup:
	mkdir ~/woof_backup/
	mkdir ~/woof_backup/bin/
	mkdir ~/woof_backup/.woof/
	cp ~/bin/woof ~/woof_backup/bin/
	cp -r ~/.woof/* ~/woof_backup/.woof/
	cd ~ ; zip -r woof_backup.zip woof_backup/
	rm -r ~/woof_backup/

restore:
	cd ~ ; unzip woof_backup.zip
	cp -f ~/woof_backup/bin/woof ~/bin/
	cp -fr ~/woof_backup/.woof ~/.woof
	rm -r ~/woof_backup/
	rm -r ~/woof_backup.zip

clean:
	rm ${BUILD_DIR} -rf

clean-tests:
	./tools/cleanup

test: backup install run-tests clean-tests restore
	woof unmin
	woof restore

run-tests:
	./tools/test
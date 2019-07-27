ROOT_DIR=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR=${ROOT_DIR}_build/
BIN_DIR=~/bin/
INSTALL_DIR=/usr/bin/
USER_DIR=~/.woof/
VERSION=`cat ${ROOT_DIR}version`

PACKAGE_NAME=woof_v${VERSION}
build: clean
	mkdir -p ${BUILD_DIR}

	cd ${ROOT_DIR}/lib/src/ ; zip -r ${BUILD_DIR}/woof.zip *
	echo '#!/usr/bin/env python' | cat - ${BUILD_DIR}/woof.zip > ${BUILD_DIR}/woof
	chmod +x ${BUILD_DIR}/woof
	rm ${BUILD_DIR}/woof.zip

	echo "Version: ${VERSION}"
	echo "Package name: ${PACKAGE_NAME}"
	mkdir ${BUILD_DIR}${PACKAGE_NAME}/
	mkdir ${BUILD_DIR}${PACKAGE_NAME}/config/
	mkdir ${BUILD_DIR}${PACKAGE_NAME}/layouts/
	cp ${BUILD_DIR}woof ${BUILD_DIR}${PACKAGE_NAME}/
	cp -r ${ROOT_DIR}config ${BUILD_DIR}${PACKAGE_NAME}/
	cp -r ${ROOT_DIR}layouts ${BUILD_DIR}${PACKAGE_NAME}/
	cp ${ROOT_DIR}/README.org ${BUILD_DIR}${PACKAGE_NAME}/
	cd ${BUILD_DIR} ; zip -r ${PACKAGE_NAME}.zip ${PACKAGE_NAME}
	rm ${BUILD_DIR}${PACKAGE_NAME} -rf

	mkdir -p ${BUILD_DIR}tmp
	mv ${BUILD_DIR}woof ${BUILD_DIR}tmp/

	echo "woof built"

install: build
	mkdir -p ${INSTALL_DIR}
	mkdir -p ${USER_DIR}
	mkdir -p ${USER_DIR}/log
	mkdir -p ${USER_DIR}/status

	cp -v ${BUILD_DIR}tmp/woof ${INSTALL_DIR}

uninstall:
	rm ${INSTALL_DIR}/woof

backup:
	mkdir ~/woof_backup/
	mkdir ~/woof_backup/bin/
	mkdir ~/woof_backup/.woof/
	cp ~/bin/woof ~/woof_backup/bin/
	cp -r ~/.woof/* ~/woof_backup/.woof/
	cd ~ ; tar -cvf woof_backup.tar woof_backup/
	rm -r ~/woof_backup/

restore:
	cd ~ ; tar -xvf woof_backup.tar
	mkdir -p ~/.woof/
	cp -f ~/woof_backup/bin/woof ~/bin/
	cp -fr ~/woof_backup/.woof/* ~/.woof/
	rm -r ~/woof_backup/
	rm ~/woof_backup.tar

clean:
	rm ${BUILD_DIR} -rf

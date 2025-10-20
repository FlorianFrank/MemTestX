#!/usr/bin/bash

echo "***************************************"
echo "********** Build PS Firmware **********"
echo "***************************************"

BUILD_DIR="./build"

 if [ ! -x "$BUILD_DIR" ]; then
   echo "Create build dir: $BUILD_DIR"
   mkdir -p $BUILD_DIR
 else
   echo "Build Dir already exist -> Recreate"
   rm -r $BUILD_DIR
   mkdir -p $BUILD_DIR
 fi

 pushd $BUILD_DIR
  cmake ../memory_controller
  make
 popd

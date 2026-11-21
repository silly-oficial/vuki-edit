ARCHS = arm64
TARGET = iphone:clang:latest:16.0
THEOS_PACKAGE_SCHEME = rootless
TOOL_NAME = natorgamerd
natorgamerd_FILES = main.m
natorgamerd_FRAMEWORKS = Foundation
natorgamerd_LIBRARIES = proc
natorgamerd_CFLAGS = -fobjc-arc -Wall -Wextra
include $(THEOS)/makefiles/common.mk
include $(THEOS_MAKE_PATH)/tool.mk

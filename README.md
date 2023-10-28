# Kwix

Kwix provides mouseless quick actions for desktop, like Double Shift in Intellij IDEA or ctrl+shift+P in VSCode.
It can be used to quickly perform frequently used actions which are too numerous to configure hot keys for them.

## Usage

By default, kwix is configured to activate on `Ctrl+;` hotkey.
Kwix also runs embedded web-server on default port 23844 and can be activated by `curl -X POST http://127.0.0.1:23844/activate`




## Build on Linux

	`cd kwix && sh build-pyproject && sh build-pyinstaller`

## Build on Windows

The procedure is awfull, sorry for that.

-	install [msys2](https://www.msys2.org/) and open "MSYS2 MINGW64" command prompt

-	install `pacman -S --noconfirm python mingw-w64-x86_64-python-pip mingw-w64-x86_64-python-gobject mingw-w64-x86_64-python-cairo mingw-w64-x86_64-python-pillow'
	(when installing pygobject with pacman in msys2, set pygopject version in pyproject.toml equal to actually installed, sorry for that)

-	do `cd kwix; USE_VENV=false sh build-pyinstaller` (this [article](https://snarky.ca/why-you-should-use-python-m-pip/) can be helpfull for understanding)


If errors, the following can be helpful.

-	do `pacman -S mingw-w64-x86_64-pkg-config mingw-w64-x86_64-python3-cairo mingw-w64-x86_64-toolchain mingw-w64-x86_64-python-cairo gcc mingw-w64-x86_64-python-pillow`

-	If got error somethins like this:

		Package glib-2.0 was not found in the pkg-config search path.
		Perhaps you should add the directory containing `glib-2.0.pc'
		to the PKG_CONFIG_PATH environment variable

	then do `PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/mingw64/lib/pkgconfig:`

-	do `export SETUPTOOLS_USE_DISTUTILS=stdlib` as in [tutorial](https://www.msys2.org/news/#2021-12-21-potential-incompatibilities-with-newer-python-setuptools)

-	[this tutorial](https://pygobject.readthedocs.io/en/latest/devguide/dev_environ.html#windows-logo-windows)

		pacman -S --needed --noconfirm base-devel mingw-w64-x86_64-toolchain git \
			mingw-w64-x86_64-python3 mingw-w64-x86_64-python3-cairo \
			mingw-w64-x86_64-gobject-introspection mingw-w64-x86_64-libffi


## todo

	fix paste into selection query entry bug
	folders
	obsidian daily note
	Read the SSL Certificate information from a remote server
	save action selector query in cache
	save selectors between activations
	ctrl+home & ctrl+end
	restart action
	rename kwix.Ui.destroy to stop?
	rename kwix.ui.Selector.go to show
	--collect-data TKinterModernThemes
	if activation event fired when window already on screen, activate it and bring to foreground
	fix freeze when interrupt signal received (Ctrl+C in shell)
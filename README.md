# kvix

kvix provides mouseless quick actions for desktop, like Double Shift in Intellij IDEA or ctrl+shift+P in VSCode.
It can be used to quickly perform frequently used actions which are too numerous to configure hot keys for them.

## Usage

By default, kvix is configured to activate on `Ctrl+;` hotkey.
kvix also runs embedded web-server on default port 23844 and can be activated by `curl -X POST http://127.0.0.1:23844/activate`




## Build on Linux

	`cd kvix && sh run pyproject pyinstaller`

## Build on Windows

The procedure is awfull, sorry for that.

-	install [msys2](https://www.msys2.org/) and open "MSYS2 MINGW64" command prompt

-	install python & pip: `pacman --sync --noconfirm mingw-w64-x86_64-python mingw-w64-x86_64-python-pip`

-	install specific versions of prebuild libraries which cannot be installed with pip

		pacman --noconfirm --upgrade \
			https://repo.msys2.org/mingw/mingw64/mingw-w64-x86_64-python-gobject-3.46.0-1-any.pkg.tar.zst \
			https://repo.msys2.org/mingw/mingw64/mingw-w64-x86_64-python-cairo-1.25.1-1-any.pkg.tar.zst \
			https://repo.msys2.org/mingw/mingw64/mingw-w64-x86_64-python-pillow-10.1.0-1-any.pkg.tar.zst

-	do `cd kvix; USE_VENV=false sh run msys2pyinstaller` (this [article](https://snarky.ca/why-you-should-use-python-m-pip/) can be helpfull for understanding)


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


## Development

### Visual Studio Code configuration

Use launch configuration `.vscode/launch.json`:

	{
		"version": "0.2.0",
		"configurations": [
			
			{
				"name": "debug kvix gui",
				"type": "python",
				"request": "launch",
				"code": "import sys; sys.path.insert(0,'./src'); import kvix.app; kvix.app.main()",
				"justMyCode": false
			}
		]
	}



## todo

	fix paste into selection query entry bug
	folders
	obsidian daily note
	Read the SSL Certificate information from a remote server
	save action selector query in cache
	save selectors between activations
	ctrl+home & ctrl+end
	restart action
	rename kvix.Selector.go to activate
	rename kvix.Ui.destroy to stop?
	rename kvix.ui.Selector.go to show
	--collect-data TKinterModernThemes
	if activation event fired when window already on screen, activate it and bring to foreground
	fix freeze when interrupt signal received (Ctrl+C in shell)
	on windows set focus when show window
	https://stackoverflow.com/questions/22751100/tkinter-main-window-focus
	fix new case action if clipboard is empty
	hide kvix after all windows loose focus
	separate dialog to select action for editing
	fix paste if entry has text
	fix clipboard https://stackoverflow.com/questions/21944895/running-powershell-script-within-python-script-how-to-make-python-print-the-pow
	control systemctl services
	find local files
	run desktop files
	show actions that `query_match(query, action.title)` above those that `query_match(query, action.action_type.title)` above others
	open two clipboard contents in diff program
	if top line in selector results selected, arrow up should select bottom line
	(list cases to open in action selector)
	Shift+F10 to open context menu of selected element
	прятать окно при потере фокуса
	сделать упорядочивание списка результатов в селекторе
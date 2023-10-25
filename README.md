# Kwix

Kwix provides mouseless quick actiones for desktop, like Double Shift in Intellij IDEA or ctrl+shift+P in VSCode.
It can be used to quickly perform frequently used actions which are too numerous to configure hot keys for them.

## Usage

By default, kwix is configured to activate on `Ctrl+;` hotkey.
Kwix also starts embedded web-server on default port 23844 and can be activated by send POSTING

	curl -X POST http://127.0.0.1:23844/activate






## Dev info

	sudo apt install pkg-config libcairo2-dev libgirepository1.0-dev


todo:
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
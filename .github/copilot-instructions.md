<!-- GitHub Copilot / AI Agent instructions for contributors and coding agents -->
# Quick agent guide for kvix

Purpose: help an AI coding agent become productive quickly in this codebase — where to look, how the app is structured, and concrete patterns to follow.

**Big picture**
- **What kvix is:** a desktop quick-action launcher (keyboard hotkeys + embedded HTTP activation). See top-level README.md for usage and build notes.
- **Runtime flow:** `run.py` boots `src/kvix/app.py::main()` which either forwards remote commands or starts `App.run()` to initialize config, action storages, action registry, plugins and UI.

**Major components & where to read them**
- App orchestration: [src/kvix/app.py](src/kvix/app.py)
- Core abstractions (Action, ActionType, Plugin, Selector, Ui): [src/kvix/impl.py](src/kvix/impl.py)
- Plugin helpers & loader: [src/kvix/plugin/impl.py](src/kvix/plugin/impl.py) and builtin plugins in [src/kvix/plugin/builtin](src/kvix/plugin/builtin)
- Remote control (embedded web server + client): [src/kvix/remote.py](src/kvix/remote.py)
- Storage helpers (Yaml file-backed stor): [src/kvix/stor.py](src/kvix/stor.py)
- UI implementations: [src/kvix/ui](src/kvix/ui)
- CLI / packaging hints: `pyproject.toml` and README.md (packaging uses pyinstaller/appimage entries).

**Key design patterns to preserve**
- Action model: actions are configured as dicts with a required `type` field. ActionType implementations expose `action_from_config` / `create_default_action`. See `BaseActionType` and `BaseActionRegistry` in [src/kvix/impl.py](src/kvix/impl.py).
- Plugins: modules expose a `Plugin` class subclassing `kvix.Plugin`. Agents adding plugins should follow the `FromModule`/`FromModules` pattern and register `ActionType` and actions through that interface. See [src/kvix/plugin/impl.py](src/kvix/plugin/impl.py) and the `builtin` folder for examples.
- UI thread model: UIs use a `ThreadRouter` abstraction and `Ui.on_ready` callbacks; avoid blocking the mainloop and use `_exec_in_mainloop` when interacting with UI from other threads. See `BaseUi` in [src/kvix/impl.py](src/kvix/impl.py) and `ui/tk` implementation.
- Localization: strings use `kvix.l10n._().setup(...)` patterns; don't hardcode UI text.

**Developer workflows / commands**
- Run locally (dev): `python run.py` (this prepends `./src` on sys.path and calls `kvix.app.main()`).
- Debug in VSCode: the README contains a `launch.json` example that runs `kvix.app.main()` with `./src` on `sys.path`.
- Build (Linux): README build steps — `cd kvix && sh run pyproject pyinstaller` (install prerequisites first).
- Tests: `pytest` will run tests under `test/` (see `pyproject.toml` test config).

**Project-specific conventions**
- Config/storage: YAML storages live under a data/config/cache dir resolved by `kvix.util.get_config_dir()` / `get_data_dir()`; code expects `YamlFile` semantics (load/save dicts/lists).
- Action config shape: required `type`, plus `title`, optional `description`, `pattern`, and action-specific keys. When producing configs, use `Action.to_config()` to preserve structure.
- Property helpers: classes expose `Propty` and `setup()` patterns used across the codebase — follow existing patterns when adding config entries or UI fields.

**Integration & external dependencies**
- Hotkeys: uses `pynput` GlobalHotKeys for global key binding in `app.py`.
- System tray: `pystray` via `kvix.ui.tray`.
- GTK/GObject/Tk: UI requires `pygobject` (Linux) or tkinter implementation. Packaging requires native libs (see README prerequisites).
- Remote activation: HTTP on port 23844 (embedded server). RemoteClient/Server are the integration points — don't change URLs/commands without updating `app.run()` behavior.

**Concrete examples agents should use/modify**
- To add a new action type: subclass `ActionType` patterns in `impl.py` and implement `action_from_config` + editor with `create_editor`.
- To declare a plugin: follow builtins in `src/kvix/plugin/builtin/*` — expose `Plugin` class and register ActionType(s).
- To change startup behavior: modify `src/kvix/app.py::run()`; remote commands are parsed via `-r/--remote` and map to `RemoteCommand`.

**Safety and non-goals for automated edits**
- Avoid changing global hotkey defaults or server port silently — these affect running user instances.
- Do not reformat localization text or change `l10n` keys without updating usages.

If anything in this guide is unclear or you want more focused sections (e.g., plugin authoring examples or test harness details), tell me which area to expand.

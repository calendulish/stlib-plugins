Official stlib plugins
======================

[![build status](https://badges.lara.monster/calendulish/.github/stlib-plugins-build)](https://github.com/calendulish/stlib-plugins/actions/workflows/build.yml)
[![Quality](https://api.codiga.io/project/34835/score/svg)](https://app.codiga.io/hub/project/34835/stlib-plugins)
[![GitHub license](https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat)](https://www.gnu.org/licenses/gpl-3.0.html)

Current plugins:

- SteamTrades
- SteamGifts

How to Create Plugins
=====================

Just create a new class by extending the class `utils.Base` from `stlib`.  
Nothing special here, you can use stlib-plugins as an example.

How to Use Plugins
==================

```python
from stlib import plugins

# You can modify the default search path prior the plugin manager initialization
# Must be called before use any method from 'plugins' module
# Warning: Your custom search paths will take precedence over default search paths
plugins.add_search_paths(<mypath>, <anotherpath>, ...)

# You can get a list of all available plugins
all_plugins = plugins.get_available_plugins()

# You can check if there has a plugin called <plugin_name>
if plugins.has_plugin(<plugin_name>):
   # So you can load the plugin by plugin name
   plugin = plugins.get_plugin(<plugin_name>)
```

Default search paths are:

```python
# For Windows:
<current_directory>\\plugins  
%LOCALAPPDATA%\\stlib\\plugins

# For Linux:
<current_directory>/plugins  
/usr/share/stlib/plugins  
$HOME/.local/share/stlib/plugins
```

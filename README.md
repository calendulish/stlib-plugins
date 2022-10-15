Official stlib plugins
======================

[![build status](https://badges.lara.monster/ShyPixie/.github/stlib-plugins-build)](https://github.com/ShyPixie/stlib-plugins/actions/workflows/build.yml)
[![Quality](https://api.codiga.io/project/34835/score/svg)](https://app.codiga.io/hub/project/34835/stlib-plugins)
[![GitHub license](https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat)](https://www.gnu.org/licenses/gpl-3.0.html)

Current plugins:

 - SteamTrades
 - SteamGifts

How to Create Plugins
=====================

You can use stlib-plugin as an example.

1) Create all files needed by your plugin as a common python module, and you're done.

How to Use Plugins
==================

```
from stlib import plugins

# Check if has a plugin called <plugin_name>
if plugins.has_plugin(<plugin_name>):
   # Load a plugin by plugin name
   plugin = plugins.get_plugin(<plugin_name>)
```

Default search paths are:

#####For Windows:
```
<current_directory>\\plugins  
%LOCALAPPDATA%\\stlib\\plugins
``` 

#####For Linux:
```
<current_directory>/plugins  
/usr/share/stlib/plugins  
$HOME/.local/share/stlib/plugins
``` 

You can modify the default search path prior the plugin manager initialization:

```
from stlib import plugins

# Must be called before use any method from 'plugins' module
plugins.add_search_paths(<mypath>, <anotherpath>, ...)
...
```

Warning: Your custom search paths will take precedence over default search paths

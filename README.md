Official stlib plugins
======================

Current plugins:

 - SteamTrades
 - SteamGifts

How to Create Plugins
=====================

You can use stlib-plugin as an example.

1) Create all files needed by your plugin as a common python module, and you're done.

2) You can specify the search path when initializing plugin manager. Default search paths are:

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

How to Use Plugins
==================

   ```
   from stlib import plugins
   
   # Check if has a plugin called <plugin_name>
   if plugins.has_plugin(<plugin_name>):
       # Load a plugin by plugin name
       plugin = plugins.get_plugin(<plugin_name>)
   ```



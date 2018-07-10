Official stlib plugins
======================

Current plugins:

 - SteamTrades

How to Create Plugins
=====================

You can use stlib-plugin as an example.

1) You just need a "stlib_plugins" entry point in your setup.py with your plugin name. E.g.:
   
   ```
   entry_points={
       'stlib_plugins': [
           'your_plugin_name = your_module',
           ...
       ]
   },
   ```

2) Create all files needed by your plugin as a common python module, and you're done.

How to Use Plugins
==================

1) stlib will automatically finds and integrates all installed plugins
2) You can use `get_plugin(<name>)` to get a plugin by name. E.g.:

   ```
   from stlib import plugins
   
   steamtrades = plugins.get_plugin("steamtrades")
   ``` 



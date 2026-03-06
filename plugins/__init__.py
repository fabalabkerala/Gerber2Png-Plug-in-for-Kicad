try:
    from .plugin import Gerber2PngPlugin
    plugin = Gerber2PngPlugin()
    plugin.register()
except Exception as e:
    import logging
    root = logging.getLogger()
    root.debug(repr(e))

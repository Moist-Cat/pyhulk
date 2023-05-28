from code import InteractiveConsole
import sys

from pyhulk import settings

banner = """
#######################################
# pyhulk interactive console #
#######################################
"""
i = InteractiveConsole(locals=locals())
i.interact(banner=banner)

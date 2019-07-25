import os
import sys

import machine

sys.path.insert(0, os.getcwd())

bot = machine.Machine()

try:
    bot.run()
except KeyboardInterrupt:
    machine.utils.text.announce("Thanks for playing!")

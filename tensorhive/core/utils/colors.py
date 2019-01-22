# More colors: https://i.stack.imgur.com/6otvY.png
red = lambda text: '\x1b[{color}m{text}{reset}'.format(color='6;30;41', text=text, reset='\x1b[0m')
orange = lambda text: '\x1b[{color}m{text}{reset}'.format(color='6;30;43', text=text, reset='\x1b[0m')
green = lambda text: '\x1b[{color}m{text}{reset}'.format(color='6;30;42', text=text, reset='\x1b[0m')

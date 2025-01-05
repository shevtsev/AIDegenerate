import re
from telebot import types

class keyboards:
    #Клавиатура с двумя кнопками
    def keyboard_two_blank(self, name: list[str], data: list[str]) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(str(name[i]), callback_data=str(data[i])) for i in range(len(data))]
        if len(buttons) % 2 == 0:
            [keyboard.add(buttons[i], buttons[i+1]) for i in range(0, len(buttons), 2)]
        else:
            [keyboard.add(buttons[i], buttons[i+1]) for i in range(0, len(buttons)-1, 2)]
            keyboard.add(buttons[-1])
        return keyboard
    
    def html_tags_insert(self, response: str) -> str:
            patterns = [(r'#### (.*?)\n', r'<h4>\1</h4>\n'), # H4
                        (r'### (.*?)\n', r'<h3>\1</h3>\n'), # H3
                        (r'## (.*?)\n', r'<h2>\1</h2>\n'), # H2
                        (r'# (.*?)\n', r'<h1>\1</h1>\n'),# H1
                        (r'```(\w+)?\n(.*?)\n```', r'<pre><code \1>\n\2\n</code></pre>'), # Code and copy
                        (r'`(.*?)`', r'<pre>\1</pre>'), # Copy field
                        (r'\*\*(.*?)\*\*', r'<i>\1</i>'), # Italic
                        (r'([*+-.=|!()_–\[\]~{}#\\`])', r'\\\1'), # Special symbols
                        (r'<i>(.*?)</i>', r'_\1_'), # Italic rewrite
                        (r'<h1>(.*?)</h1>', r'*__\1__*'), # H1 rewrite
                        (r'<h2>(.*?)</h2>', r'*_\1_*'), # H2 rewrite
                        (r'<h3>(.*?)</h3>', r'_\1_'), # H3 rewrite
                        (r'<h4>(.*?)</h4>', r'*\1*'), # H4 rewrite
                        (r'<pre><code (\w+)?>\n(.*?)\n</code></pre>', r'```\1\n\2\n```'), # Code and copy rewrite
                        (r'<pre>(.*?)</pre>', r'`\1`'), # Copy field rewrite
                        (r'([<>])', r'\\\1') # Special symbols rewrite
                        ]
            for pattern in patterns:
                response = re.sub(pattern[0], pattern[1], response, flags=re.DOTALL)
            return response

import re

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import platform, get_color_from_hex
from kivy.metrics import dp, sp

if platform not in ("android", "ios"):
    Window.size = (360, 640)

Window.clearcolor = get_color_from_hex("#14161F")

COLORS = {
    "number": "#262A3B",    
    "operator": "#5B6CFF",  
    "equals": "#2ED3A6",    
    "clear": "#FF5C7A",  
    "func": "#3A3F55",    
}


class RoundButton(Button):
    """Köşeleri yuvarlatılmış, basınca rengi açılan tuş."""

    def __init__(self, bg_hex, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.font_size = sp(26)
        self.bold = True

        self.base_color = get_color_from_hex(bg_hex)
        with self.canvas.before:
            self.bg_color = Color(*self.base_color)
            self.bg_rect = RoundedRectangle(radius=[dp(20)])

        self.bind(pos=self.update_rect, size=self.update_rect, state=self.update_color)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_color(self, *args):
        r, g, b, a = self.base_color
        if self.state == "down":
            self.bg_color.rgba = (min(r + 0.15, 1), min(g + 0.15, 1), min(b + 0.15, 1), a)
        else:
            self.bg_color.rgba = self.base_color


class Calculator(BoxLayout):
    OPERATORS = "+-×÷"

    def __init__(self, **kwargs):
        if platform == "ios":
            padding = [dp(16), dp(50), dp(16), dp(30)]
        else:
            padding = [dp(16), dp(16), dp(16), dp(16)]
        super().__init__(orientation="vertical", padding=padding, spacing=dp(12), **kwargs)

        self.expression = ""
        self.just_calculated = False

        display_box = BoxLayout(orientation="vertical", size_hint=(1, 0.3), padding=[dp(8), 0])

        self.history = Label(
            text="",
            font_size=sp(20),
            color=get_color_from_hex("#8A90A8"),
            halign="right",
            valign="bottom",
        )
        self.display = Label(
            text="0",
            font_size=sp(56),
            bold=True,
            color=(1, 1, 1, 1),
            halign="right",
            valign="middle",
            shorten=True,
            shorten_from="left", 
        )
        for label in (self.history, self.display):
            label.bind(size=lambda inst, value: setattr(inst, "text_size", value))
            display_box.add_widget(label)
        self.add_widget(display_box)

        buttons = [
            ["C", "DEL", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["00", "0", ".", "="],
        ]

        grid = GridLayout(cols=4, spacing=dp(12), size_hint=(1, 0.7))
        for row in buttons:
            for key in row:
                btn = RoundButton(bg_hex=self.color_for(key), text=key)
                btn.bind(on_press=self.on_button_press)
                grid.add_widget(btn)
        self.add_widget(grid)

    def color_for(self, key):
        if key in self.OPERATORS:
            return COLORS["operator"]
        if key == "=":
            return COLORS["equals"]
        if key == "C":
            return COLORS["clear"]
        if key in ("DEL", "%"):
            return COLORS["func"]
        return COLORS["number"]

    def on_button_press(self, instance):
        key = instance.text

        if key == "C":
            self.expression = ""
            self.history.text = ""
        elif key == "DEL":
            self.expression = self.expression[:-1]
        elif key == "=":
            self.calculate()
            return
        else:
            if self.just_calculated and key not in self.OPERATORS + "%":
                self.expression = ""
          
            if key in self.OPERATORS and self.expression and self.expression[-1] in self.OPERATORS:
                self.expression = self.expression[:-1]
            self.expression += key

        self.just_calculated = False
        self.refresh()

    def calculate(self):
        if not self.expression:
            return

        expr = (
            self.expression.replace("×", "*")
            .replace("÷", "/")
            .replace("%", "/100")
        )
        expr = re.sub(r"\b0+(?=\d)", "", expr)

        try:
            result = eval(expr)
            if isinstance(result, float):
                result = round(result, 10)
                if result.is_integer():
                    result = int(result)
            self.history.text = self.expression + " ="
            self.expression = str(result)
            self.refresh()
        except Exception:
            # Sıfıra bölme, yarım kalmış işlem vb.
            self.history.text = self.expression
            self.expression = ""
            self.display.text = "Hata"

        self.just_calculated = True

    def refresh(self):
        self.display.text = self.expression or "0"


class CalculatorApp(App):
    def build(self):
        self.title = "Hesap Makinesi"
        return Calculator()


if __name__ == "__main__":
    CalculatorApp().run()

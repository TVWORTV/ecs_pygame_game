class DigitAtlas:
    def __init__(self, font, color_normal, color_crit, color_player):
        chars = "0123456789-!"
        self.normal = {c: font.render(c, True, color_normal).convert_alpha() for c in chars}
        self.crit = {c: font.render(c, True, color_crit).convert_alpha() for c in chars}
        self.player = {c: font.render(c, True, color_player).convert_alpha() for c in chars}

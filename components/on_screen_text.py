



class OnScreenTextComponent:
    __slots__ = ("text", "is_crit", "is_player", "lifetime")

    def _set(self, text : str, crit : bool, player : bool, lifetime : float):
        self.text = text
        self.is_crit = crit 
        self.is_player = player
        self.lifetime = lifetime
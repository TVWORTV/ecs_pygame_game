import pygame

from scenes.sceneObject import *
from scenes.scene import *

from UI.button import *
from UI.text import *
from UI.color import *

from consts import *

from abilities.ability_definition import *

class AbilityObject(SceneObject):

    def __init__(
            self, 
            pos : pygame.Vector2, 
            size : pygame.Vector2, 
            button_image,button_image_hover, 
            callbacks_on_selection,
            ability_resolver, 
            name_font, 
            desc_font, 
            name_text_pos : pygame.Vector2,
            desc_text_pos : pygame.Vector2,
            ):
        super().__init__()
        self.setPosition(pos)
        self.ability_assigned = None 

        self.button = Button((0, 0, size.x, size.y), None, self.on_selection, image=button_image, hoverImage=button_image_hover)
        self.addChild(self.button)
        
        self.name_text_pos = name_text_pos
        self.desc_text_pos = desc_text_pos

        self.name_text = StaticText("", name_font, pygame.Vector2(0,0), color = Color(ABILITY_NAME_COLOR))
        self.desc_text = StaticText("", desc_font, pygame.Vector2(0,0), color = Color(ABILITY_DESC_COLOR))

        self.addChild(self.name_text)
        self.addChild(self.desc_text)

        self.callbacks = callbacks_on_selection

        self.ability_resolver = ability_resolver

    def initialize(self, ability: PlayerAbility):
        self.ability_assigned = ability 
        self.button.interactable = True 

        self.name_text.setPosition(self.name_text_pos)   
        self.desc_text.setPosition(self.desc_text_pos)  

        self.name_text.setText(ability._name)
        self.desc_text.setText(ability._description)

    def on_selection(self):
        self.button.interactable = False 
        for callback in self.callbacks:
            callback()
        if not self.ability_assigned:
            raise RuntimeError("not assigned ability that was selected")

        self.ability_resolver.on_ability_selected(self.ability_assigned)
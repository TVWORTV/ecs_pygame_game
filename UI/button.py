import pygame
from scenes.sceneObject import SceneObject
from UI.image import StaticImage
from UI.text import StaticText
from UI.color import *


class Button(SceneObject):
    def __init__(self, rect, font, on_click, text=None,
                 image=None, hoverImage=None, nineSliced=False, border=0,
                 textColor=None, worldSpace=False,
                 interactable=True
                 ):
        super().__init__()

        rect = pygame.Rect(rect)
        self.setPosition(rect.topleft)
        self.width = rect.width
        self.height = rect.height

        self.font = font
        self.textColor = textColor if textColor is not None else Color()

        self.on_click = []
        self.on_click.append(on_click)

        self.hovered = False
        self.worldSpace = worldSpace

        self.normalImage = image
        self.hoverImage = hoverImage

        self.interactable = interactable

        self.bgImage = None
        if self.normalImage is not None:
            self.bgImage = StaticImage(
                self.normalImage, (0, 0),
                size=(self.width, self.height),
                nineSliced=nineSliced, border=border
            )
            self.addChild(self.bgImage)

        self.text = text
        self.labelText = None
        if self.text is not None:
            self._createLabel(self.text)

    def _createLabel(self, text):
        textWidth, textHeight = self.font.size(text)
        localLabelPos = (
            round((self.width - textWidth) / 2),
            round((self.height - textHeight) / 2)
        )
        self.labelText = StaticText(
            text, self.font, localLabelPos,
            color=self.textColor
        )
        self.addChild(self.labelText)

    def getRect(self):
        worldPos = self.getWorldPosition()
        return pygame.Rect(worldPos.x, worldPos.y, self.width, self.height)

    def setSprite(self, sprite):
        self.bgImage.setImage(sprite)

    def setText(self, text):
        self.text = text
        if self.labelText is None:
            self._createLabel(text)
        else:
            self.labelText.setText(text)

    def addEvent(self, event, overrideAll=False):
        if overrideAll:
            self.on_click.clear()
        self.on_click.append(event)

    def getSize(self):
        return (self.width, self.height)

    def handle_event(self, event):
        rect = self.getRect()
        if event.type == pygame.MOUSEMOTION:
            wasHovered = self.hovered
            self.hovered = rect.collidepoint(event.pos)
            if self.hovered != wasHovered and self.bgImage is not None and self.interactable:
                nextImage = self.hoverImage if (self.hovered and self.hoverImage) else self.normalImage
                self.bgImage.setImage(nextImage)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.interactable:
            if rect.collidepoint(event.pos):
                for callback in self.on_click:
                    callback()

    def draw(self, screen):
        if self.bgImage is None:
            rect = self.getRect()
            color = Color((180, 180, 180, 255)) if self.hovered and self.interactable else Color((120, 120, 120, 255))
            pygame.draw.rect(screen, color.rgba, rect, border_radius=6)

        super().draw(screen)
import pygame

def draw_nine_slice(screen, image, dest_rect, border):
    w, h = image.get_size()

    if isinstance(border, (int, float)):
        bl = bt = br = bb = border
    else:
        bl, bt, br, bb = border

    dx, dy, dw, dh = dest_rect

    if bl + br > dw:
        scale = dw / (bl + br) if (bl + br) > 0 else 1
        bl, br = bl * scale, br * scale
    if bt + bb > dh:
        scale = dh / (bt + bb) if (bt + bb) > 0 else 1
        bt, bb = bt * scale, bb * scale

    bl, bt, br, bb = int(bl), int(bt), int(br), int(bb)

    src = {
        "tl": pygame.Rect(0, 0, bl, bt),
        "tr": pygame.Rect(w - br, 0, br, bt),
        "bl": pygame.Rect(0, h - bb, bl, bb),
        "br": pygame.Rect(w - br, h - bb, br, bb),
        "top":    pygame.Rect(bl, 0, w - bl - br, bt),
        "bottom": pygame.Rect(bl, h - bb, w - bl - br, bb),
        "left":   pygame.Rect(0, bt, bl, h - bt - bb),
        "right":  pygame.Rect(w - br, bt, br, h - bt - bb),
        "center": pygame.Rect(bl, bt, w - bl - br, h - bt - bb),
    }

    mid_w = max(dw - bl - br, 0)
    mid_h = max(dh - bt - bb, 0)

    # corners
    if bl and bt:
        screen.blit(image.subsurface(src["tl"]), (dx, dy))
    if br and bt:
        screen.blit(image.subsurface(src["tr"]), (dx + dw - br, dy))
    if bl and bb:
        screen.blit(image.subsurface(src["bl"]), (dx, dy + dh - bb))
    if br and bb:
        screen.blit(image.subsurface(src["br"]), (dx + dw - br, dy + dh - bb))

    # edges
    if mid_w > 0 and bt:
        screen.blit(pygame.transform.scale(image.subsurface(src["top"]), (mid_w, bt)), (dx + bl, dy))
    if mid_w > 0 and bb:
        screen.blit(pygame.transform.scale(image.subsurface(src["bottom"]), (mid_w, bb)), (dx + bl, dy + dh - bb))
    if mid_h > 0 and bl:
        screen.blit(pygame.transform.scale(image.subsurface(src["left"]), (bl, mid_h)), (dx, dy + bt))
    if mid_h > 0 and br:
        screen.blit(pygame.transform.scale(image.subsurface(src["right"]), (br, mid_h)), (dx + dw - br, dy + bt))

    # center
    if mid_w > 0 and mid_h > 0:
        screen.blit(pygame.transform.scale(image.subsurface(src["center"]), (mid_w, mid_h)), (dx + bl, dy + bt))
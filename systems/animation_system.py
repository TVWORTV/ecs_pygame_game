from typing import TYPE_CHECKING

from components.animation import *
from components.rendering import *

if TYPE_CHECKING:
    from world.world import World


def animation_system(world: "World", dt: float):
    for e in world.entities:
        anim, renderer = e.get(AnimationComponent), e.get(RenderingComponent)
        if not (anim and renderer):
            continue

        _update_state_machine(world, e, anim)
        clip = anim.clips[anim.current_clip]

        if anim.frame_index >= len(clip.frames):
            anim.frame_index = len(clip.frames) - 1

        if anim.playing and not anim.finished:
            anim.elapsed += dt
            while anim.elapsed >= clip.frame_duration:
                anim.elapsed -= clip.frame_duration
                anim.frame_index += 1

                if anim.frame_index >= len(clip.frames):
                    if clip.loop:
                        anim.frame_index = 0
                    else:
                        anim.frame_index = len(clip.frames) - 1
                        anim.playing = False
                        anim.finished = True
                        break

                _fire_frame_events(world, e, anim)

        renderer.image = clip.frames[anim.frame_index]


def _update_state_machine(world, e, anim):
    sm = anim.stateMachine
    if sm is None:
        return

    candidates = [
        t for t in sm.transitions
        if (t.from_state == anim.current_state or t.from_state == "*") and t.condition(e)
    ]
    if not candidates:
        return

    best = max(candidates, key=lambda t: t.priority)
    if best.to_state == anim.current_state:
        return

    _change_state(world, e, anim, sm, best.to_state)


def _change_state(world, e, anim, sm, new_state):
    anim.current_state = new_state
    anim.frame_index = 0
    anim.elapsed = 0.0
    anim.playing = True
    anim.finished = False
    _fire_frame_events(world, e, anim)


def _fire_frame_events(world, e, anim):
    sm = anim.stateMachine
    for call in sm.get_frame_events(anim.current_state, anim.frame_index):
        call(world, e)
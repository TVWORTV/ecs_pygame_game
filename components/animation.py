
from dataclasses import dataclass, field
from typing import Callable

from general.entity import *
from components.movement import *
from components.health import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from world.world import World

class AnimationComponent:
    __slots__ = ("state_machine_name", "stateMachine", "frame_index", "elapsed",
                 "playing", "finished", "current_state")

    def __init__(self, stateMachine, starting_clip, firstFrame=0, state_machine_name=""):
        self.stateMachine = stateMachine
        self.current_state = starting_clip
        self.frame_index = firstFrame
        self.elapsed = 0.0
        self.playing = True
        self.finished = False
        self.state_machine_name = state_machine_name

    @property
    def clips(self):
        return self.stateMachine.states

    @property
    def current_clip(self) -> str:
        return self.current_state              

    def reset(self, starting_state: str | None = None):
        self.frame_index = 0
        self.elapsed = 0.0
        self.playing = True
        self.finished = False
        if starting_state is not None:
            self.current_state = starting_state


@dataclass
class AnimationStateMachine:
    states: dict[str, "AnimationClip"]
    transitions: list["Transition"] = field(default_factory=list)
    state_machine_name: str = ""
    frame_events: list["FrameEvent"] = field(default_factory=list)
    _frame_event_lookup: dict[tuple[str, int], list[Callable]] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._rebuild_frame_event_lookup()

    def _rebuild_frame_event_lookup(self):
        self._frame_event_lookup = {}
        for fe in self.frame_events:
            key = (fe.clip, fe.frame)
            self._frame_event_lookup.setdefault(key, []).extend(fe.calls)

    def get_frame_events(self, clip: str, frame: int) -> list[Callable]:
        return self._frame_event_lookup.get((clip, frame), [])


@dataclass
class Transition:
    from_state: str
    to_state: str
    condition: Callable[["Entity"], bool]
    priority: int = 0


class AnimationClip:
    __slots__ = ("frames", "frame_duration", "loop")

    def __init__(self, frames, frame_duration=0.1, loop=True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop


def is_moving(e: "Entity") -> bool:
    move = e.get(MovementComponent)
    if not move:
        return False
    return abs(move.velocity.x) > 0.1 or abs(move.velocity.y) > 0.1


def is_idle(e: "Entity") -> bool:
    return not is_moving(e)


def is_dying(e : "Entity") -> bool:
    health = e.get(HealthComponent)
    if not health:
        return False 
    return health.dying

@dataclass
class FrameEvent:
    clip: str
    frame: int
    calls: list[Callable[["World", "Entity"], None]]


def add_event(world: "World", list_of_events: str, event) -> None:
    try:
        getattr(world, list_of_events).append(event)
    except AttributeError:
        raise AttributeError(f"World has no event list '{list_of_events}'")
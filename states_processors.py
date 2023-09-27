from time import sleep
from math import sqrt

from devices import DeviceManager
from colors import *


class States:
    MAIN_SCREEN = -1
    SENSOR_1 = 1
    SENSOR_2 = 2
    SENSOR_3 = 3
    SENSOR_4 = 4
    SENSOR_5 = 5
    SENSOR_6 = 6
    SENSOR_7 = 7
    SENSOR_8 = 8
    SENSOR_9 = 9


class Types:
    JUMP = 1
    STEP = 2


class StateMachine:
    jumps = {}
    steps = {}

    def __init__(self):
        self.current_state = None
        self.dm = DeviceManager(debug=False)

    @classmethod
    def register(cls, state: States, typ: str):
        def deco(f):
            if typ == Types.JUMP:
                if state in cls.jumps:
                    raise ValueError('state jump processor already registered')
                cls.jumps[state] = f
            elif typ == Types.STEP:
                if state in cls.steps:
                    raise ValueError('state step processor already registered')
                cls.steps[state] = f
            return f
        return deco

    def jump(self, state):
        if state in StateMachine.jumps:
            self.current_state = state
            StateMachine.jumps[state](self.dm)
        else:
            print(f'jump {state} not configured')

    def step(self):
        if not self.current_state:
            return
        if self.current_state in StateMachine.steps:
            StateMachine.steps[self.current_state](self, self.dm)
        else:
            print(f'step {self.current_state} not configured')

    def shutdown(self):
        self.dm.shutdown()
        self.current_state = None


class SquareArea:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.h = h
        self.w = w

    def draw(self, dm):
        dm.display.draw_rectangle(self.x, self.y, self.w, self.h, GREEN)

    def check(self, x, y):
        return all(
            [
                x >= self.x,
                x <= self.x + self.w,
                y >= self.y,
                y <= self.y + self.h
            ]
        )


class RoundArea:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def draw(self, dm):
        dm.display.draw_circle(self.x, self.y, self.r, GREEN)

    def check(self, x, y):
        distance = sqrt((x-self.x)**2 + (y-self.y)**2)
        return distance <= self.r


MAIN_SCREEN_AREAS = [
    {'state': States.SENSOR_1, 'area': SquareArea(21, 21, 50, 50)},
    {'state': States.SENSOR_2, 'area': SquareArea(94, 21, 50, 50)},
    {'state': States.SENSOR_3, 'area': SquareArea(167, 21, 50, 50)},
    {'state': States.SENSOR_4, 'area': SquareArea(21, 95, 50, 50)},
    {'state': States.SENSOR_5, 'area': SquareArea(94, 95, 50, 50)},
    {'state': States.SENSOR_6, 'area': SquareArea(167, 95, 50, 50)},
    {'state': States.SENSOR_7, 'area': SquareArea(21, 169, 50, 50)},
    {'state': States.SENSOR_8, 'area': SquareArea(94, 169, 50, 50)},
    {'state': States.SENSOR_9, 'area': SquareArea(167, 169, 50, 50)},
]

BACK_AREA = {'state': States.MAIN_SCREEN, 'area': SquareArea(55, 250, 130, 40)}


def check_back_button(sm, dm) -> bool:
    if dm.touch_pressed():
        x, y = dm.get_touch_coordinates()
        back_area = BACK_AREA
        if back_area['area'].check(x, y):
            sm.jump(States.MAIN_SCREEN)
            return True
    return False


@StateMachine.register(States.MAIN_SCREEN, Types.JUMP)
def main_screen_init(dm):
    dm.display.draw_image('images/main_screen.raw', 0, 0)
    if dm.debug:
        for item in MAIN_SCREEN_AREAS:
            item['area'].draw(dm)


@StateMachine.register(States.MAIN_SCREEN, Types.STEP)
def main_screen_run(sm, dm):
    if dm.touch_pressed():
        x, y = dm.get_touch_coordinates()
        for item in MAIN_SCREEN_AREAS:
            if item['area'].check(x, y):
                sm.jump(item['state'])
                break


@StateMachine.register(States.SENSOR_1, Types.JUMP)
def sensor_1_init(dm):
    dm.display.draw_image('images/dht_sensor.raw', 0, 0)
    if dm.debug:
        BACK_AREA['area'].draw(dm)


@StateMachine.register(States.SENSOR_1, Types.STEP)
def sensor_1_run(sm, dm):
    if check_back_button(sm, dm):
        return

    temperature, humidity = dm.dht_sensor.read()
    if temperature and humidity:
        dm.display.fill_circle(10, 10, 5, BLUE)
        dm.display.draw_text(120, 55, f'{temperature:.}', dm.font, YELLOW)
        dm.display.draw_text(120, 150, f'{humidity:.}', dm.font, YELLOW)
    else:
        dm.display.fill_circle(10, 10, 5, BLACK)

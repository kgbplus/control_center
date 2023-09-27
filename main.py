from time import sleep

from states_processors import StateMachine, States


class Main:
    def __init__(self):
        self.sm = StateMachine()
        self.sm.jump(States.MAIN_SCREEN)

    def run(self) -> None:
        try:
            while True:
                self.sm.step()
                sleep(.1)

        except KeyboardInterrupt:
            print("\nCtrl-C pressed.  Cleaning up and exiting...")
        finally:
            self.sm.shutdown()


main = Main()
main.run()
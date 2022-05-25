# from classes.image import Image


class StateManager:
    def __init__(self, max_states=16, initial_state=None):
        self.s = initial_state if initial_state else []
        self.cur = -1
        self.max = max_states

    def add(self, state: any):
        if len(self.s) == self.max:
            self.s.pop(0)
            self.cur -= 1

        self.cur += 1
        self.s.append(state)

    def prev(self):
        if self.cur > 0:
            changed = "input" if self.s[self.cur].input else "output"
            self.cur -= 1
            i = 0
            while self.cur - i >= 0:
                if (changed == "output" and self.s[self.cur - i].output) or (
                    changed == "input" and self.s[self.cur - i].input
                ):
                    return self.s[self.cur - i]
                i += 1
        return None

    def next(self):
        """
        Go to the next state
        """
        if self.cur < len(self.s) - 1:
            self.cur += 1
            return self.s[self.cur]
        return None


class CanvasState:
    def __init__(self, inp: any = None, out: any = None):
        self.input, self.output = inp, out

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from textx import metamodel_from_file


# ============================================================
# CONFIG
# ============================================================

OPCODE_BUCKETS = [
    (0, 25, "SET"),
    (26, 51, "ADD"),
    (130, 155, "MOD"),
    (156, 181, "PRINT"),
    (208, 233, "CMP"),
    (234, 259, "JUMP"),
    (260, 285, "JUMP_IF_FALSE"),
    (286, 311, "LABEL"),
    (312, 337, "HALT"),
]

Y_BUCKETS = [
    (0, 31, "EQ"),
    (32, 63, "NE"),
    (64, 95, "LT"),
    (96, 127, "GT"),
    (128, 159, "LE"),
    (160, 191, "GE"),
]

LETTERS = "abcdefghijklmnopqrstuvwxyz"

STRING_SYMBOLS = (
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    " 0123456789!?"
)


# ============================================================
# HELPERS
# ============================================================



def decode_letter_from_x(x: int) -> str:
    bucket_size = 512 / len(LETTERS)
    idx = min(int(x / bucket_size), len(LETTERS) - 1)
    return LETTERS[idx]


def decode_string_char_from_x(x: int) -> str:
    bucket_size = 512 / len(STRING_SYMBOLS)
    idx = min(int(x / bucket_size), len(STRING_SYMBOLS) - 1)
    return STRING_SYMBOLS[idx]


def decode_opcode_from_x(x: int) -> str:
    for lo, hi, name in OPCODE_BUCKETS:
        if lo <= x <= hi:
            return name
    raise ValueError(f"x out of opcode range: {x}")


def decode_cmp_from_y(y: int) -> str:
    for lo, hi, name in Y_BUCKETS:
        if lo <= y <= hi:
            return name.lower()
    raise ValueError(f"y out of cmp range: {y}")


def decode_slider_integer(x: int, y: int) -> int:
    return abs(x - y)


def decode_spinner_bank(start_time: int, end_time: int) -> str:
    duration = end_time - start_time

    if 1000 <= duration < 2000:
        return "NORMAL"
    if 2000 <= duration < 3000:
        return "VARIABLE"
    if 3000 <= duration < 4000:
        return "LABEL"
    if 4000 <= duration < 5000:
        return "CONTROL"
    if 5000 <= duration < 6000:
        return "STRING"

    raise ValueError(f"spinner duration out of range: {duration}")  

# ============================================================
# OSU FILE PARSING
# ============================================================

@dataclass
class HitObject:
    x: int
    y: int
    time: int
    obj_type: int
    end_time: Optional[int]
    raw: str


def read_osu_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_mode(text: str) -> Optional[int]:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("Mode:"):
            return int(line.split(":", 1)[1].strip())
    return None


def extract_hitobject_lines(text: str) -> List[str]:
    lines = text.splitlines()
    in_hitobjects = False
    hitobjects: List[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line == "[HitObjects]":
            in_hitobjects = True
            continue
        if in_hitobjects:
            hitobjects.append(line)

    return hitobjects


def parse_hitobject_line(line: str) -> HitObject:
    parts = line.split(",")

    obj_type = int(parts[3])
    end_time = None

    if (obj_type & 8) != 0:
        end_time = int(parts[5])

    return HitObject(
        x=int(parts[0]),
        y=int(parts[1]),
        time=int(parts[2]),
        obj_type=obj_type,
        end_time=end_time,
        raw=line,
    )


def parse_hitobjects(lines: List[str]) -> List[HitObject]:
    objs = [parse_hitobject_line(line) for line in lines]
    return sorted(objs, key=lambda obj: obj.time)


def is_circle(obj_type: int) -> bool:
    return (obj_type & 1) != 0


def is_slider(obj_type: int) -> bool:
    return (obj_type & 2) != 0


def is_spinner(obj_type: int) -> bool:
    return (obj_type & 8) != 0


# ============================================================
# OSU -> DSL TRANSLATOR
# ============================================================

class OsuToDslTranslator:
    def __init__(self) -> None:
        self.bank = "NORMAL"
        self.pos = 0
        self.objects: List[HitObject] = []

    def current(self) -> Optional[HitObject]:
        if self.pos >= len(self.objects):
            return None
        return self.objects[self.pos]

    def advance(self) -> Optional[HitObject]:
        obj = self.current()
        if obj is not None:
            self.pos += 1
        return obj

    def consume_spinners(self) -> None:
        while self.current() is not None and is_spinner(self.current().obj_type):
            obj = self.advance()
            if obj.end_time is None:
                raise ValueError("Spinner missing end time.")
            self.bank = decode_spinner_bank(obj.time, obj.end_time)

    def read_variable_name(self) -> str:
        self.consume_spinners()
        if self.bank != "VARIABLE":
            raise ValueError("Expected VARIABLE bank.")
        obj = self.current()
        if obj is None or not is_circle(obj.obj_type):
            raise ValueError("Expected variable circle.")
        self.advance()
        return decode_letter_from_x(obj.x)

    def read_label_name(self) -> str:
        self.consume_spinners()
        if self.bank != "LABEL":
            raise ValueError("Expected LABEL bank.")
        chars: List[str] = []
        while self.current() is not None and is_circle(self.current().obj_type):
            chars.append(decode_letter_from_x(self.advance().x))
        if not chars:
            raise ValueError("Expected label characters.")
        return "".join(chars)

    def read_cmp(self) -> str:
        self.consume_spinners()
        if self.bank != "CONTROL":
            raise ValueError("Expected CONTROL bank.")
        obj = self.current()
        if obj is None or not is_circle(obj.obj_type):
            raise ValueError("Expected control circle.")
        self.advance()
        return decode_cmp_from_y(obj.y)

    def read_string_value(self) -> str:
        self.consume_spinners()
        if self.bank != "STRING":
            raise ValueError("Expected STRING bank.")
        chars: List[str] = []
        while self.current() is not None:
            obj = self.current()
            if is_spinner(obj.obj_type):
                break
            if not is_circle(obj.obj_type):
                raise ValueError("Expected string circle.")
            chars.append(decode_string_char_from_x(obj.x))
            self.advance()
        return '"' + "".join(chars) + '"'

    def read_value(self) -> str:
        self.consume_spinners()
        obj = self.current()
        if obj is None:
            raise ValueError("Expected value, got EOF.")

        if self.bank == "STRING":
            return self.read_string_value()

        if is_slider(obj.obj_type):
            self.advance()
            return str(decode_slider_integer(obj.x, obj.y))

        if is_circle(obj.obj_type) and self.bank == "VARIABLE":
            return self.read_variable_name()

        raise ValueError("Expected slider int, variable, or string.")

    def translate(self, objects: List[HitObject]) -> str:
        self.objects = objects
        self.pos = 0
        self.bank = "NORMAL"

        lines: List[str] = ["begin"]

        while self.current() is not None:
            self.consume_spinners()
            obj = self.current()
            if obj is None:
                break

            if not is_circle(obj.obj_type) or self.bank != "NORMAL":
                self.advance()
                continue

            opcode = decode_opcode_from_x(obj.x)
            self.advance()

            if opcode == "SET":
                name = self.read_variable_name()
                value = self.read_value()
                lines.append(f"set {name} {value}")

            elif opcode == "ADD":
                name = self.read_variable_name()
                value = self.read_value()
                lines.append(f"add {name} {value}")

            elif opcode == "PRINT":
                value = self.read_value()
                lines.append(f"print {value}")

            elif opcode == "CMP":
                left = self.read_value()
                cmp_op = self.read_cmp()
                right = self.read_value()
                lines.append(f"cmp {left} {cmp_op} {right}")

            elif opcode == "MOD":
                name = self.read_variable_name()
                value = self.read_value()
                lines.append(f"mod {name} {value}")

            elif opcode == "LABEL":
                label = self.read_label_name()
                lines.append(f"label {label}")

            elif opcode == "JUMP":
                label = self.read_label_name()
                lines.append(f"jump {label}")

            elif opcode == "JUMP_IF_FALSE":
                label = self.read_label_name()
                lines.append(f"jump_if_false {label}")

            elif opcode == "HALT":
                lines.append("halt")

            else:
                raise ValueError(f"Unsupported opcode in reset build: {opcode}")

        lines.append("end")
        return "\n".join(lines)


# ============================================================
# INTERPRETER
# ============================================================

class OsuProgram:
    def __init__(self):
        self.variables = {}
        self.last_cmp = False
        self.labels = {}

    def resolve_value(self, value):
        name = value.__class__.__name__

        if name == "IntValue":
            return value.value

        if name == "StringValue":
            return value.value

        if name == "IdValue":
            return self.variables.get(value.value, 0)

        return value

    def build_label_table(self, model):
        for i, c in enumerate(model.commands):
            if c.__class__.__name__ == "LabelCommand":
                self.labels[c.name] = i

    def interpret(self, model):
        self.build_label_table(model)

        pc = 0
        while pc < len(model.commands):
            c = model.commands[pc]
            name = c.__class__.__name__
            if c == "halt":
                break
            if name == "SetCommand":
                self.variables[c.name] = self.resolve_value(c.value)
                pc += 1

            elif name == "AddCommand":
                self.variables[c.name] = self.variables.get(c.name, 0) + self.resolve_value(c.value)
                pc += 1

            elif name == "PrintCommand":
                print(self.resolve_value(c.value))
                pc += 1

            elif name == "CmpCommand":
                left = self.resolve_value(c.left)
                right = self.resolve_value(c.right)

                if c.op == "eq":
                    self.last_cmp = left == right
                elif c.op == "ne":
                    self.last_cmp = left != right
                elif c.op == "lt":
                    self.last_cmp = left < right
                elif c.op == "gt":
                    self.last_cmp = left > right
                elif c.op == "le":
                    self.last_cmp = left <= right
                elif c.op == "ge":
                    self.last_cmp = left >= right
                else:
                    raise ValueError(f"Unknown comparison op: {c.op}")

                pc += 1
                
            elif name == "ModCommand":
                self.variables[c.name] = self.variables.get(c.name, 0) % self.resolve_value(c.value)
                pc += 1

            elif name == "LabelCommand":
                pc += 1

            elif name == "JumpCommand":
                pc = self.labels[c.label]

            elif name == "JumpIfFalseCommand":
                if not self.last_cmp:
                    pc = self.labels[c.label]
                else:
                    pc += 1

            elif name == "HaltCommand":
                break

            else:
                raise ValueError(f"Unknown command: {name}")

# ============================================================
# Run
# ============================================================
def run_osu_program(osu_text: str) -> str:
    hit_lines = extract_hitobject_lines(osu_text)
    objects = parse_hitobjects(hit_lines)

    translator = OsuToDslTranslator()
    program_text = translator.translate(objects)

    osu_mm = metamodel_from_file("osu.tx")
    osu_model = osu_mm.model_from_str(program_text)

    program = OsuProgram()

    import io
    import sys

    old_stdout = sys.stdout
    buffer = io.StringIO()

    try:
        sys.stdout = buffer
        program.interpret(osu_model)
    finally:
        sys.stdout = old_stdout

    return buffer.getvalue()
# ============================================================
# MAIN Local testing
# ============================================================
def run_osu_program(osu_text: str) -> str:
    import io
    import sys

    hit_lines = extract_hitobject_lines(osu_text)
    objects = parse_hitobjects(hit_lines)

    translator = OsuToDslTranslator()
    program_text = translator.translate(objects)

    osu_mm = metamodel_from_file("osu.tx")
    osu_model = osu_mm.model_from_str(program_text)

    program = OsuProgram()

    # capture ALL print output
    old_stdout = sys.stdout
    buffer = io.StringIO()

    try:
        sys.stdout = buffer
        program.interpret(osu_model)
    finally:
        sys.stdout = old_stdout

    return buffer.getvalue()
#EDIT MAIN TO CHANGE FILE NAMES
def main():
    osu_mm = metamodel_from_file("osu.tx")

    osu_text = read_osu_file("workingEditor.osu")
    mode = parse_mode(osu_text)
    if mode != 0:
        raise ValueError(f"Only osu!standard is supported. Found Mode={mode}")

    hit_lines = extract_hitobject_lines(osu_text)
    objects = parse_hitobjects(hit_lines)

    translator = OsuToDslTranslator()
    program_text = translator.translate(objects)
    with open("program.osuDsl", "w", encoding="utf-8") as f:
        f.write(program_text)

    # print("=== DSL ===")
    # print(program_text)
    # to test generated DSL

    osu_model = osu_mm.model_from_file("program.osuDsl")

    program = OsuProgram()
    program.interpret(osu_model)


if __name__ == "__main__":
    main()
    
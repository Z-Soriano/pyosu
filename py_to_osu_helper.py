timeScale = 1
SLIDER_GAP = 1200
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

def encode_letter_to_x(ch: str) -> int:
    idx = LETTERS.index(ch)
    bucket_size = 512 / len(LETTERS)
    return int(idx * bucket_size + bucket_size / 2)
def encode_string_to_x(ch: str) -> int:
    idx = STRING_SYMBOLS.index(ch)
    bucket_size = 512 / len(STRING_SYMBOLS)
    return int(idx * bucket_size + bucket_size / 2)

def circle(x: int, y: int, t: int) -> str:
    return f"{x},{y},{t},1,0,0:0:0:0:"


def spinner_for_bank(bank: str, t: int) -> str:
    durations = {
        "NORMAL": 1500,
        "VARIABLE": 2500,
        "LABEL": 3500,
        "CONTROL": 4500,
        "STRING": 5500,
    }

    duration = durations[bank]
    return f"256,192,{t},12,0,{t + duration},0:0:0:0:"


def slider_from_int(n: int, t: int) -> str:
    return f"100,{100+n},{t},2,0,L|{100+n}:{100+n},1,100,0:0:0:0:"


def emit_variable(name: str, start_t: int):
    lines = [spinner_for_bank("VARIABLE", start_t)]
    t = start_t + 2600 * timeScale
    for ch in name:
        lines.append(circle(encode_letter_to_x(ch), 200, t))
        t += 500 * timeScale 
    return lines, t


def emit_label(name: str, start_t: int):
    lines = [spinner_for_bank("LABEL", start_t)]
    t = start_t + 3600 * timeScale
    for ch in name:
        lines.append(circle(encode_letter_to_x(ch), 200, t))
        t += 500 * timeScale 
    return lines, t


def emit_string(text: str, start_t: int):
    lines = [spinner_for_bank("STRING", start_t)]
    t = start_t + 5600 * timeScale

    for ch in text:
        lines.append(circle(encode_string_to_x(ch), 200, t))
        t += 500 * timeScale 
    return lines, t


def emit_back_to_normal(t: int):
    return spinner_for_bank("NORMAL", t), t + 1600


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

 
# to create a new python to hitobjects generator, write a similar function
def build_fizzbuzz_program() -> str:
    lines = ["[HitObjects]"]
    t = 1000 * timeScale

    # opcode x values
    X_SET = 12
    X_ADD = 38
    X_MOD = 140
    X_PRINT = 168
    X_CMP = 220
    X_JUMP = 246
    X_JUMP_IF_FALSE = 272
    X_LABEL = 298
    X_HALT = 324

    # comparison y values
    Y_EQ = 10
    Y_GT = 111

    # set x 1
    lines.append(circle(X_SET, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(1, t))
    t += SLIDER_GAP

    # label loop
    lines.append(circle(X_LABEL, 200, t))
    label_lines, t = emit_label("loop", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # ---------- FIZZBUZZ (15) ----------
    lines.append(circle(X_SET, 200, t))
    var_lines, t = emit_variable("yx", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_MOD, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(15, t))
    t += SLIDER_GAP

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    lines.append(spinner_for_bank("CONTROL", t))
    t += 200
    lines.append(circle(10, Y_EQ, t))
    t += 100 * timeScale
    lines.append(slider_from_int(0, t))
    t += SLIDER_GAP
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP_IF_FALSE, 200, t))
    label_lines, t = emit_label("fizz", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_PRINT, 200, t))
    str_lines, t = emit_string("FizzBuzz", t + 100)
    lines += str_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP, 200, t))
    label_lines, t = emit_label("after", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # ---------- FIZZ (3) ----------
    lines.append(circle(X_LABEL, 200, t))
    label_lines, t = emit_label("fizz", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_SET, 200, t))
    var_lines, t = emit_variable("yx", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_MOD, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(3, t))
    t += SLIDER_GAP

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    lines.append(spinner_for_bank("CONTROL", t))
    t += 200
    lines.append(circle(10, Y_EQ, t))
    t += 100 * timeScale
    lines.append(slider_from_int(0, t))
    t += SLIDER_GAP
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP_IF_FALSE, 200, t))
    label_lines, t = emit_label("buzz", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_PRINT, 200, t))
    str_lines, t = emit_string("Fizz", t + 100)
    lines += str_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP, 200, t))
    label_lines, t = emit_label("after", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # ---------- BUZZ (5) ----------
    lines.append(circle(X_LABEL, 200, t))
    label_lines, t = emit_label("buzz", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_SET, 200, t))
    var_lines, t = emit_variable("yx", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_MOD, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(5, t))
    t += SLIDER_GAP

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    lines.append(spinner_for_bank("CONTROL", t))
    t += 200
    lines.append(circle(10, Y_EQ, t))
    t += 100 * timeScale
    lines.append(slider_from_int(0, t))
    t += SLIDER_GAP
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP_IF_FALSE, 200, t))
    label_lines, t = emit_label("num", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_PRINT, 200, t))
    str_lines, t = emit_string("Buzz", t + 100)
    lines += str_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP, 200, t))
    label_lines, t = emit_label("after", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # ---------- NUMBER ----------
    lines.append(circle(X_LABEL, 200, t))
    label_lines, t = emit_label("num", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_PRINT, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # ---------- AFTER ----------
    lines.append(circle(X_LABEL, 200, t))
    label_lines, t = emit_label("after", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_ADD, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(1, t))
    t += SLIDER_GAP

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    lines.append(spinner_for_bank("CONTROL", t))
    t += 200
    lines.append(circle(10, Y_GT, t))
    t += 100 * timeScale
    lines.append(slider_from_int(100, t))
    t += SLIDER_GAP
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP_IF_FALSE, 200, t))
    label_lines, t = emit_label("loop", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_HALT, 200, t))

    return "\n".join(lines)
def build_simple_print_program() -> str:
    lines = ["[HitObjects]"]
    t = 1000 * timeScale

    X_PRINT = 168
    X_HALT = 324

    # print "Hello"
    lines.append(circle(X_PRINT, 200, t))
    str_lines, t = emit_string("Hello", t + 100)
    lines += str_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # halt
    lines.append(circle(X_HALT, 200, t))

    return "\n".join(lines)
#replicate the below code to generate new generated_hitobjects#.txt files with different python programs
with open("generated_hitobjects1.txt", "w", encoding="utf-8") as f:
    f.write(build_fizzbuzz_program())
    
with open("generated_hitobjects2.txt", "w", encoding="utf-8") as f:
    f.write(build_simple_print_program())

def build_only_div4_program() -> str:
    lines = ["[HitObjects]"]
    t = 1000 * timeScale

    X_SET = 12
    X_ADD = 38
    X_MOD = 140
    X_PRINT = 168
    X_CMP = 220
    X_JUMP = 246
    X_JUMP_IF_FALSE = 272
    X_LABEL = 298
    X_HALT = 324

    Y_EQ = 10
    Y_GT = 111

    # set x 1
    lines.append(circle(X_SET, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(1, t))
    t += SLIDER_GAP

    # label loop
    lines.append(circle(X_LABEL, 200, t))
    label_lines, t = emit_label("loop", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # y = x
    lines.append(circle(X_SET, 200, t))
    var_lines, t = emit_variable("yx", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # y % 4
    lines.append(circle(X_MOD, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(4, t))
    t += SLIDER_GAP

    # cmp y == 0
    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    lines.append(spinner_for_bank("CONTROL", t))
    t += 200
    lines.append(circle(10, Y_EQ, t))
    t += 100 * timeScale
    lines.append(slider_from_int(0, t))
    t += SLIDER_GAP
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # if NOT divisible → skip print
    lines.append(circle(X_JUMP_IF_FALSE, 200, t))
    label_lines, t = emit_label("after", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # print x (ONLY when divisible)
    lines.append(circle(X_PRINT, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # label after
    lines.append(circle(X_LABEL, 200, t))
    label_lines, t = emit_label("after", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # x += 1
    lines.append(circle(X_ADD, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(1, t))
    t += SLIDER_GAP

    # stop at 100
    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    lines.append(spinner_for_bank("CONTROL", t))
    t += 200
    lines.append(circle(10, Y_GT, t))
    t += 100 * timeScale
    lines.append(slider_from_int(100, t))
    t += SLIDER_GAP
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP_IF_FALSE, 200, t))
    label_lines, t = emit_label("loop", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # halt
    lines.append(circle(X_HALT, 200, t))

    return "\n".join(lines)
with open("generated_hitobjects3.txt", "w", encoding="utf-8") as f:
    f.write(build_only_div4_program())
def build_fibonacci_program() -> str:
    lines = ["[HitObjects]"]
    t = 1000 * timeScale

    X_SET = 12
    X_ADD = 38
    X_PRINT = 168
    X_CMP = 220
    X_JUMP = 246
    X_JUMP_IF_FALSE = 272
    X_LABEL = 298
    X_HALT = 324

    Y_GT = 111

    def emit_set_int(var_name: str, value: int):
        nonlocal t
        lines.append(circle(X_SET, 200, t))
        var_lines, t = emit_variable(var_name, t + 100)
        lines.extend(var_lines)
        back, t = emit_back_to_normal(t)
        lines.append(back)
        lines.append(slider_from_int(value, t))
        t += SLIDER_GAP

    def emit_set_var(left: str, right: str):
        nonlocal t
        lines.append(circle(X_SET, 200, t))
        var_lines, t = emit_variable(left + right, t + 100)
        lines.extend(var_lines)
        back, t = emit_back_to_normal(t)
        lines.append(back)

    def emit_add_var(left: str, right: str):
        nonlocal t
        lines.append(circle(X_ADD, 200, t))
        var_lines, t = emit_variable(left + right, t + 100)
        lines.extend(var_lines)
        back, t = emit_back_to_normal(t)
        lines.append(back)

    def emit_print_var(var_name: str):
        nonlocal t
        lines.append(circle(X_PRINT, 200, t))
        var_lines, t = emit_variable(var_name, t + 100)
        lines.extend(var_lines)
        back, t = emit_back_to_normal(t)
        lines.append(back)

    def emit_label_line(label: str):
        nonlocal t
        lines.append(circle(X_LABEL, 200, t))
        label_lines, t = emit_label(label, t + 100)
        lines.extend(label_lines)
        back, t = emit_back_to_normal(t)
        lines.append(back)

    def emit_jump(label: str):
        nonlocal t
        lines.append(circle(X_JUMP, 200, t))
        label_lines, t = emit_label(label, t + 100)
        lines.extend(label_lines)
        back, t = emit_back_to_normal(t)
        lines.append(back)

    def emit_jump_if_false(label: str):
        nonlocal t
        lines.append(circle(X_JUMP_IF_FALSE, 200, t))
        label_lines, t = emit_label(label, t + 100)
        lines.extend(label_lines)
        back, t = emit_back_to_normal(t)
        lines.append(back)

    def emit_cmp_gt(var_name: str, value: int):
        nonlocal t
        lines.append(circle(X_CMP, 200, t))
        var_lines, t = emit_variable(var_name, t + 100)
        lines.extend(var_lines)
        lines.append(spinner_for_bank("CONTROL", t))
        t += 200
        lines.append(circle(10, Y_GT, t))
        t += 100 * timeScale
        lines.append(slider_from_int(value, t))
        t += SLIDER_GAP
        back, t = emit_back_to_normal(t)
        lines.append(back)

    emit_set_int("a", 1)
    emit_set_int("b", 1)

    emit_label_line("loop")

    emit_cmp_gt("a", 100)
    emit_jump_if_false("body")

    lines.append(circle(X_HALT, 200, t))
    t += 200

    emit_label_line("body")

    emit_print_var("a")

    emit_set_var("c", "a")
    emit_add_var("c", "b")
    emit_set_var("a", "b")
    emit_set_var("b", "c")

    emit_jump("loop")

    return "\n".join(lines)

with open("generated_hitobjects_fibonacci.txt", "w", encoding="utf-8") as f:
    f.write(build_fibonacci_program())
def build_dom_goated_program() -> str:
    lines = ["[HitObjects]"]
    t = 1000 * timeScale

    X_PRINT = 168
    X_HALT = 324

    # print "dom is goated"
    lines.append(circle(X_PRINT, 200, t))
    str_lines, t = emit_string("dom is goated", t + 100)
    lines.extend(str_lines)

    back, t = emit_back_to_normal(t)
    lines.append(back)

    # halt
    lines.append(circle(X_HALT, 200, t))

    return "\n".join(lines)
with open("generated_dom.txt", "w", encoding="utf-8") as f:
    f.write(build_dom_goated_program())
def build_simple_math_program() -> str:
    lines = ["[HitObjects]"]
    t = 1000 * timeScale

    X_SET = 12
    X_ADD = 38
    X_PRINT = 168
    X_HALT = 324

    # x = 5
    lines.append(circle(X_SET, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines.extend(var_lines)
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(5, t))
    t += SLIDER_GAP

    # x = x + 3
    lines.append(circle(X_ADD, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines.extend(var_lines)
    back, t = emit_back_to_normal(t)
    lines.append(back)
    lines.append(slider_from_int(3, t))
    t += SLIDER_GAP

    # print x
    lines.append(circle(X_PRINT, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines.extend(var_lines)
    back, t = emit_back_to_normal(t)
    lines.append(back)

    # halt
    lines.append(circle(X_HALT, 200, t))

    return "\n".join(lines)
with open("simplemath.txt", "w", encoding="utf-8") as f:
    f.write(build_simple_math_program())
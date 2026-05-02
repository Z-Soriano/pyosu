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


def spinner(x: int, t: int) -> str:
    return f"{x},200,{t},12,0,{t+100},0:0:0:0:"


def slider_from_int(n: int, t: int) -> str:
    return f"100,{100+n},{t},2,0,L|{100+n}:{100+n},1,100,0:0:0:0:"


def emit_variable(name: str, start_t: int):
    lines = [spinner(150, start_t)]
    t = start_t + 200
    for ch in name:
        lines.append(circle(encode_letter_to_x(ch), 200, t))
        t += 100
    return lines, t


def emit_label(name: str, start_t: int):
    lines = [spinner(250, start_t)]
    t = start_t + 200
    for ch in name:
        lines.append(circle(encode_letter_to_x(ch), 200, t))
        t += 100
    return lines, t


def emit_string(text: str, start_t: int):
    lines = [spinner(450, start_t)]
    t = start_t + 200
    for ch in text:
        lines.append(circle(encode_string_to_x(ch), 200, t))
        t += 100
    return lines, t


def emit_back_to_normal(t: int):
    return spinner(50, t), t + 200


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


def decode_spinner_bank(x: int) -> str:
    if 0 <= x <= 102:
        return "NORMAL"
    if 103 <= x <= 204:
        return "VARIABLE"
    if 205 <= x <= 306:
        return "LABEL"
    if 307 <= x <= 408:
        return "CONTROL"
    if 409 <= x <= 512:
        return "STRING"
    raise ValueError(f"spinner x out of range: {x}")

# to create a new python to hitobjects generator, write a similar function
def build_fizzbuzz_program() -> str:
    lines = ["[HitObjects]"]
    t = 1000

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
    t += 200

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
    t += 200

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    lines.append(spinner(350, t))
    t += 200
    lines.append(circle(10, Y_EQ, t))
    t += 100
    lines.append(slider_from_int(0, t))
    t += 200
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
    t += 200

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    lines.append(spinner(350, t))
    t += 200
    lines.append(circle(10, Y_EQ, t))
    t += 100
    lines.append(slider_from_int(0, t))
    t += 200
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
    t += 200

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("y", t + 100)
    lines += var_lines
    lines.append(spinner(350, t))
    t += 200
    lines.append(circle(10, Y_EQ, t))
    t += 100
    lines.append(slider_from_int(0, t))
    t += 200
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
    t += 200

    lines.append(circle(X_CMP, 200, t))
    var_lines, t = emit_variable("x", t + 100)
    lines += var_lines
    lines.append(spinner(350, t))
    t += 200
    lines.append(circle(10, Y_GT, t))
    t += 100
    lines.append(slider_from_int(100, t))
    t += 200
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_JUMP_IF_FALSE, 200, t))
    label_lines, t = emit_label("loop", t + 100)
    lines += label_lines
    back, t = emit_back_to_normal(t)
    lines.append(back)

    lines.append(circle(X_HALT, 200, t))

    return "\n".join(lines)
#replicate the below code to generate new generated_hitobjects#.txt files with different python programs
with open("generated_hitobjects1.txt", "w", encoding="utf-8") as f:
    f.write(build_fizzbuzz_program())
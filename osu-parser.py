#parse the entire osu file
def parse_osu(text):
    lines = text.splitlines()
    mode = None
    hitobjects = []
    #Loops through ever line in the file, looking for the mode and hitobjects section. 
    #Once it finds the hitobjects section, it stores all the lines after that as hitobjects 
    #until it reaches the end of the file.
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("Mode:"):
            mode = int(line.split(":")[1].strip())
        if line == "[HitObjects]":
            #for every line after the hitobjects section, if the line is not empty, add it to the hitobjects list
            hitobjects = [x.strip() for x in lines[i + 1:] if x.strip()]
            break

    return mode, hitobjects

#parse hitobjects after parsing the entire osu file
def parse_hitobjects(hitobjects):
    parsed = []
    #Loops through every line in the hitobjects list, splits the line by commas, 
    # and checks if there are at least 6 parts. 
    # If there are, it extracts the x, y, obj_type, and sixth values and appends them as a tuple 
    # to the parsed list.
    for line in hitobjects:
        parts = line.split(",")

        if len(parts) < 6:
            continue

        x = int(parts[0])
        y = int(parts[1])
        obj_type = int(parts[3])
        sixth = parts[5][0]

        parsed.append((x, y, obj_type, sixth))

    return parsed


# read file
with open("osufiletest.txt", encoding="utf-8") as f:
    text = f.read()

mode, hitobjects = parse_osu(text)
parsed = parse_hitobjects(hitobjects)

print("Mode: " + str(mode))
print("(x, y, obj_type, sixth)")
for obj in parsed[:5]:
    print(obj)

object_type_dict = {
    1: "Circle",
    2: "Slider",
    3: "Spinner",
    5: "Circle (New Combo)",
    6: "Slider (New Combo)",
    8: "Spinner (New Combo)"
    }
mapped = [
    (x, y, object_type_dict.get(obj_type, obj_type), sixth)
    for (x, y, obj_type, sixth) in parsed
]
print("Parsed Hit Objects with Object Types:")
print("(x, y, obj_type, sixth)")
for obj in mapped[:5]:
    print(obj)

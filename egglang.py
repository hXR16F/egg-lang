import codecs


def encode(text: str) -> str:
    try:
        string_to_encode = codecs.encode(bytes(text, "utf-8"), "base64").decode()[::-1]
    except:
        return "Error while encoding", "err"

    d = {}
    with open("egg_lang_data.txt") as f:
        for line in f:
            (key, val) = line.split()
            d[key] = val

    encoded = []
    for letter in string_to_encode:
        found = False
        for k, v in d.items():
            if letter == v:
                found = True
                encoded.append(f"{k[0:3]} {k[3:6]}")
                encoded.append(" ")
        if not found:
            encoded.append(letter)
    
    try:
        return "".join(encoded).replace("\n", " ").replace("\r", "")[1::][:-1], ""
    except:
        return "Error while encoding", "err"


def decode(text: str) -> str:
    string_to_decode = text

    d = {}
    with open("egg_lang_data.txt") as f:
        for line in f:
            (key, val) = line.split()
            d[key] = val

    lst = []
    i = 0
    while True:
        if string_to_decode[i : i + 7].lower() == "egg egg":
            lst.append(string_to_decode[i : i + 7])
            i += 7
        elif string_to_decode[i : i + 7].lower() == "":
            break
        else:
            lst.append(string_to_decode[i : i + 1])
            i += 1

    decoded = []
    for item in lst:
        if item.lower() == "egg egg":
            decoded.append(d.get(item.split(" ")[0] + item.split(" ")[1]))
        else:
            decoded.append(item)

    try:
        return codecs.decode(bytes("".join(decoded)[::-1], "utf-8"), "base64").decode(), ""
    except:
        return "Error while decoding", "err"
import struct
import os
import re

def compile_po_file(po_path, mo_path):
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = {}
    pattern = re.compile(
        r'msgid\s+((?:"(?:[^"\\]|\\.)*"\s*)+)\s*msgstr\s+((?:"(?:[^"\\]|\\.)*"\s*)+)',
        re.MULTILINE
    )

    for match in pattern.finditer(content):
        raw_id = match.group(1)
        raw_str = match.group(2)

        def clean_po_str(s):
            parts = re.findall(r'"((?:[^"\\]|\\.)*)"', s)
            joined = "".join(parts)
            joined = joined.replace(r'\n', '\n').replace(r'\t', '\t').replace(r'\"', '"').replace(r'\\', '\\')
            return joined

        msgid = clean_po_str(raw_id)
        msgstr = clean_po_str(raw_str)

        # Include all entries including the empty header entry
        entries[msgid] = msgstr

    # Ensure header entry specifies UTF-8 charset
    if "" not in entries:
        entries[""] = "Content-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: 8bit\n"
    elif "charset=" not in entries[""]:
        entries[""] += "\nContent-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: 8bit\n"

    keys = sorted(entries.keys())
    offsets = []
    ids = b''
    strs = b''

    for k in keys:
        v = entries[k]
        k_bytes = k.encode('utf-8')
        v_bytes = v.encode('utf-8')

        offsets.append((len(ids), len(k_bytes), len(strs), len(v_bytes)))
        ids += k_bytes + b'\x00'
        strs += v_bytes + b'\x00'

    keystart = 7 * 4 + len(keys) * 8 * 2
    valuestart = keystart + len(ids)

    koffsets = []
    voffsets = []
    for id_off, id_len, str_off, str_len in offsets:
        koffsets.append((id_len, keystart + id_off))
        voffsets.append((str_len, valuestart + str_off))

    output = struct.pack(
        "Iiiiiii",
        0x950412de,  # Magic
        0,           # Version
        len(keys),   # Number of strings
        7 * 4,       # Offset of table with original strings
        7 * 4 + len(keys) * 8, # Offset of table with translation strings
        0,           # Size of hashing table
        0            # Offset of hashing table
    )

    for o_len, o_off in koffsets:
        output += struct.pack("ii", o_len, o_off)
    for t_len, t_off in voffsets:
        output += struct.pack("ii", t_len, t_off)

    output += ids + strs

    with open(mo_path, 'wb') as f:
        f.write(output)

    print(f"Properly compiled {po_path} -> {mo_path} with UTF-8 header ({len(keys)} entries)")

if __name__ == '__main__':
    for root, dirs, files in os.walk('locale'):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                mo_path = os.path.splitext(po_path)[0] + '.mo'
                compile_po_file(po_path, mo_path)

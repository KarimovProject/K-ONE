"""Compile .po to .mo using Python stdlib's msgfmt module."""
import struct
import array

def compile_po(po_path, mo_path):
    """Minimal PO to MO compiler."""
    messages = {}
    msgid = None
    msgstr = None
    
    with open(po_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("msgid "):
                if msgid is not None and msgstr is not None:
                    messages[msgid] = msgstr
                msgid = line[7:-1]  # strip msgid " and trailing "
                msgstr = None
            elif line.startswith("msgstr "):
                msgstr = line[8:-1]  # strip msgstr " and trailing "
            elif line.startswith('"') and line.endswith('"'):
                val = line[1:-1]
                if msgstr is not None:
                    msgstr += val
                elif msgid is not None:
                    msgid += val
    
    if msgid is not None and msgstr is not None:
        messages[msgid] = msgstr
    
    # Remove empty msgid (header)
    messages.pop("", None)
    
    # Build MO file
    keys = sorted(messages.keys())
    offsets = []
    key_data = b""
    val_data = b""
    key_offsets = []
    val_offsets = []
    
    for key in keys:
        key_bytes = key.encode("utf-8")
        val_bytes = messages[key].encode("utf-8")
        key_offsets.append((len(key_bytes), len(key_data)))
        val_offsets.append((len(val_bytes), len(val_data)))
        key_data += key_bytes + b"\0"
        val_data += val_bytes + b"\0"
    
    n = len(keys)
    # Header: magic, revision, nstrings, offset_keys, offset_vals, size_hash, offset_hash
    header_size = 7 * 4
    key_table_offset = header_size
    val_table_offset = key_table_offset + n * 8
    key_data_offset = val_table_offset + n * 8
    val_data_offset = key_data_offset + len(key_data)
    
    output = struct.pack(
        "Iiiiiii",
        0x950412de,  # magic
        0,  # revision
        n,  # nstrings
        key_table_offset,
        val_table_offset,
        0,  # hash size
        0,  # hash offset
    )
    
    for length, offset in key_offsets:
        output += struct.pack("ii", length, key_data_offset + offset)
    
    for length, offset in val_offsets:
        output += struct.pack("ii", length, val_data_offset + offset)
    
    output += key_data + val_data
    
    with open(mo_path, "wb") as f:
        f.write(output)
    
    print(f"  Compiled {po_path} -> {mo_path} ({n} entries)")


compile_po(
    r"C:\IEMS\locale\ru\LC_MESSAGES\django.po",
    r"C:\IEMS\locale\ru\LC_MESSAGES\django.mo",
)
compile_po(
    r"C:\IEMS\locale\en\LC_MESSAGES\django.po",
    r"C:\IEMS\locale\en\LC_MESSAGES\django.mo",
)
print("Done!")

import os
import struct
import zlib
import math


def create_png_bytes(width: int, height: int) -> bytes:
    """
    Generate a crisp RGBA PNG image of an Obsidian-purple & Vedic-gold
    South Indian Horary Mandala + Crystal emblem.
    """
    raw_rows = bytearray()
    cx, cy = width / 2.0, height / 2.0
    r_outer = width * 0.46

    for y in range(height):
        raw_rows.append(0)  # PNG filter type 0 (None)
        for x in range(width):
            nx = (x - cx) / (width / 2.0)
            ny = (y - cy) / (height / 2.0)
            dist = math.hypot(x - cx, y - cy)

            # Rounded square background (Obsidian dark #15131e)
            max_c = max(abs(nx), abs(ny))
            if max_c > 0.92:
                raw_rows.extend((0, 0, 0, 0))
                continue

            # Base background with subtle radial purple glow
            glow = max(0.0, 1.0 - (dist / r_outer))
            r = int(20 + 48 * (glow ** 1.6))
            g = int(18 + 22 * (glow ** 1.6))
            b = int(32 + 88 * (glow ** 1.6))
            a = 255

            # Outer Gold/Purple Border of South Indian Chart Square
            sq = max(abs(nx), abs(ny))
            if 0.80 <= sq <= 0.88:
                # Gold border (#f59e0b)
                r, g, b = 245, 158, 11
            elif 0.72 <= sq < 0.80:
                # Inner dark margin
                pass
            elif sq < 0.72:
                # 4x4 South Indian Rasi Grid lines inside [-0.72, 0.72]
                gx = (nx + 0.72) / 1.44 * 4.0  # 0..4
                gy = (ny + 0.72) / 1.44 * 4.0  # 0..4
                in_center_2x2 = (1.08 < gx < 2.92) and (1.08 < gy < 2.92)

                fx = abs(gx - round(gx))
                fy = abs(gy - round(gy))
                line_thresh = 0.085

                if not in_center_2x2 and (fx < line_thresh or fy < line_thresh):
                    # Obsidian Violet grid lines (#a78bfa)
                    r, g, b = 167, 139, 250
                elif in_center_2x2:
                    # Center 2x2 Box: Draw glowing gold/violet diamond crystal
                    diamond = abs(nx) * 1.15 + abs(ny) * 0.95
                    if diamond < 0.26:
                        if abs(nx) < 0.035 or abs(ny) < 0.035:
                            r, g, b = 254, 240, 138  # Bright gold facet
                        elif nx < 0:
                            r, g, b = 139, 92, 246   # Left crystal facet (#8b5cf6)
                        else:
                            r, g, b = 109, 40, 217   # Right crystal facet (#6d28d9)
                    elif diamond < 0.31:
                        r, g, b = 245, 158, 11       # Gold crystal rim

            raw_rows.extend((r, g, b, a))

    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw_rows), level=9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )


def generate_ico_file(output_paths: list[str]):
    sizes = [16, 32, 48, 64, 128, 256]
    png_blobs = [create_png_bytes(sz, sz) for sz in sizes]

    # ICO Header: Reserved (2B=0), Type (2B=1 for ICO), Count (2B)
    ico_header = struct.pack("<HHH", 0, 1, len(sizes))
    dir_entries = bytearray()
    data_offset = 6 + 16 * len(sizes)

    for sz, blob in zip(sizes, png_blobs):
        w_byte = 0 if sz == 256 else sz
        h_byte = 0 if sz == 256 else sz
        entry = struct.pack(
            "<BBBBHHII",
            w_byte,
            h_byte,
            0,
            0,
            1,
            32,
            len(blob),
            data_offset,
        )
        dir_entries.extend(entry)
        data_offset += len(blob)

    ico_bytes = ico_header + bytes(dir_entries) + b"".join(png_blobs)

    for path in output_paths:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as f:
            f.write(ico_bytes)
        print(f"Generated icon: {path} ({len(ico_bytes)} bytes)")


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    generate_ico_file([
        os.path.join(base, "assets", "app_icon.ico"),
        os.path.join(base, "static", "favicon.ico"),
    ])


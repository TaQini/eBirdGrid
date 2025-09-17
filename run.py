from PIL import Image, ImageDraw, ImageFont
import math, os, sys

CANDIDATE_FONTS = [
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    # Windows
    "C:\\Windows\\Fonts\\msyh.ttc",
    "C:\\Windows\\Fonts\\msyh.ttf",
    "C:\\Windows\\Fonts\\simhei.ttf",
    "C:\\Windows\\Fonts\\simsun.ttc",
    # Linux common locations
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.otf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/arphic/ukai.ttc",
]

my_txt = "my_bj.txt"
all_txt = "bj.txt"

def find_font():
    for p in CANDIDATE_FONTS:
        if os.path.exists(p):
            return p
    return None

def clean_chinese(name: str) -> str:
    name = name.split('/')[0].split('(')[0].strip()
    if name == "原鸽":
        return "野化家鸽"
    return name

def parse_line(line: str):
    parts = line.strip().split()
    if len(parts) < 3:
        return clean_chinese(line.strip()), line.strip()
    latin = " ".join(parts[-2:])
    chinese_raw = "".join(parts[:-2])
    return clean_chinese(chinese_raw), latin

def draw_grid(all_file=all_txt, my_file=my_txt, output="output.png",
              cell_w=520, cn_h=160, lat_h=100, padding=12, max_cols=12):
    with open(all_file, 'r', encoding='utf-8-sig') as f:
        all_items = [parse_line(line) for line in f if line.strip()]
    with open(my_file, 'r', encoding='utf-8-sig') as f:
        my_items = set(tuple(parse_line(line)) for line in f if line.strip())

    n = len(all_items)
    cols = min(max_cols, n)
    rows = math.ceil(n / cols)
    cell_h = cn_h + lat_h

    img = Image.new("RGB", (cols * cell_w, rows * cell_h), color="white")
    draw = ImageDraw.Draw(img)

    font_path = find_font()
    if not font_path:
        print("[WARN] 没找到中文字体，可能出现乱码")

    def fit_font(text, max_w, max_h):
        for size in range(int(max_h), 6, -1):
            f = ImageFont.truetype(font_path, size=size) if font_path else ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=f)
            if bbox[2] - bbox[0] + 2 * padding <= max_w:
                return f
        return ImageFont.truetype(font_path, 6) if font_path else ImageFont.load_default()

    for idx, (ch_name, latin_name) in enumerate(all_items):
        row, col = divmod(idx, cols)
        x0, y0 = col * cell_w, row * cell_h
        x1, y1 = x0 + cell_w, y0 + cell_h
        bg = "white" if (ch_name, latin_name) in my_items else "#d3d3d3"

        draw.rectangle([x0, y0, x1, y1], fill=bg, outline="black")

        cn_font = fit_font(ch_name, cell_w, cn_h)
        bbox_ch = draw.textbbox((0, 0), ch_name, font=cn_font)
        cw, ch = bbox_ch[2] - bbox_ch[0], bbox_ch[3] - bbox_ch[1]
        draw.text((x0 + (cell_w - cw) / 2, y0 + (cn_h - ch) / 2),
                  ch_name, fill="black", font=cn_font)

        lat_font = fit_font(latin_name, cell_w, lat_h)
        bbox_lat = draw.textbbox((0, 0), latin_name, font=lat_font)
        lw, lh = bbox_lat[2] - bbox_lat[0], bbox_lat[3] - bbox_lat[1]
        draw.text((x0 + (cell_w - lw) / 2, y0 + cn_h + (lat_h - lh) / 2),
                  latin_name, fill="black", font=lat_font)

    img.save(output)
    print(f"[OK] 图片已保存为 {output}")

if __name__ == "__main__":
    draw_grid(all_txt, my_txt, "output.png",
              cell_w=520, cn_h=160, lat_h=100, padding=12, max_cols=12)
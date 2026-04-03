"""Draw a clean Transformer Encoder diagram using Python PIL"""
from PIL import Image, ImageDraw, ImageFont
import math

# Canvas size 16:9
W, H = 1920, 1080

# Colors
C_BG       = (255, 255, 255)
C_BLUE_D   = (44, 106, 170)   # dark blue
C_BLUE_M   = (74, 144, 217)   # medium blue
C_BLUE_L   = (237, 243, 251)  # light blue fill
C_BLUE_B   = (27, 79, 122)    # border blue
C_GRAY_D   = (61, 79, 96)     # dark gray
C_GRAY_L   = (240, 244, 248)  # light gray fill
C_ATTN     = (46, 107, 158)   # attention block
C_LN       = (91, 135, 176)   # layernorm block
C_TEXT_W   = (255, 255, 255)
C_TEXT_D   = (26, 58, 92)     # dark text
C_TEXT_M   = (74, 122, 170)   # medium text
C_LINE     = (74, 144, 217)
C_RESIDUAL = (120, 154, 186)  # residual line
C_ACCENT   = (220, 76, 76)    # red accent

# Load fonts
def font(size, bold=False):
    f1 = "C:/Windows/Fonts/msyh.ttc"
    f2 = "C:/Windows/Fonts/simhei.ttf"
    f3 = "C:/Windows/Fonts/arial.ttf"
    candidates = [f1, f2, f3]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except:
            pass
    return ImageFont.load_default()

FONT_TITLE  = font(40, True)
FONT_MAIN   = font(26, True)
FONT_SUB    = font(20)
FONT_EN     = font(18)
FONT_SM     = font(16)
FONT_XS     = font(14)
FONT_FORMULA= font(16)

def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    r = radius
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill, outline=outline, width=width)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill, outline=outline, width=width)
    draw.pieslice([x0, y0, x0+2*r, y0+2*r], 180, 270, fill=fill, outline=outline, width=width)
    draw.pieslice([x1-2*r, y0, x1, y0+2*r], 270, 360, fill=fill, outline=outline, width=width)
    draw.pieslice([x0, y1-2*r, x0+2*r, y1], 90, 180, fill=fill, outline=outline, width=width)
    draw.pieslice([x1-2*r, y1-2*r, x1, y1], 0, 90, fill=fill, outline=outline, width=width)

def solid_box(draw, x, y, w, h, fc, bc, text, sub=None, radius=10, fontsize=26):
    """Draw a solid rounded box with centered text"""
    rounded_rect(draw, [x, y, x+w, y+h], radius, fc, bc, 2)
    # Main text
    if sub:
        ty = y + h//2 - fontsize//3
        draw.text((x+w//2, ty), text, font=font(fontsize, True), fill=bc, anchor="mm")
        ty2 = y + h//2 + fontsize//2
        draw.text((x+w//2, ty2), sub, font=font(fontsize-6), fill=C_TEXT_M, anchor="mm")
    else:
        ty = y + h//2
        draw.text((x+w//2, ty), text, font=font(fontsize, True), fill=bc, anchor="mm")

def light_box(draw, x, y, w, h, fc, bc, text, sub=None, radius=8, fontsize=26):
    """Draw a light-filled box"""
    rounded_rect(draw, [x, y, x+w, y+h], radius, fc, bc, 2)
    if sub:
        ty = y + h//2 - fontsize//3
        draw.text((x+w//2, ty), text, font=font(fontsize, True), fill=C_TEXT_D, anchor="mm")
        ty2 = y + h//2 + fontsize//2
        draw.text((x+w//2, ty2), sub, font=font(fontsize-6), fill=C_TEXT_M, anchor="mm")
    else:
        ty = y + h//2
        draw.text((x+w//2, ty), text, font=font(fontsize, True), fill=C_TEXT_D, anchor="mm")

def arrow(draw, x0, y0, x1, y1, color=None, dashed=False, lw=2):
    if color is None:
        color = C_LINE
    if dashed:
        # Draw dashed line
        dx, dy = x1-x0, y1-y0
        length = math.sqrt(dx*dx+dy*dy)
        if length < 1:
            return
        step = 8
        dash_len = 6
        gap_len = 4
        for i in range(0, int(length), step):
            t0 = i / length
            t1 = min((i+dash_len)/length, 1.0)
            px0, py0 = x0+t0*dx, y0+t0*dy
            px1, py1 = x0+t1*dx, y0+t1*dy
            draw.line([px0, py0, px1, py1], fill=color, width=lw)
    else:
        draw.line([x0, y0, x1, y1], fill=color, width=lw)
    # Arrowhead
    dx, dy = x1-x0, y1-y0
    length = math.sqrt(dx*dx+dy*dy)
    if length < 1:
        return
    ux, uy = dx/length, dy/length
    ax, ay = ux*10, uy*10
    draw.line([x1-ax+ay*0.4, y1-ay-ax*0.4, x1, y1], fill=color, width=lw)
    draw.line([x1-ax-ay*0.4, y1-ay+ax*0.4, x1, y1], fill=color, width=lw)

def residual_arrow(draw, path_points, color=None, lw=1):
    """Draw a dashed residual connection"""
    if color is None:
        color = C_RESIDUAL
    for i in range(len(path_points)-1):
        arrow(draw, path_points[i][0], path_points[i][1],
              path_points[i+1][0], path_points[i+1][1], color, dashed=True, lw=lw)
    # Small circle at start
    draw.ellipse([path_points[0][0]-4, path_points[0][1]-4,
                  path_points[0][0]+4, path_points[0][1]+4], fill=color)

def small_box(draw, x, y, w, h, fc, text, sub=None, radius=6):
    """Draw a small colored box (for Q, K, V)"""
    rounded_rect(draw, [x, y, x+w, y+h], radius, fc, C_BLUE_B, 1)
    if sub:
        ty = y + h//2 - 10
        draw.text((x+w//2, ty), text, font=font(24, True), fill=C_TEXT_W, anchor="mm")
        ty2 = y + h//2 + 8
        draw.text((x+w//2, ty2), sub, font=font(14), fill=(192, 216, 240), anchor="mm")
    else:
        draw.text((x+w//2, y+h//2), text, font=font(24, True), fill=C_TEXT_W, anchor="mm")

# ============ Draw ============
img = Image.new("RGB", (W, H), C_BG)
draw = ImageDraw.Draw(img)

# ===== Title =====
draw.text((W//2, 42), "标准 Transformer 编码器结构", font=FONT_TITLE, fill=C_TEXT_D, anchor="mm")
draw.line([120, 65, W-120, 65], fill=C_BLUE_M, width=1)

# ===== Layout =====
# Top input row: Input X → Embedding → Positional Encoding
TOP_Y = 120
ROW_H = 60

# Input vector box
IX, IW = 40, 140
solid_box(draw, IX, TOP_Y, IW, ROW_H, C_BLUE_L, C_BLUE_M, "输入向量", "Input  X", fontsize=22)

# Arrow
AX0 = IX+IW; AX1 = IX+IW+30; AY = TOP_Y+ROW_H//2
arrow(draw, AX0, AY, AX1, AY)

# Embedding box
EX, EW = IX+IW+30, 180
solid_box(draw, EX, TOP_Y, EW, ROW_H, C_BLUE_M, C_BLUE_B, "输入嵌入", "Input Embedding", fontsize=22)

# Arrow
AX0 = EX+EW; AX1 = EX+EW+30
arrow(draw, AX0, AY, AX1, AY)

# Positional Encoding box
PX, PW = EX+EW+30, 200
solid_box(draw, PX, TOP_Y, PW, ROW_H, C_GRAY_D, C_GRAY_D, "位置编码", "Positional Encoding", fontsize=22)

# ===== Encoder Layer =====
ENC_TOP = TOP_Y + ROW_H + 50
ENC_BOTTOM = H - 100
ENC_LEFT = PX + PW + 60
ENC_RIGHT = W - 60

# Encoder block label
draw.text((W//2, ENC_TOP - 15), "编码器层（Encoder Layer）", font=font(18, True), fill=C_BLUE_M, anchor="mm")

# Encoder background box (dashed)
draw.rectangle([ENC_LEFT, ENC_TOP, ENC_RIGHT, ENC_BOTTOM],
               outline=C_BLUE_M, width=2)

# ===== Sub-layer 1: Multi-Head Self-Attention =====
MHSA_TOP = ENC_TOP + 15
MHSA_LEFT = ENC_LEFT + 40
MHSA_RIGHT = ENC_RIGHT - 30
MHSA_H = 140

light_box(draw, MHSA_LEFT, MHSA_TOP, MHSA_RIGHT-MHSA_LEFT, MHSA_H,
          C_BLUE_L, C_ATTN, "多头自注意力", "Multi-Head Self-Attention", fontsize=24)

# Q, K, V sub-boxes
QV_W, QV_H = 110, 50
QV_TOP = MHSA_TOP + 70

# Q box
Q_X = MHSA_LEFT + 60
small_box(draw, Q_X, QV_TOP, QV_W, QV_H, C_ATTN, "Q", "查询")

# K box
K_X = Q_X + QV_W + 30
small_box(draw, K_X, QV_TOP, QV_W, QV_H, C_ATTN, "K", "键")

# V box
V_X = K_X + QV_W + 30
small_box(draw, V_X, QV_TOP, QV_W, QV_H, C_ATTN, "V", "值")

# Right side: Scale Dot-Product label
SCL_X = V_X + QV_W + 40
draw.text((SCL_X + 100, QV_TOP + 15), "缩放点积注意力", font=font(18), fill=C_TEXT_M, anchor="mm")
draw.text((SCL_X + 100, QV_TOP + 38), "Scale Dot-Product", font=font(14), fill=C_RESIDUAL, anchor="mm")
draw.text((SCL_X + 100, QV_TOP + 60), "Attention(Q,K,V)", font=font(14), fill=C_TEXT_M, anchor="mm")

# Concat & Linear arrow
CONCAT_X0 = V_X + QV_W + 15
CONCAT_X1 = SCL_X - 20
draw.line([CONCAT_X0, QV_TOP+QV_H//2, CONCAT_X1, QV_TOP+QV_H//2], fill=C_ATTN, width=1)
draw.text(((CONCAT_X0+CONCAT_X1)//2, QV_TOP+QV_H//2-12), "Concat & Linear",
          font=font(12), fill=C_ATTN, anchor="mm")

# ===== Add & Norm 1 =====
AN1_Y = MHSA_TOP + MHSA_H + 12
AN1_H = 60
AN1_W = 350
AN1_X = (ENC_LEFT + ENC_RIGHT)//2 - AN1_W//2

solid_box(draw, AN1_X, AN1_Y, AN1_W, AN1_H, C_LN, C_BLUE_B,
          "Add & Norm", "残差连接 + 层归一化", fontsize=22)

# ===== Feed Forward Network =====
FFN_Y = AN1_Y + AN1_H + 12
FFN_H = 80
FFN_W = 280
FFN_X = ENC_LEFT + 40

light_box(draw, FFN_X, FFN_Y, FFN_W, FFN_H, C_BLUE_L, C_ATTN,
          "前馈网络", "Feed Forward Network", fontsize=22)

# FFN internal: Linear and ReLU
LIN_W, LIN_H = 90, 20
LIN_Y = FFN_Y + FFN_H - 35
LIN_X = FFN_X + 25
draw.rectangle([LIN_X, LIN_Y, LIN_X+LIN_W, LIN_Y+LIN_H], outline=C_BLUE_M, width=1, fill=C_BG)
draw.text((LIN_X+LIN_W//2, LIN_Y+LIN_H//2), "Linear(d→d)",
          font=font(11), fill=C_BLUE_M, anchor="mm")

RELU_X = LIN_X + LIN_W + 20
draw.rectangle([RELU_X, LIN_Y, RELU_X+LIN_W, LIN_Y+LIN_H], outline=C_BLUE_M, width=1, fill=C_BG)
draw.text((RELU_X+LIN_W//2, LIN_Y+LIN_H//2), "ReLU",
          font=font(11), fill=C_BLUE_M, anchor="mm")

draw.line([LIN_X+LIN_W, LIN_Y+LIN_H//2, RELU_X, LIN_Y+LIN_H//2], fill=C_BLUE_M, width=1)

# ===== Add & Norm 2 =====
AN2_Y = FFN_Y
AN2_H = AN1_H
AN2_W = AN1_W
AN2_X = ENC_RIGHT - AN1_W - 30

solid_box(draw, AN2_X, AN2_Y, AN2_W, AN2_H, C_LN, C_BLUE_B,
          "Add & Norm", "残差连接 + 层归一化", fontsize=22)

# ===== Output =====
OUT_Y = FFN_Y + FFN_H + 12
OUT_H = ROW_H
OUT_X = ENC_RIGHT - 180
OUT_W = 180
light_box(draw, OUT_X, OUT_Y, OUT_W, OUT_H, C_BLUE_L, C_BLUE_M,
          "输出表示", "Output Encoder", fontsize=22)

# ===== Arrows between components =====
# Top row → encoder
arrow(draw, PX+PW//2, TOP_Y+ROW_H, PX+PW//2, ENC_TOP, C_LINE)

# MHSA → AN1
MHSA_CX = MHSA_LEFT + (MHSA_RIGHT-MHSA_LEFT)//2
arrow(draw, MHSA_CX, MHSA_TOP+MHSA_H, MHSA_CX, AN1_Y, C_LINE)

# AN1 → FFN
arrow(draw, AN1_X+AN1_W, AN1_Y+AN1_H//2, FFN_X, FFN_Y+FFN_H//2, C_LINE)

# FFN → AN2
arrow(draw, FFN_X+FFN_W, FFN_Y+FFN_H//2, AN2_X, AN2_Y+AN2_H//2, C_LINE)

# AN2 → Output
arrow(draw, AN2_X+AN2_W, AN2_Y+AN2_H//2, OUT_X, OUT_Y+OUT_H//2, C_LINE)

# ===== Residual connections =====
# Residual from input → Add & Norm 1 (skip MHSA)
RX0 = PX+PW//2
RX1 = ENC_LEFT + 20
# Path: from top input column down, then left to encoder left edge, then up
MID_Y = (TOP_Y+ROW_H + ENC_TOP) // 2
residual_arrow(draw, [
    (RX0, TOP_Y+ROW_H),
    (RX0, MID_Y),
    (RX1, MID_Y),
    (RX1, AN1_Y + AN1_H//2),
])
draw.text((RX1+8, MID_Y-5), "Add", font=font(18, True), fill=C_RESIDUAL)

# Residual from input → Add & Norm 2 (skip FFN)
FFN_MID_Y = FFN_Y + FFN_H//2
residual_arrow(draw, [
    (RX0, TOP_Y+ROW_H),
    (RX0, FFN_MID_Y),
    (AN2_X, FFN_MID_Y),
])
draw.text((RX0+8, FFN_MID_Y-5), "Add", font=font(18, True), fill=C_RESIDUAL)

# ===== N× Stacked Encoder Block (right side) =====
NB_X = ENC_RIGHT + 30
NB_Y = ENC_TOP
NB_W = 180
NB_H = ENC_BOTTOM - ENC_TOP

draw.rectangle([NB_X, NB_Y, NB_X+NB_W, NB_Y+NB_H], outline=C_BLUE_M, width=1, fill=(240, 246, 252))

# N× text
draw.text((NB_X+NB_W//2, NB_Y+30), "N×", font=font(44, True), fill=C_BLUE_M, anchor="mm")
draw.text((NB_X+NB_W//2, NB_Y+70), "编码器层", font=font(20, True), fill=C_TEXT_M, anchor="mm")
draw.text((NB_X+NB_W//2, NB_Y+92), "Encoder", font=font(14), fill=C_RESIDUAL, anchor="mm")
draw.text((NB_X+NB_W//2, NB_Y+108), "Block", font=font(14), fill=C_RESIDUAL, anchor="mm")

# Bidirectional arrow and label
BAY = NB_Y + NB_H - 60
draw.line([NB_X+20, BAY, NB_X+NB_W-20, BAY], fill=C_BLUE_M, width=1)
# arrow heads both ways
draw.line([NB_X+20, BAY, NB_X+35, BAY-8], fill=C_BLUE_M, width=1)
draw.line([NB_X+20, BAY, NB_X+35, BAY+8], fill=C_BLUE_M, width=1)
draw.line([NB_X+NB_W-20, BAY, NB_X+NB_W-35, BAY-8], fill=C_BLUE_M, width=1)
draw.line([NB_X+NB_W-20, BAY, NB_X+NB_W-35, BAY+8], fill=C_BLUE_M, width=1)
draw.text((NB_X+NB_W//2, BAY+18), "堆叠 N 层", font=font(16), fill=C_TEXT_M, anchor="mm")
draw.text((NB_X+NB_W//2, BAY+38), "N≥1，通常 N=6", font=font(14), fill=C_RESIDUAL, anchor="mm")

# Arrow from N× box to encoder
arrow(draw, NB_X, ENC_TOP+(ENC_BOTTOM-ENC_TOP)//2, ENC_RIGHT, ENC_TOP+(ENC_BOTTOM-ENC_TOP)//2, C_BLUE_M)

# ===== Legend =====
LEG_Y = H - 55
LEG_X = 60
draw.rectangle([LEG_X, LEG_Y, LEG_X+900, LEG_Y+38], outline=(208, 224, 238), width=1, fill=(245, 249, 252))
draw.text((LEG_X+10, LEG_Y+19), "图例：", font=font(16), fill=C_TEXT_M, anchor="lm")

# Legend items
LX = LEG_X + 70
items = [
    (C_BLUE_M, "嵌入层"),
    (C_GRAY_D, "编码层"),
    (C_ATTN,   "注意力"),
    (C_LN,     "归一化"),
]
for i, (col, label) in enumerate(items):
    bx = LX + i * 140
    draw.rectangle([bx, LEG_Y+9, bx+28, LEG_Y+30], fill=col, outline=C_BLUE_B, width=1)
    draw.text((bx+36, LEG_Y+19), label, font=font(14), fill=C_TEXT_M, anchor="lm")

# Arrow legend
ARX = LX + 600
draw.line([ARX, LEG_Y+19, ARX+25, LEG_Y+19], fill=C_LINE, width=2)
draw.line([ARX+20, LEG_Y+12, ARX+25, LEG_Y+19], fill=C_LINE, width=2)
draw.line([ARX+20, LEG_Y+26, ARX+25, LEG_Y+19], fill=C_LINE, width=2)
draw.text((ARX+32, LEG_Y+19), "数据流向", font=font(14), fill=C_TEXT_M, anchor="lm")

# Residual legend
RRX = ARX + 120
draw.line([RRX, LEG_Y+19, RRX+25, LEG_Y+19], fill=C_RESIDUAL, width=1)
for j in range(3):
    draw.line([RRX+j*9, LEG_Y+16, RRX+j*9+6, LEG_Y+22], fill=C_RESIDUAL, width=1)
draw.text((RRX+32, LEG_Y+19), "残差连接", font=font(14), fill=C_TEXT_M, anchor="lm")

# ===== Complexity note (bottom right) =====
draw.text((W-60, LEG_Y+19), "时间复杂度: O(n² · d)",
          font=font(16), fill=(160, 176, 200), anchor="rm")

# ===== Border =====
draw.rectangle([0, 0, W-1, H-1], outline=(220, 230, 238), width=1)

# Save
img.save("transformer_encoder_diagram_final.png", "PNG", optimize=True)
import os
print(f"Saved: transformer_encoder_diagram_final.png ({os.path.getsize('transformer_encoder_diagram_final.png')/1024:.0f} KB)")

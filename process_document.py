#!/usr/bin/env python3
"""
去除文档照片中的拼接痕迹和背景
- 检测文档边界
- 透视校正
- 去除键盘背景
- 增强文档清晰度
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import os

def perspective_transform(image):
    """检测文档边界并进行透视校正"""
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 应用高斯模糊
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 边缘检测
    edged = cv2.Canny(blurred, 75, 200)
    
    # 膨胀以连接边缘线
    kernel = np.ones((5, 5), np.uint8)
    edged = cv2.dilate(edged, kernel, iterations=2)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    # 寻找四边形轮廓（文档）
    doc_contour = None
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if len(approx) == 4:
            doc_contour = approx
            break
    
    if doc_contour is None:
        # 如果没找到四边形，使用整张图片
        return image, None
    
    # 按顺序排列四个角点 (top-left, top-right, bottom-right, bottom-left)
    def order_points(pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=2)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts.reshape(4, 2), axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    ordered = order_points(doc_contour.reshape(4, 2))
    
    # 计算目标点 - 使用标准A4比例
    (tl, tr, br, bl) = ordered
    
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))
    
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))
    
    # 透视变换
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")
    
    M = cv2.getPerspectiveTransform(ordered.astype("float32"), dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    
    return warped, M

def remove_keyboard_background(image):
    """去除键盘背景并填充白色"""
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 创建掩码 - 文档区域（较亮的区域）
    _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 形态学操作去除噪点
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 找到文档轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # 找到最大轮廓（文档）
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 创建文档掩码
        doc_mask = np.zeros_like(mask)
        cv2.drawContours(doc_mask, [largest_contour], -1, 255, -1)
        
        # 平滑掩码边缘
        doc_mask = cv2.GaussianBlur(doc_mask.astype(np.float32), (21, 21), 0)
        doc_mask = (doc_mask > 127).astype(np.uint8) * 255
        
        # 填充背景为白色
        result = image.copy()
        bg_mask = 255 - doc_mask
        result[bg_mask == 255] = [255, 255, 255]
        
        # 对文档区域应用轻微去噪
        denoised = cv2.fastNlMeansDenoisingColored(result, None, 10, 10, 7, 21)
        
        # 合并
        final = np.where(doc_mask[:, :, np.newaxis] == 255, denoised, result)
        
        return final
    
    return image

def enhance_document(image):
    """增强文档可读性"""
    # 转换为灰度图进行增强
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 自适应直方图均衡化
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    
    # 增加对比度
    alpha = 1.2  # 对比度控制
    beta = 10    # 亮度控制
    enhanced_gray = cv2.convertScaleAbs(enhanced_gray, alpha=alpha, beta=beta)
    
    # 锐化
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(enhanced_gray, -1, kernel)
    
    # 转回BGR
    result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
    
    return result

def fix_seams(image):
    """修复拼接痕迹"""
    # 检测水平拼接线
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 使用拉普拉斯算子检测边缘
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    
    # 找到明显的水平线（可能的拼接痕迹）
    horizontal_lines = []
    for y in range(50, gray.shape[0] - 50, 10):
        row = gray[y, :]
        if np.std(row) > 50:  # 变化较大的行
            horizontal_lines.append(y)
    
    result = image.copy()
    
    # 对检测到的拼接线区域进行混合处理
    for y in horizontal_lines:
        # 在接缝处进行高斯模糊混合
        mask = np.zeros_like(gray)
        mask[max(0, y-10):min(gray.shape[0], y+10), :] = 255
        
        # 创建混合权重
        blend = np.zeros((20, gray.shape[1]))
        for i in range(20):
            blend[i, :] = np.exp(-((10 - i) ** 2) / (2 * 5 ** 2))
        
        # 应用混合
        for i, offset in enumerate(range(-10, 10)):
            row_idx = y + offset
            if 0 <= row_idx < result.shape[0]:
                weight = blend[i, :]
                result[row_idx] = (result[row_idx] * (1 - weight)[:, np.newaxis] + 
                                   result[row_idx].astype(float) * weight[:, np.newaxis]).astype(np.uint8)
    
    return result

def process_document_image(input_path, output_path):
    """主处理流程"""
    print(f"读取图片: {input_path}")
    image = cv2.imread(input_path)
    
    if image is None:
        print(f"无法读取图片: {input_path}")
        return False
    
    print("步骤1: 透视校正...")
    corrected, M = perspective_transform(image)
    
    print("步骤2: 去除背景...")
    cleaned = remove_keyboard_background(corrected)
    
    print("步骤3: 修复拼接痕迹...")
    fixed = fix_seams(cleaned)
    
    print("步骤4: 增强文档...")
    enhanced = enhance_document(fixed)
    
    print(f"保存结果: {output_path}")
    cv2.imwrite(output_path, enhanced)
    
    return True

if __name__ == "__main__":
    input_path = r"C:\Users\胡宠博\.cursor\projects\d-transformer\assets\c__Users_____AppData_Roaming_Cursor_User_workspaceStorage_ffe4367e1984b3badb725d86ba8d9375_images_bd49ced24d3fa1b7faa1008c815e9714-21b7088a-2740-475a-ab83-734d7b436e2e.png"
    output_path = r"C:\Users\胡宠博\.cursor\projects\d-transformer\assets\document_cleaned.png"
    
    success = process_document_image(input_path, output_path)
    if success:
        print("处理完成!")

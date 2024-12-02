import cv2
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import uuid
import os
import random
import math
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def config():
    with open("word_dict.txt", encoding="utf-8") as f:
        word = f.readlines()
    word_dict_length = len(word)
    font_dir = "Tangut_fonts"
    min_words_length = 8
    max_words_length = 12
    img_count = 30000
    return word, font_dir, min_words_length, max_words_length, img_count


def draw_to_image(size, fontPath, font_size, text, rotate = 0, salt = 22):
    img = Image.new("RGB", (size[1], size[0]), "black")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(fontPath, font_size)
    # 获取字体的宽高
    font_width, font_height = draw.textsize(text, font)
    offset_x, offset_y = font.getoffset(text)
    # 计算字体绘制的x,y坐标，主要是让文字画在图标中心
    x = (size[1] - font_width - offset_x) // 2
    y = (size[0] - font_height - offset_y) // 2
    draw.text((x, y), text, (255, 255, 255), font=font)
    if rotate != 0:
        img = img.rotate(rotate)
    np_img = np.asarray(img.getdata(), dtype='uint8')
    # 降维，3通道转为1通道，并组成矩阵
    np_img = np_img[:, 0].reshape(size)
    for i in range(salt):  # 添加噪声
        temp_x = np.random.randint(0, np_img.shape[0])
        temp_y = np.random.randint(0, np_img.shape[1])
        np_img[temp_x][temp_y] = 255
    time_value = int(round(time.time() * 1000))
    out_path = "images/{}_{}_{}.png".format(str(uuid.uuid4()), time_value, rotate)
    cv2.imwrite("F:/gen/" + out_path, np_img)
    return out_path


def generate_words(word, count, length_range_min, length_range_max):
    line_words_list = []
    line_words = ""
    globe_word_dict_index = 0
    for k in range(count + 1):
        bit_length = np.random.randint(length_range_min, length_range_max)
        for i in range(bit_length + 1):
            try:
                line_words = line_words + word[globe_word_dict_index].split("\n")[0]
            except:
                globe_word_dict_index = 0
                line_words = line_words + word[globe_word_dict_index].split("\n")[0]
            globe_word_dict_index += 1
        line_words_list.append(line_words)
        line_words = ""
    return line_words_list


def generate_image(font_name, font_dir, img_count, min_words_length, max_words_length, word):
    line_words_list = generate_words(word, img_count, min_words_length, max_words_length)
    image_paths = []
    for line in line_words_list:
        length = len(line)
        font_size = 33 if np.random.randint(0, 2) == 0 else 20
        if font_size == 33:
            size = (66, math.ceil(length * 34.4))
        else:
            size = (40, math.ceil(length * 20.8))

        font_path = os.path.join(font_dir, font_name)
        for k in range(-5, 5, 1):
            file_name = draw_to_image(size, font_path, font_size, line, rotate=k, salt=5 - k)
            image_paths.append((file_name, line))

    return image_paths


def save_to_label(image_paths):
    with open("F:/gen/label", "a", encoding="utf-8") as f:
        for image_path, line in image_paths:
            f.write(image_path + "\t" + line + "\n")


if __name__ == "__main__":
    word, font_dir, min_words_length, max_words_length, img_count = config()
    line_words_list = generate_words(word, img_count, min_words_length, max_words_length)
    font_files = os.listdir(font_dir)

    # 这里使用ProcessPoolExecutor来并行处理每种字体
    with ProcessPoolExecutor() as executor:
        future_to_font = {executor.submit(generate_image, font_name, font_dir, img_count, min_words_length, max_words_length, word): font_name
                          for font_name in font_files}

        all_image_paths = []
        for future in future_to_font:
            image_paths = future.result()
            all_image_paths.extend(image_paths)

        save_to_label(all_image_paths)

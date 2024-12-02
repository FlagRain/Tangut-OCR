import pandas as pd


url = "https://zh.wikipedia.org/wiki/Template:Unicode_chart_Tangut"

df = pd.read_html(url)[0]
print(df)

chars_tangut = []

for col in df.columns:
    for value in df[col]:
        if isinstance(value, str):
            for char in value:
                if 0x17000 <= ord(char) <= 0x187FF:
                    chars_tangut.append(char)

# 将符合条件的字符写入txt文件，每个字符一行
with open('word_dict.txt', 'w', encoding='utf-8') as f:
    for char in chars_tangut:
        f.write(char + '\n')


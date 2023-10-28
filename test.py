import jieba
import re
import wordcloud
from PIL import Image
import numpy as np
import datetime
import shutil
import os

plugin_path = '/home/flandre/桌面/xcw2/HoshinoBot/hoshino/modules/wordcloud-hoshino/'

font_path = os.path.join(plugin_path,f"3STKAITI.TTF")

txt = "测试用文字"
w = wordcloud.WordCloud(font_path = font_path)
        		    
w.generate(txt)
    

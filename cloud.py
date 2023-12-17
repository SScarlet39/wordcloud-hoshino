import jieba
import re
import nonebot
import wordcloud
import hoshino
from hoshino.typing import CQEvent
from hoshino import Service,R
from nonebot import MessageSegment,NoticeSession
import base64
from PIL import Image
import numpy as np
import datetime
import shutil
import os

sv = Service('词云', enable_on_default=True)


plugin_path = ''

loadpath = ''	
self_id = ''		
load_in_path = ''

tycpath = os.path.join(plugin_path,f"tyc.txt")


@nonebot.scheduler.scheduled_job(
    'cron',
    day='*',
    hour='23',
    minute='55'
)
async def makecloud():
    bot=nonebot.get_bot()
    try:
        makeclouds()
    except Exception as e:
        today = datetime.date.today().__format__('%Y-%m-%d')
        await bot.send_private_msg(user_id=hoshino.config.SUPERUSERS[2], message=f'{today}词云生成失败,失败原因:{e}')
        
@sv.on_rex(f'^查询(.*)月(\d+)日词云$')
async def ciyun(bot, ev: CQEvent):
    match = ev['match']
    month = int(match.group(1))
    day = int(match.group(2))
    
    monthdayQue = os.path.join(load_in_path,f"2021-{month:02}-{day:02}.png") 
    
  
    
    await bot.send(ev,MessageSegment.image(monthdayQue)) 

@sv.on_fullmatch('总结')
async def getciyun(bot, ev: CQEvent):
    if not hoshino.priv.check_priv(ev, hoshino.priv.OWNER):
        #await bot.send(ev,message = '',at_sender = False)
        return
    await bot.send(ev,message = '正在生成本群今日词云，请耐心等待')
    gid = ev.group_id
    makeclouds(gid)
    today = datetime.date.today().__format__('%Y-%m-%d')
    
    todayGid = os.path.join(load_in_path,f"{today}-{gid}.png") 
    image = open(todayGid,'rb')
    img_file = f'[CQ:image,file=base64://{base64.b64encode(image.read()).decode()}]'
    msg = MessageSegment.text("今日词云：") + img_file
    await bot.send(ev, msg) 
     
    #使用base64方式发送图片
    
    #await bot.send(ev,MessageSegment.image(todayGid))


@sv.on_fullmatch('昨日总结')
async def getciyunb(bot, ev: CQEvent):
    if not hoshino.priv.check_priv(ev, hoshino.priv.OWNER):
        await bot.send(ev,message = '仅限群主可用',at_sender = True)
        return
    await bot.send(ev,message = '正在生成本群昨日词云，请耐心等待',at_sender = True)
    gid = ev.group_id
    makecloudsb(gid)
    yesterday = (datetime.date.today() + datetime.timedelta(-1)).__format__('%Y-%m-%d')
    
    yesterdayGid = os.path.join(load_in_path,f"{yesterday}-{gid}.png") 
    
    image = open(yesterdayGid,'rb')
    img_file = f'[CQ:image,file=base64://{base64.b64encode(image.read()).decode()}]'
    msg = MessageSegment.text("昨日词云：") + img_file
    await bot.send(ev, msg)
    #使用base64方式发送图片
    
    #await bot.send(ev,MessageSegment.image(yesterdayGid))
    
def random_color_func(word=None, font_size=None, position=None,
                      orientation=None, font_path=None, random_state=None):
  
    if random_state is None:
        random_state = Random()
    return "hsl(%d, 75%%, 62%%)" % random_state.randint(0, 225)#值，饱和度，色相
    
def makeclouds(gid):
    global loadpath
    global logpath
    bot = nonebot.get_bot()
    today = datetime.date.today().__format__('%Y-%m-%d')
  
    logpath = os.path.join(loadpath,f"{today}.log") 
    f = open(logpath, "r", encoding="utf-8") #改善读取文件的方式，使其在所用操作系统上可用
    
    f.seek(0)
    gida = str(gid)
    msg=''
    for line in f.readlines():          #删除前缀和自己的发言
        if self_id in line or gida not in line:
            continue
        try:                         
            o = line.split("的消息: ")[1]
            msg += o  
        except:
            pass
    msg = re.sub('''[a-zA-Z0-9'!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘'！[\\]^_`{|}~\s]+''', "", msg)
    msg = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', msg)
    banword = []#此处为不显示的删除禁词
    ls = jieba.lcut(msg,cut_all=True)#制作分词
    stopwords = set()
    
    global tycpath  
    
    tycpath = os.path.join(plugin_path,f"tyc.txt")
    
    content = [line.strip() for line in open(tycpath,encoding='utf-8').readlines()]
    stopwords.update(content)
    txt = " ".join(ls)
    w = wordcloud.WordCloud(font_path=os.path.join(plugin_path,f"SimHei.ttf"),\
                            max_words=10000, width=2560, height=1440,\
                            background_color='white',stopwords=stopwords,\
                            relative_scaling=0.5,min_word_length=2,\
                            color_func=random_color_func#调色
        		    )
        		    
    w.generate(txt)
    w.to_file(f"{today}-{gid}.png")
    if gid:
        try:
            shutil.move(f"{today}-{gid}.png",load_in_path)
        except:
            #os.remove(load_in_path+f"\\{today}-{gid}.png")
            
            os.remove(os.path.join(load_in_path,f"{today}-{gid}.png") )
            
            shutil.move(f"{today}-{gid}.png",load_in_path)
            
    else:
        try:
            shutil.move(f"{today}.png",load_in_path)
        except:
           # os.remove(load_in_path+f"\\{today}.png")
           
            os.remove(os.path.join(load_in_path,f"{today}.png") )
            
            shutil.move(f"{today}.png",load_in_path)
        
        
def makecloudsb(gid):
    global loadpath
    bot = nonebot.get_bot()
    today = datetime.date.today().__format__('%Y-%m-%d')
    yesterday = (datetime.date.today() + datetime.timedelta(-1)).__format__('%Y-%m-%d')
    gida = str(gid)
    
    f = open(os.path.join(loadpath,f"{yesterday}.log"), "r", encoding="utf-8")
    f.seek(0)
    
    msg=''
    for line in f.readlines():          #删除前缀和自己的发言
        if self_id in line or gida not in line:
            continue
        try:                         
            o = line.split("的消息: ")[1]
            msg += o  
        except:
            pass
    msg = re.sub('''[a-zA-Z0-9'!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘'！[\\]^_`{|}~\s]+''', "", msg)
    msg = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', msg)
    banword = []#此处为不显示的删除禁词
    ls = jieba.lcut(msg)#制作分词
    stopwords = set()
    content = [line.strip() for line in open(tycpath,encoding='utf-8').readlines()]
    stopwords.update(content)
    txt = " ".join(ls)
    w = wordcloud.WordCloud(font_path=os.path.join(plugin_path,f"SimHei.ttf"),\
                            max_words=10000, width=2560, height=1440,\
                            background_color='white',stopwords=stopwords,\
                            relative_scaling=0.5,min_word_length=2,\
                            color_func=random_color_func#词汇上限，宽，高,背景颜色去除停用词(tyc.txt),频次与大小相关度，最小词长,调色
        )
    w.generate(txt)
    w.to_file(f"{yesterday}-{gid}.png")
    if gid:
        try:
            shutil.move(f"{yesterday}-{gid}.png",load_in_path)
        except:
            os.remove(os.path.join(load_in_path,f"{yesterday}-{gid}.png") )
            
            shutil.move(f"{yesterday}-{gid}.png",load_in_path)
    else:
    
        try:
            shutil.move(f"{yesterday}.png",load_in_path)
        except:
        
            os.remove(os.path.join(load_in_path,f"{yesterday}.png") )
            
            shutil.move(f"{yesterday}.png",load_in_path)
            
            

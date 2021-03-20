import requests
import hoshino
from hoshino import Service, R
from .submit import *

sv_help = '''
=====命令=====
注意：[]内为指令，外为改指令实现的功能
自动打卡无需命令，14.15自动打卡
初始化和删除用户仅限维护组
==============
[打卡帮助] 查看帮助
[初始化] 初始化用户信息
[添加用户 学号 密码 QQ] 添加新用户
(注意参照格式：添加用户 2018214233 xxxaaa 23332)
[删除用户 学号] 删除信息
[打卡] 今日校园手动打卡
[打卡用户列表] 看所有用户

'''.strip()

sv = Service('cpdaily-HFUT', help_=sv_help, enable_on_default=False, bundle='今日校园订阅')

#帮助界面
@sv.on_fullmatch("打卡帮助")
async def help(bot, ev):
    await bot.send(ev, sv_help)

#手动打卡功能
@sv.on_fullmatch(('打卡','今日校园打卡'))
async def cpdailyHFUT(bot, ev):
    config = getYmlConfig()
    bot = hoshino.get_bot()
    msg = '今日校园打卡系统（手动模式）：正在开始处理'
    await bot.send(ev, msg)
    for user in config['users']:
        printLog(f'开始处理用户{user["user"]["username"]}')
        try:
            # login and submit
            if login(user['user']['username'], user['user']['password']) and submit(user['user']['location']):
                # succeed
                printLog('当前用户处理成功')
                # 下面的emailmsg邮件消息内容可随意更改
                emailmsg = '''

你好：

    来自(QQ:2047788491)优衣酱~的消息：

                      自动提交成功！
                '''
                InfoSubmit(emailmsg, user['user']['email'])
                msg = '已为'+ f'{user["user"]["username"]}' + '完成提交'
                await bot.send(ev, msg)
            else:
                # failed
                printLog('发生错误，终止当前用户的处理')
                # 下面的emailmsg邮件消息内容可随意更改
                emailmsg = '''

你好：

    来自(QQ:2047788491)优衣酱~的消息：

                      自动提交失败！
    发生错误，原因未知，请联系维护组~
                '''
                InfoSubmit(emailmsg, user['user']['email'])
                msg = '发生错误，错误用户为'+ f'{user["user"]["username"]}' + '，详情请联系维护组'
                await bot.send(ev, msg)
        except HTTPError as httpError:
            print(f'发生HTTP错误：{httpError}，终止当前用户的处理')
            emailmsg = '''

你好：

    来自(QQ:2047788491)优衣酱~的消息：

                      自动提交失败！
    发生HTTP错误，请联系维护组~
                '''
            InfoSubmit(emailmsg, user['user']['email'])
            msg = '发生HTTP错误，已停止用户'+ f'{user["user"]["username"]}' + '的提交，详情请联系维护组'
            await bot.send(ev, msg)
            # process next user
            continue

    printLog('所有用户处理结束')
    msg = '今天是' + str(get_time()) + get_week_day(get_time()) + '\n所有用户手动处理结束，今日校园打卡结果已出，详情请关注邮件'
    await bot.send(ev, msg)

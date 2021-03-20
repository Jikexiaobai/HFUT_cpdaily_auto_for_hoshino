import requests
import hoshino
from hoshino import Service, R
from .submit import *

svsub = Service('cpdaily-HFUT-auto', enable_on_default=False, help_='今日校园自动打卡')

# 自动打卡功能
@svsub.scheduled_job('cron', hour='14', minute='15')
async def cpdailyHFUTauto():
    config = getYmlConfig()
    msg = '今日校园自动打卡系统：正在开始处理'
    await svsub.broadcast(msg, 'cpdaily-HFUT-auto', 0.2)
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
                await svsub.broadcast(msg, 'cpdaily-HFUT-auto', 0.2)
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
                await svsub.broadcast(msg, 'cpdaily-HFUT-auto', 0.2)
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
            await svsub.broadcast(msg, 'cpdaily-HFUT-auto', 0.2)
            # process next user
            continue

    printLog('所有用户处理结束')
    msg = '今天是' + str(get_time()) + get_week_day(get_time()) + '\n所有用户自动处理结束，今日校园打卡结果已出，详情请关注邮件'
    await svsub.broadcast(msg, 'cpdaily-HFUT-auto', 0.2)

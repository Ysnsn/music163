


def start(user, task={}):
    music = user.music

    resp = music.daily_task(3)
    if resp['code'] == 200:
        user.taskInfo(task['taskName'], 'εδΊ«ζε')
    else:
        user.taskInfo(task['taskName'], user.errMsg(resp))

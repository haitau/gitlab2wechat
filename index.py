# -*- coding: utf8 -*-
import json
import transform_commit


def main_handler(event, context):
    """
    :param event: Python dict 对象    触发事件数据
    :param context: Python dict 对象  运行时信息
    :return:
    """
    try:
        # 读取配置文件，得到企业微信机器人URL前缀
        # json.dumps  将python 对象     序列化为  json格式的字符串
        # json.loads  将json格式的字符串 反序列化为 python 对象
        fp = open("config.json", "r")
        config_dict = json.load(fp)
        fp.close()
        wechat_robot_url = config_dict["URL"]

        # 首先获取到gitlab提交的key，并从配置中取到相应值，拼凑成完整的企业微信机器人URL
        wechat_robot_url += config_dict[event["queryString"]["key"]]

        print("GitLab 事件信息: " + json.dumps(event))

        # 转换处理gitlab 信息, 提交给 企业微信机器人
        transform_commit.transform_commit(event["headers"]["x-gitlab-instance"],json.loads(event["body"]), wechat_robot_url)

    except Exception as e:
        print(e)

    return True


"""
# -*- coding: utf8 -*-
import json
def main_handler(event, context):
    print("Received event: " + json.dumps(event, indent = 2)) 
    print("Received context: " + str(context))
    print("Hello world")
    return("Hello World")
"""

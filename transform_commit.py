# -*- coding: utf8 -*-
"""
GITLAB 不同事件的处理并提交给企业微信机器人
"""
import json
import urllib.request


def transform_commit(gitlab_server_url, gitlab_event_body, wechat_robot_url):
    """
    :param gitlab_server_url: gitlab 服务器域名url string
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :param wechat_robot_url: 企业微信机器人URL   string
    :return: True
    """
    try:
        # 使用markdown 传递消息，定义企业微信message
        # content: markdown内容，最长不超过4096个字节，必须是utf8编码
        msg_md_dict = {"msgtype": "markdown", "markdown": {"content": ""}}
        content_str = ""

        #  针对gitlab event 构造 企业微信 markdown 消息的 content 字串内容
        if gitlab_event_body["object_kind"] == "push":
            content_str = event_push_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "note":
            content_str = event_comment_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "deployment":
            content_str = event_deployment_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "feature_flag":
            content_str = event_feature_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "issue":
            content_str = event_issue_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "build":
            content_str = event_job_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "merge_request":
            content_str = event_merge_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "pipeline":
            content_str = event_pipeline_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "release":
            content_str = event_release_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "tag_push":
            content_str = event_tag_str(gitlab_server_url, content_str, gitlab_event_body)
        elif gitlab_event_body["object_kind"] == "wiki_page":
            content_str = event_wiki_str(gitlab_server_url, content_str, gitlab_event_body)
        else:
            content_str = "不支持的事件类型"

        # 赋值给 markdown dict 中的 content
        msg_md_dict["markdown"]["content"] = content_str

        # 提交给企业微信机器人
        headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}
        req = urllib.request.Request(wechat_robot_url, bytes(json.dumps(msg_md_dict), 'utf8'), headers, 'Post')
        response = urllib.request.urlopen(req).read()
        # print(response)

    except Exception as e:
        print(e)

    return True


def event_push_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab push 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "[" + gitlab_event_body["user_name"] + "]"
        content_str += "(" + gitlab_server_url + "/" + gitlab_event_body["user_username"] + ")"
        content_str += " 推送了 " + str(gitlab_event_body["total_commits_count"]) + " 个新的提交到 "
        content_str += "[" + gitlab_event_body["project"]["name"] + "]"
        content_str += "(" + gitlab_event_body["project"]["web_url"] + ")"
        content_str += " 的 [" + gitlab_event_body["ref"][11:] + "]"
        content_str += ("(" + gitlab_event_body["project"]["homepage"]
                        + "/-/tree/" + gitlab_event_body["ref"][11:] + ")")
        content_str += " 分支\n"

        # markdown 各次commit 的相关内容
        # print(gitlab_event_body["commits"])
        for index, element in enumerate(gitlab_event_body["commits"]):
            content_str += ">"
            content_str += "[" + element["id"][0:8] + "]"
            content_str += "(" + element["url"] + ")"
            content_str += " - " + element["message"] + "\n"
    except Exception as e:
        print(e)
    return content_str


def event_comment_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab comment 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "[" + gitlab_event_body["user"]["name"] + "](" + gitlab_server_url + "/" + \
                      gitlab_event_body["user"]["username"] + ")"
        if gitlab_event_body["object_attributes"]["noteable_type"] == "Commit":
            content_str += " 评论了你的提交 [" + gitlab_event_body["commit"]["title"] + "](" + \
                           gitlab_event_body["object_attributes"]["url"] + ")\n"
            content_str += ">"
            content_str += "-- 评论内容为：" + gitlab_event_body["object_attributes"]["note"]

        elif gitlab_event_body["object_attributes"]["noteable_type"] == "MergeRequest":
            content_str += " 评论了你的合并请求 [" + gitlab_event_body["merge_request"]["title"] + "](" + \
                           gitlab_event_body["object_attributes"]["url"] + ")\n"
            content_str += ">"
            content_str += "-- 评论内容为：" + gitlab_event_body["object_attributes"]["note"]

        elif gitlab_event_body["object_attributes"]["noteable_type"] == "Issue":
            content_str += " 评论了你的议题 [" + gitlab_event_body["issue"]["title"] + "](" + \
                           gitlab_event_body["object_attributes"]["url"] + ")\n"
            content_str += ">"
            content_str += "-- 评论内容为：" + gitlab_event_body["object_attributes"]["note"]

        elif gitlab_event_body["object_attributes"]["noteable_type"] == "Snippet":
            content_str += " 评论了你的代码片段 [" + gitlab_event_body["snippet"]["title"] + "](" + \
                           gitlab_event_body["object_attributes"]["url"] + ")\n"
            content_str += ">"
            content_str += "-- 评论内容为：" + gitlab_event_body["object_attributes"]["note"]

        else:
            pass

    except Exception as e:
        print(e)
    return content_str


def event_deployment_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab deployment 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = ""
        # print(content_str)

    except Exception as e:
        print(e)
    return content_str


def event_feature_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab feature 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = ""
        # print(content_str)

    except Exception as e:
        print(e)
    return content_str


def event_issue_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab issue 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容、议题事件
        content_str = "[" + gitlab_event_body["user"]["name"] + "](" + gitlab_server_url + "/" + \
                      gitlab_event_body["user"]["username"] + ")"
        content_str += " 发表了[" + gitlab_event_body['repository']['name'] + "](" + \
                       gitlab_event_body['repository']['homepage'] + ")"
        content_str += " 的议题： [" + gitlab_event_body["object_attributes"]["title"] + "](" + \
                       gitlab_event_body['object_attributes']['url'] + ")\n"
        content_str += ">"
        content_str += " -- 议题内容：" + gitlab_event_body['object_attributes']['description']

    except Exception as e:
        print(e)
    return content_str


def event_job_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab job 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "[" + gitlab_event_body["user"]["name"] + "](" + gitlab_server_url + "/" + \
                      gitlab_event_body["user"]["username"] + ")"
        content_str += " 的作业 [" + gitlab_event_body["commit"]["message"] + "](" + \
                       gitlab_event_body["repository"]["homepage"] + "/-/pipelines/" + \
                       str(gitlab_event_body["commit"]["id"]) + ")\n"
        content_str += ">"
        content_str += "[" + gitlab_event_body["sha"][0:8] + "](" + \
                       gitlab_event_body["repository"]["homepage"] + "/-/commit/" + \
                       gitlab_event_body["sha"] + ")"
        content_str += " -- 第 [" + str(gitlab_event_body["commit"]["id"]) + "](" + \
                       gitlab_event_body["repository"]["homepage"] + "/-/jobs)"
        content_str += " 流水线状态变更为 " + gitlab_event_body["build_status"]

    except Exception as e:
        print(e)
    return content_str


def event_merge_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab merge 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "[" + gitlab_event_body['user']['name'] + "](" + gitlab_server_url + \
                      "/" + gitlab_event_body['user']['username'] + ")"
        content_str += " 的合并请求：[" + gitlab_event_body['object_attributes']['title'] + \
                       '](' + gitlab_event_body['object_attributes']['url'] + ')\n'
        content_str += "请求将 " + gitlab_event_body["object_attributes"]["source_branch"]
        content_str += " 合并到 " + gitlab_event_body["object_attributes"]["target_branch"] + "\n"
        content_str += ">"
        content_str += "合并内容: " + gitlab_event_body["object_attributes"]["description"]
        # print(content_str)

    except Exception as e:
        print(e)
    return content_str


def event_pipeline_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab pipeline 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "[" + gitlab_event_body["user"]["name"] + "](" + \
                      gitlab_server_url + "/" + gitlab_event_body["user"]["username"] + ")"
        content_str += " 提交了个作业-流水线 [" + gitlab_event_body["commit"]["title"] + "](" + \
                       gitlab_event_body["commit"]["url"] + ")\n"
        content_str += ">"
        content_str += "[" + gitlab_event_body["object_attributes"]["sha"][0:8] + \
                       "](" + gitlab_event_body["commit"]["url"] + ")"
        content_str += " -- 目前阶段：" + gitlab_event_body["builds"][0]["stage"]

    except Exception as e:
        print(e)
    return content_str


def event_release_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab release 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "由-" + gitlab_event_body["commit"]["author"]["name"] + "-添加的标签 "
        content_str += "[" + gitlab_event_body["tag"] + "](" + gitlab_event_body["project"]["web_url"] + \
                       "/-/tags/" + gitlab_event_body["tag"] + ")"
        content_str += " 发行了 [" + gitlab_event_body["name"] + "](" + gitlab_event_body["url"] + ")\n"
        content_str += ">"
        content_str += " [" + gitlab_event_body["commit"]["id"][0:8] + "](" + \
                       gitlab_event_body["commit"]["url"] + ")"
        content_str += " -- 部署内容：" + gitlab_event_body["description"]

    except Exception as e:
        print(e)
    return content_str


def event_tag_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab tag 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "[" + gitlab_event_body["user_name"] + "]"
        content_str += "(" + gitlab_server_url + "/" + gitlab_event_body["user_username"] + ")"
        content_str += " 推送了 " + str(gitlab_event_body["total_commits_count"]) + " 标签到 "
        content_str += "[" + gitlab_event_body["project"]["name"] + "]"
        content_str += "(" + gitlab_event_body["repository"]["homepage"] + ") 上\n"
        content_str += "标签：[" + gitlab_event_body["ref"][10:] + "]"
        content_str += "(" + gitlab_event_body["repository"]["homepage"] + "/-/tags/)\n"
        content_str += "消息：" + gitlab_event_body["message"] + "\n"

        # markdown 各次commit 的相关内容
        # print(gitlab_event_body["commits"])
        for index, element in enumerate(gitlab_event_body["commits"]):
            content_str += ">"
            content_str += "[" + element["id"][0:8] + "]"
            content_str += "(" + element["url"] + ")"
            content_str += " - " + element["title"] + "\n"

    except Exception as e:
        print(e)
    return content_str


def event_wiki_str(gitlab_server_url, content_str, gitlab_event_body):
    """
    对 gitlab wiki 事件进行处理，返回拼接的字符串
    :param gitlab_server_url:  gitlab 服务器地址
    :param content_str:  预备传递给企业微信群机器人的消息中的字符串
    :param gitlab_event_body: gitlab 事件的信息  Python dict 对象
    :return: 拼接的字符串
    """
    try:
        # markdown 首行内容
        content_str = "[" + gitlab_event_body["user"]["name"] + "](" + gitlab_server_url + "/" + \
                      gitlab_event_body["user"]["username"] + ")"
        content_str += " 提交了一个wiki [" + gitlab_event_body["object_attributes"]["title"] + "](" + \
                       gitlab_event_body["object_attributes"]["url"] + ")\n"
        content_str += ">"
        content_str += " -- " + gitlab_event_body["object_attributes"]["content"]
        # print(content_str)

    except Exception as e:
        print(e)
    return content_str

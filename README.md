# Gitlab 2 WeChat

**原始需求**：将Gitlab的动态发送给企业微信群机器人  
**实现方法**：使用腾讯云函数接收Gitlab消息，在转换后发送给企业微信群机器人  
**相关资料**： 
 + [Gitlab Event](https://archives.docs.gitlab.com/15.11/ee/user/project/integrations/webhook_events.html)  
 + [企业微信群机器人配置说明](https://developer.work.weixin.qq.com/document/path/91770)  
   > *请注意：这里的 Gitlab event 版本为15.11。如果是其它版本，最好是切换版本查看。*

**环境要求**：
 + [腾讯云](https://cloud.tencent.com/login)账号
 + Gitlab 服务器（或项目）管理权限
 + 企业微信群管理员（可创建群机器人）
***
## 1. 代码说明  
三个文件：index.py 、transform_commit.py 、 config.json  
*目录：gitlab_event_json 是 Gitlab 事件向 webhook 提交的内容范例*
   > *范例文件的信息是不全的，要另外提取事件内容进行内容的分析与转换*
***
### 1.1 index.py  
腾讯云函数默认入口文件。  
Gitlab 事件调用 webhook url （云函数的公网地址）后，相关事件信息传入到入口文件主函数的 event、content 中（两者为Python dict对象）  

如果在新建腾讯云函数时，启用了日志功能，则如下代码会将 Gitlab 事件信息打印到日志中：  
` print("GitLab 事件信息: " + json.dumps(event)) ` 

在实际调试过程中，要根据打印的内容来做实际的代码编写。  
现在的代码没有完成所有事件的处理。

***
### 1.2 transform_commit.py
将 Gitlab 事件信息转换成 企业微信群机器人能接受的信息并提交。

***
### 1.3 config.json
一个腾讯云函数用于多个 Git 项目、多个企业微信群机器人时，可以用此配置文件来定义相互之间的映射关系。

***
## 2. 部署过程
### 2.1 企业微信机器人
在企业微信群添加群机器人后，查看群机器人信息：  
![群机器人信息](https://github.com/haitau/res/blob/main/git2wechat/wechat_robot_info.png?raw=true)  
所有群机器人的 webhook 地址都类似于：  
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=wechat_robot_key  
 key 的值 wechat_robot_key 在后面的操作中需要配置到云函数的 config.json 的键值对中。 
***
### 2.2 腾讯云函数
#### 2.2.1 新建云函数  
![新建云函数](https://github.com/haitau/res/blob/main/git2wechat/tencent_01.png?raw=true)  

   新建窗口，创建类型选择“从头开始”，其它内容不需要变更  
   如果需要在日志中打印运行结果，可选择开启日志服务  
![新建窗口](https://github.com/haitau/res/blob/main/git2wechat/tencent_02.png?raw=true)

***
#### 2.2.2 设置云函数  
 + 创建函数URL  
![创建URL](https://github.com/haitau/res/blob/main/git2wechat/tencent_03.png?raw=true)  
在弹出的窗口选择：公网访问 启用  
![创建URL](https://github.com/haitau/res/blob/main/git2wechat/tencent_04.png?raw=true)  
 + 拷贝公网链接备用  
![拷贝URL](https://github.com/haitau/res/blob/main/git2wechat/tencent_05.png?raw=true)  

***
#### 2.2.3 编辑部署云函数  
 + 编辑 index.py, 将项目 index.py 的内容拷贝过去覆盖线上内容  
![编辑 index.py](https://github.com/haitau/res/blob/main/git2wechat/tencent_06.png?raw=true)  
  
  
 + 创建 transform_commit.py  
在 src 目录下创建 transform_commit.py 文件，将项目同名文件内容拷贝过去  
  
  
 + 创建 config.json  
在 src 目录下创建 config.json 文件，将项目同名文件内容拷贝过去  
  
  
 + 修改 config.json  
使用工具，生成一个随机字符串，用来替代 gitlab_key_01, 同时用企业微信群机器人的 key 的值替换掉 wechat_robot_key_01  
![编辑 config.json](https://github.com/haitau/res/blob/main/git2wechat/tencent_07.png?raw=true) 
***
### 2.3 Gitlab 配置
#### 2.3.1 生成 gitlab 项目使用的 webhook url  
在前面，已经拿到了腾讯云函数的公网访问链接，以及生成了一个随机字符串 gitlab_key_01  
现在将此二者拼接成 gitlab 需要使用的 webhook url ，类似如下形式： 

https://444444444-xxxxxxxxxx-ad.scf.tencentcs.com/send?key=gitlab_key_01  

#### 2.3.2 配置 gitlab 项目的 webhook 
![配置 gitlab 项目 webhook](https://github.com/haitau/res/blob/main/git2wechat/gitlab_01.png?raw=true) 

#### 2.3.3 多Git项目与多企业微信机器人  
类似前面的步骤：  
 + 拿到企业微信群机器人的 key ；  
 + 生成随机字串 ； 
 + 将两个值成对配置进 config.json  
 + 云函数URL与随机字串拼接生成 webhook url
 + 用拼接的 webhook url 配置 gitlab 项目  


## 关于 cynet
cynet是一个基于mastodon的网络类网盘协议。
扩展了mastodon的 **上传 下载 分享链接** 功能
# cynet 命令行使用手册
## 主要命令
```shell
gu #1{类型:文件 /登录验证信息/ } #2{类型:文件夹 /上传文件夹内的所有文件/ }

u #1{类型:文件 /上传的task任务路径/ }

gd #1{类型:url /下载链接/ } #2{ 类型:文件夹 /下载到哪个文件夹/ }

d #1{类型:文件 /下载的task任务路径/ }
```

# 使用范例
## 上传文件
### 第一步 生成上传task.json
**gu login.json d:\donwload\**
login.json 是一个用于登录验证的文件，它的内容通常是这样的。你需要在上传前创建它
```javascript
{
      "instance": "xmx.net", //登录的实例
      "username": "asdsa2@outlook.com", //登录的用户名
      "password": "isanc21" //登录的密码
}
```
### 第二步 执行上传task.json
**u task.u.随机任务名称.json**
这一步成功执行后会生成一个下载链接，通常是 **cynet:?p=传输协议:i=实例名称:u=1f8b0800c72f3d5e02ffad98ef6a1d470cc55f25f873e33bd268a499bc4a294...**

**到这一步用得到的 下载链接 就可以实现分享下载**

## 下载文件
### 第一步 生成下载task.json
获取到得到一个cynet链接，使用命令先生成一个下载任务
**gd cynet:?p=https:i=pawoo.net:u=1f8b0800c72f3d5 d:\download\**
会得到一个 task.u.随机任务名称.json 文件

### 第二步 执行下载task.json
**u task.u.随机任务名称.json**

### 注意事项
- 本工具的 **断点上传下** 载实现是 **基于文件** 的断点而非传输协流的断点。
如果需要强行中断任务 不能够直接关闭程序,应该通过网络设置 **断开网络连接**。
等待程序出现**网络断开的提示后再关闭程序**
否则会有一定几率损坏 task 文件
- 文件的分割不要太大 最大最好不要超过**39mb**。
mastodon的mp4最大不能超过**40mb**，另外本程序的打包数据占用了不超过1mb的空间。
目前经过我测试 每个包最好保持在 **1-10mb** 最佳。原因是实例大多位于国外服务器。网络通信延时高，丢包率高。为保证快速缓存文件压缩包尽量小一点为好。

# task.json说明
**task.json定义了上传下载任务的配置信息**
## 上传任务
上传下载任务都是通过配置json文件执行
一个上传任务的json文件通常是这样的
**执行上传任务之前**
```javascript
{
  "type": "upload",
  "instance": "xmx.net", //登录的实例
  "username": "asdsa2@outlook.com", //登录的用户名
  "password": "isanc21" //登录的密码
  "path": "_test/upload",//上传路径
  "jobs": [
    {
      "md5": "", //没有上传到服务器之前是没有这个值的
      "name": "blender-2.81a-windows64.zip.001",
      "status": 0, //0 代表还没有被上传到服务器
      "url": "" //没有上传到服务器之前是没有这个值的
    },
    {
      "md5": "",
      "name": "blender-2.81a-windows64.zip.002",
      "status": 0,
      "url": ""
    }//...
}
```
**执行上传任务之后**
```javascript
{
  "type": "upload",//任务类型
  "instance": "xmx.net", //登录的实例
  "username": "asdsa2@outlook.com", //登录的用户名
  "password": "isanc21" //登录的密码
  "path": "_test/upload",//上传路径
  "jobs": [
    {
      "md5": "7c1ec2c18604c28f42e418db9cd11813", //文件验证的md5值
      "name": "blender-2.81a-windows64.zip.001",//压缩包名称
      "status": 1, //1 代表文件已经上传到了服务器
      "url": "https://img.pawoo.net/media_attachments/files/024/261/500/original/d2dc60100314d7ad.mp4" //上传文件的真实地址
    },
    {
      "md5": "0a9e30212570d8215efc557d11ea6207",
      "name": "blender-2.81a-windows64.zip.002",
      "status": 1,
      "url": "https://img.pawoo.net/media_attachments/files/024/261/502/original/727cfbabb77f5c65.mp4"
    }//...
}
```

##下载任务
下载任务是通过配置json文件执行
一个下载任务的json文件通常是这样的
**执行下载任务之前**
```javascript
{
  "type": "download",//任务类型
  "path": "test",//下载到哪个文件夹
  "jobs": [
    {
      "md5": "7c1ec2c18604c28f42e418db9cd11813",//文件的md5值
      "name": "blender-2.81a-windows64.zip.001",//压缩包名称
      "status": 0,//文件下载到本地之前是 0
      "url": "https://img.pawoo.net/media_attachments/files/024/261/500/original/d2dc60100314d7ad.mp4"//文件的真实下载地址
    }
}
```
**执行下载任务之后**
status 值会变成 1 代表已经下载到本地

#关于账户安全
**与他人分享文件的时候，不要直接分享 task.u.json 给别人，里面包含了你的账号信息。分享下载地址的时候最好分享 cynet链接。也或者是 task.d.json**
#最后 关于本协议
只要 **作者还活着** cynet会持续更新。我会把它当成一个大坑来填。继续完善它的功能。
因为 **最美好的回忆，应当给最爱的人 (●’◡’●)**
# 用前参考

## 更新事宜

目前已适配2.1版本新增的三个副本

## 功能

1. 自动副本挑战以及再次挑战（拟造花萼金/赤、凝滞虚影、侵蚀隧洞和历战余响）
2. 自动重复委托派遣
3. 自动领取无名勋礼
4. 自动每日实训、邮件和助战奖励领取

## 后续安排

- [x] 重构代码，补全委托派遣和无名勋礼功能
- [ ] 图形化界面
- [ ] 侵蚀隧洞挑战成功暂停功能（打完后自动暂停，可以查看遗器属性）
- [ ] 遗器自动化一键整理（自动上锁，解锁，弃置）

## 如何指定副本

修改HSR_Help/auto_daily/config/config.json以确认你的需求，格式已在文件中给定。
配置内容请从HSR_Help/auto_daily/Types.py中参考获取，或者参考下面：

```json
{
  "mode": [
    {
      "mode": "Types.ModeType.QSSD",
      "detail": "Types.QSSDMode.SF",
      "round": 2
    },
    {
      "mode": "Types.ModeType.QSSD",
      "detail": "Types.QSSDMode.SF",
      "round": 3
    }
  ]
}
```

参考类型（detail的类型必须以mode为准，例如你选择了QSSD，那么detail必须为QSSDMode的枚举类）

```
mode:  Types.ModeType
detail: Types.LZYXMode | Types.QSSDMode | Types.NZXYMode | Types.NZHECMode | Types.NZHEJMode
round: int
````

## 如何运行

HSR_Help/auto_daily/main.py为程序入口，目前只开放了自动副本挑战以及再次挑战功能，
如需要其他功能请自行在HSR_Help/auto_daily/daily.py的auto_do_daily()函数中添加即可

## 注意事项

如果你正在使用多屏幕，请把游戏置于主屏幕上运行！
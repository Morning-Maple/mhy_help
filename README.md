# 用前参考

## 如何指定副本

修改HSR_Help/auto_daily/config.json以确认你的需求，格式已在文件中给定。
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

HSR_Help/auto_daily/main.py为程序入口

## 注意事项

如果你正在使用多屏幕，请把游戏置于主屏幕上运行！
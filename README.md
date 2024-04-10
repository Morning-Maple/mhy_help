# 用前参考

## 更新事宜

1. 采用了三线程，现在UI，日志轮询和脚本执行各自占据一个线程
2. 分辨率现在还未适配，仅能运行于1366x768下，且目前只有副本挑战通过了多轮测试，其余功能还在测试中
3. UI界面仅展示当次运行状态，如需查看完整情况，请移步logs文件夹下按”log_年月日.log“找到当天的日志查看情况

## 功能

1. 自动副本挑战以及再次挑战（拟造花萼金/赤、凝滞虚影、侵蚀隧洞和历战余响）
2. 自动重复委托派遣
3. 自动领取无名勋礼
4. 自动每日实训、邮件和助战奖励领取

## 后续安排

- [x] 重构代码，补全委托派遣和无名勋礼功能
- [x] 图形化界面
- [x] 侵蚀隧洞挑战成功暂停功能（打完后自动暂停，可以查看遗器属性）
- [ ] 分辨率适配
- [ ] 项目打包成exe文件
- [ ] 遗器自动化一键整理（自动上锁，解锁，弃置）

## 如何使用

clone代码后，请先安装好所需要的包，然后找到main.py文件，运行即可

## 注意事项

如果你正在使用多屏幕，请把游戏置于主屏幕上运行！
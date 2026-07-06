# Songguo Power Card for Home Assistant

松果电子电脑开机卡的 Home Assistant HACS 自定义集成。

## 功能

- 通过 UI 配置账号、密码，并从松果电子 API 获取设备列表选择设备。
- 提供电脑电源状态二进制传感器。
- 提供开机、关机、重启、强制关机、强制重启按钮。

## HACS 安装

1. 将本仓库添加到 HACS 的自定义仓库。
2. 类别选择 `Integration`。
3. 安装后重启 Home Assistant。
4. 在 `设置 -> 设备与服务 -> 添加集成` 中搜索 `Songguo Power Card`。
5. 输入账号和密码后，从自动获取的设备列表中选择开机卡设备。

## API 说明

本集成使用松果电子开放 API：

- 控制接口：`https://songguoyun.topwd.top/Esp_Api_new.php`
- 获取设备列表接口：`https://songguoyun.topwd.top/Esp_Api_advance.php`

标准开机卡动作值：

| value | 动作 |
| --- | --- |
| 0 | 关机 |
| 1 | 开机 |
| 2 | 强制重启 |
| 11 | 查询状态 |
| 14 | 强制关机 |
| 25 | 重启 |

## 注意

松果电子 API 文档说明只支持主账号调用，子账号和共享账号无权限。

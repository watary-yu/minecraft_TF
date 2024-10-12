# minecraft_TF

## What
Minecraft TwillightForestのマルチサーバーをEC2に立てた時の備忘録

## 環境
### Minecraft
* Minecraft/forge 1.20.1
* TwillightForest 4.3.2508

### インフラ
* EC2
    * type:t4g.medium
    * OS:Amazon Linux 2023
    * storage:EBS
        * type:gp3
        * volume:8GiB
    * Elastic IP:off
* domain:Route53

## 作業内容
WIP
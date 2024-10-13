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

### AWS設定
#### EC2立ち上げ

#### IAM

#### Route53
適当にドメインを買っておく\
Route53で買っておけばホストゾーンの設定はよしなにしてくれる。\
cloudfrareとかで購入した場合はがんばる

Minecraftクライアントから接続するサブドメインはEC2の起動時に自動登録させるのでここでは設定しない

### Minecraftサーバー設定
#### インストール

#### 自動起動
service登録する

#### ホワイトリスト制にする
port25565でランダムアクセスして荒らす不届き者がいるようなので、理由がなければホワイトリスト推奨\
もしくはport変えるか

### EC2内インフラ作業
#### script等配置
* `/script`の内容物を`home`ディレクトリに配置
* `/service/route53_attach.service`のEnvironmentを書き換え、`/lib/systemd/system/route53_attach.service`として配置

#### 環境変数登録
```bash
vim ~/.bashrc
```

以下を最下部に追記する(値は書き換える)
```text
export HOSTED_ZONE_ID='your_hosted_zone_id'
export DOMAIN_NAME='your_domain_name'
```

#### route53にIPを通知するサービス登録
```bash
# システムデーモンのリロード
sudo systemctl daemon-reload

# サービスの有効化
sudo systemctl enable route53_attach.service

# サービスの開始
sudo systemctl start route53_attach.service

# サービスの状態確認
sudo systemctl status route53_attach.service
```

#### インスタンス自動停止
0人が10分続けばインスタンスを停止するjob
```bash
crontab -e
```

以下を登録
```text
* * * * * /bin/screen -p 0 -S minecraft -X eval 'stuff "list\015"'
*/10 * * * * /usr/bin/python3 /home/ec2-user/count_active.py
```

以降はsshもドメインで接続できる

## 雑記
ConoHaVPSでも従量課金があると思い一度構築したが、インスタンス生成中(停止中でも)課金されるスタイルだったので解約。\
稼働しっぱなしならConoHaVPSの方が安いと思うが、週末のプレイ時のみ稼働のスタイルだと従量課金のEC2でインスタンス停止する方がコスト最適になりそうと思い構築。

EC2でIP固定したら待機中もコストかかるけど、DDNSすれば削減できそうなのでそこもトライ。\
ドメイン取得してみたい気持ちもあったので決断。\
(そのためドメイン取得・維持料金はコストから度外視している)


## 参考Link
* https://zenn.dev/suiteck/articles/f9e983ecb9d38d
* https://qiita.com/keys/items/264a64c2841875d51cdd
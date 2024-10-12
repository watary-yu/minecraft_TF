import os
import boto3
import re
import requests

# トークンとログのディレクトリを指定
TOKEN_DIR="token.txt"
LOG_DIR='minecraft/logs/screenlog.0'

# EC2リソースをIAMロールを使用して設定
ec2 = boto3.resource('ec2')

# ログのパターンを定義
pattern = r'.*?\[\d{2}:\d{2}:\d{2}\] \[Server thread/INFO\] \[minecraft/MinecraftServer\]: There are (\d+) of a max of \d+ players online:.*$'
repat = re.compile(pattern)

# ログ行がリストログかどうかを判定する関数
def isListLog(line):
    return repat.fullmatch(line) is not None

# インスタンスIDを取得する関数
def get_instance_id():
    try:
        # メタデータサービスバージョン2のトークンを取得
        token_response = requests.put(
            'http://169.254.169.254/latest/api/token',
            headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
            timeout=5
        )
        token_response.raise_for_status()
        token = token_response.text

        # トークンを使用してインスタンスIDを取得
        response = requests.get(
            'http://169.254.169.254/latest/meta-data/instance-id',
            headers={'X-aws-ec2-metadata-token': token},
            timeout=5
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

# メイン処理
def main():
    zero_count = 0  # 0人のカウントを初期化
    try:
        # ログファイルを読み込み、行を逆順にする
        with open(LOG_DIR) as f:
            lines = f.read().splitlines()
            lines.reverse()
            # リストログを探してプレイヤー数を確認
            for s in lines:
                if isListLog(s):
                    num_players = int(repat.fullmatch(s).groups()[0])
                    if num_players == 0:
                        zero_count += 1
                    else:
                        break  # 1人以上のタイミングがあったらループを終了
                    if zero_count >= 10:
                        # 0人が10回連続した場合、インスタンスを停止
                        instance_id = get_instance_id()
                        if instance_id:
                            instance = ec2.Instance(instance_id)
                            instance.stop()
                        break
    except Exception as e:
        pass  # エラー処理を追加する場合はここに記述

# スクリプトのエントリーポイント
if __name__ == '__main__':
    main()
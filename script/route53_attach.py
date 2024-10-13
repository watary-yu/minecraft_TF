import boto3
import requests
import sys
import logging
import os

# ログの設定
logging.basicConfig(
    filename='route53_attach.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Route 53のクライアントを作成
route53 = boto3.client('route53')

# ホストゾーンIDを指定
HOSTED_ZONE_ID = os.getenv('HOSTED_ZONE_ID')

# ドメイン名を指定
DOMAIN_NAME = os.getenv('DOMAIN_NAME')

def get_instance_ip():
    """インスタンスのパブリックIPを取得"""
    try:
        # トークンを取得
        token_response = requests.put(
            'http://169.254.169.254/latest/api/token',
            headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
            timeout=5
        )
        token_response.raise_for_status()
        token = token_response.text

        # パブリックIPを取得
        response = requests.get(
            'http://169.254.169.254/latest/meta-data/public-ipv4',
            headers={'X-aws-ec2-metadata-token': token},
            timeout=5
        )
        response.raise_for_status()
        logging.debug(f"Public IP obtained: {response.text}")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to get public IP: {e}")
        return None

def update_route53_record(action, ip_address=None):
    """Route 53のレコードを更新"""
    try:
        change_batch = {
            'Comment': 'Update record for EC2 instance',
            'Changes': [
                {
                    'Action': action,
                    'ResourceRecordSet': {
                        'Name': DOMAIN_NAME,
                        'Type': 'A',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': ip_address}] if ip_address else []
                    }
                }
            ]
        }
        response = route53.change_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            ChangeBatch=change_batch
        )
        logging.info(f"Route 53 record {action} successful: {response}")
    except Exception as e:
        logging.error(f"Failed to update Route 53 record: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'delete':
        # 停止時にレコードを削除
        logging.info("Executing DELETE action")
        update_route53_record('DELETE')
    else:
        # 起動時にレコードを作成または更新
        logging.info("Executing UPSERT action")
        ip_address = get_instance_ip()
        if ip_address:
            update_route53_record('UPSERT', ip_address)
        else:
            logging.warning("No IP address found, skipping UPSERT")

if __name__ == '__main__':
    logging.info("Script started")
    main()
    logging.info("Script finished")
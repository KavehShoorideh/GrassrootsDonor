from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

filename = config.get('filenames', '2020_candidate_file').strip('\'')
api_key = config.get('api_keys', )
endpoint = f'http://api.followthemoney.org/entity.php?eid=#######&APIKey={api_key}&mode=json'
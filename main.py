import json
from pathlib import Path
import dotenv

from nostr_dvm.framework import DVMFramework
# from nostr_dvm.tasks.generic_dvm import GenericDVM
from nostr_dvm.tasks.discovery_trending_lumina_relay import TrendingLUMINARelay
from nostr_dvm.utils.admin_utils import AdminConfig
from nostr_dvm.utils.dvmconfig import build_default_config
from nostr_dvm.utils.nip89_utils import NIP89Config, check_and_set_d_tag
from nostr_sdk import Keys, Kind



def playground(announce=False):
    framework = DVMFramework()

    admin_config = AdminConfig()
    admin_config.REBROADCAST_NIP89 = announce
    admin_config.REBROADCAST_NIP65_RELAY_LIST = announce
    admin_config.UPDATE_PROFILE = announce

    name = "Trending Pictures"
    identifier = "trending_pictures_lumina"  # Chose a unique identifier in order to get a lnaddress
    dvm_config = build_default_config(identifier)
    dvm_config.KIND = Kind(5300)  # Manually set the Kind Number (see data-vending-machines.org)

    # Add NIP89
    nip89info = {
        "name": name,
        "picture": "https://nosto.re/9a743767cdaa96889c335bc4ded7d5d72bd881b43d04fd95b1e69f102466f7a3.png",
        "about": "I show trending pictures (powered by LUMINA.rocks)",
        "supportsEncryption": True,
        "personalized": False,
        "amount": 0,
        "acceptsNutZaps": dvm_config.ENABLE_NUTZAP,
        "nip90Params": {
        }
    }

    nip89config = NIP89Config()
    nip89config.DTAG = check_and_set_d_tag(identifier, name, dvm_config.PRIVATE_KEY, nip89info["picture"])
    nip89config.CONTENT = json.dumps(nip89info)

    dvm = TrendingLUMINARelay(name=name, dvm_config=dvm_config, nip89config=nip89config,
                 admin_config=admin_config)
    
    framework.add(dvm)

    framework.run()

if __name__ == '__main__':
    env_path = Path('.env')
    if not env_path.is_file():
        with open('.env', 'w') as f:
            print("Writing new .env file")
            f.write('')
    if env_path.is_file():
        print(f'loading environment from {env_path.resolve()}')
        dotenv.load_dotenv(env_path, verbose=True, override=True)
    else:
        raise FileNotFoundError(f'.env file not found at {env_path} ')
    announce = False

    playground(announce=announce)

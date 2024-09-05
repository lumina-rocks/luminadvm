import os

from nostr_sdk import Keys, LogLevel

from nostr_dvm.utils.nip88_utils import NIP88Config
from nostr_dvm.utils.nip89_utils import NIP89Config
from nostr_dvm.utils.nostr_utils import check_and_set_private_key
from nostr_dvm.utils.outbox_utils import AVOID_OUTBOX_RELAY_LIST
from nostr_dvm.utils.zap_utils import check_and_set_ln_bits_keys

class DVMConfig:
    SUPPORTED_DVMS = []
    PRIVATE_KEY: str = ""
    PUBLIC_KEY: str = ""
    FIX_COST: float = None
    PER_UNIT_COST: float = None

    RELAY_LIST = ["wss://relay.primal.net",
                  "wss://nostr.mom", "wss://nostr.oxtr.dev",
                  "wss://relay.nostr.net"
                  ]

    RECONCILE_DB_RELAY_LIST = ["wss://relay.damus.io", "wss://nostr21.com",
                   "wss://nostr.oxtr.dev",
                  "wss://relay.nostr.net" , "wss://relay.primal.net"] #, "wss://relay.snort.social"]

    MUTE =  ["npub1x5vhtx7j2prvueeenwf7tmesrzmuzc50zs0aakgd75v5c30ekj3s5zjckj",
              "npub1l03urys27uet2u6wq6u90rnzf7kv5c3wfu3cyndqz9lq75g46c5q0wkpsj",
              "npub17g7qhlu4caefd88vateedm9wau9ys6xt6jhjcfu2kqyw9xmnucxs5d6crj",
              "npub1epwccahqndqhseh6q02seu40cqa2ghk3u9tvu92yh4hd6lmxg33spwzujc",
              "npub1v0kgu3hymtd4fw9zrlem6l74c3cwl8jdqentt4qsxrrzan6paxaqkkf6dr",
            ]

    AVOID_PAID_OUTBOX_RELAY_LIST = AVOID_OUTBOX_RELAY_LIST
    #If a DVM has a paid subscription, overwrite list without the paid one.


    RELAY_TIMEOUT = 5
    RELAY_LONG_TIMEOUT = 30
    EXTERNAL_POST_PROCESS_TYPE = 0 # Leave this on None, except the DVM is external
    LNBITS_INVOICE_KEY = ''  # Will all automatically generated by default, or read from .env
    LNBITS_ADMIN_KEY = ''  # In order to pay invoices, e.g. from the bot to DVMs, or reimburse users.
    LNBITS_URL = 'https://lnbits.com'
    LN_ADDRESS = ''
    SCRIPT = ''
    IDENTIFIER = ''
    USE_OWN_VENV = False  # Make an own venv for each dvm's process function.Disable if you want to install packages into main venv. Only recommended if you dont want to run dvms with different dependency versions
    DB: str
    NEW_USER_BALANCE: int = 0  # Free credits for new users
    SUBSCRIPTION_MANAGEMENT = 'https://noogle.lol/discovery'
    NIP88: NIP88Config = NIP88Config()
    NIP89: NIP89Config = NIP89Config()
    SEND_FEEDBACK_EVENTS = True
    SHOW_RESULT_BEFORE_PAYMENT: bool = False  # if this is true show results even when not paid right after autoprocess
    SCHEDULE_UPDATES_SECONDS = 0
    UPDATE_DATABASE = True  # DVMs that use a db manage their db by default. If a dvm should use the same db as another DVM, deactive it for those who do.
    CUSTOM_PROCESSING_MESSAGE = None
    LOGLEVEL = LogLevel.DEBUG
    KIND = None

    # Make sure you have the cashu library installed and built correctly on your system, before enableing nutzaps for a DVM
    # this is not installed by default
    # pip install cashu. You might run into trouble with building secp256k1
    # More info see here: https://github.com/cashubtc/nutshell

    ENABLE_NUTZAP = False
    NUTZAP_RELAYS = ["wss://relay.primal.net"]
    NUZAP_MINTS = ["https://mint.minibits.cash/Bitcoin", "https://mint.gwoq.com"]
    ENABLE_AUTO_MELT = False
    AUTO_MELT_AMOUNT = 1000


def build_default_config(identifier):
    dvm_config = DVMConfig()
    dvm_config.PRIVATE_KEY = check_and_set_private_key(identifier)
    dvm_config.IDENTIFIER = identifier
    npub = Keys.parse(dvm_config.PRIVATE_KEY).public_key().to_bech32()
    invoice_key, admin_key, wallet_id, user_id, lnaddress = check_and_set_ln_bits_keys(identifier, npub)
    dvm_config.LNBITS_INVOICE_KEY = invoice_key
    dvm_config.LNBITS_ADMIN_KEY = admin_key  # The dvm might pay failed jobs back
    dvm_config.LNBITS_URL = os.getenv("LNBITS_HOST")
    dvm_config.LN_ADDRESS = lnaddress
    return dvm_config

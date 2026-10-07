from datetime import datetime, timedelta
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

host: str = "https://clob.polymarket.com"
key: str = "fill in later" # private key
chain_id: int = 137 # No need to adjust this
POLYMARKET_PROXY_ADDRESS: str = '0xeD8E886aF055D45C876a73AEbD7E659F0AE69670' # This is the address listed below your profile picture when using the Polymarket site.

polymarkets_client = ClobClient(host, key=key, chain_id=chain_id, signature_type=2, funder=POLYMARKET_PROXY_ADDRESS)
polymarkets_client.set_api_creds(polymarkets_client.create_or_derive_api_creds()) 

order_args = OrderArgs(
    price=payload["polymarket_info"]["price"],
    size=payload["bet"]["numbers"]["potential_return"],  
    side=BUY,
    token_id=payload["polymarket_info"]["tok_addr"], 
)

## GTC(Good-Till-Cancelled) Order
try:
    signed_order = polymarkets_client.create_order(order_args)
    resp = polymarkets_client.post_order(signed_order, OrderType.GTC)
    payload["polymarket_info"]["resp"] = resp
    # use orderID for the txhash to record maybe
    if not resp["success"] or resp["errorMsg"] != "":
        err_notification(payload, f"{resp['success']} success and {resp['errorMsg']} err msg")
    else:
        if resp["status"] != "matched":
            err_notification(payload, f"Polymarket bet wasn't matched, it was {resp['status']}")
except Exception as err:
    if "resp" not in payload["polymarket_info"]:
        # hasn't been set yet by line 68
        payload["polymarket_info"]["resp"] = "polymarket placing failed error"
    err_notification(payload, err)

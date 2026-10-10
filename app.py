import os
import asyncio
import traceback

from flask import Flask, request, jsonify
from polymarket import AsyncSecureClient

PRIVATE_KEY: str =  os.environ.get("PRIVATE_KEY")  # private key
POLYMARKET_PROXY_ADDRESS: str = '0xeD8E886aF055D45C876a73AEbD7E659F0AE69670' # This is the address listed below your profile picture when using the Polymarket site.
TARGET_STAKE = 5
POLYMARKET_AMOUNT_DECIMAL_PLACES = 2
POLYMARKET_PRICE_DECIMAL_PLACES = 2
CHECK_RETRIES = 3

async def place(clob_token_addr, price):
    client = await AsyncSecureClient.create(
        private_key=PRIVATE_KEY,
        wallet=POLYMARKET_PROXY_ADDRESS,
    )
    response = await client.place_market_order(
        asset_id=clob_token_addr,
        side="BUY",
        amount=round(TARGET_STAKE / price, POLYMARKET_AMOUNT_DECIMAL_PLACES) * price,  # amount needs to be 2 decimal places
        max_price=price, 
    )

    check_counter = 0
    while check_counter < CHECK_RETRIES:
        await asyncio.sleep(1)
        page = await client.list_positions().first_page()
        position = next(
            (item for item in page.items if item.asset_id == clob_token_addr),
            None,
        )  
        if position is not None:
            return {
                "success": True,
                "order_id": response.order_id,
                "avg_price": position.avg_price,
                "placed_stake": position.entry_cost_usdc
            }
        check_counter += 1
        
    return {
        "success": False
    }

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def request_router():
    if request.method == "POST":
        payload = request.get_json()
        try:
            response = asyncio.run(
                place(
                    payload["clob_token_id"], 
                    round(payload["price"], POLYMARKET_PRICE_DECIMAL_PLACES)  # price has to be 2 dec places
                )
            )
        except Exception as e:
            response = {
                "success": False,
                "stack_trace": traceback.format_exc()
            }
        return jsonify(response)
    else:
        return "CALLED WITH GET REQUEST SOMEHOW"

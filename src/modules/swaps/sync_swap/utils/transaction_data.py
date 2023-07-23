from web3.middleware import geth_poa_middleware
from web3.contract import Contract
from eth_typing import Address
from eth_abi import encode
from web3 import Web3

from src.modules.swaps.tokens import tokens
from src.utils.data import load_contract
from config import SLIPPAGE


async def get_amount_out(contract_address: str, amount: int, from_token_address: Address,
                         to_token_address: Address, web3: Web3) -> int:
    contract = await load_contract(contract_address, web3, 'linea_swap')
    amount_out = contract.functions.getAmountsOut(
        amount,
        [from_token_address, to_token_address]
    ).call()
    return amount_out[1]


async def create_swap_tx(from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                         to_token_address: str, account_address: Address, amount: int, web3: Web3) -> dict:
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    swap_data = encode(
        ["address", "address", "uint8"],
        [Web3.to_checksum_address(from_token_address), account_address, 1 if from_token.upper() == 'BUSD' else 2]
    )
    native_eth_address = "0x0000000000000000000000000000000000000000"
    steps = [{
        "pool": '0x7f72E0D8e9AbF9133A92322b8B50BD8e0F9dcFCB',
        "data": swap_data,
        "callback": native_eth_address,
        "callbackData": '0x'
    }]
    paths = [{
        "steps": steps,
        "tokenIn": Web3.to_checksum_address(
            from_token_address) if from_token.lower() != 'eth' else Web3.to_checksum_address(
            native_eth_address),
        "amountIn": amount,
    }]

    tx = contract.functions.swap(
        paths,
        int(amount_out * (1 - SLIPPAGE)),
        int(web3.eth.get_block('latest').timestamp) + 1200
    ).build_transaction({
        'from': account_address,
        'value': amount if from_token.lower() == 'eth' else 0,
        'nonce': web3.eth.get_transaction_count(account_address),
        'maxFeePerGas': 0,
        'maxPriorityFeePerGas': 0,
        'gas': 0
    })
    return tx


async def setup_for_liquidity(token: str) -> tuple[str, str]:
    if token.lower() == 'busd':
        from_token_address = tokens[token.upper()]
        to_token_address = tokens['ETH']
    else:
        from_token_address = tokens[token.upper()]
        to_token_address = tokens['BUSD']

    return to_token_address, from_token_address

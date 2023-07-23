from time import time

from web3.contract import Contract
from eth_typing import Address
from config import SLIPPAGE
from web3 import Web3


async def get_amount_out(contract: Contract, amount: int, from_token_address: Address,
                         to_token_address: Address) -> int:
    amount_out = contract.functions.getAmountsOut(
        amount,
        [from_token_address, to_token_address]
    ).call()
    return amount_out[1]


async def create_swap_tx(from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                         to_token_address: str, account_address: Address, amount: int, web3: Web3) -> dict:
    if from_token.lower() == 'eth':
        tx = contract.functions.swapExactETHForTokens(
            int(amount_out * (1 - SLIPPAGE)), [from_token_address, to_token_address], account_address,
            int(time() + 1200)). \
            build_transaction({
            'value': amount if from_token.lower() == 'eth' else 0,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })
    else:
        tx = contract.functions.swapExactTokensForETH(
            amount,
            int(amount_out * (1 - SLIPPAGE)),
            [from_token_address, to_token_address],
            account_address,
            int(time() + 1200)
        ).build_transaction({
            'value': amount if from_token.lower() == 'eth' else 0,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })

    return tx


async def create_liquidity_tx(from_token: str, contract: Contract, amount_out: int,
                              to_token_address: str, account_address: Address, amount: int, web3: Web3) -> dict:
    tx = contract.functions.addLiquidityETH(
        to_token_address,
        amount_out,
        int(amount_out * (1 - SLIPPAGE)),
        int(amount * (1 - SLIPPAGE)),
        account_address,
        int(time() + 1200)
    ).build_transaction({
        'value': amount if from_token.lower() == 'eth' else 0,
        'nonce': web3.eth.get_transaction_count(account_address),
        'from': account_address,
        'maxFeePerGas': 0,
        'maxPriorityFeePerGas': 0,
        'gas': 0
    })

    return tx


async def create_liquidity_remove_tx(web3: Web3, contract: Contract, from_token_pair_address: str, amount: int,
                                     account_address: Address) -> dict:
    tx = contract.functions.removeLiquidityETH(
        from_token_pair_address,
        amount,
        0,
        0,
        account_address,
        int(time() + 1200)
    ).build_transaction({
        'value': 0,
        'nonce': web3.eth.get_transaction_count(account_address),
        'from': account_address,
        'maxFeePerGas': 0,
        'maxPriorityFeePerGas': 0,
        'gas': 0
    })

    return tx

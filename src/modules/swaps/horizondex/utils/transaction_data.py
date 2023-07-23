from time import time

from web3.contract import Contract
from eth_typing import Address
from hexbytes import HexBytes
from config import SLIPPAGE
from eth_abi import encode
from web3 import Web3

from src.utils.data import load_contract


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
    if from_token.lower() == 'eth':
        tx_data = [Web3.to_checksum_address(from_token_address),
                   Web3.to_checksum_address(to_token_address),
                   300,
                   account_address,
                   int(time() + 1200),
                   amount,
                   int(amount_out * (1 - SLIPPAGE)),
                   0]
        tx = contract.functions.swapExactInputSingle(tx_data).build_transaction({
            'value': amount if from_token.lower() == 'eth' else 0,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })
    else:
        swap_data = encode(['address', 'address', 'uint24', 'address', 'uint256', 'uint256', 'uint256', 'uint160'],
                           [Web3.to_checksum_address(from_token_address),
                            Web3.to_checksum_address(to_token_address),
                            300,
                            Web3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                            int(time() + 1200),
                            amount,
                            int(amount_out * (1 - SLIPPAGE)),
                            0]).hex()

        unwrap_data = encode(['uint256', 'address'],
                             [int(amount_out * (1 - SLIPPAGE)), account_address]).hex()
        tx = contract.functions.multicall(
            [HexBytes('0xa8c9ed67' + swap_data), HexBytes('0xbac37ef7' + unwrap_data)]
        ).build_transaction({
            'value': amount if from_token.lower() == 'eth' else 0,
            'nonce': web3.eth.get_transaction_count(account_address),
            'from': account_address,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })

    return tx

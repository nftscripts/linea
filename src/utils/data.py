from asyncio import sleep
import json

from random import (
    randint,
    uniform,
)

from web3.contract import Contract
from loguru import logger
from web3 import Web3

from eth_typing import (
    Address,
    HexStr,
)


async def load_abi(name: str) -> str:
    with open(f'./assets/abi/{name}.json') as f:
        abi: str = json.load(f)
    return abi


async def load_contract(address: str, web3: Web3, abi_name: str) -> Contract | None:
    if address is None:
        return

    address = web3.to_checksum_address(address)
    return web3.eth.contract(address=address, abi=await load_abi(abi_name))


async def get_wallet_balance(token: str, w3: Web3, address: Address, stable_address: str,
                             from_chain: str) -> float:
    if token.lower() != 'eth':
        stable_contract = w3.eth.contract(address=Web3.to_checksum_address(stable_address), abi=await load_abi('erc20'))
        balance = stable_contract.functions.balanceOf(address).call()
    else:
        balance = w3.eth.get_balance(address)

    return balance


async def get_contract(web3: Web3, from_token_address: str) -> Contract:
    return web3.eth.contract(address=web3.to_checksum_address(from_token_address),
                             abi=await load_abi('erc20'))


async def approve_token(amount: float, private_key: str, chain: str, from_token_address: str, spender: str,
                        address_wallet: Address, web3: Web3) -> HexStr:
    try:
        spender = web3.to_checksum_address(spender)
        contract = await get_contract(web3, from_token_address)
        allowance_amount = await check_allowance(web3, from_token_address, address_wallet, spender)

        if amount > allowance_amount:
            logger.debug('Approving token...')
            tx = contract.functions.approve(
                spender,
                100000000000000000000000000000000000000000000000000000000000000000000000000000
            ).build_transaction(
                {
                    'chainId': web3.eth.chain_id,
                    'from': address_wallet,
                    'nonce': web3.eth.get_transaction_count(address_wallet),
                    'gasPrice': 0,
                    'gas': 0,
                    'value': 0
                }
            )
            if chain == 'bsc':
                tx['gasPrice'] = randint(1000000000, 1050000000)
            else:
                gas_price = await add_gas_price(web3)
                tx['gasPrice'] = gas_price

            gas_limit = await add_gas_limit(web3, tx)
            tx['gas'] = gas_limit

            signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
            raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(raw_tx_hash)
            while tx_receipt is None:
                await sleep(1)
                tx_receipt = web3.eth.get_transaction_receipt(raw_tx_hash)
            tx_hash = web3.to_hex(raw_tx_hash)
            logger.info(f'Token approved | Tx hash: {tx_hash}')
            await sleep(5)
            return tx_hash

    except Exception as ex:
        logger.error(f'Something went wrong | {ex}')


async def check_allowance(web3: Web3, from_token_address: str, address_wallet: Address, spender: str) -> float:
    try:
        contract = web3.eth.contract(address=web3.to_checksum_address(from_token_address),
                                     abi=await load_abi('erc20'))
        amount_approved = contract.functions.allowance(address_wallet, spender).call()
        return amount_approved

    except Exception as ex:
        logger.error(f'Something went wrong | {ex}')


async def add_gas_price(web3: Web3) -> int:
    try:
        gas_price = web3.eth.gas_price
        gas_price = int(gas_price * uniform(1.01, 1.02))
        return gas_price
    except Exception as ex:
        logger.error(f'Something went wrong | {ex}')


async def add_gas_limit(web3: Web3, tx: dict) -> int:
    tx['value'] = 0
    gas_limit = web3.eth.estimate_gas(tx)
    return gas_limit

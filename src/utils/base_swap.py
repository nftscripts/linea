from asyncio import sleep
from typing import Any
import random

from web3.contract import Contract
from eth_typing import Address
from loguru import logger
from web3 import Web3

from src.modules.swaps.tokens import tokens
from src.utils.chains import LINEA

from src.utils.data import (
    load_contract,
    get_wallet_balance,
    approve_token,
)


class BaseSwap:
    def __init__(self,
                 private_key: str,
                 from_token: str,
                 to_token: str,
                 amount_from: float,
                 amount_to: float,
                 swap_all_balance: bool
                 ) -> None:
        self.private_key = private_key
        self.from_token = from_token
        self.to_token = to_token
        self.amount = round(random.uniform(amount_from, amount_to), 7)
        self.swap_all_balance = swap_all_balance
        self.web3 = Web3(Web3.HTTPProvider(LINEA.rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address

    async def swap(self) -> None:
        contract_address = await self.get_contract_address()
        abi_name = await self.get_abi_name()
        from_token_address, to_token_address = tokens[self.from_token.upper()], tokens[self.to_token.upper()]
        contract = await load_contract(contract_address, self.web3, abi_name)
        decimals = 18
        balance = await get_wallet_balance(self.from_token, self.web3, self.account_address, from_token_address,
                                           'linea')
        if balance == 0:
            logger.error(f"Your balance is 0 | {self.account_address}")
            return
        if self.swap_all_balance is True and self.from_token.lower() == 'eth':
            logger.error("You can't use swap_all_balance = True with ETH token. Using amount_from, amount_to")
        if self.swap_all_balance is True and self.from_token.lower() != 'eth':
            amount = balance
        else:
            amount = int(self.amount * 10 ** decimals)

        if amount > balance:
            logger.error(f'Not enough balance for wallet {self.account_address}')
            return

        amount_out = await self.get_amount_out(contract, amount, Web3.to_checksum_address(from_token_address),
                                               Web3.to_checksum_address(to_token_address))

        if self.from_token.lower() != 'eth':
            await approve_token(amount,
                                self.private_key,
                                'linea',
                                from_token_address,
                                contract_address,
                                self.account_address,
                                self.web3)

        tx = await self.create_swap_tx(self.from_token, contract, amount_out, from_token_address, to_token_address,
                                       self.account_address, amount, self.web3)

        retries = 0
        while retries < 3:
            try:
                tx.update({'maxFeePerGas': self.web3.eth.gas_price})
                tx.update({'maxPriorityFeePerGas': self.web3.eth.max_priority_fee})

                gasLimit = self.web3.eth.estimate_gas(tx)
                tx.update({'gas': gasLimit})

                signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
                raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_hash = self.web3.to_hex(raw_tx_hash)
                logger.success(
                    f'Successfully swapped {"all" if self.swap_all_balance is True and self.from_token.lower() != "eth" else self.amount} {self.from_token} tokens => {self.to_token} | TX: https://lineascan.build/tx/{tx_hash}'
                )
                break
            except Exception as ex:
                if 'exceeds allowance' in str(ex):
                    logger.error('Not enough money for transaction')
                    return
                logger.error(f'Something went wrong {ex}')
                await sleep(random.randint(15, 20))
                logger.debug('Trying one more time')
                retries += 1
                continue

    async def get_abi_name(self) -> str:
        raise NotImplementedError("Subclasses must implement get_abi_name()")

    async def get_contract_address(self) -> str:
        raise NotImplementedError("Subclasses must implement get_contract_address()")

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address) -> int:
        raise NotImplementedError("Subclasses must implement get_amount_out()")

    async def create_swap_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                             to_token_address: str, account_address: Address, amount: int, web3: Web3) -> Any:
        raise NotImplementedError("Subclasses must implement create_tx()")

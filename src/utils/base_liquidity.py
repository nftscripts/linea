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


class BaseLiquidity:
    def __init__(self,
                 private_key: str,
                 token: str,
                 token2: str,
                 amount_from: float,
                 amount_to: float,
                 ) -> None:
        self.private_key = private_key
        self.token = token
        self.token2 = token2
        self.amount = round(random.uniform(amount_from, amount_to), 7)
        self.web3 = Web3(Web3.HTTPProvider(LINEA.rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address

    async def add_liquidity(self) -> None:
        abi_name = await self.get_abi_name()
        contract_address = await self.get_contract_address()
        from_token_address, to_token_address = tokens[self.token.upper()], tokens[self.token2.upper()]
        contract = await load_contract(contract_address, self.web3, abi_name)
        decimals = 18
        amount = int(self.amount * 10 ** decimals)
        balance = await get_wallet_balance(self.token, self.web3, self.account_address, from_token_address,
                                           'linea')

        if amount > balance:
            logger.error(f'Not enough balance for wallet {self.account_address}')
            return

        await approve_token(amount,
                            self.private_key,
                            'linea',
                            to_token_address,
                            contract_address,
                            self.account_address,
                            self.web3)

        while True:
            stable_balance = await get_wallet_balance(self.token2, self.web3, self.account_address, to_token_address,
                                                      'linea')
            amount_out = await self.get_amount_out(contract, amount, Web3.to_checksum_address(from_token_address),
                                                   Web3.to_checksum_address(to_token_address))
            if amount_out > stable_balance:
                logger.error(f'Not enough {self.token2.upper()} balance for wallet {self.account_address}')
                logger.info(f'Swapping {self.amount} ETH => {self.token2.upper()}')
                swap = await self.get_swap_instance(self.private_key, self.token, self.token2, self.amount, self.amount)
                await swap.swap()
                sleep_time = random.randint(45, 75)
                logger.info(f'Sleeping {sleep_time} seconds...')
                await sleep(sleep_time)
                continue
            break

        tx = await self.create_liquidity_tx(self.token, contract, amount_out, from_token_address, to_token_address,
                                            self.account_address, amount, self.web3)

        tx.update({'maxFeePerGas': int(self.web3.eth.gas_price * 1.1)})
        tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})

        gasLimit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gasLimit})

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        logger.success(
            f'Successfully added liquidity with {self.amount} ETH, {amount_out / 10 ** 18} {self.token2.upper()} | TX: https://lineascan.build/tx/{tx_hash}'
        )

    async def get_abi_name(self) -> None:
        raise NotImplementedError("Subclasses must implement get_abi_name()")

    async def get_contract_address(self) -> None:
        raise NotImplementedError("Subclasses must implement get_contract_address()")

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address) -> int:
        raise NotImplementedError("Subclasses must implement get_amount_out()")

    async def create_liquidity_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                                  to_token_address: str, account_address: Address, amount: int, web3: Web3) -> Any:
        raise NotImplementedError("Subclasses must implement create_liquidity_tx()")

    async def get_swap_instance(self, private_key: str, token: str, token2: str, amount_from: float,
                                amount_to: float) -> Any:
        raise NotImplementedError("Subclasses must implement get_swap_instance()")

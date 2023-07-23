from typing import Any

from web3.contract import Contract
from eth_typing import Address
from loguru import logger
from web3 import Web3

from src.utils.chains import LINEA

from src.modules.swaps.tokens import (
    liquidity_tokens,
    tokens,
)

from src.utils.data import (
    load_contract,
    get_wallet_balance,
    approve_token,
)


class BaseLiquidityRemove:
    def __init__(self,
                 private_key: str,
                 from_token_pair: str,
                 remove_all: bool,
                 removing_percentage: float
                 ) -> None:
        self.private_key = private_key
        self.from_token_pair = from_token_pair
        self.remove_all = remove_all
        self.removing_percentage = removing_percentage
        self.web3 = Web3(Web3.HTTPProvider(LINEA.rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address

    async def remove_liquidity(self) -> None:
        abi_name = await self.get_abi_name()
        contract_address = await self.get_contract_address()
        pool_name = await self.get_pool_name()
        contract = await load_contract(contract_address, self.web3, abi_name)
        liquidity_token_address = liquidity_tokens[pool_name]['ETH'][self.from_token_pair.upper()]
        balance = await get_wallet_balance('XXX', self.web3, self.account_address, liquidity_token_address,
                                           'linea')

        if balance == 0:
            logger.error("Looks like you don't have any tokens to withdraw")
            return

        if self.remove_all is True:
            amount = balance
        else:
            amount = int(balance * self.removing_percentage)

        await approve_token(amount,
                            self.private_key,
                            'linea',
                            liquidity_token_address,
                            contract_address,
                            self.account_address,
                            self.web3)

        tx = await self.create_liquidity_remove_tx(self.web3, contract, tokens[self.from_token_pair.upper()],
                                                   amount, self.account_address)

        tx.update({'maxFeePerGas': int(self.web3.eth.gas_price * 1.1)})
        tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})

        gasLimit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gasLimit})

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        logger.success(
            f'Removed {"all" if self.remove_all else f"{self.removing_percentage * 100}%"} tokens from {pool_name} pool | TX: https://lineascan.build/tx/{tx_hash}'
        )

    async def get_abi_name(self) -> str:
        raise NotImplementedError("Subclasses must implement get_abi_name()")

    async def get_contract_address(self) -> str:
        raise NotImplementedError("Subclasses must implement get_contract_address()")

    async def create_liquidity_remove_tx(self, web3: Web3, contract: Contract, from_token_pair_address: str,
                                         amount: int, account_address: Address) -> Any:
        raise NotImplementedError("Subclasses must implement create_liquidity_remove_tx()")

    async def get_pool_name(self) -> str:
        raise NotImplementedError("Subclasses must implement get_pool_name()")

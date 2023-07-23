import random

from web3.contract import Contract
from eth_typing import Address
from eth_abi import encode
from loguru import logger
from web3 import Web3

from src.utils.base_swap import BaseSwap
from src.utils.chains import LINEA

from src.modules.swaps.sync_swap.utils.transaction_data import (
    setup_for_liquidity,
    get_amount_out,
    create_swap_tx,
)

from src.utils.data import (
    get_wallet_balance,
    approve_token,
    load_abi,
)


class SyncSwap(BaseSwap):
    async def get_contract_address(self) -> str:
        return '0x80e38291e06339d10AAB483C65695D004dBD5C69'

    async def get_abi_name(self) -> str:
        return 'syncswap'

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address):
        return await get_amount_out('0x3228d205a96409a07a44d39916b6ea7b765d61f4',
                                    amount, from_token_address, to_token_address, self.web3)

    async def create_swap_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                             to_token_address: str, account_address: Address, amount: int, web3: Web3):
        return await create_swap_tx(from_token, contract, amount_out, from_token_address, to_token_address,
                                    account_address, amount, web3)


class SyncSwapLiquidity:
    def __init__(self,
                 private_key: str,
                 token: str,
                 amount_from: float,
                 amount_to: float
                 ) -> None:
        self.private_key = private_key
        self.token = token
        self.amount = random.uniform(amount_from, amount_to)
        self.router_address = '0x80e38291e06339d10AAB483C65695D004dBD5C69'
        self.web3 = Web3(Web3.HTTPProvider(LINEA.rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address

    async def add_liquidity(self) -> None:
        to_token_address, from_token_address = await setup_for_liquidity(self.token)
        value = int(self.amount * 10 ** 18)

        balance = await get_wallet_balance(self.token, self.web3, self.account_address, from_token_address,
                                           'linea')

        if value > balance:
            logger.error(f'Not enough money for wallet {self.account_address}')
            return

        native_eth_address = "0x0000000000000000000000000000000000000000"

        min_liquidity = 0
        callback = native_eth_address

        router = self.web3.eth.contract(address=Web3.to_checksum_address(self.router_address),
                                        abi=await load_abi('syncswap'))

        if self.token.lower() != 'eth':
            await approve_token(amount=value,
                                private_key=self.private_key,
                                chain='linea',
                                from_token_address=from_token_address,
                                spender=self.router_address,
                                address_wallet=self.account_address,
                                web3=self.web3)

        data = encode(
            ["address"],
            [self.account_address]
        )

        tx = router.functions.addLiquidity2(
            Web3.to_checksum_address('0x7f72E0D8e9AbF9133A92322b8B50BD8e0F9dcFCB'),
            [(Web3.to_checksum_address(to_token_address), 0),
             (Web3.to_checksum_address(callback), value)] if self.token.lower() == 'eth' else [
                (Web3.to_checksum_address(from_token_address), value)],
            data,
            min_liquidity,
            callback,
            '0x'
        ).build_transaction({
            'from': self.account_address,
            'value': value if self.token.lower() == 'eth' else 0,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })
        tx.update({'maxFeePerGas': int(self.web3.eth.gas_price * 1.1)})
        tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})

        gasLimit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gasLimit})

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        logger.success(
            f'Added {self.amount} {self.token} tokens to liquidity pool | TX: https://lineascan.build/tx/{tx_hash}')


class SyncSwapLiquidityRemove:
    def __init__(self,
                 private_key: str,
                 remove_all: bool,
                 removing_percentage: float) -> None:
        self.private_key = private_key
        self.router_address = '0x80e38291e06339d10AAB483C65695D004dBD5C69'
        self.remove_all = remove_all
        self.removing_percentage = removing_percentage
        self.web3 = Web3(Web3.HTTPProvider(LINEA.rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address

    async def remove_liquidity(self) -> None:
        value = await get_wallet_balance('XXX', self.web3, self.account_address,
                                         '0x7f72e0d8e9abf9133a92322b8b50bd8e0f9dcfcb', 'linea')
        if self.remove_all is False:
            value = int(value * self.removing_percentage)

        if value == 0:
            logger.error("Looks like you don't have any tokens to withdraw")
            return

        router = self.web3.eth.contract(address=Web3.to_checksum_address(self.router_address),
                                        abi=await load_abi('syncswap'))

        await approve_token(amount=value,
                            private_key=self.private_key,
                            chain='linea',
                            from_token_address='0x7f72e0d8e9abf9133a92322b8b50bd8e0f9dcfcb',
                            spender=self.router_address,
                            address_wallet=self.account_address,
                            web3=self.web3)

        data = encode(
            ["address", "uint8"],
            [self.account_address, 1]
        )

        tx = router.functions.burnLiquidity(
            Web3.to_checksum_address("0x7f72E0D8e9AbF9133A92322b8B50BD8e0F9dcFCB"),
            value,
            data,
            [0, 0],
            "0x0000000000000000000000000000000000000000",
            '0x'

        ).build_transaction({
            'from': self.account_address,
            'nonce': self.web3.eth.get_transaction_count(self.account_address),
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'gas': 0
        })

        tx.update({'maxFeePerGas': self.web3.eth.gas_price})
        tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})

        gasLimit = self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gasLimit})

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        logger.success(
            f'Removed {"all" if self.remove_all else f"{self.removing_percentage * 100}%"} tokens from liquidity pool | TX: https://lineascan.build/tx/{tx_hash}'
        )

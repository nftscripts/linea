import random

from loguru import logger
from web3 import Web3

from src.utils.chains import ETH, LINEA

from src.utils.data import (
    load_contract,
    get_wallet_balance,
)


class MainBridge:
    def __init__(self,
                 private_key: str,
                 amount_from: float,
                 amount_to: float) -> None:
        self.private_key = private_key
        self.amount = random.uniform(amount_from, amount_to)
        self.web3 = Web3(Web3.HTTPProvider(ETH.rpc))
        self.linea_web3 = Web3(Web3.HTTPProvider(LINEA.rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address
        self.bridge_address = '0xd19d4B5d358258f05D7B411E21A1460D11B0876F'

    async def deposit(self) -> None:
        contract = await load_contract(self.bridge_address, self.web3, 'main_bridge')
        fee = int(self.linea_web3.eth.gas_price * 10e4)
        amount = int(self.amount * 10 ** 18 + fee)
        balance = await get_wallet_balance('ETH', self.web3, self.account_address, None, 'ETH')

        if amount > balance:
            logger.error(f'Not enough balance for wallet {self.account_address}')
            return

        tx = contract.functions.sendMessage(
            self.account_address,
            fee,
            b""
        ).build_transaction({
            'from': self.account_address,
            'maxFeePerGas': int(self.web3.eth.gas_price + self.web3.eth.gas_price * 0.1),
            'maxPriorityFeePerGas': self.web3.eth.gas_price,
            'value': amount,
            'nonce': self.web3.eth.get_transaction_count(self.account_address)
        })

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        raw_tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = self.web3.to_hex(raw_tx_hash)
        logger.success(
            f'Successfully bridged {self.amount} ETH to Linea network | TX: {ETH.scan}/{tx_hash}')

    async def withdraw(self) -> None:
        pass

from fractions import Fraction
import random

from loguru import logger
from web3 import Web3

from src.modules.bridges.orbiter_bridge.utils.config import chain_without_eipstandart
from src.utils.data import get_wallet_balance

from src.modules.bridges.orbiter_bridge.utils.transaction_data import (
    check_eligibility,
    get_router,
    get_chain_id,
    get_scan_url,
)


class OrbiterBridge:
    def __init__(self,
                 private_key: str,
                 amount_from: float,
                 amount_to: float,
                 from_chain: str,
                 to_chain: str,
                 rpc: str,
                 code: int) -> None:
        self.private_key = private_key
        self.amount = random.uniform(amount_from, amount_to)
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.account = self.web3.eth.account.from_key(private_key)
        self.account_address = self.account.address
        self.code = code

    async def bridge(self) -> None:
        contract_router = await get_router('ETH')
        amount = int(self.amount * 10 ** 18)
        balance = await get_wallet_balance('ETH', self.web3, self.account_address, None, self.from_chain)
        eligibility, min_limit, max_limit = await check_eligibility(self.from_chain, self.to_chain, 'ETH', amount)

        if not eligibility:
            logger.error(f'Limits error | Min: {min_limit}, Max: {max_limit}')
            return

        if amount > balance:
            logger.error(f'Not enough balance for wallet {self.account_address}')
            return

        amount = int(str(Fraction(amount))[:-4] + str(self.code))

        tx = {
            "chainId": await get_chain_id(self.from_chain),
            'to': self.web3.to_checksum_address(contract_router),
            'value': amount,
            'nonce': self.web3.eth.get_transaction_count(self.account_address)
        }
        if not (self.from_chain.lower() in chain_without_eipstandart):
            tx.update({'maxFeePerGas': self.web3.eth.gas_price})
            tx.update({'maxPriorityFeePerGas': self.web3.eth.gas_price})
        else:
            tx.update({'gasPrice': self.web3.eth.gas_price})
        if self.from_chain.lower() == 'linea':
            tx.update({'chainId': 59144})
        try:
            gasLimit = self.web3.eth.estimate_gas(tx)
            tx.update({'gas': gasLimit})
        except Exception as ex:
            logger.error(f'Impossible to calculate gas limit... | {ex}')

        scan_url = await get_scan_url(self.from_chain)
        try:
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
            self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash = self.web3.to_hex(self.web3.keccak(signed_tx.rawTransaction))
            logger.success(f'Successfully bridged {self.amount} ETH from {self.from_chain.upper()} => {self.to_chain.upper()} | TX: {scan_url}/{tx_hash}')
        except Exception as ex:
            logger.error(f'Something went wrong {ex}')

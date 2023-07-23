from typing import Any

from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.utils.base_swap import BaseSwap

from src.modules.swaps.horizondex.utils.transaction_data import (
    get_amount_out,
    create_swap_tx,
)


class HorizonDexSwap(BaseSwap):
    async def get_contract_address(self) -> str:
        return '0x272e156df8da513c69cb41cc7a99185d53f926bb'

    async def get_abi_name(self) -> str:
        return 'horizon_dex'

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address) -> int:
        return await get_amount_out('0x3228d205a96409a07a44d39916b6ea7b765d61f4',
                                    amount, from_token_address, to_token_address, self.web3)

    async def create_swap_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                             to_token_address: str, account_address: Address, amount: int, web3: Web3) -> Any:
        return await create_swap_tx(from_token, contract, amount_out, from_token_address, to_token_address,
                                    account_address, amount, web3)

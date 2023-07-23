from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.utils.base_liquidity_remove import BaseLiquidityRemove
from src.utils.base_liquidity import BaseLiquidity
from src.utils.base_swap import BaseSwap

from src.modules.swaps.linea_swap.utils.transaction_data import (
    create_liquidity_remove_tx,
    create_liquidity_tx,
    get_amount_out,
    create_swap_tx,
)


class LineaSwap(BaseSwap):
    async def get_contract_address(self) -> str:
        return '0x3228d205a96409a07a44d39916b6ea7b765d61f4'

    async def get_abi_name(self) -> str:
        return 'linea_swap'

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address):
        return await get_amount_out(contract, amount, from_token_address, to_token_address)

    async def create_swap_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                             to_token_address: str, account_address: Address, amount: int, web3: Web3):
        return await create_swap_tx(from_token, contract, amount_out, from_token_address, to_token_address,
                                    account_address, amount, web3)


class LineaLiquidity(BaseLiquidity):
    async def get_contract_address(self) -> str:
        return '0x3228d205a96409a07a44d39916b6ea7b765d61f4'

    async def get_abi_name(self) -> str:
        return 'linea_swap'

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address):
        return await get_amount_out(contract, amount, from_token_address, to_token_address)

    async def create_liquidity_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                                  to_token_address: str, account_address: Address, amount: int, web3: Web3):
        return await create_liquidity_tx(from_token, contract, amount_out, to_token_address,
                                         account_address, amount, web3)

    async def get_swap_instance(self, private_key: str, token: str, token2: str, amount_from: float,
                                amount_to: float) -> LineaSwap:
        return LineaSwap(private_key, token, token2, amount_from, amount_to, False)


class LineaLiquidityRemove(BaseLiquidityRemove):
    async def get_contract_address(self) -> str:
        return '0x3228d205a96409a07a44d39916b6ea7b765d61f4'

    async def get_abi_name(self) -> str:
        return 'linea_swap'

    async def create_liquidity_remove_tx(self, web3: Web3, contract: Contract, from_token_pair_address: str,
                                         amount: int,
                                         account_address: Address) -> None:
        return await create_liquidity_remove_tx(web3, contract, from_token_pair_address, amount, account_address)

    async def get_pool_name(self) -> None:
        return 'LineaSwap'

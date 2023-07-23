from typing import Any

from web3.contract import Contract
from eth_typing import Address
from web3 import Web3

from src.utils.base_liquidity_remove import BaseLiquidityRemove
from src.utils.base_liquidity import BaseLiquidity
from src.utils.base_swap import BaseSwap

from src.modules.swaps.echodex.utils.transaction_data import (
    create_liquidity_remove_tx,
    create_liquidity_tx,
    get_amount_out,
    create_swap_tx,
)


class EchoDexSwap(BaseSwap):
    async def get_contract_address(self) -> str:
        return '0xc66149996d0263C0B42D3bC05e50Db88658106cE'

    async def get_abi_name(self) -> str:
        return 'echo_dex'

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address) -> int:
        return await get_amount_out(contract, amount, from_token_address, to_token_address)

    async def create_swap_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                             to_token_address: str, account_address: Address, amount: int, web3: Web3) -> Any:
        return await create_swap_tx(from_token, contract, amount_out, from_token_address, to_token_address,
                                    account_address, amount, web3)


class EchoDexLiquidity(BaseLiquidity):
    async def get_contract_address(self) -> str:
        return '0xc66149996d0263C0B42D3bC05e50Db88658106cE'

    async def get_abi_name(self) -> str:
        return 'echo_dex'

    async def get_amount_out(self, contract: Contract, amount: int, from_token_address: Address,
                             to_token_address: Address) -> int:
        return await get_amount_out(contract, amount, from_token_address, to_token_address)

    async def create_liquidity_tx(self, from_token: str, contract: Contract, amount_out: int, from_token_address: str,
                                  to_token_address: str, account_address: Address, amount: int, web3: Web3) -> Any:
        return await create_liquidity_tx(from_token, contract, amount_out, to_token_address,
                                         account_address, amount, web3)

    async def get_swap_instance(self, private_key: str, token: str, token2: str, amount_from: float,
                                amount_to: float) -> EchoDexSwap:
        return EchoDexSwap(private_key, token, token2, amount_from, amount_to, False)


class EchoDexLiquidityRemove(BaseLiquidityRemove):
    async def get_contract_address(self) -> str:
        return '0xc66149996d0263C0B42D3bC05e50Db88658106cE'

    async def get_abi_name(self) -> str:
        return 'echo_dex'

    async def create_liquidity_remove_tx(self, web3: Web3, contract: Contract, from_token_pair_address: str,
                                         amount: int, account_address: Address) -> None:
        return await create_liquidity_remove_tx(web3, contract, from_token_pair_address, amount, account_address)

    async def get_pool_name(self) -> None:
        return 'EchoDex'

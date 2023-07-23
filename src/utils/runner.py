from loguru import logger
import tqdm

from src.modules.bridges.orbiter_bridge.orbiter_bridge import OrbiterBridge
from src.modules.bridges.main_bridge.main_bridge import MainBridge
from src.modules.swaps.horizondex.horizondex import HorizonDexSwap

from src.utils.chains import chain_mapping
from config import *

from src.modules.swaps.sync_swap.sync_swap import (
    SyncSwap,
    SyncSwapLiquidity,
    SyncSwapLiquidityRemove
)

from src.modules.swaps.echodex.echodex import (
    EchoDexLiquidityRemove,
    EchoDexLiquidity,
    EchoDexSwap,
)

from src.modules.swaps.linea_swap.linea_swap import (
    LineaSwap,
    LineaLiquidity,
    LineaLiquidityRemove,
)


async def process_main_bridge(private_key: str, pbar: tqdm) -> None:
    amount_from = MainBridgeConfig.amount_from
    amount_to = MainBridgeConfig.amount_to
    action = MainBridgeConfig.action

    bridge = MainBridge(
        private_key=private_key,
        amount_from=amount_from,
        amount_to=amount_to,
    )
    logger.info('Bridging on Main bridge...')

    if action == 'deposit':
        await bridge.deposit()
    elif action == 'withdraw':
        await bridge.withdraw()
    else:
        logger.error(f'Unknown action {action}. Use only: deposit/withdraw')
        return

    pbar.update()


async def process_orbiter_bridge(private_key: str, pbar: tqdm) -> None:
    supported_chains = ['ARB']
    chain = OrbiterBridgeConfig.chain
    token = OrbiterBridgeConfig.token
    amount_from = OrbiterBridgeConfig.amount_from
    amount_to = OrbiterBridgeConfig.amount_to
    action = OrbiterBridgeConfig.action
    if token.upper() != 'ETH':
        logger.error(f'Not supported token {token}. Use only ETH.')
        return

    if chain.upper() not in supported_chains:
        logger.error(f'Not supported chain {chain}. Use only: ARB')
        return

    if action.lower() == 'deposit':
        from_chain = chain
        to_chain = 'linea'
    elif action.lower() == 'withdraw':
        from_chain = 'linea'
        to_chain = chain
    else:
        logger.error(f'Unknown action {action}. Use only: deposit/withdraw')
        return

    bridge = OrbiterBridge(
        private_key=private_key,
        amount_from=amount_from,
        amount_to=amount_to,
        from_chain=from_chain,
        to_chain=to_chain,
        rpc=chain_mapping[from_chain.lower()].rpc,
        code=chain_mapping[to_chain.lower()].code
    )
    logger.info('Bridging on Orbiter...')

    await bridge.bridge()
    pbar.update()


async def process_linea_swap(private_key: str, pbar: tqdm) -> None:
    from_token = LineaSwapConfig.from_token
    to_token = LineaSwapConfig.to_token
    amount_from = LineaSwapConfig.amount_from
    amount_to = LineaSwapConfig.amount_to
    swap_all_balance = LineaSwapConfig.swap_all_balance

    linea_swap = LineaSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount_from=amount_from,
        amount_to=amount_to,
        swap_all_balance=swap_all_balance
    )
    logger.info('Swapping on LineaSwap...')
    await linea_swap.swap()
    pbar.update()


async def process_linea_liquidity(private_key: str, pbar: tqdm) -> None:
    token = LineaLiqConfig.token
    token2 = LineaLiqConfig.token2
    amount_from = LineaLiqConfig.amount_from
    amount_to = LineaLiqConfig.amount_to

    linea_liq = LineaLiquidity(
        private_key=private_key,
        token=token,
        token2=token2,
        amount_from=amount_from,
        amount_to=amount_to,
    )
    logger.info('Adding liquidity on LineaSwap...')
    await linea_liq.add_liquidity()
    pbar.update()


async def process_linea_liquidity_remove(private_key: str, pbar: tqdm) -> None:
    from_token_pair = LineaLiqRemoveConfig.from_token_pair
    remove_all = LineaLiqRemoveConfig.remove_all
    removing_percentage = LineaLiqRemoveConfig.removing_percentage

    linea_liq_remove = LineaLiquidityRemove(
        private_key=private_key,
        from_token_pair=from_token_pair,
        remove_all=remove_all,
        removing_percentage=removing_percentage
    )
    logger.info('Removing liquidity from LineaSwap...')
    await linea_liq_remove.remove_liquidity()
    pbar.update()


async def process_echodex_swap(private_key: str, pbar: tqdm) -> None:
    from_token = EchoDexSwapConfig.from_token
    to_token = EchoDexSwapConfig.to_token
    amount_from = EchoDexSwapConfig.amount_from
    amount_to = EchoDexSwapConfig.amount_to
    swap_all_balance = EchoDexSwapConfig.swap_all_balance

    echo_dex_swap = EchoDexSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount_from=amount_from,
        amount_to=amount_to,
        swap_all_balance=swap_all_balance
    )
    logger.info('Swapping on EchoDex...')
    await echo_dex_swap.swap()
    pbar.update()


async def process_echodex_liquidity(private_key: str, pbar: tqdm) -> None:
    token = EchoDexLiqConfig.token
    token2 = EchoDexLiqConfig.token2
    amount_from = EchoDexLiqConfig.amount_from
    amount_to = EchoDexLiqConfig.amount_to

    echo_dex_liq = EchoDexLiquidity(
        private_key=private_key,
        token=token,
        token2=token2,
        amount_from=amount_from,
        amount_to=amount_to,
    )
    logger.info('Adding liquidity on EchoDex...')
    await echo_dex_liq.add_liquidity()
    pbar.update()


async def process_echodex_liquidity_remove(private_key: str, pbar: tqdm) -> None:
    from_token_pair = EchoDexLiqRemoveConfig.from_token_pair
    remove_all = EchoDexLiqRemoveConfig.remove_all
    removing_percentage = EchoDexLiqRemoveConfig.removing_percentage

    echo_dex_liq_remove = EchoDexLiquidityRemove(
        private_key=private_key,
        from_token_pair=from_token_pair,
        remove_all=remove_all,
        removing_percentage=removing_percentage
    )
    logger.info('Removing liquidity from EchoDex...')
    await echo_dex_liq_remove.remove_liquidity()
    pbar.update()


async def process_sync_swap(private_key: str, pbar: tqdm) -> None:
    from_token = SyncSwapConfig.from_token
    to_token = SyncSwapConfig.to_token
    amount_from = SyncSwapConfig.amount_from
    amount_to = SyncSwapConfig.amount_to
    swap_all_balance = SyncSwapConfig.swap_all_balance

    sync_swap = SyncSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount_from=amount_from,
        amount_to=amount_to,
        swap_all_balance=swap_all_balance
    )
    logger.info('Swapping on SyncSwap...')
    await sync_swap.swap()
    pbar.update()


async def process_syncswap_liquidity(private_key: str, pbar: tqdm) -> None:
    token = SyncSwapLiqConfig.token
    amount_from = SyncSwapLiqConfig.amount_from
    amount_to = SyncSwapLiqConfig.amount_to

    syncswap_liq = SyncSwapLiquidity(
        private_key=private_key,
        token=token,
        amount_from=amount_from,
        amount_to=amount_to,
    )
    logger.info('Adding liquidity on SyncSwap...')
    await syncswap_liq.add_liquidity()
    pbar.update()


async def process_syncswap_liquidity_remove(private_key: str, pbar: tqdm) -> None:
    remove_all = SyncSwapLiqRemoveConfig.remove_all
    removing_percentage = SyncSwapLiqRemoveConfig.removing_percentage

    syncswap_liq_remove = SyncSwapLiquidityRemove(
        private_key=private_key,
        remove_all=remove_all,
        removing_percentage=removing_percentage
    )
    logger.info('Removing liquidity from SyncSwap...')
    await syncswap_liq_remove.remove_liquidity()
    pbar.update()


async def process_horizondex_swap(private_key: str, pbar: tqdm) -> None:
    from_token = HorizonDexSwapConfig.from_token
    to_token = HorizonDexSwapConfig.to_token
    amount_from = HorizonDexSwapConfig.amount_from
    amount_to = HorizonDexSwapConfig.amount_to
    swap_all_balance = HorizonDexSwapConfig.swap_all_balance

    horizon_dex_swap = HorizonDexSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount_from=amount_from,
        amount_to=amount_to,
        swap_all_balance=swap_all_balance
    )
    logger.info('Swapping on HorizonDex...')
    await horizon_dex_swap.swap()
    pbar.update()

from src.utils.runner import *

module_handlers = {
    'main_bridge': process_main_bridge,
    'orbiter_bridge': process_orbiter_bridge,
    'linea_swap': process_linea_swap,
    'linea_liq': process_linea_liquidity,
    'linea_liq_remove': process_linea_liquidity_remove,
    'echo_dex_swap': process_echodex_swap,
    'echo_dex_liq': process_echodex_liquidity,
    'echo_dex_liq_remove': process_echodex_liquidity_remove,
    'sync_swap': process_sync_swap,
    'syncswap_liq': process_syncswap_liquidity,
    'syncswap_liq_remove': process_syncswap_liquidity_remove,
    'horizon_dex_swap': process_horizondex_swap,
    'sync_swap_liq': process_syncswap_liquidity,
    'sync_swap_liq_remove': process_syncswap_liquidity_remove
}

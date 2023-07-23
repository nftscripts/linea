RANDOMIZE = False
RUN_FOREVER = False
NUM_THREADS = 1
SLIPPAGE = 0.03
MIN_PAUSE = 60
MAX_PAUSE = 120

# -------------------------------------Модули--------------------------------#

# --- Bridges --- #
main_bridge = False
orbiter_bridge = False

# --- Swaps --- #
linea_swap = False
echo_dex_swap = False
sync_swap = False
horizon_dex_swap = False

# --- Liquidity --- #
linea_liq = False
linea_liq_remove = False

echo_dex_liq = False
echo_dex_liq_remove = False

sync_swap_liq = False
sync_swap_liq_remove = False


# --- Bridges --- #
class MainBridgeConfig:
    amount_from = 0.001
    amount_to = 0.001
    action = 'deposit'  # deposit/withdraw


class OrbiterBridgeConfig:
    chain = 'ARB'
    token = 'ETH'  # ETH
    amount_from = 0.0051
    amount_to = 0.0051
    action = 'withdraw'  # deposit/withdraw


# --- Swaps --- #
class LineaSwapConfig:
    from_token = 'BUSD'
    to_token = 'ETH'
    amount_from = 0.001
    amount_to = 0.001
    swap_all_balance = True


class EchoDexSwapConfig:
    from_token = 'BUSD'
    to_token = 'ETH'
    amount_from = 0.001
    amount_to = 0.001
    swap_all_balance = True


class SyncSwapConfig:
    from_token = 'BUSD'
    to_token = 'ETH'
    amount_from = 0.001
    amount_to = 0.001
    swap_all_balance = True


class HorizonDexSwapConfig:
    from_token = 'BUSD'
    to_token = 'ETH'
    amount_from = 0.001
    amount_to = 0.001
    swap_all_balance = True


# --- Liquidity --- #
class LineaLiqConfig:
    token = 'ETH'  # ETH
    token2 = 'BUSD'
    amount_from = 0.0005
    amount_to = 0.0005


class LineaLiqRemoveConfig:
    from_token_pair = 'BUSD'
    remove_all = True
    removing_percentage = 0.5


class EchoDexLiqConfig:
    token = 'ETH'  # ETH
    token2 = 'BUSD'
    amount_from = 0.0005
    amount_to = 0.0005


class EchoDexLiqRemoveConfig:
    from_token_pair = 'BUSD'
    remove_all = True
    removing_percentage = 0.5


class SyncSwapLiqConfig:
    token = 'ETH'  # ETH/BUSD
    amount_from = 0.001
    amount_to = 0.001


class SyncSwapLiqRemoveConfig:
    remove_all = True
    removing_percentage = 0.5

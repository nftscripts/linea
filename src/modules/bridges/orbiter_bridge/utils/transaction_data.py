from src.modules.bridges.orbiter_bridge.utils.orbiter_limits import transfer_limit
from src.utils.chains import *
from src.modules.bridges.orbiter_bridge.utils.config import (
    contract_orbiter_router,
    contract_stable,
)


async def get_router(token: str) -> str:
    return contract_orbiter_router[token.lower()]


async def get_chain_id(from_chain) -> int:
    chain_mapping = {
        'OP': OP.chain_id,
        'ARB': ARB.chain_id,

    }
    return chain_mapping.get(from_chain.upper(), 0)


async def get_scan_url(from_chain) -> str:
    url_mapping = {
        'OP': OP.scan,
        'ARB': ARB.scan,
        'LINEA': LINEA.scan
    }
    return url_mapping.get(from_chain.upper(), 0)


async def check_eligibility(from_chain: str, to_chain: str, token: str, amount: float) -> tuple[bool, str, str]:
    if token.lower() == 'eth':
        amount = amount / 10 ** 18
    else:
        amount = amount / 10 ** 6

    limits = transfer_limit[from_chain.lower()][to_chain.lower()][token.lower()]

    if limits['max'] >= amount >= limits['min']:
        if limits['min'] <= amount <= limits['min'] + \
                limits['withholding_fee']:
            amount = amount + limits['withholding_fee']
            amount = round(amount, 4)

        if (amount + limits['withholding_fee']) >= limits['max']:
            amount = amount - transfer_limit['withholding_fee']

        return True, limits['min'], limits['max']
    else:
        return False, limits['min'], limits['max']

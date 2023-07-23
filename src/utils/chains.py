class Chain:
    def __init__(self, chain_id: int, rpc: str, scan: str, code: int) -> None:
        self.chain_id = chain_id
        self.rpc = rpc
        self.scan = scan
        self.code = code


ETH = Chain(
    chain_id=1,
    rpc='https://rpc.ankr.com/eth',
    scan='https://etherscan.io/tx',
    code=9001,
)

LINEA = Chain(
    chain_id=59144,
    rpc='https://rpc.linea.build/',
    scan='https://lineascan.build/tx',
    code=9023
)

OP = Chain(
    chain_id=10,
    rpc='https://rpc.ankr.com/optimism',
    scan='https://optimistic.etherscan.io/tx',
    code=9007
)

ARB = Chain(
    chain_id=42161,
    rpc='https://arb1.arbitrum.io/rpc',
    scan='https://arbiscan.io/tx',
    code=9002
)

chain_mapping = {
    'eth': ETH,
    'op': OP,
    'arb': ARB,
    'linea': LINEA
}

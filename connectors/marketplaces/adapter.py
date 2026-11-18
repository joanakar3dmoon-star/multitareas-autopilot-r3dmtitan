from connectors.base import DisabledConnector
class MarketplaceConnector(DisabledConnector):
    def __init__(self, provider: str):
        super().__init__(f"marketplace:{provider}", "official API, account scope and terms not yet verified")

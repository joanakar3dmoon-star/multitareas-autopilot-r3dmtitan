"""Permisos de mínimo privilegio. Denegación por defecto para dinero saliente."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentPermissions:
    can_research: bool = True
    can_prepare_work: bool = True
    can_contact_customer: bool = False
    can_collect_payment: bool = False
    can_spend: bool = False
    can_transfer_out: bool = False
    can_place_investment_order: bool = False

    def require(self, action: str) -> None:
        field = {
            "research": "can_research",
            "prepare_work": "can_prepare_work",
            "contact_customer": "can_contact_customer",
            "collect_payment": "can_collect_payment",
            "spend": "can_spend",
            "transfer_out": "can_transfer_out",
            "investment_order": "can_place_investment_order",
        }.get(action)
        if field is None or not getattr(self, field):
            raise PermissionError(f"Action not authorized: {action}")

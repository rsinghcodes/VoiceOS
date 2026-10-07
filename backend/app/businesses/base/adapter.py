"""Base business adapter protocol — the contract all business adapters must satisfy."""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class BusinessAdapter(ABC):
    """
    Abstract base adapter for all business integrations.

    The agent calls these methods without knowing which business is behind them.
    Each concrete adapter connects to its specific backend (POS, DB, external API).
    """

    # ---- Catalog ----

    @abstractmethod
    async def search_catalog(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search catalog items by natural language query."""
        ...

    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Dict]:
        """Get a specific catalog item by ID."""
        ...

    @abstractmethod
    async def check_availability(self, product_id: str, quantity: int = 1) -> bool:
        """Check if a product/service is available."""
        ...

    # ---- Cart / Session ----

    @abstractmethod
    async def create_cart(self, session_id: str, customer_id: Optional[str] = None) -> str:
        """Create a new cart and return its ID."""
        ...

    @abstractmethod
    async def get_cart(self, cart_id: str) -> Dict:
        """Get the current cart state."""
        ...

    @abstractmethod
    async def add_to_cart(
        self,
        cart_id: str,
        product_id: str,
        quantity: int,
        customizations: Optional[List[str]] = None,
    ) -> Dict:
        """Add an item to the cart."""
        ...

    @abstractmethod
    async def update_cart(self, cart_id: str, product_id: str, quantity: int) -> Dict:
        """Update item quantity in the cart."""
        ...

    @abstractmethod
    async def remove_from_cart(self, cart_id: str, product_id: str) -> Dict:
        """Remove an item from the cart."""
        ...

    @abstractmethod
    async def calculate_total(self, cart_id: str) -> Dict:
        """Calculate and return the full price breakdown for the cart."""
        ...

    # ---- Transaction ----

    @abstractmethod
    async def create_transaction(self, cart_id: str, customer_data: Dict) -> Dict:
        """Create a confirmed order/booking from the cart."""
        ...

    @abstractmethod
    async def get_status(self, transaction_id: str) -> Dict:
        """Get current status of an order/booking."""
        ...

    @abstractmethod
    async def cancel_transaction(self, transaction_id: str, reason: Optional[str] = None) -> Dict:
        """Cancel an active order/booking."""
        ...

    # ---- Knowledge ----

    @abstractmethod
    async def search_knowledge(self, query: str) -> List[Dict]:
        """Search the business knowledge base (FAQs, policies, descriptions)."""
        ...

    # ---- Metadata ----

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return the list of capabilities this business supports."""
        ...

    @abstractmethod
    def get_business_context(self) -> Dict[str, Any]:
        """Return business name, type, and policy config for prompt assembly."""
        ...

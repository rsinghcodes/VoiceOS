"""Adapter factory — instantiate the correct BusinessAdapter for a given business_id."""

from app.businesses.base.adapter import BusinessAdapter


def get_adapter(business_id: str) -> BusinessAdapter:
    """
    Factory: return the correct BusinessAdapter for a given business.

    Looks up business type from config/DB, then instantiates the appropriate adapter.
    Raises ValueError for unknown business IDs.
    """
    # TODO: Look up business type from config/database
    raise NotImplementedError(
        f"Adapter factory not yet implemented for business_id='{business_id}'. "
        "Register business types as adapters are built."
    )

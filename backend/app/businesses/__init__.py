"""
Business adapter layer.

Isolates business-specific integrations from the generic agent core.
The agent only interacts with BusinessAdapter — not with any specific backend.

Implementations:
  - RestaurantAdapter  → app/businesses/restaurant/
  - SalonAdapter       → app/businesses/salon/
"""

from app.businesses.base.adapter import BusinessAdapter

__all__ = ["BusinessAdapter"]

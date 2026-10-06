from pydantic import BaseModel, Field
from typing import Any
from ..schemas.models import MarketingOutput, FinanceOutput, ProductOutput, ValidationOutput

class FinanceInput(BaseModel):
    revenue_per_customer: float = Field(default=299, ge=0)
    starting_customers: int = Field(default=100, ge=0)
    monthly_growth_rate: float = Field(default=0.20, ge=0, le=5)
    variable_cost_per_customer: float = Field(default=90, ge=0)
    fixed_monthly_cost: float = Field(default=90000, ge=0)
    marketing_monthly_cost: float = Field(default=30000, ge=0)
    initial_setup_cost: float = Field(default=250000, ge=0)

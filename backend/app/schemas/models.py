from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, EmailStr

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserOut

class RunCreate(BaseModel):
    startup_idea: str = Field(min_length=20, max_length=5000)
    target_location: str | None = None
    industry: str | None = None
    budget: str | None = None
    target_audience: str | None = None

class RunOut(BaseModel):
    run_id: str
    status: str
    startup_idea: str
    created_at: datetime
    completed_at: datetime | None = None

class Source(BaseModel):
    title: str
    url: str
    retrieved_at: str | None = None
    note: str | None = None

class MarketingOutput(BaseModel):
    market_overview: str
    target_audience: list[str]
    ideal_customer_profile: list[str]
    customer_pain_points: list[str]
    competitors: list[dict[str, Any]]
    market_opportunities: list[str]
    go_to_market_strategy: list[str]
    acquisition_channels: list[dict[str, Any]]
    marketing_budget_allocation: list[dict[str, Any]]
    ad_copies: list[str] = Field(min_length=3)
    seo_keywords: list[str]
    content_calendar: list[dict[str, Any]]
    sources: list[Source]
    assumptions: list[str]

class FinanceOutput(BaseModel):
    executive_summary: str
    revenue_models: list[dict[str, Any]] = Field(min_length=3, max_length=3)
    recommended_revenue_model: str
    initial_startup_costs: list[dict[str, Any]]
    monthly_operating_expenses: list[dict[str, Any]]
    marketing_expenses: list[dict[str, Any]]
    revenue_assumptions: dict[str, Any]
    year1_projection: list[dict[str, Any]] = Field(min_length=12, max_length=12)
    break_even: dict[str, Any]
    funding_requirements: dict[str, Any]
    funding_path: str
    financial_risks: list[str]
    assumptions: list[str]
    sources: list[Source]

class ProductOutput(BaseModel):
    product_overview: str
    problem_statement: str
    target_users: list[str]
    product_goals: list[str]
    mvp_features: list[dict[str, Any]]
    feature_prioritization: dict[str, list[str]]
    user_stories: list[str] = Field(min_length=5)
    roadmap: list[dict[str, Any]] = Field(min_length=3, max_length=3)
    kpi_targets: list[dict[str, Any]]
    technology_stack: list[str]
    product_risks: list[str]
    future_features: list[str]
    assumptions: list[str]

class ValidationOutput(BaseModel):
    overall_consistency_score: int = Field(ge=0, le=100)
    marketing_validation: list[str]
    finance_validation: list[str]
    product_validation: list[str]
    cross_agent_consistency: list[str]
    unsupported_claims: list[str]
    verify_flags: list[str]
    contradictions: list[str]
    risky_assumptions: list[str]
    recommended_corrections: list[str]
    final_validation_status: Literal['PASS','PASS WITH WARNINGS','REQUIRES VERIFICATION']

class ReportOut(BaseModel):
    run_id: str
    startup_idea: str
    marketing: MarketingOutput
    finance: FinanceOutput
    product: ProductOutput
    validation: ValidationOutput
    sources: list[Source]
    generated_at: datetime
    demo_mode: bool
    execution_mode: str = 'live_ai'

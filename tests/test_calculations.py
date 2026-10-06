from backend.app.services.calculations import build_financial_model

def test_financial_model_has_12_months():
    result=build_financial_model({'revenue_per_customer':100,'starting_customers':10,'monthly_growth_rate':0,'variable_cost_per_customer':20,'fixed_monthly_cost':100,'marketing_monthly_cost':100})
    assert len(result['year1_projection'])==12
    assert result['year1_projection'][0]['revenue']==1000
    assert result['year1_projection'][0]['profit_loss']==600

def test_break_even_math():
    result=build_financial_model({'revenue_per_customer':100,'variable_cost_per_customer':20,'fixed_monthly_cost':800,'marketing_monthly_cost':200,'starting_customers':1,'monthly_growth_rate':0})
    assert result['break_even']['break_even_customers']==12.5

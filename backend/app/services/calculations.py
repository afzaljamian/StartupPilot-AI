def build_financial_model(a: dict) -> dict:
    rpc=float(a.get('revenue_per_customer',299)); customers=int(a.get('starting_customers',100)); growth=float(a.get('monthly_growth_rate',.2)); variable=float(a.get('variable_cost_per_customer',90)); fixed=float(a.get('fixed_monthly_cost',90000)); marketing=float(a.get('marketing_monthly_cost',30000))
    rows=[]
    for month in range(1,13):
        c=round(customers)
        revenue=round(c*rpc,2); var_cost=round(c*variable,2); total_expense=round(var_cost+fixed+marketing,2); profit=round(revenue-total_expense,2)
        rows.append({'month':month,'customers':c,'revenue':revenue,'variable_cost':var_cost,'fixed_cost':fixed,'marketing_cost':marketing,'total_expenses':total_expense,'profit_loss':profit})
        customers*=1+growth
    contribution=rpc-variable
    be_customers=round((fixed+marketing)/contribution,2) if contribution>0 else None
    be_month=next((r['month'] for r in rows if r['profit_loss']>=0), None)
    return {'year1_projection':rows,'break_even':{'break_even_customers':be_customers,'break_even_month':be_month,'contribution_margin_per_customer':contribution}}

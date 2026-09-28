from policyengine_us.model_api import *


class ks_liheap_self_employment_expenses(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Kansas LIEAP allowable self-employment expenses"
    documentation = "Annual actual income-producing costs allowable under KEESM 13360. Used with gross receipts when claiming actual costs gives a larger deduction than the standard percentage."
    reference = "https://content.dcf.ks.gov/ees/keesm/current/keesm13360.htm"

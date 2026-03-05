from policyengine_us.model_api import *


class nj_senior_freeze(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Senior Freeze (Property Tax Reimbursement) benefit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nj.gov/treasury/taxation/ptr/index.shtml"

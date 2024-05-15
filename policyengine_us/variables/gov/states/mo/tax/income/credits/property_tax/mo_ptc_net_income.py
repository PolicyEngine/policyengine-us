from policyengine_us.model_api import *


class mo_ptc_net_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri property tax credit net income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://dor.mo.gov/forms/4711_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        gross_income = tax_unit("mo_ptc_gross_income", period)
        income_offset = tax_unit("mo_ptc_income_offset", period)
        return max_(0, gross_income - income_offset)  # Form MO-PTS, line 10

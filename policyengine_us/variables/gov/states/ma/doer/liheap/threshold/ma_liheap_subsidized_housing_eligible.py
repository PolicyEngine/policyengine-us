from policyengine_us.model_api import *


class ma_liheap_subsidized_housing_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.MA
    label = "Massachusetts LIHEAP threshold for subsidized housing"
    reference = "https://liheapch.acf.hhs.gov/tables/FY2015/subsidize.htm#MA"

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        rent = spm_unit.members("rent", period).sum()
        housing_assistance = spm_unit("housing_assistance", period)
        p = parameters(period).gov.states["ma"].doer.liheap.threshold

        rent_threshold = income * p.rent_rate

        return (rent >= rent_threshold) & (housing_assistance > 0)

from policyengine_us.model_api import *


class wi_tanf_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin TANF income limit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/"
        "03.2.1_115_Percent_Gross_Income_Test.htm",
        "https://docs.legis.wisconsin.gov/code/admin_code/dcf/"
        "101_199/101/09/3",
    )
    defined_for = StateCode.WI

    def formula(spm_unit, period, parameters):
        # Use household size (spm_unit_size) for income limit lookup
        household_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.wi.dcf.tanf.income_limit
        return p.amount[household_size]

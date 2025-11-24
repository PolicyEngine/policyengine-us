from policyengine_us.model_api import *


class wi_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/"
        "03.2.1_115_Percent_Gross_Income_Test.htm",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145"
        "#(2)(a)",
    )
    defined_for = StateCode.WI
    documentation = """
    Wisconsin W-2 requires total countable income to be less than or
    equal to 115% of the Federal Poverty Level for the W-2 Group size.
    """

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("wi_tanf_countable_income", period)
        income_limit = spm_unit("wi_tanf_income_limit", period)
        return countable_income <= income_limit

from policyengine_us.model_api import *


class il_hbi_senior_income_level(Variable):
    value_type = float
    entity = Person
    label = "Illinois HBIS income as share of federal poverty level"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = ("https://www.dhs.state.il.us/page.aspx?item=161600",)
    # HBIS uses AABD methodology for income counting but compares against
    # 100% of the federal poverty level.

    def formula(person, period, parameters):
        # Get monthly AABD-methodology income and annualize
        income = person("il_hbi_senior_countable_income", period)

        # Get household FPL based on SPM unit size
        fpg = person.spm_unit("spm_unit_fpg", period)

        # Return income as fraction of FPL (handle divide by zero)
        return where(fpg > 0, income / fpg, 0)

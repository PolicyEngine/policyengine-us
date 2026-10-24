from policyengine_us.model_api import *


class ssi_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI income (deemed from ineligible spouse)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"
    documentation = """
    Spousal deeming: 
      1) If leftover spouse income <= (coupleFBR - indivFBR), then 0 is deemed.
      2) Otherwise, spouse's deemed = (couple combined countable) - (individual alone countable).
      Each month is calculated before annual amounts are summed.
    """
    defined_for = "is_ssi_eligible_individual"
    unit = USD

    def formula(person, period, parameters):
        # Sum completed monthly budgets; supplied amounts retain their annual basis.
        return person("ssi_income_deemed_from_ineligible_spouse_monthly", period)

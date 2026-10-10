from policyengine_us.model_api import *


class la_general_relief_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Los Angeles County General Relief housing payment"
    definition_period = MONTH
    # Person has to be a resident of LA County
    defined_for = "la_general_relief_housing_subsidy_eligible"
    reference = (
        "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/gr/homelessness/housing-subsidy-management-program.html#custom-title-f75ca3f760",
        "https://dpss.lacounty.gov/content/dam/dpss/documents/en/gr/gr-housing-subsidy/PA%206182%20%28English%29%20ADA%20APPROVED.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        subsidy_amount = spm_unit("la_general_relief_housing_subsidy_amount", period)
        # Read the same contribution used by the cash grant deduction,
        # including supplied inputs. Its subsidy dependency is independent
        # of this total payment, so the calculation remains acyclic.
        rent_contributions = spm_unit("la_general_relief_rent_contribution", period)
        # The amount can not exceed rent
        rent = add(spm_unit, period, ["rent"])
        return min_(rent, subsidy_amount + rent_contributions)

from policyengine_us.model_api import *


class az_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP household size"
    documentation = "Number of household members who are U.S. citizens or qualified noncitizens. Other members are not counted in household size, although the income of every adult member counts toward household income."
    reference = (
        # Eligible Household Member and Mixed-Status Household definitions
        # (pages 4-5) and Section VI.A.6.d.i (page 8).
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=8",
    )
    defined_for = StateCode.AZ

    # Section VI.A.6.d: "In Mixed-Status Households: i. Only Eligible Household
    # Members will be considered as part of the Household size; and ii. Income
    # from all Household members aged 18 and older - regardless of eligibility -
    # is considered Household income." An Eligible Household Member is "a U.S.
    # citizen or Qualified Noncitizen" (page 4). The model's qualified statuses
    # omit COFA citizens, trafficking victims and battered noncitizens.
    adds = ["is_citizen_or_legal_immigrant"]

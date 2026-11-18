from policyengine_us.model_api import *


class az_property_tax_credit_claimant(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claimant of the household's Arizona property tax credit"
    definition_period = YEAR
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(G), (H)(1)
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
    ]
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # ARS 43-1072(G): "Only one claimant per household per year shall be
        # entitled to a tax credit"; A.A.C. R15-2C-502(D) says the same. Under
        # (H)(1), when two members qualify "they may determine between them as
        # to whom the claimant shall be". As a modeling convention, the
        # household picks the eligible tax unit whose claim
        # (az_property_tax_credit_potential) is largest. A tie goes to the tax
        # unit holding the household head, and otherwise to the tax unit whose
        # head comes first in the simulation's person order.
        person = tax_unit.members
        candidate = person("is_tax_unit_head", period) & person.tax_unit(
            "az_property_tax_credit_eligible", period
        )
        claim = person.tax_unit("az_property_tax_credit_potential", period)
        largest = person.household.max(where(candidate, claim, -np.inf))
        tied = candidate & (claim >= largest)
        holds_household_head = person.tax_unit.any(person("is_household_head", period))
        # get_rank sorts by members_position, so rank 0 goes to the first tied
        # tax unit holding the household head, or, if none does, to the tied
        # tax unit whose head comes first in the simulation's person order.
        rank = person.get_rank(
            person.household, where(holds_household_head, 0, 1), condition=tied
        )
        return tax_unit.any(tied & (rank == 0))

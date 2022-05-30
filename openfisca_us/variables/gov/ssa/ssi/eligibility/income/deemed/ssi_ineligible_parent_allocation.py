from openfisca_us.model_api import *
from openfisca_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import _apply_ssi_exclusions


class ssi_ineligible_parent_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible parent allocation"
    unit = USD
    documentation = "The amount of income that SSI deems ought to be spent on this parent, and therefore is not deemed to SSI claimants."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        ssi = parameters(period).ssa.ssi.amount
        ineligible_parent = person("is_ssi_ineligible_parent", period)
        num_ineligible_parents = person.tax_unit.sum(ineligible_parent)
        return where(num_ineligible_parents == 2, ssi.couple, ssi.individual * ineligible_parent)
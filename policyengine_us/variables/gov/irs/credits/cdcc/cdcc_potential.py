from policyengine_us.model_api import *


class cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Potential value of the Child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        expenses = tax_unit("cdcc_relevant_expenses", period)
        rate = tax_unit("cdcc_rate", period)
        # The IRC 21(e)(2) joint-return requirement applies here, before the
        # tax liability cap, so state credits computed from this pre-cap
        # amount (rather than from cdcc) also exclude separate filers.
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        return eligible * expenses * rate

from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.credits.ctc.maximum.individual.ctc_child_individual_maximum import (
    ctc_child_individual_maximum,
)
from policyengine_us.variables.gov.irs.credits.ctc.maximum.individual.ctc_adult_individual_maximum import (
    ctc_adult_individual_maximum,
)
from policyengine_us.parameters import default_parameters


class ctc_maximum_without_arpa(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC maximum without ARPA"
    unit = USD
    documentation = "Used to compute the additional CTC reduction under ARPA."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ctc = parameters(period).gov.irs.credits.ctc
        # defined_for didn't work.
        # We only
        if not ctc.phase_out.arpa.in_effect:
            return 0
        # Calculate the increase - do this by finding the original CTC if
        # ARPA had not applied - this year's variables, last year's parameters.
        no_arpa_parameters = default_parameters.clone()
        old_ctc = parameters(period.last_year).gov.irs.credits.ctc
        no_arpa_ctc = no_arpa_parameters.gov.irs.credits.ctc
        no_arpa_ctc.child.young.increase.update(value=0, period=period)
        no_arpa_ctc.child.amount.update(
            value=old_ctc.child.amount, period=period
        )

        ctc_child_without_arpa = ctc_child_individual_maximum.formula(
            tax_unit.members, period, no_arpa_parameters
        )
        ctc_adult_without_arpa = ctc_adult_individual_maximum.formula(
            tax_unit.members, period, no_arpa_parameters
        )
        return tax_unit.sum(ctc_child_without_arpa + ctc_adult_without_arpa)

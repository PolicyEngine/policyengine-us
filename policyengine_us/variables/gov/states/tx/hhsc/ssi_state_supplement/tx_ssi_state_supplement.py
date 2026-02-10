from policyengine_us.model_api import *


class tx_ssi_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Texas SSI State Supplement"
    unit = USD
    definition_period = YEAR
    defined_for = "tx_ssi_state_supplement_eligible"
    reference = (
        "https://statutes.capitol.texas.gov/Docs/HR/htm/HR.32.htm",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-6000-co-payment-ssi-cases",
    )

    def formula(person, period, parameters):
        # Per 42 USC 1382(e)(1)(B) and Texas HR Code 32.024(w)
        p = parameters(period).gov.states.tx.hhsc.ssi_state_supplement
        pna = p.personal_needs_allowance
        federal_reduced = parameters(
            period
        ).gov.ssa.ssi.amount.institutional.individual
        return max_(pna - federal_reduced, 0) * MONTHS_IN_YEAR

from policyengine_us.model_api import *


class tx_ssi_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Texas SSI State Supplement"
    unit = USD
    definition_period = MONTH
    defined_for = "tx_ssi_state_supplement_eligible"
    reference = (
        "https://statutes.capitol.texas.gov/Docs/HR/htm/HR.32.htm",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-1500-personal-needs-allowance",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-6000-co-payment-ssi-cases",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-358-381",
    )

    def formula(person, period, parameters):
        # 1 TAC 358.381(c)(2): "For a person receiving the reduced SSI federal
        # benefit rate, HHSC issues a supplement to give the person a PNA at
        # the minimum level set by the HHSC executive commissioner." MEPD
        # Handbook H-6000: "HHSC supplements the reduced SSI payment standard
        # by $45 per month to ensure SSI recipients also have a $75 personal
        # needs allowance", i.e. the allowance (Texas HR Code 32.024(w)) less
        # the $30 reduced federal benefit (42 USC 1382(e)(1)(B)).
        # H-6000 states the supplement as a fixed amount on the reduced
        # standard and, separately, has workers check SSI recipients for other
        # income and calculate a co-payment; no Texas source subtracts the
        # recipient's income from the supplement. For an individual paid SSI
        # on the reduced standard, federal SSI plus countable income equals
        # the $30 standard, so the allowance less both is the same amount.
        p = parameters(period).gov.states.tx.hhsc.ssi_state_supplement
        pna = p.personal_needs_allowance
        federal_reduced = parameters(period).gov.ssa.ssi.amount.medical_facility
        return max_(pna - federal_reduced, 0)

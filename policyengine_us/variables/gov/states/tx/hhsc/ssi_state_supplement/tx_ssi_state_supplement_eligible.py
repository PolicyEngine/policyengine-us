from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class tx_ssi_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Texas SSI State Supplement eligible"
    definition_period = MONTH
    defined_for = StateCode.TX
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-358-381",
        "https://statutes.capitol.texas.gov/Docs/HR/htm/HR.32.htm",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-6000-co-payment-ssi-cases",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-1500-personal-needs-allowance",
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(f)(5)",
    )

    def formula(person, period, parameters):
        # 1 TAC 358.381(c)(2): "For a person receiving the reduced SSI federal
        # benefit rate, HHSC issues a supplement to give the person a PNA at
        # the minimum level set by the HHSC executive commissioner." The
        # reduced rate is SSI's medical treatment facility rate (20 CFR
        # 416.414), so a facility resident still on the full rate, as in the
        # month of entry (H-6000), receives no supplement.
        arrangement = person("ssi_federal_living_arrangement", period)
        on_reduced_rate = (
            arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        # H-6000: the resident "remains eligible for SSI if their countable
        # income does not exceed the SSI reduced standard payment amount", so
        # countable income equal to it, with a $0 federal payment, still
        # qualifies. 20 CFR 416.1163(f)(5): while the $30 rate applies, an
        # ineligible spouse's income is not deemed and only the resident's own
        # countable income counts. For a couple both in a facility, SSI's
        # couple computation gives each spouse half the couple's countable
        # income, held to their $30 half of the $60 couple standard (H-6000).
        p = parameters(period).gov.ssa.ssi
        own_countable_income = max_(
            person("ssi_countable_income_monthly", period)
            - person("ssi_income_deemed_from_ineligible_spouse_monthly", period),
            0,
        )
        within_reduced_rate = own_countable_income <= p.amount.institutional.individual
        eligible_for_ssi = (
            person("is_ssi_eligible", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
            & within_reduced_rate
            & ~p.abolish_ssi
        )
        receives_ssi = person("receives_ssi", period)
        in_facility = person("is_in_medicaid_facility", period)
        return (eligible_for_ssi | receives_ssi) & on_reduced_rate & in_facility

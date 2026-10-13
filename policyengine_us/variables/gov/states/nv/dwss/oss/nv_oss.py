from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class nv_oss(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Nevada Optional State Supplementation"
    defined_for = StateCode.NV
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#i",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-2025.htm",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320430#d",
        "https://secure.ssa.gov/poms.nsf/lnx/0502001005",
        "https://secure.ssa.gov/poms.nsf/lnx/0502001010",
    )

    def formula(person, period, parameters):
        eligible = person("is_ssi_eligible", period) & person(
            "takes_up_ssi_if_eligible", period.this_year
        )
        standard = person("nv_oss_payment_standard", period)
        countable_income = person("ssi_countable_income", period)
        federal_amount = person("ssi_amount_if_eligible", period)
        excess_income = max_(countable_income - federal_amount, 0)
        payment = max_(standard - excess_income, 0)

        # A spouse's deemed income uses the couple supplement, capped at
        # the payment due using the claimant's own income and individual rate.
        # Deeming excludes a joint claim, so the standard is that individual rate.
        deeming = person("is_ssi_spousal_deeming_applies", period.this_year)
        p = parameters(period).gov.states.nv.dwss.oss.payment
        arrangement = person("nv_oss_living_arrangement", period)
        category = person("ssi_category", period.this_year)
        couple_payment = max_(p.couple[arrangement][category] - excess_income, 0)
        own_income = max_(
            countable_income
            - person("ssi_income_deemed_from_ineligible_spouse", period),
            0,
        )
        ssi = parameters(period).gov.ssa.ssi
        federal_arrangement = person("ssi_federal_living_arrangement", period)
        own_federal_amount = ssi.amount.individual * where(
            federal_arrangement
            == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            1 - ssi.amount.one_third_reduction_rate,
            1,
        )
        own_payment = max_(standard - max_(own_income - own_federal_amount, 0), 0)
        payment = where(deeming, min_(own_payment, couple_payment), payment)
        # SI 02001.010: ignore digits after the third decimal place, then
        # round each member's state payment up to cents. Truncation also
        # prevents floating-point residue at the income cutoff paying $1.
        payment = np.ceil(np.floor(payment * 1_000) / 10) / 100
        minimum = ssi.state_supplement.minimum_payment
        return where(eligible & (payment > 0), max_(payment, minimum), 0)

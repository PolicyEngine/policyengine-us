from policyengine_us.model_api import *


class nm_armed_forces_retirement_pay_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "New Mexico armed forces retirement pay exemption per person "
    unit = USD
    definition_period = YEAR
    reference = (
        # NMSA 7-2-5.13; HB 252 sections 32 and 42 (PDF pages 102, 147)
        # extend eligibility to surviving spouses for tax years beginning in 2025.
        "https://www.nmlegis.gov/Sessions/24%20Regular/final/HB0252.PDF#page=102",
    )
    defined_for = StateCode.NM

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.nm.tax.income.exemptions.armed_forces_retirement_pay
        retirement_pay = person("military_retirement_pay", period)
        survivor_pay = person("military_retirement_pay_survivors", period)
        surviving_spouse = person("is_surviving_spouse", period)
        armed_forces_retirement_pay = (
            retirement_pay + survivor_pay * surviving_spouse * p.survivors_eligible
        )

        capped_amount = min_(armed_forces_retirement_pay, p.cap)
        qualifies = person("is_tax_unit_head_or_spouse", period)
        return qualifies * capped_amount

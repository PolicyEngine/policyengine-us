from policyengine_us.model_api import *


class mo_liheap_medical_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Missouri LIHEAP medical deduction"
    documentation = "Missouri's monthly medical deduction, annualized and given once per household when the applicant or spouse is elderly or disabled. Disabled means totally and permanently disabled or blind and receiving a listed disability benefit. Tax-unit heads and spouses who are citizens or legal immigrants stand in for the applicant and spouse."
    reference = (
        # PDF pages 2-3
        "https://web.archive.org/web/20250603190025/https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-19.pdf#page=2",
        # PDF pages 36, 48
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2025/10/liheap-policy-procedure-manual.pdf#page=36",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.liheap.income
        person = spm_unit.members
        applicant_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        # The 2025 manual (page 36) is silent on a spouse left out of the
        # household as a non-citizen, and a non-citizen applicant makes the case
        # ineligible (page 43); the model keeps the citizenship requirement.
        qualified = person("is_citizen_or_legal_immigrant", period)
        elderly = person("age", period) >= p.elderly_age
        disabled_or_blind = person("is_disabled", period) | person("is_blind", period)
        receives_disability_benefit = (
            add(person, period, p.disability_benefit_sources) > 0
        )
        qualifies = (
            applicant_or_spouse
            & qualified
            & (elderly | (disabled_or_blind & receives_disability_benefit))
        )
        return spm_unit.any(qualifies) * p.medical_deduction * MONTHS_IN_YEAR

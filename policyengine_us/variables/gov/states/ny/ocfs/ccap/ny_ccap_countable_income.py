from policyengine_us.model_api import *


class ny_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York CCAP countable income"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "Income counted for New York Child Care Assistance Program income "
        "eligibility and the family share. New York defines countable income "
        "in 18 NYCRR 404.5(b)(5) rather than in Part 415, which contains no "
        "income-composition rule. Public assistance is countable under "
        "404.5(b)(5)(vi) but is omitted here because counting it creates a "
        "CCAP-to-TANF circular dependency through the TANF dependent care "
        "deduction; see countable_income_sources.yaml. Defined annually so "
        "the monthly consumers read it with the bare period and Core divides "
        "it."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/404-Eligibility.pdf#page=10",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.income
        countable = add(spm_unit, period, p.countable_income_sources)
        person = spm_unit.members
        # ssi is monthly, so add() sums it across the year.
        # 404.5(b)(5)(vi) excludes the SSI of any child in the unit; an
        # adult's SSI stays countable.
        adult_ssi = add(person, period, ["ssi"]) * ~person("is_child", period)
        return countable + spm_unit.sum(adult_ssi)

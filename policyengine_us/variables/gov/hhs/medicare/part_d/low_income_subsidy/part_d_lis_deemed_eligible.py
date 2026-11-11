from policyengine_us.model_api import *


class part_d_lis_deemed_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Deemed eligible for the Medicare Part D low-income subsidy"
    documentation = (
        "Treated as eligible for the full subsidy without an income or "
        "resource test: full-benefit dual eligibles (Medicaid enrollees), "
        "Supplemental Security Income recipients, and people eligible for a "
        "Medicare Savings Program (QMB, SLMB or QI)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_B_v",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.773#p-423.773(c)",
    )

    def formula(person, period, parameters):
        medicaid = person("medicaid_enrolled", period)
        ssi = add(person, period, ["ssi"]) > 0
        msp = add(person, period, ["msp_eligible"]) > 0
        return medicaid | ssi | msp

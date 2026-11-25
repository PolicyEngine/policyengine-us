from policyengine_us.model_api import *


class ma_tafdc_full_earned_income_disregard_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Is eligible for the full earned income disregard under the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281",  # (A)
        # 2018 c. 154, Sections 55 and 113.
        "https://malegislature.gov/Laws/SessionLaws/Acts/2018/Chapter154",
    )
    defined_for = StateCode.MA

    # Legal onset: July 1, 2018. January 1 preserves the existing 2018+ annual
    # approximation; it does not establish January-June eligibility or a
    # six-month receipt/employment history. Earlier computed defaults do not
    # independently qualify the 2015-2016 rules.
    def formula_2018_01_01(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.tafdc.earned_income_disregard.full_disregard
        gross_income = person.spm_unit(
            "ma_tafdc_applicable_income_for_financial_eligibility", period
        )

        fpg = person.spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.fpg_limit
        return gross_income < income_limit

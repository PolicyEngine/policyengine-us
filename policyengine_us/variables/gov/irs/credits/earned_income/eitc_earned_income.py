from policyengine_us.model_api import *


class eitc_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Earned income for the EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#c_2",
        "https://www.law.cornell.edu/uscode/text/26/402#e_3",
        "https://www.law.cornell.edu/uscode/text/26/125#a",
        "https://www.law.cornell.edu/uscode/text/26/106#d",
        "https://www.irs.gov/publications/p596",
        "https://www.irs.gov/instructions/i1040gi",
    )

    def formula(tax_unit, period, parameters):
        # IRC 32(c)(2)(A)(i) includes employee compensation only when
        # includible in gross income. The EIC worksheet starts from Form
        # 1040 line 1z (including W-2 box 1), already reduced by qualifying
        # payroll deductions. Reuse federal taxable wages without another
        # deduction, so supplied W-2 wages are not reduced twice.
        earned_income_sources = [
            "irs_employment_income",
            "self_employment_income",
            "sstb_self_employment_income",
            "farm_operations_income",
            "partnership_self_employment_net_earnings",
        ]
        gross_earned_income = sum(
            tax_unit_non_dep_sum(source, tax_unit, period)
            for source in earned_income_sources
        )
        self_employment_tax_ald = tax_unit_non_dep_sum(
            "self_employment_tax_ald_person", tax_unit, period
        )
        return max_(0, gross_earned_income - self_employment_tax_ald)

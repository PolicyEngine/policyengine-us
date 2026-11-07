from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.tax_unit_taxable_section_86_benefits import (
    SECTION_86_GROSS_INCOME_SOURCES,
)


class ira_219g_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified AGI for the IRC 219(g) IRA deduction phase-out"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g_3_A",
        "https://www.irs.gov/publications/p590a",
    )

    def formula(tax_unit, period, parameters):
        irs = parameters(period).gov.irs
        sources = [
            s
            for s in irs.gross_income.sources
            if s not in SECTION_86_GROSS_INCOME_SOURCES
            and s != "taxable_unemployment_compensation"
        ]
        if "taxable_unemployment_compensation" in irs.gross_income.sources:
            # 219(g)(3)(A)(ii): without regard to 85(c).
            sources.append("total_unemployment_compensation")
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross = 0
        for source in sources:
            gross += not_dependent * max_(0, add(person, period, [source]))
        gross = tax_unit.sum(gross)
        # 219(g)(3)(A)(i): after section 86 (benefits figured before the IRA
        # deduction, Pub. 590-A App. B Worksheet 1 line 17).
        gross += tax_unit("ira_219g_taxable_social_security", period)
        # Section 911 exclusions are disregarded for IRA MAGI.
        gross += tax_unit("section_911_excluded_income", period)
        deductions = [
            d
            for d in irs.ald.deductions
            if d not in irs.ald.ira.magi_excluded_deductions
        ]
        magi = gross - tax_unit_non_dep_add(
            tax_unit,
            period,
            deductions,
            include_dependents=irs.ald.filer_amounts_recorded_on_dependents,
        )
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            magi += add(tax_unit, period, ["basic_income"])
        return magi

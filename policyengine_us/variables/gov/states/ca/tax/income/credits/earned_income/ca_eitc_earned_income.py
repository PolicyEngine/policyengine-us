from policyengine_us.model_api import *


class ca_eitc_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "California earned income for the CalEITC, YCTC and FYTC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052",  # (c)(4)
        "https://www.ftb.ca.gov/forms/2023/2023-3514-instructions.html",  # Lines 13-19, Worksheet 3
        "https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.html",
        "https://edd.ca.gov/siteassets/files/pdf_pub_ctr/de231eb.pdf#page=3",  # HSA payroll contributions
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # FTB 3514 line 13: filers' California taxable wages (W-2 box 16).
        filer_wages = tax_unit_non_dep_sum("ca_taxable_wages", tax_unit, period)

        # FTB 3514 line 19 nets wages and business income or losses for the
        # whole return. Worksheet 3 includes farm income and partnership
        # self-employment earnings, less the deductible part of SE tax. A loss
        # of one spouse offsets the other spouse's wages before the final floor.
        self_employment_sources = [
            "self_employment_income",
            "sstb_self_employment_income",
            "farm_operations_income",
            "partnership_self_employment_net_earnings",
        ]
        self_employment_income = sum(
            tax_unit_non_dep_sum(source, tax_unit, period)
            for source in self_employment_sources
        )
        self_employment_tax_ald = tax_unit_non_dep_sum(
            "self_employment_tax_ald_person", tax_unit, period
        )
        return max_(0, filer_wages + self_employment_income - self_employment_tax_ald)

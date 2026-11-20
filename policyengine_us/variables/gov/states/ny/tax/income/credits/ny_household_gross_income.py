from policyengine_us.model_api import *


class ny_household_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York IT-214 household gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "IT-214 household gross income (Step 3, line 16) is the eligibility "
        "and credit-sizing income measure through tax year 2024; from 2025 the "
        "credit uses federal AGI instead (see ny_real_property_tax_credit). By "
        "statute (Tax Law 606(e)(1)(C)) household gross income is the income of "
        "all members of the household, and a household is everyone who shares "
        "the residence (606(e)(1)(B)). This variable sums every member of the "
        "PolicyEngine household, including other tax units and tax unit "
        "dependents, and gives each tax unit in the household that total. "
        "606(e)(1)(B) leaves out a tenant, subtenant, roomer or boarder who is "
        "not related to the claimant; no input marks those members, so their "
        "income counts. Not yet added: New York additions other than "
        "tax-exempt interest (line 10) and nontaxable strike benefits (line 15)."
    )
    reference = (
        # 606(e)(1)(B) defines the household; 606(e)(1)(C) defines household
        # gross income for taxable years before 2025.
        "https://www.nysenate.gov/legislation/laws/TAX/606",
        # Year-specific 2024 instructions: line 7 (household members) and
        # lines 9 to 15. The current_forms/ URL resolves to the latest (2025)
        # form, whose Step 3 uses federal AGI, not this measure.
        "https://www.tax.ny.gov/pdf/2024/inc/it214i_2024.pdf#page=2",
        # 2024 Form IT-214 Step 3, lines 9 to 16.
        "https://www.tax.ny.gov/pdf/2024/inc/it214_2024_fill_in.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        # Form IT-214, Step 3 "Determine household gross income": line 16 is
        # the sum of lines 9 through 15, "the total of all amounts, even if
        # not taxable, that you, your spouse (if married), and all other
        # household members received". Each amount is figured per person and
        # summed over the household.
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_dependent = person("is_tax_unit_dependent", period)
        # Line 9: federal AGI "for all members of your household". Each tax
        # unit's recomputed federal AGI (IT-201 line 19a) counts once, on its
        # head. A tax unit dependent's AGI is on their own return.
        line_9 = is_head * person.tax_unit(
            "ny_recomputed_federal_agi", period
        ) + person("dependent_adjusted_gross_income", period)
        # Line 11: "Social Security payments not included on line 9,
        # including all payments received under the Social Security Act and
        # veterans disability pensions" (606(e)(1)(C): "veterans' disability
        # pensions"). A dependent's taxable Social Security is in their own
        # AGI.
        social_security = person("social_security", period)
        taxable_social_security = where(
            is_dependent,
            person("dependent_taxable_social_security", period),
            person("taxable_social_security", period),
        )
        nontaxable_social_security = max_(social_security - taxable_social_security, 0)
        line_11 = nontaxable_social_security + person("veterans_benefits", period)
        # Line 12: Supplemental Security Income payments.
        line_12 = person("ssi", period)
        # Line 13: pensions and annuities not included on lines 9 through 12;
        # 606(e)(1)(C) counts "the gross amount of any pension or annuity
        # benefits to the extent not included in such adjusted gross income".
        line_13 = person("tax_exempt_pension_income", period)
        # Line 14: cash public assistance and relief (606(e)(1)(C): "the
        # amount of cash public assistance and relief, other than medical
        # assistance for the needy"). TANF is paid to the SPM unit, and
        # tanf_person is each member's equal share. The New York State
        # Supplement Program payment is state cash relief paid on top of SSI.
        line_14 = add(person, period, ["tanf_person", "general_assistance", "ny_ssp"])
        # Line 15: other income, including nontaxable New York interest,
        # workers' compensation, support money, income earned abroad exempted
        # by IRC 911 and the gross amount of loss-of-time insurance, each also
        # named in 606(e)(1)(C). The section 911 amount is a tax unit total,
        # so it counts on the head.
        line_15 = add(
            person,
            period,
            [
                "tax_exempt_interest_income",
                "workers_compensation",
                "child_support_received",
                "tax_exempt_disability_benefits",
            ],
        ) + is_head * person.tax_unit("section_911_excluded_income", period)
        income = line_9 + line_11 + line_12 + line_13 + line_14 + line_15
        # Every tax unit in the household gets the household's total.
        return tax_unit.max(person.household.sum(income))

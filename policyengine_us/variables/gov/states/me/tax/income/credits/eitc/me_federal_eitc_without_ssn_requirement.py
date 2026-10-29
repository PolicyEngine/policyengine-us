from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import federal_eitc_tax_unit


class me_federal_eitc_without_ssn_requirement(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without the SSN requirement for Maine"
    unit = USD
    documentation = "The federal earned income credit, computed from 2021 with an ITIN or any Social Security number accepted for the filer, spouse and qualifying children in place of the IRC 32(m) Social Security number, on a return whose filer files a federal income tax return (me_eitc_ssn_limitation_waived). All other federal rules apply, including the minimum age, take-up, the bar on section 911 claimants and any reform of the federal credit."
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-S.html",
        "https://www.law.cornell.edu/uscode/text/26/32#m",
        # Maine Revenue Services, Earned Income Tax Credit Worksheet for Tax
        # Year 2024, special instructions for line 1.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/24_earned_income_cred_ff_0.pdf",
        # 2025 Form 1040ME instructions, Schedule A, line 4.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_gen_instr_w_cover_pg.pdf#page=10",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # § 5219-S(7): "for an individual who files a federal income tax
        # return, notwithstanding Section 32(m) of the Code, for purposes of calculating the credit allowed pursuant to this section,
        # the taxpayer identification number required by Section 32(c)(1)(E)
        # and 32(c)(3)(D) of the Code means a federal individual taxpayer
        # identification number issued to an individual by the Internal
        # Revenue Service or a social security number". The MRS worksheet has
        # the filer answer "Yes" to the federal SSN question with either
        # number and complete a pro forma federal EIC worksheet.
        federal = federal_eitc_tax_unit(tax_unit, period)
        return federal("eitc", period)

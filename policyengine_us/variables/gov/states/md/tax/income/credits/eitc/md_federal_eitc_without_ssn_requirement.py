from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import federal_eitc_tax_unit


class md_federal_eitc_without_ssn_requirement(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without the SSN requirement for Maryland"
    unit = USD
    documentation = "The federal earned income credit allowable, or that would have been allowable but for the IRC 32(m) Social Security number limitation. All other federal rules apply, including the minimum age, take-up, the bar on section 911 claimants and any reform of the federal credit."
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",
        "https://www.law.cornell.edu/uscode/text/26/32#m",
        # 2025 Resident Booklet, Instruction 18, Line 22.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=22",
        # 2025 Resident Booklet, Instruction 19, Local Earned Income Credit.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=26",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # § 10-704(c)(1)(i) and (d)(1)(i) base the state and county credits
        # on "the earned income credit allowable for the taxable year under
        # § 32 of the Internal Revenue Code or that would have been allowable
        # but for the limitation under § 32(m)", and (c)(2)(iii) computes the
        # refund the same way. Instruction 18: "If you or your spouse do not
        # possess a valid SSN but are otherwise eligible for the federal
        # credit and are filing your Maryland return using an ITIN, you may
        # claim the state earned income credit by calculating the federal
        # earned income credit disregarding the SSN requirement."
        federal = federal_eitc_tax_unit(tax_unit, period)
        return federal("eitc", period)

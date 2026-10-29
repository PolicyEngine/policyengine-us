from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import federal_eitc_tax_unit


class md_eitc_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Maryland EITC qualifying children"
    documentation = "Qualifying children Maryland's earned income credits take into account. From 2020 a child with an ITIN or any Social Security number counts."
    definition_period = YEAR
    reference = (
        # (c)(1)(i), (c)(2)(iii), (c)(3)(i)2 and (d) compute the § 32 credit
        # without regard to the limitation under § 32(m).
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",
        # IRC 32(c)(3)(D) requires a qualifying child's taxpayer
        # identification number, which 32(m) limits to an SSN.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_D",
        "https://www.law.cornell.edu/uscode/text/26/32#m",
        # 2025 Resident Booklet, Instruction 5: "A valid SSN or ITIN is
        # required for any claim or exemption for a dependent."
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=11",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.eitc
        federal = federal_eitc_tax_unit(tax_unit, period, p.itin_eligible)
        return federal("eitc_child_count", period)

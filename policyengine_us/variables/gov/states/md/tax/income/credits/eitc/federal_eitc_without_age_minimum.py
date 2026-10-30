from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import eitc_section_911_eligible


class federal_eitc_without_age_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without age minimum"
    unit = USD
    documentation = "The federal EITC with the minimum age condition ignored; the maximum age condition and the bar on section 911 claimants still apply."
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_C",
        # 2025 Maryland Resident Booklet, Instruction 18.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=22",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Per Md. Code Tax-Gen. § 10-704(c)(3), childless filers claim the
        # state EITC as if the federal § 32 minimum-age requirement did not
        # apply. Recompose the federal EITC without the minimum age; the
        # maximum age in § 32(c)(1)(A)(ii)(II) and other federal § 32 rules
        # (investment income, section 911) still apply. Section 10-704(c)(3)(i)
        # also waives the § 32(m) SSN definition, which this formula does not
        # yet model: it still requires an SSN.
        person = tax_unit.members
        has_child = tax_unit("eitc_child_count", period) > 0
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        below_max_age = person("age", period) <= max_age
        meets_max_age = has_child | tax_unit.any(below_max_age & is_filer_or_spouse)
        phased_in = tax_unit("eitc_phased_in", period)
        maximum = tax_unit("eitc_maximum", period)
        reduction = tax_unit("eitc_reduction", period)
        investment_eligible = tax_unit("eitc_investment_income_eligible", period)
        filer_has_ssn = tax_unit("filer_meets_eitc_identification_requirements", period)
        # § 32(c)(1)(C): no credit for an individual who claims the benefits
        # of section 911. The 2025 Resident Booklet (Instruction 18) waives the
        # minimum age only for a filer who is "otherwise eligible for the
        # federal credit for those without a qualifying child".
        section_911_eligible = eitc_section_911_eligible(tax_unit, period)
        return (
            min_(phased_in, max_(0, maximum - reduction))
            * investment_eligible
            * filer_has_ssn
            * section_911_eligible
            * meets_max_age
        )

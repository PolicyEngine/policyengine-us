from policyengine_us.model_api import *


class md_poverty_line_credit_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland poverty line credit earned income"
    documentation = (
        "Earned income under IRC section 32(c)(2) of the filers who can take "
        "the Maryland poverty line credit: every filer, unless a filer can be "
        "claimed as a dependent on another return, in which case only the "
        "filers who cannot be claimed."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-709&enactments=false",
        "https://www.law.cornell.edu/uscode/text/26/32#c_2",
        # PDF pages 12-13, 23: filing status 6, Instruction 8 and the poverty
        # level credit.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
    )

    def formula(tax_unit, period, parameters):
        # § 10-709(a)(3)(iii) excludes a taxpayer "claimed as an exemption on
        # another individual's tax return", and the instructions bar filing
        # status 6 (a person who can be claimed as a dependent). A married
        # person who can be claimed files a separate Maryland return, so on a
        # federal joint return only the spouse who cannot be claimed can take
        # the credit, on that spouse's own earned income.
        person = tax_unit.members
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        sources = [
            "employment_income",
            "self_employment_income",
            "sstb_self_employment_income",
            "farm_operations_income",
            "partnership_self_employment_net_earnings",
        ]
        gross = add(person, period, sources)
        self_employment_tax_ald = person("self_employment_tax_ald_person", period)
        own_earned_income = max_(0, gross - self_employment_tax_ald)
        can_claim = person("is_tax_unit_head_or_spouse", period) & ~person(
            "claimed_as_dependent_on_another_return", period
        )
        return where(
            filer_is_dependent,
            tax_unit.sum(own_earned_income * can_claim),
            tax_unit("eitc_earned_income", period),
        )

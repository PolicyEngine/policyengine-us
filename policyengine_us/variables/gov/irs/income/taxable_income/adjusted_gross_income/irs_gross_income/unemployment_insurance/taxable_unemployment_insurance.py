from policyengine_us.model_api import *


class taxable_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "Taxable unemployment compensation"
    unit = USD
    documentation = (
        "Unemployment compensation a person received less the part IRC 85(c) "
        "excludes from gross income on the return it is reported on: the tax "
        "unit's return for the head and spouse, the dependent's own return "
        "for a dependent."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/85",
        # 2020 Instructions for Form 1040 (rev. 4-2021), Unemployment
        # Compensation Exclusion Worksheet, Schedule 1, line 8.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2020.pdf#page=88",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.unemployment_compensation.exemption
        received = person("unemployment_compensation", period)
        # IRC 85(c)(1) tests the adjusted gross income of the return the
        # compensation is on. Members who are not dependents are on the tax
        # unit's return, as in irs_gross_income.
        filing_status = person.tax_unit("filing_status", period)
        filer_agi = person.tax_unit("taxable_uc_agi", period)
        filer_eligible = filer_agi < p.cutoff[filing_status]
        # A dependent's compensation is on the dependent's own return, filed
        # separately if they live with their spouse and single otherwise
        # (a dependent can't file jointly or claim dependents).
        lives_with_spouse = person("dependent_lives_with_spouse", period)
        dependent_cutoff = where(
            lives_with_spouse, p.cutoff["SEPARATE"], p.cutoff["SINGLE"]
        )
        dependent_agi = person("dependent_taxable_uc_agi", period)
        dependent_eligible = dependent_agi < dependent_cutoff
        is_dependent = person("is_tax_unit_dependent", period)
        eligible = where(is_dependent, dependent_eligible, filer_eligible)
        # Each person excludes up to the amount of the compensation they
        # received, so on a joint return each spouse does (worksheet lines 8
        # and 9). A net repayment is not excluded.
        excluded = eligible * min_(max_(0, received), p.amount)
        return received - excluded

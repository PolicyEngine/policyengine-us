from policyengine_us.model_api import *


class deductible_mortgage_insurance_premiums_indiv(Variable):
    value_type = float
    entity = Person
    label = "Deductible mortgage insurance premiums allocated to each filer"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Allocates the tax unit's qualified mortgage insurance premium "
        "deduction after its AGI phase-out to the head and spouse, in "
        "proportion to their reported premiums on both residences. If "
        "neither filer reports premiums, splits the deduction equally "
        "between filers. Allocations sum to the tax-unit deduction."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/163#h_3_E"

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        reported_premiums = head_or_spouse * add(
            person,
            period,
            [
                "mortgage_insurance_premiums",
                "second_residence_mortgage_insurance_premiums",
            ],
        )
        total_reported_premiums = person.tax_unit.sum(reported_premiums)
        share = np.zeros_like(total_reported_premiums)
        reported_mask = total_reported_premiums > 0
        share[reported_mask] = (
            reported_premiums[reported_mask] / total_reported_premiums[reported_mask]
        )
        filer_count = person.tax_unit.sum(head_or_spouse)
        equal_share = np.zeros_like(total_reported_premiums)
        filer_mask = filer_count > 0
        equal_share[filer_mask] = head_or_spouse[filer_mask] / filer_count[filer_mask]
        share = where(total_reported_premiums > 0, share, equal_share)
        return person.tax_unit("deductible_mortgage_insurance_premiums", period) * share

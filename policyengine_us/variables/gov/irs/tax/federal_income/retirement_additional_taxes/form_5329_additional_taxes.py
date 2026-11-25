from policyengine_us.model_api import *


class form_5329_additional_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Additional taxes on qualified plans, IRAs and annuities computed from detailed inputs"
    documentation = (
        "Early distribution tax (Form 5329 Part I) and excise tax on missed "
        "required minimum distributions (Part IX), for the head and spouse. "
        "Schedule 2 line 8. Computed from detailed inputs; callers that "
        "supply qualified_retirement_penalty directly should leave these "
        "inputs empty so the tax is not counted twice."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/instructions/i5329",
        "https://www.irs.gov/pub/irs-pdf/f1040s2.pdf",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            ["early_distribution_additional_tax", "missed_rmd_excise_tax"],
        )

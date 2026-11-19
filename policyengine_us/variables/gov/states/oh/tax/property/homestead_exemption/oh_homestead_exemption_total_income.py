from policyengine_us.model_api import *


class oh_homestead_exemption_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio homestead exemption total income"
    documentation = (
        "R.C. 323.151(C) defines total income as the owner's and spouse's "
        "modified adjusted gross income under R.C. 5747.01 for the year "
        "before the year of application. PolicyEngine books the homestead "
        "exemption to that income year, so this reads Ohio modified adjusted "
        "gross income for the same year as the exemption."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-323.151",
        "https://codes.ohio.gov/assets/laws/revised-code/authenticated/3/323/323.151/10-27-2023/323.151-10-27-2023.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        # R.C. 323.151(C) counts the income of the year before application.
        # The model books the relief to that income year, so it reads the
        # same year's Ohio modified AGI.
        return tax_unit("oh_modified_agi", period)

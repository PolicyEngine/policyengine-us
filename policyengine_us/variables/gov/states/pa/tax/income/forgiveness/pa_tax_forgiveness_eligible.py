from policyengine_us.model_api import *


class pa_tax_forgiveness_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible to claim Pennsylvania tax forgiveness"
    documentation = (
        "Whether this head or spouse can claim Pennsylvania tax forgiveness. "
        "A filer who can be claimed as a dependent on another return cannot "
        "claim forgiveness under Tax Reform Code section 301(c.2)."
    )
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = (
        # Tax Reform Code of 1971, section 301(c.2): a "Claimant" "is not a
        # dependent of another taxpayer for purposes of section 151".
        "https://www.legis.state.pa.us/WU01/LI/LI/US/PDF/1971/0/0002..PDF#page=112",
        # 2025 PA-40 Schedule SP instructions.
        # PDF pages 3-5
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40sp.pdf#page=3",
        "https://www.pa.gov/agencies/revenue/forms-and-publications/pa-personal-income-tax-guide/tax-forgiveness",
    )

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        claimable = person("claimable_as_dependent_on_another_return", period)
        # The instructions say a dependent child can qualify through a parent.
        # Sections 301(c.2) and 304 exclude dependents without that exception.
        return head_or_spouse & ~claimable

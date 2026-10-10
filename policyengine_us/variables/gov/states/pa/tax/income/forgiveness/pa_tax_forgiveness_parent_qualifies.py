from policyengine_us.model_api import *


class pa_tax_forgiveness_parent_qualifies(Variable):
    value_type = bool
    entity = Person
    label = "Parent who claims this person as a dependent qualifies for Pennsylvania tax forgiveness"
    documentation = (
        "Whether the parent, grandparent or foster parent who claims this "
        "person as a dependent qualifies for Pennsylvania Tax Forgiveness and "
        "lists this person on their PA-40 Schedule SP (Schedule SP eligibility "
        "questions, lines 1 and 2). Read only for a person who can be claimed "
        "as a dependent on another return."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        # 2025 PA-40 Schedule SP instructions, eligibility questions.
        # PDF pages 3-4
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40sp.pdf#page=3",
        "https://www.pa.gov/agencies/revenue/forms-and-publications/pa-personal-income-tax-guide/tax-forgiveness",
    )

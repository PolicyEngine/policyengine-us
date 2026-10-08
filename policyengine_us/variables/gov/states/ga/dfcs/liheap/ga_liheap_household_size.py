from policyengine_us.model_api import *


class ga_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Georgia LIHEAP household size"
    defined_for = StateCode.GA
    # Pages 51-52 exclude nonqualified members from size; page 62 counts income.
    reference = "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=51"

    # Lawful immigrants count in the size; undocumented members do not
    # (manual 101.2 page 3, 1100.3 page 50, 1100.5 a page 51: "Do not include
    # the undocumented adults in the household size"). The manual conflicts
    # with itself: 1100.14 (page 57) lists "Applicants where ALL household
    # members are non-U.S. citizens" as ineligible, and the glossary (page 76)
    # counts non-citizen members' income "but do not include in the household
    # size". This follows the specific eligibility sections.
    # The SPM unit approximates the economic unit purchasing energy together.
    # Existing inputs do not identify all roomers, boarders, foster-child
    # elections, or excluded group-quarter arrangements.
    adds = ["is_citizen_or_legal_immigrant"]

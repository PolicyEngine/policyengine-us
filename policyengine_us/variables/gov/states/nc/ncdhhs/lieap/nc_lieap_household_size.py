from policyengine_us.model_api import *


class nc_lieap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "North Carolina LIEAP eligible household size"
    documentation = (
        "Counts the SPM unit members who are citizens or hold a qualified "
        "immigration status. SPM units approximate the residents who share "
        "heat (EP-150.01). EP-175.01 requires at least one citizen or eligible "
        "alien, and the EP-175.05 chart lists permanent residents, refugees, "
        "asylees, parolees, conditional entrants and aliens whose deportation "
        "is withheld as eligible for Energy Programs and states no waiting "
        "period. EP-300.10 excludes ineligible aliens from the size and specifies "
        "their income treatment. The qualified-status variable cannot resolve "
        "every EP-175 document or PRUCOL category, qualified-but-ineligible "
        "members, or the optional inclusion of foster children, so those "
        "cases remain partial."
    )
    defined_for = StateCode.NC
    reference = (
        # EP-150.01, household composition (single-page document).
        "https://policies.ncdhhs.gov/wp-content/uploads/eps150.pdf",
        # EP-175.01 (page 1) and the EP-175.05 alien status chart (pages 4-6).
        "https://policies.ncdhhs.gov/wp-content/uploads/eps175.pdf#page=4",
        # Section 300.10 A (pages 15-16).
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=15",
    )
    # EP-175.05 (page 4) lists these statuses as eligible with no waiting period,
    # so the SNAP immigration variable, which applies SNAP's own restrictions,
    # is not used here.
    adds = ["is_citizen_or_legal_immigrant"]

from policyengine_us.model_api import *


class md_paa(Variable):
    value_type = float
    entity = Person
    label = "Maryland Public Assistance to Adults"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.09",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.04",
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/md.html",
    )

    def formula(person, period, parameters):
        # Model PAA as a prospective SSI state-supplement cascade: the
        # applicant applies for federal SSI, federal SSI is imputed under
        # federal rules, and Maryland pays the remaining gap to PAA needs.
        # COMAR 07.03.07.08 defines PAA countable income; we approximate it
        # with ssi_countable_income because PAA historically mirrors SSI's
        # $20 unearned / $65 earned exclusions. PAA-specific income details
        # (lump sums, parent contributions, irregular-income carve-outs)
        # are not tracked at the moment.
        combined_need = person("md_paa_total_cost_of_care", period)
        available_resources = add(
            person,
            period,
            ["ssi_countable_income", "md_paa_imputed_federal_ssi"],
        )
        return max_(combined_need - available_resources, 0)

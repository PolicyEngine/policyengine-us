from policyengine_us.model_api import *


class ca_marin_general_relief_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for the Marin County General Relief based on the immigration status requirements"
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=10"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.marin.general_relief
        immigration_status = person("immigration_status", period.this_year)
        immigration_status_str = immigration_status.decode_to_str()
        # The Standards require US citizenship, legal permanent residency, or
        # permanently residing in the United States under color of law (PRUCOL).
        # We do not track a PRUCOL flag at the moment, so PRUCOL is approximated
        # with the available humanitarian statuses in the qualified list.
        qualified = np.isin(immigration_status_str, p.qualified_immigration_status)
        # Section II.E ties the citizenship requirement to the General Relief
        # Applicant/Recipient, so only the head or spouse of the tax unit must
        # hold a qualifying status; a dependent's status does not make the unit
        # eligible.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        return qualified & head_or_spouse

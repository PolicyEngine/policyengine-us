from policyengine_us.model_api import *


class ca_sbd_general_relief_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for San Bernardino County General Relief"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/eae80072-cef4-49e5-b04e-a9b442290034.docx",
    )

    def formula(person, period, parameters):
        immigration_eligible = person(
            "ca_sbd_general_relief_immigration_status_eligible", period
        )
        receives_other_cash_assistance = person(
            "ca_sbd_general_relief_receives_other_cash_assistance", period
        )
        # The grant is not paid to or for any applicant or recipient who is a
        # resident of a treatment program or treatment facility. GR's
        # facility definition is broader than the SSI medical-treatment-
        # facility concept used as its proxy.
        in_treatment_facility = person(
            "ssi_lives_in_medical_treatment_facility", period
        )
        meets_linkage = person(
            "ca_sbd_general_relief_meets_linkage_requirements", period
        )
        return (
            immigration_eligible
            & ~receives_other_cash_assistance
            & ~in_treatment_facility
            & meets_linkage
        )

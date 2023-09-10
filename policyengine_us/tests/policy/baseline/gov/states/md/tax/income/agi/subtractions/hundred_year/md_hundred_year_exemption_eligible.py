- name: Ineligible
  period: 2023
  input:
    age: 100
    state_code: MD
  output:
    md_hundred_year_exemption_eligible: true

- name: Eligible
  period: 2023
  input:
    age: 99
    state_code: MD
  output:
    md_hundred_year_exemption_eligible: false

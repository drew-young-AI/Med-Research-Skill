"""
v13 Master MD updater - update reference column for newly downloaded papers
"""
import os

report_path = r'D:\project\Med Deep Research\reports\v13.0_LeadApron_DICOM_Master.md'

with open(report_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Row 04: Add PDF link (EuropePMC PMC4799263)
# Current: [Web (Europe PMC)](...) \| [Web (Springer)](...)
old_04 = '[Web (Europe PMC)](https://europepmc.org/article/MED/26842670) \\| [Web (Springer)](https://doi.org/10.1007/s00540-016-2140-2)'
new_04 = '[PDF](../papers/Evaluation%20of%20lead%20aprons%20and%20their%20maintenance%20and%20management%20at%20our%20hospital.pdf) \\| [Web (Europe PMC)](https://europepmc.org/article/MED/26842670) \\| [Web (Springer)](https://doi.org/10.1007/s00540-016-2140-2)'
content = content.replace(old_04, new_04)

# Row 01: Mark with note (2026 Springer only, no preprint exists)
old_01 = '[Web (Springer)](https://doi.org/10.1007/s12194-026-01086-2)'
new_01 = '[Web (Springer)](https://doi.org/10.1007/s12194-026-01086-2) *(Paywall; no preprint confirmed)*'
content = content.replace(old_01, new_01)

# Row 06: Mark with note (2026 IOP HYBRID OA, no preprint)
old_06 = '[PENDING](https://doi.org/10.1088/1361-6498/ae7122)'
new_06 = '[Web (IOP)](https://doi.org/10.1088/1361-6498/ae7122) *(Hybrid OA CC-BY-NC-ND; PMID:42167284; no preprint confirmed)*'
content = content.replace(old_06, new_06)

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Report updated successfully.')
print(f'Row 04: PDF link added.')
print(f'Row 01: Paywall note added.')
print(f'Row 06: Hybrid OA + PMID noted.')

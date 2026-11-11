# Post-quantum inventory

```
references read:
  nist-ir-8547:                version and date read
  fips-203/204/205:            date read
  ietf-tls-hybrid:             draft or rfc name and date

track 1: key exchange (confidentiality)
  endpoint            peer      library+version   config file:line   hybrid allowed   blocker
  ----------------------------------------------------------------------------------------------

track 2: signatures (authentication)
  artefact            verifier  algorithm         file:line          dual-verify      blocker
  ----------------------------------------------------------------------------------------------

data with long confidentiality requirement:
  dataset             retention        captured when        priority basis

agility
  where the group or suite is selected:
  where signature verification happens:
  downgrade detectable: yes / no / unknown

blockers, ordered
  1.                                                        confirmed / claimed / inferred

not determined
  -                                                         question for: role

mutation or test evidence (only if the project already has a harness)
```

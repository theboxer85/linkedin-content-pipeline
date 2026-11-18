---
id: 2026-12-03-gcp-dns-return-path-thu
publish_at: "2026-12-03 07:45"
day: thursday
pillar: continuity
scenario: gcp-dns-return-path
pair: 2026-11-30-gcp-dns-return-path-mon
format: image
alt_text: "The same GCP-to-on-prem design, now with the edge firewall's BGP import list accepting 35.199.192.0/19 so DNS replies return and apps resolve their databases."
document_title: ""
test_variable: "baseline: plain answer before technical detail"
source_issue: 0
status: scheduled
---
Monday's puzzle: a GCP migration where nothing in the cloud could resolve on-prem hostnames, and production apps lost their databases.

The answer was a single prefix. When Cloud DNS forwards a query on-prem, it doesn't come from your GCP subnets. It comes from 35.199.192.0/19, a range Google owns. The queries made it on-prem. The replies had no way back.

The on-prem edge firewall's BGP import list didn't include that range, so there was no return route to GCP. The firewall showed TCP resets the whole time. Once the import list was amended to accept 35.199.192.0/19, resolution started working.

Before a hybrid migration, ask your team one thing. Does anyone know every source range the cloud provider uses on your behalf, and has the firewall team seen that list?

Outages like this usually live in the handoff between the cloud, network and DNS teams.

Has a cloud provider's own IP range ever caught your team off guard?

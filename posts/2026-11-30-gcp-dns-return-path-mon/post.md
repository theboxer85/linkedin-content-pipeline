---
id: 2026-11-30-gcp-dns-return-path-mon
publish_at: "2026-11-30 07:45"
day: monday
pillar: continuity
scenario: gcp-dns-return-path
pair: 2026-12-03-gcp-dns-return-path-thu
format: image
alt_text: "Diagram of a GCP VPC forwarding DNS queries over HA VPN to on-prem Infoblox, with the reply path failing and apps unable to reach their databases."
document_title: ""
test_variable: "baseline: consequence-first hook"
source_issue: 0
status: scheduled
---
A recent move to GCP went smoothly, except for one thing. Nothing in GCP could resolve a single on-prem hostname. Production apps couldn't reach their back-end databases, and users saw it. That's an outage.

On paper, everything was right. HA VPN tunnels up, BGP sharing a default route from on-prem to GCP, and Cloud DNS forwarding on-prem zones to Infoblox. Infoblox was reachable from GCP. The DNS team swore nothing was blocked.

Queries still timed out.

So what was the problem? What would you check first? I'll share what we found Thursday.

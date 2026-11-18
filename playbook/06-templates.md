# 6. Templates

## Monday: the challenge

1. **Hook (lines 1–2):** what broke, then what it cost the business, in plain words. If users saw it, say so.
2. **"On paper, everything was right":** what was in place, with specific technology, and what had already been ruled out.
3. **Tension line:** one short sentence on its own line, the symptom that shouldn't be happening.
4. **Close:** a real question readers can answer ("What would you check first?") and a promise of Thursday's answer. Never give the fix.

Set the scenario at Contoso, Fabrikam or Northwind Traders, or name no company at all.

### Reference example

```
A recent move to GCP went smoothly, except for one thing. Nothing in GCP could resolve a single on-prem hostname. Production apps couldn't reach their back-end databases, and users saw it. That's an outage.

On paper, everything was right. HA VPN tunnels up, BGP sharing a default route from on-prem to GCP, and Cloud DNS forwarding on-prem zones to Infoblox. Infoblox was reachable from GCP. The DNS team swore nothing was blocked.

Queries still timed out.

So what was the problem? What would you check first? I'll share what we found Thursday.
```

## Thursday: the resolution

1. **Recap (line 1):** "Monday's puzzle:" followed by the problem and its business impact in one sentence. Must make sense to someone who missed Monday.
2. **Plain answer first:** one sentence a director understands ("The answer was a single prefix."), then the technical reason.
3. **The fix:** what changed, kept short, with the evidence that confirmed it (logs, resets, counters).
4. **The leader's question:** "Before a [kind of project], ask your team one thing." A question they can take into their next meeting.
5. **The lesson:** one line, an observation, never a lecture.
6. **Reader question:** easy to answer from experience.

### Reference example

```
Monday's puzzle: a GCP migration where nothing in the cloud could resolve on-prem hostnames, and production apps lost their databases.

The answer was a single prefix. When Cloud DNS forwards a query on-prem, it doesn't come from your GCP subnets. It comes from 35.199.192.0/19, a range Google owns. The queries made it on-prem. The replies had no way back.

The on-prem edge firewall's BGP import list didn't include that range, so there was no return route to GCP. The firewall showed TCP resets the whole time. Once the import list was amended to accept 35.199.192.0/19, resolution started working.

Before a hybrid migration, ask your team one thing. Does anyone know every source range the cloud provider uses on your behalf, and has the firewall team seen that list?

Outages like this usually live in the handoff between the cloud, network and DNS teams.

Has a cloud provider's own IP range ever caught your team off guard?
```

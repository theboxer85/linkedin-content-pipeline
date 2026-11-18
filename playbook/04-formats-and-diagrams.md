# 4. Formats and diagrams

Every post pairs text with a diagram. Monday shows the problem design, Thursday shows the fix.

| Day | Default format (`format:` in front matter) | What the visual shows |
| --- | --- | --- |
| Monday | `image`: text + one diagram | The broken or risky design. Never reveal the fix. |
| Thursday | `image`, or `document` for a 4–6 page carousel | The fixed design, or a walkthrough of the resolution |

## Diagram rules

- Each post folder holds `diagram.drawio` (uncompressed draw.io XML). The pipeline renders it to `diagram.png` (format `image`) or `carousel.pdf` (format `document`, one draw.io page per carousel page).
- Portrait 4:5 canvas: 1080 × 1350 for every page. The first shape on every page is a white background rectangle at x=0, y=0, 1080 × 1350, with no border (`strokeColor=none`). It keeps the export at full canvas size. Keep everything else inside it with at least 40px of margin.
- Consistent style every time:
  - Background white. Title text 40px bold, dark gray `#1F2937`, top-left.
  - Cloud boundary: rounded rectangle, fill `#EFF6FF`, stroke `#2563EB`.
  - On-prem boundary: rounded rectangle, fill `#F3F4F6`, stroke `#4B5563`.
  - Components: white rounded rectangles, stroke `#374151`, 20px labels.
  - Working paths: solid `#16A34A` arrows. Broken or failing paths: dashed `#DC2626` arrows with a short red label.
  - Plain shapes and labels only (no vendor icon libraries), so it renders identically in CI.
- Labels use the real product names (Cloud DNS, HA VPN, Cloud Router, Infoblox), never client hostnames or client IP ranges.
- Video and polls are not used in the first 90 days.

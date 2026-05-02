# Boliglån Negotiation MCP 🇳🇴

**Stop paying too much on your mortgage.**

This MCP Server connects directly to **Finansportalen** and **Norges Bank** so you can tell Claude/Cursor:

> "My mortgage is 3.2M NOK at 5.9% in DNB..."

…and instantly get:
- Current best competitor rates
- Realistic 5-year savings calculation (including rate path forecasts)
- A strong, professional negotiation email ready to send to your bank advisor
- "Switch bank" recommendation if that's better

### Why this exists
Norwegian banks are known for "snik-økning" — quietly raising your rate over time. Most people never notice. This tool makes it easy (and data-driven) to fight back.

---

## Installation

### Requirements
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Via uvx (recommended — no install needed)
```bash
uvx boliglan-mcp
```

### Via pip
```bash
pip install boliglan-mcp
```

### From source
```bash
git clone https://github.com/jakobkoding2/boligl-n-mcp.git
cd boligl-n-mcp
pip install -e .
```

---

## Claude Desktop configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or the equivalent on your platform:

```json
{
  "mcpServers": {
    "boliglan": {
      "command": "uvx",
      "args": ["boliglan-mcp"]
    }
  }
}
```

Or if installed via pip:
```json
{
  "mcpServers": {
    "boliglan": {
      "command": "boliglan-mcp"
    }
  }
}
```

Restart Claude Desktop after saving.

---

## Cursor / Windsurf / VS Code

Add to your MCP settings file:

```json
{
  "boliglan": {
    "command": "uvx",
    "args": ["boliglan-mcp"]
  }
}
```

---

## Usage

Once connected, you can talk to Claude naturally:

> "Analyser boliglånet mitt. Jeg har 3.2M NOK hos DNB til 5.9 %."

> "Hent beste boliglånsrenter for 4M NOK med 65 % belåning."

> "Hva er Norges Banks rentebane?"

> "Generer en forhandlingsepost til Nordea. Jeg heter Kari Olsen, har 2.8M i lån til 6.1 %."

---

## Tools

| Verktøy | Beskrivelse |
|---------|-------------|
| `analyser_boliglan` | **Hovedverktøy.** Full analyse: renter + besparelser + forhandlingsepost i én operasjon. |
| `hent_boliglansrenter` | Hent sanntidsrenter fra Finansportalen, sortert fra lavest til høyest. |
| `hent_rentebane` | Norges Banks styringsrente og kvartalsvise rentebane. |
| `beregn_besparelser` | Beregn månedlig og total besparelse ved rentereduksjon. |
| `generer_forhandlingsepost` | Generer profesjonell norsk forhandlingsepost til din rådgiver. |
| `generer_bankbytte_epost` | Generer epost til ny bank for refinansiering/bankbytte. |

---

## Data sources

- **[Finansportalen](https://www.finansportalen.no)** — Norwegian Consumer Authority's official loan comparison portal. Live API with fallback to curated data.
- **[Norges Bank](https://data.norges-bank.no)** — Central bank open data API (SDMX-JSON) for policy rate and quarterly rate path forecasts.

---

## Features
- Real-time boliglån rates via Finansportalen
- Norges Bank rentebane integration
- Smart savings calculator (monthly / 1 / 3 / 5 years / full term)
- High-converting Norwegian negotiation emails
- Supports both forhandling and full bank switch scenarios
- Works natively with Claude Desktop, Cursor, Windsurf etc.
- Graceful fallback if APIs are temporarily unavailable

**Made for Norwegian homeowners who refuse to overpay.**

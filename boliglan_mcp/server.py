"""Boliglån Negotiation MCP Server – entry point."""

import asyncio

from mcp.server.fastmcp import FastMCP

from .calculator import calculate_savings
from .email_generator import generate_bank_switch_email, generate_negotiation_email
from .finansportalen import fetch_rates
from .norges_bank import fetch_policy_rate, fetch_rate_forecast

mcp = FastMCP(
    "Boliglån Forhandler 🇳🇴",
    instructions=(
        "Du hjelper norske boligeiere med å forhandle ned renten på boliglånet. "
        "Bruk verktøyene til å hente sanntidsrenter, beregne besparelser og generere "
        "profesjonelle forhandlingse-poster."
    ),
)


@mcp.tool()
async def hent_boliglansrenter(
    lanebelop: int,
    belaning: float = 60.0,
) -> str:
    """
    Hent gjeldende boliglånsrenter fra Finansportalen, sortert fra lavest til høyest.

    Args:
        lanebelop: Lånebeløp i NOK (f.eks. 3200000).
        belaning: Belåningsgrad i prosent (f.eks. 60 for 60 %). Standard: 60.
    """
    rates = await fetch_rates(lanebelop, belaning)
    if not rates:
        return "Kunne ikke hente renter. Sjekk internettforbindelsen og prøv igjen."

    rates.sort(key=lambda r: r["effective_rate"])

    source_note = ""
    if rates and rates[0].get("source") == "fallback":
        source_note = "\n> ⚠️ *Viser estimerte renter – live-data fra Finansportalen er midlertidig utilgjengelig.*\n"

    lines = [
        f"## Boliglånsrenter – {lanebelop:,} NOK, {belaning:.0f} % belåningsgrad",
        source_note,
        "| Bank | Nom. rente | Eff. rente |",
        "|------|-----------|-----------|",
    ]
    for r in rates[:15]:
        lines.append(f"| {r['bank']} | {r['nominal_rate']:.2f} % | {r['effective_rate']:.2f} % |")

    lines.append(f"\n*{len(rates)} produkter funnet. Sorter på effektiv rente.*")
    return "\n".join(lines)


@mcp.tool()
async def hent_rentebane() -> str:
    """
    Hent Norges Banks styringsrente og rentebane (prognose for fremtidige renter).
    Nyttig for å vurdere om det lønner seg med fastrente.
    """
    current_rate, forecast = await asyncio.gather(
        fetch_policy_rate(),
        fetch_rate_forecast(),
    )

    lines = [
        "## Norges Banks Rentebane",
        f"\n**Gjeldende styringsrente: {current_rate:.2f} %**\n",
        "### Prognose (kvartal):",
    ]
    for period, rate in sorted(forecast.items()):
        lines.append(f"- {period}: {rate:.2f} %")

    lines.append("\n*Kilde: Norges Bank SDMX-JSON API*")
    return "\n".join(lines)


@mcp.tool()
async def beregn_besparelser(
    lanebelop: int,
    gjeldende_rente: float,
    beste_rente: float,
    tid_ar: int = 5,
    gjenvaerende_loptid_ar: int = 25,
) -> str:
    """
    Beregn potensiell besparelse ved å forhandle ned boliglånsrenten.

    Args:
        lanebelop: Restgjeld i NOK (f.eks. 3200000).
        gjeldende_rente: Nåværende rente i prosent (f.eks. 5.9).
        beste_rente: Beste tilgjengelige rente i prosent (f.eks. 5.2).
        tid_ar: Tidshorisont for total-beregning i år. Standard: 5.
        gjenvaerende_loptid_ar: Resterende løpetid på lånet i år. Standard: 25.
    """
    s = calculate_savings(lanebelop, gjeldende_rente, beste_rente, tid_ar, gjenvaerende_loptid_ar)

    lines = [
        "## Besparelseskalkulator",
        f"\n**Lånebeløp:** {lanebelop:,} NOK",
        f"**Nåværende rente:** {gjeldende_rente:.2f} %",
        f"**Beste tilgjengelige rente:** {beste_rente:.2f} %",
        f"**Rentedifferanse:** {s['rate_diff']:.2f} prosentpoeng\n",
        "### Månedlig betaling:",
        f"- Nå: {s['current_monthly']:,} NOK",
        f"- Med ny rente: {s['new_monthly']:,} NOK\n",
        "### Besparelser:",
        f"- **Per måned:** {s['monthly']:,} NOK",
        f"- **Per år:** {s['yearly']:,} NOK",
        f"- **Over {tid_ar} år:** {s['total']:,} NOK",
        f"- **Total rentesparing (hele løpetiden):** {s['total_interest_savings']:,} NOK",
    ]
    return "\n".join(lines)


@mcp.tool()
async def generer_forhandlingsepost(
    ditt_navn: str,
    din_bank: str,
    lanesaldo: int,
    gjeldende_rente: float,
    beste_konkurrentrente: float,
    beste_konkurrent_bank: str,
    eiendomsverdi: int = 0,
    inkluder_bytte_advarsel: bool = True,
) -> str:
    """
    Generer en profesjonell norsk forhandlingsepost til din bankrådgiver.

    Args:
        ditt_navn: Ditt fulle navn.
        din_bank: Navn på din nåværende bank (f.eks. "DNB").
        lanesaldo: Restgjeld på lånet i NOK.
        gjeldende_rente: Din nåværende rente i prosent.
        beste_konkurrentrente: Beste rente fra en konkurrerende bank.
        beste_konkurrent_bank: Navn på banken med den beste renten.
        eiendomsverdi: Boligens verdi i NOK (brukes til belåningsgrad, valgfritt).
        inkluder_bytte_advarsel: Inkluder en advarsel om mulig bankbytte. Standard: True.
    """
    ltv = (lanesaldo / eiendomsverdi * 100) if eiendomsverdi > 0 else None
    savings = calculate_savings(lanesaldo, gjeldende_rente, beste_konkurrentrente)

    return generate_negotiation_email(
        navn=ditt_navn,
        bank=din_bank,
        lanesaldo=lanesaldo,
        gjeldende_rente=gjeldende_rente,
        beste_rente=beste_konkurrentrente,
        beste_bank=beste_konkurrent_bank,
        ltv=ltv,
        savings=savings,
        inkluder_bytte_advarsel=inkluder_bytte_advarsel,
    )


@mcp.tool()
async def generer_bankbytte_epost(
    ditt_navn: str,
    naavaerende_bank: str,
    ny_bank: str,
    lanesaldo: int,
    gjeldende_rente: float,
    ny_rente: float,
) -> str:
    """
    Generer epost til en ny bank for å be om tilbud på refinansiering.
    Bruk denne når du ønsker å bytte bank i stedet for å forhandle.

    Args:
        ditt_navn: Ditt fulle navn.
        naavaerende_bank: Navn på din nåværende bank.
        ny_bank: Navn på banken du vil bytte til.
        lanesaldo: Restgjeld i NOK.
        gjeldende_rente: Din nåværende rente i prosent.
        ny_rente: Den annonserte renten i den nye banken.
    """
    savings = calculate_savings(lanesaldo, gjeldende_rente, ny_rente)
    return generate_bank_switch_email(
        navn=ditt_navn,
        current_bank=naavaerende_bank,
        new_bank=ny_bank,
        lanesaldo=lanesaldo,
        gjeldende_rente=gjeldende_rente,
        ny_rente=ny_rente,
        savings=savings,
    )


@mcp.tool()
async def analyser_boliglan(
    din_bank: str,
    gjeldende_rente: float,
    lanebelop: int,
    ditt_navn: str = "Kunde",
    belaning: float = 60.0,
    eiendomsverdi: int = 0,
) -> str:
    """
    Komplett boliglånsanalyse: sanntidsrenter, besparelsesberegning og forhandlingsepost – alt i én operasjon.

    Args:
        din_bank: Din nåværende bank (f.eks. "DNB", "Nordea", "SpareBank 1").
        gjeldende_rente: Din nåværende rente i prosent (f.eks. 5.9).
        lanebelop: Restgjeld på lånet i NOK (f.eks. 3200000).
        ditt_navn: Ditt navn for forhandlingseposten. Standard: "Kunde".
        belaning: Belåningsgrad i prosent. Standard: 60.
        eiendomsverdi: Boligens markedsverdi i NOK (valgfritt).
    """
    rates, current_policy_rate = await asyncio.gather(
        fetch_rates(lanebelop, belaning),
        fetch_policy_rate(),
    )

    lines = [
        f"# Boliglånsanalyse",
        f"\n**Din bank:** {din_bank}",
        f"**Nåværende rente:** {gjeldende_rente:.2f} %",
        f"**Lånebeløp:** {lanebelop:,} NOK",
        f"**Norges Banks styringsrente:** {current_policy_rate:.2f} %",
    ]

    if not rates:
        lines.append("\n⚠️ Kunne ikke hente sanntidsrenter fra Finansportalen. Prøv igjen.")
        return "\n".join(lines)

    source_note = ""
    if rates[0].get("source") == "fallback":
        source_note = "\n> ⚠️ *Estimerte renter – live-data midlertidig utilgjengelig.*\n"

    rates.sort(key=lambda r: r["effective_rate"])

    # Find best external competitor
    best_external = next(
        (r for r in rates if din_bank.lower() not in r["bank"].lower()),
        rates[0],
    )
    best_rate = best_external["effective_rate"]
    rate_diff = gjeldende_rente - best_rate

    # Rate table
    lines += [
        f"\n{source_note}",
        "## Beste tilgjengelige renter\n",
        "| Bank | Eff. rente | |",
        "|------|-----------|---|",
    ]
    for r in rates[:8]:
        is_current = din_bank.lower() in r["bank"].lower()
        tag = "← din bank" if is_current else ""
        is_best = r["bank"] == best_external["bank"]
        best_tag = "🏆 beste" if is_best else ""
        note = best_tag or tag
        lines.append(f"| {r['bank']} | {r['effective_rate']:.2f} % | {note} |")

    # Savings
    savings = calculate_savings(lanebelop, gjeldende_rente, best_rate)
    lines += [
        f"\n## Besparelsespotensial\n",
        f"Beste konkurrentrente: **{best_external['bank']} – {best_rate:.2f} %**\n",
        f"| Periode | Besparelse |",
        f"|---------|-----------|",
        f"| Per måned | **{savings['monthly']:,} NOK** |",
        f"| Per år | **{savings['yearly']:,} NOK** |",
        f"| Over 5 år | **{savings['total']:,} NOK** |",
        f"| Hele løpetiden | **{savings['total_interest_savings']:,} NOK** |",
    ]

    # Recommendation
    lines.append("\n## Anbefaling\n")
    if rate_diff > 0.5:
        lines.append(
            f"🚨 **Handle nå.** Du betaler {rate_diff:.2f} prosentpoeng for mye. "
            f"Det koster deg {savings['monthly']:,} NOK per måned."
        )
    elif rate_diff > 0.1:
        lines.append(
            f"✅ Det er rom for å forhandle. Send e-posten under til din rådgiver."
        )
    elif rate_diff > 0:
        lines.append(
            f"ℹ️ Liten differanse ({rate_diff:.2f} pp), men det er alltid verdt å spørre."
        )
    else:
        lines.append("✅ Du har allerede en konkurransedyktig rente! Bra jobbet.")
        return "\n".join(lines)

    # Negotiation email
    ltv = (lanebelop / eiendomsverdi * 100) if eiendomsverdi > 0 else None
    email = generate_negotiation_email(
        navn=ditt_navn,
        bank=din_bank,
        lanesaldo=lanebelop,
        gjeldende_rente=gjeldende_rente,
        beste_rente=best_rate,
        beste_bank=best_external["bank"],
        ltv=ltv,
        savings=savings,
        inkluder_bytte_advarsel=True,
    )

    lines += ["\n---\n", "## Forhandlingsepost – klar til å sende\n", f"```\n{email}\n```"]

    return "\n".join(lines)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

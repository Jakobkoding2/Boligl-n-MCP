"""Norwegian mortgage negotiation email generator."""


def generate_negotiation_email(
    navn: str,
    bank: str,
    lanesaldo: int,
    gjeldende_rente: float,
    beste_rente: float,
    beste_bank: str,
    ltv: float | None,
    savings: dict,
    inkluder_bytte_advarsel: bool = True,
) -> str:
    """Generate a high-converting Norwegian mortgage negotiation email."""

    rate_diff = gjeldende_rente - beste_rente

    ltv_setning = ""
    if ltv and ltv < 85:
        ltv_setning = (
            f" Belåningsgraden på lånet er {ltv:.0f} %, noe som gir god sikkerhet for banken."
        )

    savings_setning = (
        f"Dette tilsvarer en besparelse på {savings['monthly']:,} kr per måned "
        f"– eller {savings['yearly']:,} kr per år."
    )

    bytte_avsnitt = ""
    if inkluder_bytte_advarsel and rate_diff > 0.05:
        bytte_avsnitt = (
            f"\nDersom dere ikke kan imøtekomme denne forespørselen, vil jeg se meg nødt "
            f"til å vurdere å flytte lånet til {beste_bank}, som tilbyr {beste_rente:.2f} % "
            f"effektiv rente. Jeg ønsker å bli i {bank}, men det er vanskelig å forsvare en "
            f"rentedifferanse på {rate_diff:.2f} prosentpoeng uten en god begrunnelse.\n"
        )

    email = f"""\
Emne: Forespørsel om justering av boliglånsrente – konto [DITT KONTONUMMER]

Hei,

Jeg er kunde i {bank} og har et boliglån med restgjeld på {lanesaldo:,} kr. Per i dag betaler \
jeg {gjeldende_rente:.2f} % effektiv rente på lånet.{ltv_setning}

Jeg har nylig sammenlignet renter i markedet og ser at {beste_bank} tilbyr {beste_rente:.2f} % \
effektiv rente for tilsvarende lån. {savings_setning}
{bytte_avsnitt}
Jeg ber om at dere gjennomgår betingelsene på mitt lån og kommer tilbake med et \
konkurransedyktig tilbud innen 5 virkedager.

Jeg ser frem til en positiv tilbakemelding.

Med vennlig hilsen,
{navn}
[Telefon: XXX XX XXX]
[E-post: din@epost.no]
[Fødselsdato: DD.MM.ÅÅÅÅ]
"""
    return email


def generate_bank_switch_email(
    navn: str,
    current_bank: str,
    new_bank: str,
    lanesaldo: int,
    gjeldende_rente: float,
    ny_rente: float,
    savings: dict,
) -> str:
    """Generate an email to a new bank requesting a loan transfer offer."""

    email = f"""\
Emne: Forespørsel om boliglåntilbud – refinansiering fra {current_bank}

Hei,

Jeg ønsker å innhente et tilbud på refinansiering av mitt boliglån. Per i dag har jeg et lån \
på {lanesaldo:,} kr i {current_bank} til {gjeldende_rente:.2f} % effektiv rente.

Jeg ser at {new_bank} tilbyr {ny_rente:.2f} % effektiv rente, noe som ville gitt meg en \
besparelse på {savings['monthly']:,} kr per måned.

Jeg ber om et konkret skriftlig tilbud med vilkår, etableringsgebyr og eventuell bindingstid, \
slik at jeg kan gjøre en helhetlig vurdering.

Med vennlig hilsen,
{navn}
[Telefon: XXX XX XXX]
[E-post: din@epost.no]
[Fødselsdato: DD.MM.ÅÅÅÅ]
[Nåværende bank og kontonummer: {current_bank} – konto XXX.XX.XXXXX]
"""
    return email

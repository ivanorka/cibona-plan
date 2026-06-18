from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "assets" / "cibona-logo.png"
FONT_DIRS = [
    Path.home()
    / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/"
    / "libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype",
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/opt/homebrew/share/fonts/dejavu"),
    Path("/Library/Fonts"),
]

W, H = A4
M = 18 * mm

NAVY = HexColor("#050432")
INK = HexColor("#070821")
MUTED = HexColor("#5f6778")
LINE = HexColor("#dce6f2")
SOFT = HexColor("#f4f8fd")
BLUE = HexColor("#116bc5")
CYAN = HexColor("#20d6ee")
GREEN = HexColor("#11a26c")
WHITE = HexColor("#ffffff")


def register_fonts():
    pdfmetrics.registerFont(TTFont("DejaVu", str(find_font("DejaVuSans.ttf"))))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(find_font("DejaVuSans-Bold.ttf"))))


def find_font(filename):
    for font_dir in FONT_DIRS:
        path = font_dir / filename
        if path.exists():
            return path

    matches = sorted(
        (Path.home() / ".cache/codex-runtimes").glob(
            "*/dependencies/native/libreoffice-headless/libreoffice/"
            f"LibreOfficeDev.app/Contents/Resources/fonts/truetype/{filename}"
        )
    )
    if matches:
        return matches[0]

    raise FileNotFoundError(f"Cannot find {filename}. Install DejaVu fonts to regenerate PDFs.")


def width(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)


def wrap_text(text, font, size, max_width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            test = f"{line} {word}".strip()
            if width(test, font, size) <= max_width or not line:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def draw_wrapped(c, text, x, y, max_width, font="DejaVu", size=11, leading=None, color=MUTED):
    leading = leading or size * 1.35
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap_text(text, font, size, max_width):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_bg(c, dark=False):
    c.setFillColor(HexColor("#050432") if dark else WHITE)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if dark:
        c.setFillColor(HexColor("#0b1640"))
        c.rect(W * 0.48, 0, W * 0.52, H, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#13234e"))
        circle = HexColor("#17295c")
    else:
        c.setFillColor(SOFT)
        c.rect(0, 0, W, H, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#e7eef7"))
        circle = HexColor("#edf4fb")

    c.setLineWidth(0.55)
    step = 54
    for x in range(-220, int(W) + 260, step):
        c.line(x, 0, x + 360, H)
    for x in range(-140, int(W) + 340, step):
        c.line(x, H, x + 360, 0)

    c.setStrokeColor(circle)
    c.setLineWidth(11)
    c.circle(W - 72, H - 128, 96, stroke=1, fill=0)


def draw_logo(c, x, y, size=34):
    c.setFillColor(WHITE)
    c.roundRect(x, y, size, size, 7, stroke=0, fill=1)
    c.drawImage(str(LOGO), x + 5, y + 5, size - 10, size - 10, mask="auto")


def footer(c, page_no, text="Tixety / Cibona"):
    y = 25 * mm
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(M, y + 10, W - M, y + 10)
    c.setFillColor(MUTED)
    c.setFont("DejaVu", 8.5)
    c.drawString(M, y, text)
    c.drawRightString(W - M, y, f"{page_no:02d}")


def label(c, left, right):
    c.setFont("DejaVu-Bold", 8.5)
    c.setFillColor(CYAN)
    c.drawString(M, H - 54, left.upper())
    c.setFillColor(MUTED)
    c.drawRightString(W - M, H - 54, right)


def h2(c, text, y=H - 92):
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 27)
    return draw_wrapped(c, text, M, y, W - 2 * M - 18, "DejaVu-Bold", 27, 32, INK)


def card(c, x, y, w, h, num, title, body):
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(x, y - h, w, h, 7, stroke=1, fill=1)
    c.setFillColor(NAVY)
    c.roundRect(x + 20, y - 42, 30, 30, 7, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 11)
    c.drawCentredString(x + 35, y - 32, str(num))
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 15.5)
    draw_wrapped(c, title, x + 20, y - 70, w - 40, "DejaVu-Bold", 15.5, 18, INK)
    draw_wrapped(c, body, x + 20, y - 102, w - 40, "DejaVu", 10.7, 14.5, MUTED)


def compact_card(c, x, y, w, h, num, title, body):
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(x, y - h, w, h, 7, stroke=1, fill=1)

    c.setFillColor(NAVY)
    c.roundRect(x + 16, y - 34, 24, 24, 6, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 8.8)
    c.drawCentredString(x + 28, y - 25.5, str(num))

    title_size = 12.8
    title_lines = wrap_text(title, "DejaVu-Bold", title_size, w - 32)
    title_y = y - 50
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", title_size)
    for line in title_lines:
        c.drawString(x + 16, title_y, line)
        title_y -= 15

    draw_wrapped(c, body, x + 16, title_y - 5, w - 32, "DejaVu", 9.6, 12.5, MUTED)


def note(c, text, y, blue=False):
    h = 56
    x = M
    w = W - 2 * M
    c.setFillColor(HexColor("#eaf2fb") if blue else HexColor("#eaf8f2"))
    c.roundRect(x, y - h, w, h, 7, stroke=0, fill=1)
    c.setFillColor(BLUE if blue else GREEN)
    c.roundRect(x, y - h, 4, h, 2, stroke=0, fill=1)
    draw_wrapped(c, text, x + 22, y - 25, w - 42, "DejaVu", 11.5, 16, HexColor("#20374e" if blue else "#203f33"))
    return y - h


def cover(c, d):
    draw_bg(c, dark=True)
    draw_logo(c, M, H - 85, 34)
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 13)
    c.drawString(M + 46, H - 72, d["brand"])
    c.setFillColor(CYAN)
    c.setFont("DejaVu-Bold", 8.5)
    c.drawRightString(W - M, H - 69, d["eyebrow"].upper())

    y = H - 150
    y = draw_wrapped(c, d["title"], M, y, W - 2 * M - 35, "DejaVu-Bold", d["cover_size"], d["cover_size"] * 1.06, WHITE)
    draw_wrapped(c, d["subtitle"], M, y - 20, W - 2 * M - 42, "DejaVu", 14, 19, HexColor("#e3e7f0"))

    meta_y = H - 388
    c.setStrokeColor(HexColor("#485775"))
    c.line(M, meta_y + 26, W - M, meta_y + 26)
    cols = [M, M + 170, M + 340]
    for x, (k, v) in zip(cols, d["meta"]):
        c.setFillColor(WHITE)
        c.setFont("DejaVu-Bold", 8.3)
        c.drawString(x, meta_y, k.upper())
        c.setFillColor(HexColor("#e1e6f0"))
        c.setFont("DejaVu", 11.2)
        c.drawString(x, meta_y - 20, v)

    box_x, box_y, box_w, box_h = M, 42, W - 2 * M, 154
    c.setFillColor(HexColor("#294d73"))
    c.setStrokeColor(HexColor("#6682a5"))
    c.roundRect(box_x, box_y, box_w, box_h, 8, stroke=1, fill=1)
    c.setFillColor(HexColor("#244763"))
    c.roundRect(box_x, box_y, 108, box_h, 8, stroke=0, fill=1)
    c.setFillColor(CYAN)
    c.setFont("DejaVu-Bold", 18)
    c.drawCentredString(box_x + 54, box_y + 68, "10.07.")

    cell_w = (box_w - 108) / 2
    cell_h = box_h / 2
    for i, step in enumerate(d["focus"]):
        col = i % 2
        row = 1 - i // 2
        x = box_x + 108 + col * cell_w
        y0 = box_y + row * cell_h
        c.setStrokeColor(HexColor("#53698f"))
        c.rect(x, y0, cell_w, cell_h, stroke=1, fill=0)
        c.setFillColor(WHITE)
        c.setFont("DejaVu-Bold", 9.5)
        c.drawString(x + 17, y0 + cell_h - 22, str(i + 1))
        draw_wrapped(c, step, x + 17, y0 + cell_h - 42, cell_w - 30, "DejaVu", 10.5, 14, HexColor("#f1f4f9"))
    c.showPage()


def page_goal(c, d):
    draw_bg(c)
    label(c, d["goal_label"], "01")
    y = h2(c, d["goal_title"]) - 15
    y = draw_wrapped(c, d["goal_body"], M, y, W - 2 * M - 10, "DejaVu", 13, 18, MUTED) - 20
    y = note(c, d["goal_note"], y)
    gap, cw, ch = 18, (W - 2 * M - 18) / 2, 150
    y_cards = y - 35
    for i, item in enumerate(d["goal_cards"]):
        x = M + (i % 2) * (cw + gap)
        yy = y_cards - (i // 2) * (ch + 20)
        card(c, x, yy, cw, ch, i + 1, item[0], item[1])
    footer(c, 1)
    c.showPage()


def page_phase1(c, d):
    draw_bg(c)
    label(c, d["phase1_label"], "02")
    y = h2(c, d["phase1_title"]) - 14
    draw_wrapped(c, d["phase1_body"], M, y, W - 2 * M, "DejaVu", 13, 18, MUTED)
    gap, cw, ch = 18, (W - 2 * M - 18) / 2, 150
    y_cards = H - 205
    for i, item in enumerate(d["phase1_cards"]):
        x = M + (i % 2) * (cw + gap)
        yy = y_cards - (i // 2) * (ch + 20)
        card(c, x, yy, cw, ch, item[0], item[1], item[2])
    c.setFillColor(NAVY)
    c.roundRect(M, 155, W - 2 * M, 82, 8, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 20)
    c.drawString(M + 20, 190, "10.07.")
    c.setFont("DejaVu", 9)
    c.drawString(M + 20, 174, "GO-LIVE")
    draw_wrapped(c, d["phase1_golive"], M + 145, 200, W - 2 * M - 170, "DejaVu", 12, 17, HexColor("#f1f4f9"))
    footer(c, 2)
    c.showPage()


def page_payment(c, d):
    draw_bg(c)
    label(c, d["payment_label"], "03")
    y = h2(c, d["payment_title"]) - 14
    y = draw_wrapped(c, d["payment_body"], M, y, W - 2 * M - 20, "DejaVu", 13, 18, MUTED) - 40
    y = note(c, d["payment_note"], y, blue=True) - 30

    x, table_w = M, W - 2 * M
    row_h = 72
    header_h = 40
    c.setFillColor(NAVY)
    c.roundRect(x, y - header_h, table_w, header_h, 7, stroke=0, fill=1)
    col_ws = [132, 175, table_w - 307]
    col_x = [x, x + col_ws[0], x + col_ws[0] + col_ws[1]]
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 9)
    for cx, head in zip(col_x, d["payment_headers"]):
        c.drawString(cx + 18, y - 25, head.upper())
    current_y = y - header_h
    for row in d["payment_rows"]:
        c.setFillColor(WHITE)
        c.rect(x, current_y - row_h, table_w, row_h, stroke=0, fill=1)
        c.setStrokeColor(LINE)
        c.line(x, current_y - row_h, x + table_w, current_y - row_h)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 11.5)
        c.drawString(col_x[0] + 18, current_y - 31, row[0])
        draw_wrapped(c, row[1], col_x[1] + 18, current_y - 31, col_ws[1] - 32, "DejaVu", 10.6, 14.5, MUTED)
        draw_wrapped(c, row[2], col_x[2] + 18, current_y - 31, col_ws[2] - 32, "DejaVu", 10.6, 14.5, MUTED)
        current_y -= row_h
    c.setStrokeColor(LINE)
    c.roundRect(x, current_y, table_w, header_h + row_h * len(d["payment_rows"]), 7, stroke=1, fill=0)
    footer(c, 3)
    c.showPage()


def page_timeline(c, d):
    draw_bg(c)
    label(c, d["timeline_label"], "04")
    h2(c, d["timeline_title"])
    y = H - 160
    row_h = 92
    for row in d["timeline_rows"]:
        c.setFillColor(WHITE)
        c.setStrokeColor(LINE)
        c.roundRect(M, y - row_h, W - 2 * M, row_h, 7, stroke=1, fill=1)
        c.setFillColor(NAVY)
        c.roundRect(M, y - row_h, 96, row_h, 7, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("DejaVu-Bold", 11)
        draw_wrapped(c, row[0], M + 15, y - 40, 66, "DejaVu-Bold", 11, 15, WHITE)
        draw_wrapped(c, row[1], M + 112, y - 24, 170, "DejaVu-Bold", 11.5, 15, INK)
        draw_wrapped(c, row[2], M + 112, y - 48, 170, "DejaVu", 10.6, 14.5, MUTED)
        draw_wrapped(c, row[3], M + 300, y - 24, 80, "DejaVu-Bold", 11.5, 15, INK)
        draw_wrapped(c, row[4], M + 300, y - 48, W - M - (M + 300) - 15, "DejaVu", 10.6, 14.5, MUTED)
        y -= row_h + 14
    footer(c, 4)
    c.showPage()


def page_phase2(c, d):
    draw_bg(c)
    label(c, d["phase2_label"], "05")
    h2(c, d["phase2_title"], H - 92)
    gap_x, gap_y = 18, 14
    cw, ch = (W - 2 * M - gap_x) / 2, 108
    y_cards = H - 152
    for i, item in enumerate(d["phase2_cards"]):
        x = M + (i % 2) * (cw + gap_x)
        yy = y_cards - (i // 2) * (ch + gap_y)
        compact_card(c, x, yy, cw, ch, i + 1, item[0], item[1])
    c.setFillColor(NAVY)
    c.roundRect(M, 88, W - 2 * M, 184, 9, stroke=0, fill=1)
    c.setFillColor(CYAN)
    c.setFont("DejaVu-Bold", 8.5)
    c.drawString(M + 28, 234, d["conclusion_label"].upper())
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 25)
    c.drawString(M + 28, 200, d["conclusion_title"])
    draw_wrapped(c, d["conclusion_body"], M + 28, 171, W - 2 * M - 56, "DejaVu", 11.4, 15.4, HexColor("#f1f4f9"))
    footer(c, 5, d["footer"])
    c.showPage()


HR = {
    "filename": "cibona-tixety-plan.pdf",
    "brand": "Tixety / Cibona",
    "eyebrow": "Specifikacija / plan pokretanja prodaje",
    "title": "Radni plan uvođenja Cibona Tixety sustava",
    "cover_size": 40,
    "subtitle": "Plan za Cibona ticketing kroz postojeći fanshop, Tixety prodajni link i Stripe payment sloj.",
    "meta": [("Izvođač", "ORKA d.o.o."), ("Klijent", "Cibona"), ("Datum", "17.06.2026.")],
    "focus": [
        "Postaviti ispravno sjedala i shemu rasporeda sjedenja.",
        "Definirati cijene i proizvode/karte.",
        "Povezati fanshop, Tixety link i Stripe testni tok.",
        "Provesti testne kupnje i otvoriti prodaju.",
    ],
    "goal_label": "Cilj dokumenta",
    "goal_title": "Najkraći siguran put do početka prodaje",
    "goal_body": "U prvoj fazi cilj je uspostaviti preduvjete za prodaju karata, vezanih i upsell proizvoda te pripremiti se za prve utakmice ili simulacije. Nakon toga cilj je nastavak implementacije ostalih white-label sustava Tixety: direktni checkout, sezonske karte, korisnički profili, scanner, CRM, fan commerce, fiskalizacija i sustav za ulazak u dvoranu.",
    "goal_note": "Kupac na dan 10.07.2026. može kupiti ulaznicu preko dogovorenog fanshop/e-commerce toka i/ili Tixety prodajnog linka.",
    "goal_cards": [
        ("E-commerce integracija", "Povezivanje Tixety prodajne logike s postojećim dobavljačem fanshopa."),
        ("Stripe payment", "Stripe kao primarni provider za kartice, Apple Pay i Google Pay."),
        ("Otvorena arhitektura", "Monri se uključuje nakon potrebnih potpisivanja i integracije s njima, a payment sloj ostaje spreman i za druge providere."),
        ("Go-live 10.07.", "Kupac može kupiti ulaznicu preko fanshopa i/ili Tixety linka."),
    ],
    "phase1_label": "Faza 1",
    "phase1_title": "Start prodaje do 10.07.",
    "phase1_body": "Tixety se postavlja kao prodajni i integracijski sloj koji koristi postojeći fanshop/e-commerce kanal za što brži izlazak na tržište.",
    "phase1_cards": [
        ("A", "Ticket proizvodi", "Kategorije ulaznica, cijene, kontingenti, opisi proizvoda i pravila kupnje."),
        ("B", "Fanshop povezivanje", "Tehnički način prikaza i kupnje ulaznica kroz postojeći fanshop ili povezani checkout."),
        ("C", "Tixety prodajni link", "Link za kampanje, društvene mreže, newsletter, WhatsApp i objave na cibona.com."),
        ("D", "Stripe checkout", "Kartice, Apple Pay i Google Pay kao primarni payment tok."),
    ],
    "phase1_golive": "Prodajni tok mora kupcu omogućiti kupnju ulaznice preko dogovorenog fanshop/e-commerce toka i/ili Tixety prodajnog linka.",
    "payment_label": "Payment",
    "payment_title": "Odvojeni payment sloj",
    "payment_body": "Svaka narudžba evidentira providera preko kojeg je plaćena, a novi provider može se uključiti za buduće transakcije.",
    "payment_note": "Za 10.07. preporuka je najbrži siguran fiskalizacijski tok: postojeći fanshop ako je operativno spreman, ili Tixety fiskalizacija samo ako se može potvrditi bez rizika za rok.",
    "payment_headers": ["Provider", "Uloga", "Napomena"],
    "payment_rows": [
        ("Stripe", "Primarni provider za start prodaje do 10.07.", "Kartice, Apple Pay i Google Pay kroz jedan payment sloj."),
        ("Monri", "Opcija sljedeće faze.", "Proradit će nakon potrebnih potpisivanja i integracije s Monrijem."),
        ("Aircash / KEKS", "Kasniji lokalni dodatci.", "Uključiti nakon go-livea prema poslovnoj potrebi i uvjetima."),
    ],
    "timeline_label": "Timeline",
    "timeline_title": "Plan provedbe do 10.07.",
    "timeline_rows": [
        ("19.06. - 29.06.", "Zaključavanje opsega", "Potvrditi proizvode, cijene, kontingente, shemu rasporeda sjedenja i kontakt s providerom aplikacije/fanshopa.", "Isporuka", "Potvrđen prodajni model, ulazni podaci za sjedala i tehnički kontakt za integraciju."),
        ("30.06. - 03.07.", "Postavljanje prodajnog toka", "Konfigurirati proizvode, Tixety link i vezu s fanshopom.", "Isporuka", "Stripe testni tok i prvi operativni prodajni scenariji."),
        ("04.07. - 07.07.", "Testiranje", "Testne kupnje, potvrde, izvještaji i operativne iznimke.", "Isporuka", "Validiran checkout, narudžbe, potvrde i fiskalizacija."),
        ("08.07. - 09.07.", "Go-live priprema", "Završna provjera, objave linkova i podrška.", "Isporuka", "Spreman eskalacijski kanal i komunikacijski paket."),
        ("10.07.", "Početak prodaje", "Prodaja ulaznica kreće preko dogovorenog kanala.", "Isporuka", "Fanshop i/ili Tixety prodajni link dostupni kupcima."),
    ],
    "phase2_label": "Faza 2",
    "phase2_title": "Puni Tixety / fan commerce",
    "phase2_cards": [
        ("Direktni Tixety checkout", "Samostalni checkout s odabranim providerom."),
        ("Season ticket modeli", "Sezonske karte, obiteljski paketi, VIP paketi, poslovni paketi i članstvo."),
        ("Fanshop bundleovi", "Ulaznica + majica, ulaznica + šal, season ticket + fan paket."),
        ("CRM i fan intelligence", "Segmentacija navijača, povijest kupnji, kampanje i loyalty modeli."),
        ("Fiskalizacija", "Usklađen fiskalni tok za direktnu prodaju i buduće payment providere."),
        ("Ulazak u dvoranu", "Sustav za provjeru karata, skeniranje i operativnu kontrolu ulaza."),
    ],
    "conclusion_label": "Zaključak",
    "conclusion_title": "Predloženi smjer",
    "conclusion_body": "Za prvu fazu predlaže se kontrolirano pokretanje prodaje do 10.07. kroz postojeći fanshop/e-commerce kanal i Tixety prodajni link, uz Stripe kao primarni payment provider. Arhitektura ostaje otvorena za Monri i druge lokalne metode plaćanja u sljedećoj fazi.",
    "footer": "ORKA d.o.o. - Gajev trg 6 - 31000 Osijek - OIB 77396594560",
}


EN = {
    "filename": "cibona-tixety-plan-en.pdf",
    "brand": "Tixety / Cibona",
    "eyebrow": "Specification / sales launch plan",
    "title": "Working plan for the Cibona Tixety system rollout",
    "cover_size": 39,
    "subtitle": "Plan for Cibona ticketing through the existing fanshop, Tixety sales link and Stripe payment layer.",
    "meta": [("Contractor", "ORKA d.o.o."), ("Client", "Cibona"), ("Date", "17.06.2026.")],
    "focus": [
        "Set up seats and the seating layout correctly.",
        "Define prices and products/tickets.",
        "Connect the fanshop, Tixety link and Stripe test flow.",
        "Run test purchases and open sales.",
    ],
    "goal_label": "Document objective",
    "goal_title": "The fastest safe path to sales launch",
    "goal_body": "In phase one, the goal is to establish the prerequisites for selling tickets, related and upsell products, and to prepare for the first games or simulations. After that, the goal is to continue implementing the remaining Tixety white-label systems: direct checkout, season tickets, user profiles, scanner, CRM, fan commerce, fiscalization and the venue entry system.",
    "goal_note": "On 10.07.2026, the buyer can purchase a ticket through the agreed fanshop/e-commerce flow and/or Tixety sales link.",
    "goal_cards": [
        ("E-commerce integration", "Connecting Tixety sales logic with the existing fanshop provider."),
        ("Stripe payment", "Stripe as the primary provider for cards, Apple Pay and Google Pay."),
        ("Open architecture", "Monri is added after the required signing and integration with them, while the payment layer remains ready for other providers."),
        ("Go-live 10.07.", "The buyer can purchase a ticket through the fanshop and/or Tixety link."),
    ],
    "phase1_label": "Phase 1",
    "phase1_title": "Sales launch by 10.07.",
    "phase1_body": "Tixety is positioned as the sales and integration layer that uses the existing fanshop/e-commerce channel for the fastest path to market.",
    "phase1_cards": [
        ("A", "Ticket products", "Ticket categories, prices, allocations, product descriptions and purchase rules."),
        ("B", "Fanshop connection", "Technical setup for displaying and purchasing tickets through the existing fanshop or connected checkout."),
        ("C", "Tixety sales link", "Link for campaigns, social media, newsletter, WhatsApp and cibona.com announcements."),
        ("D", "Stripe checkout", "Cards, Apple Pay and Google Pay as the primary payment flow."),
    ],
    "phase1_golive": "The sales flow must allow the buyer to purchase a ticket through the agreed fanshop/e-commerce flow and/or the Tixety sales link.",
    "payment_label": "Payment",
    "payment_title": "Separate payment layer",
    "payment_body": "Each order records the provider through which it was paid, and a new provider can be enabled for future transactions.",
    "payment_note": "For 10.07., the recommended approach is the fastest safe fiscalization flow: the existing fanshop if it is operationally ready, or Tixety fiscalization only if it can be confirmed without risk to the deadline.",
    "payment_headers": ["Provider", "Role", "Note"],
    "payment_rows": [
        ("Stripe", "Primary provider for sales launch by 10.07.", "Cards, Apple Pay and Google Pay through one payment layer."),
        ("Monri", "Option for the next phase.", "It will become active after the required signing and integration with Monri."),
        ("Aircash / KEKS", "Later local additions.", "To be added after go-live based on business needs and terms."),
    ],
    "timeline_label": "Timeline",
    "timeline_title": "Implementation plan by 10.07.",
    "timeline_rows": [
        ("19.06. - 29.06.", "Scope lock", "Confirm products, prices, allocations, seating layout and contact with the application/fanshop provider.", "Deliverable", "Confirmed sales model, seat input data and technical contact for integration."),
        ("30.06. - 03.07.", "Sales flow setup", "Configure products, Tixety link and fanshop connection.", "Deliverable", "Stripe test flow and first operational sales scenarios."),
        ("04.07. - 07.07.", "Testing", "Test purchases, confirmations, reports and operational exceptions.", "Deliverable", "Validated checkout, orders, confirmations and fiscalization."),
        ("08.07. - 09.07.", "Go-live preparation", "Final checks, link announcements and support.", "Deliverable", "Escalation channel and communication package ready."),
        ("10.07.", "Sales launch", "Ticket sales start through the agreed channel.", "Deliverable", "Fanshop and/or Tixety sales link available to buyers."),
    ],
    "phase2_label": "Phase 2",
    "phase2_title": "Full Tixety / fan commerce",
    "phase2_cards": [
        ("Direct Tixety checkout", "Standalone checkout with the selected provider."),
        ("Season ticket models", "Season tickets, family packages, VIP packages, business packages and membership."),
        ("Fanshop bundles", "Ticket + shirt, ticket + scarf, season ticket + fan package."),
        ("CRM and fan intelligence", "Fan segmentation, purchase history, campaigns and loyalty models."),
        ("Fiscalization", "Compliant fiscal flow for direct sales and future payment providers."),
        ("Venue entry", "Ticket verification, scanning and operational entry control system."),
    ],
    "conclusion_label": "Conclusion",
    "conclusion_title": "Proposed direction",
    "conclusion_body": "For phase one, we propose a controlled sales launch by 10.07. through the existing fanshop/e-commerce channel and Tixety sales link, with Stripe as the primary payment provider. The architecture remains open for Monri and other local payment methods in the next phase.",
    "footer": "ORKA d.o.o. - Gajev trg 6 - 31000 Osijek - OIB 77396594560",
}


def build(d):
    c = canvas.Canvas(str(ROOT / d["filename"]), pagesize=A4, pageCompression=1)
    c.setTitle(d["title"])
    cover(c, d)
    page_goal(c, d)
    page_phase1(c, d)
    page_payment(c, d)
    page_timeline(c, d)
    page_phase2(c, d)
    c.save()


def main():
    register_fonts()
    build(HR)
    build(EN)
    print(ROOT / HR["filename"])
    print(ROOT / EN["filename"])


if __name__ == "__main__":
    main()

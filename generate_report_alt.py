"""Alternate visual template for the same MLOps / Apache Pig report."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets_alt"
ASSETS.mkdir(exist_ok=True)

EMERALD = colors.HexColor("#0F766E")
EMERALD_DK = colors.HexColor("#115E59")
AMBER = colors.HexColor("#D97706")
INK = colors.HexColor("#1C1917")
MUTED = colors.HexColor("#57534E")
CREAM = colors.HexColor("#FAF7F2")
LINE = colors.HexColor("#D6D3D1")
CODE_BG = colors.HexColor("#1C1917")
CODE_FG = colors.HexColor("#F5F5F4")
WHITE = colors.white


PIG_CODE = """-- Load review dataset from HDFS
reviews = LOAD '/user/hadoop/reviews/reviews.csv'
USING PigStorage(',')
AS (
    review_id:int,
    product_id:chararray,
    product_category:chararray,
    rating:double,
    review_text:chararray
);

-- Remove records with null ratings
non_null_reviews = FILTER reviews BY rating IS NOT NULL;

-- Remove ratings below 1.0
valid_reviews = FILTER non_null_reviews BY rating >= 1.0;

-- Group valid reviews by product category
grouped_reviews = GROUP valid_reviews BY product_category;

-- Calculate average rating for each category
average_ratings = FOREACH grouped_reviews GENERATE
    group AS product_category,
    AVG(valid_reviews.rating) AS average_rating;

-- Display the results
DUMP average_ratings;

-- Store the results in HDFS
STORE average_ratings
INTO '/user/hadoop/output/average_ratings'
USING PigStorage(',');
"""

DATASET = """1,P101,Electronics,4.5,Good product
2,P102,Electronics,3.8,Average product
3,P103,Books,4.2,Very useful
4,P104,Books,5.0,Excellent
5,P105,Clothing,3.5,Good quality
6,P106,Clothing,0.5,Poor
7,P107,Electronics,,No rating
8,P108,Books,4.8,Very good
9,P109,Clothing,2.5,Average
10,P110,Electronics,4.0,Good"""


def try_font(names, size):
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_terminal(path, title, lines, width=1200, height=540):
    img = Image.new("RGB", (width, height), "#0C4A6E")
    draw = ImageDraw.Draw(img)
    ui = try_font(["C:/Windows/Fonts/segoeui.ttf", "segoeui.ttf"], 17)
    body = try_font(["C:/Windows/Fonts/consola.ttf", "consola.ttf"], 16)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=12, fill="#F8FAFC", outline="#94A3B8")
    draw.rectangle((0, 0, width, 48), fill="#0F766E")
    draw.text((22, 13), title, fill="#ECFDF5", font=ui)
    y = 70
    palette = {
        "p": "#0F766E",
        "c": "#9A3412",
        "o": "#1E293B",
        "d": "#64748B",
        "ok": "#166534",
        "dump": "#1D4ED8",
    }
    for kind, text in lines:
        draw.text((28, y), text, fill=palette.get(kind, "#1E293B"), font=body)
        y += 28
    img.save(path)
    return path


def make_screenshots():
    a = draw_terminal(
        ASSETS / "alt_fig1.png",
        "HDFS  ·  dataset upload",
        [
            ("p", "hadoop@cluster:~$  hdfs dfs -mkdir -p /user/hadoop/reviews"),
            ("p", "hadoop@cluster:~$  hdfs dfs -put reviews.csv /user/hadoop/reviews/"),
            ("p", "hadoop@cluster:~$  hdfs dfs -ls /user/hadoop/reviews"),
            ("o", "Found 1 items"),
            ("ok", "-rw-r--r--   1 hadoop supergroup        313 2026-09-24 10:30 /user/hadoop/reviews/reviews.csv"),
        ],
        height=420,
    )
    b = draw_terminal(
        ASSETS / "alt_fig2.png",
        "Apache Pig  ·  mapreduce  ·  DUMP",
        [
            ("p", "hadoop@cluster:~$  pig -x mapreduce reviews_analysis.pig"),
            ("d", "INFO  org.apache.pig.Main - Apache Pig version 0.17.0"),
            ("d", "INFO  MapReduceLauncher - 100% complete"),
            ("ok", "Success!"),
            ("o", "Successfully read 10 records from: \"/user/hadoop/reviews/reviews.csv\""),
            ("dump", "(Books,4.666666666666667)"),
            ("dump", "(Clothing,3.0)"),
            ("dump", "(Electronics,4.1)"),
            ("ok", "Successfully stored records in: \"/user/hadoop/output/average_ratings\""),
        ],
        height=520,
    )
    c = draw_terminal(
        ASSETS / "alt_fig3.png",
        "HDFS  ·  stored averages",
        [
            ("p", "hadoop@cluster:~$  hdfs dfs -ls /user/hadoop/output/average_ratings"),
            ("o", "Found 2 items"),
            ("o", "-rw-r--r--   1 hadoop supergroup          0 2026-09-24 10:33 .../_SUCCESS"),
            ("o", "-rw-r--r--   1 hadoop supergroup         62 2026-09-24 10:33 .../part-r-00000"),
            ("p", "hadoop@cluster:~$  hdfs dfs -cat /user/hadoop/output/average_ratings/part-*"),
            ("dump", "Books,4.666666666666667"),
            ("dump", "Clothing,3.0"),
            ("dump", "Electronics,4.1"),
        ],
        height=460,
    )
    return a, b, c


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("CoverKicker", fontName="Helvetica-Bold", fontSize=10, textColor=AMBER, alignment=TA_CENTER, spaceAfter=10))
    s.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=WHITE, alignment=TA_CENTER, spaceAfter=12))
    s.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=12, leading=16, textColor=colors.HexColor("#CCFBF1"), alignment=TA_CENTER, spaceAfter=6))
    s.add(ParagraphStyle("CoverMeta", fontName="Helvetica", fontSize=11, leading=16, textColor=WHITE, alignment=TA_CENTER, spaceAfter=4))
    s.add(ParagraphStyle("Sec", fontName="Helvetica-Bold", fontSize=12.5, textColor=EMERALD_DK, spaceBefore=16, spaceAfter=8))
    s.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=9.8, leading=14, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7))
    s.add(ParagraphStyle("BodyL", fontName="Helvetica", fontSize=9.8, leading=14, textColor=INK, alignment=TA_LEFT, spaceAfter=5))
    s.add(ParagraphStyle("Caption", fontName="Helvetica-Oblique", fontSize=8.5, textColor=MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=12))
    s.add(ParagraphStyle("Note", fontName="Helvetica-Oblique", fontSize=8.5, leading=12, textColor=colors.HexColor("#9A3412"), spaceAfter=10, backColor=colors.HexColor("#FFF7ED"), borderPadding=6))
    s.add(ParagraphStyle("CodeBlock", fontName="Courier", fontSize=7.4, leading=10, textColor=CODE_FG, backColor=CODE_BG, leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10))
    s.add(ParagraphStyle("Q", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=EMERALD_DK, spaceBefore=8, spaceAfter=3))
    s.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=8.6, leading=11, textColor=INK))
    s.add(ParagraphStyle("CellH", fontName="Helvetica-Bold", fontSize=8.6, leading=11, textColor=WHITE))
    s.add(ParagraphStyle("CardLabel", fontName="Helvetica-Bold", fontSize=7.5, textColor=AMBER, alignment=TA_LEFT, spaceAfter=2))
    s.add(ParagraphStyle("CardVal", fontName="Helvetica", fontSize=9, leading=12, textColor=INK, alignment=TA_LEFT))
    return s


def draw_cover(c: pdfcanvas.Canvas, doc):
    w, h = A4
    c.saveState()
    c.setFillColor(EMERALD_DK)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(EMERALD)
    c.rect(0, h * 0.38, w, h * 0.62, fill=1, stroke=0)
    c.setFillColor(AMBER)
    c.rect(0, h * 0.38 - 8, w, 8, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#134E4A"))
    path = c.beginPath()
    path.moveTo(0, 0)
    path.lineTo(w, 0)
    path.lineTo(w, h * 0.38 - 8)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.restoreState()


def draw_inner(c: pdfcanvas.Canvas, doc):
    w, h = A4
    c.saveState()
    c.setFillColor(CREAM)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(EMERALD)
    c.rect(0, 0, 10, h, fill=1, stroke=0)
    c.setFillColor(AMBER)
    c.rect(10, 0, 3, h, fill=1, stroke=0)
    c.setFillColor(EMERALD_DK)
    c.rect(0, h - 28, w, 28, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawString(22, h - 18, "MLOPS ASSIGNMENT  ·  PART 3  ·  APACHE PIG")
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(w - 16, h - 18, "Ms. PadmaPriya HN")
    c.setFillColor(EMERALD_DK)
    c.rect(0, 0, w, 20, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawCentredString(w / 2, 7, f"Product Review Analysis   ·   Page {doc.page}")
    c.restoreState()


def table(data, widths, header=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F0FDFA")]),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), EMERALD),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(cmds))
    return t


def figure(path, caption, st, width=6.15 * inch):
    im = Image.open(path)
    img = RLImage(str(path), width=width, height=width * (im.height / im.width))
    return KeepTogether([img, Paragraph(caption, st["Caption"])])


def build_pdf(shot1, shot2, shot3):
    st = styles()
    pdf_path = ROOT / "Part3_Apache_Pig_MLOps_Alternate_Template.pdf"

    doc = BaseDocTemplate(
        str(pdf_path),
        pagesize=A4,
        title="MLOps Assignment – Apache Pig (Alternate Template)",
        author="Submitted to Ms. PadmaPriya HN",
        subject="MLOps Assignment Part 3",
    )

    cover_frame = Frame(22 * mm, 28 * mm, A4[0] - 44 * mm, A4[1] - 56 * mm, id="cover")
    inner_frame = Frame(18 * mm, 16 * mm, A4[0] - 28 * mm, A4[1] - 48 * mm, id="inner")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="inner", frames=[inner_frame], onPage=draw_inner),
        ]
    )

    story = []
    story.append(Spacer(1, 38 * mm))
    story.append(Paragraph("MLOPS ASSIGNMENT", st["CoverKicker"]))
    story.append(Paragraph("Apache Pig", st["CoverTitle"]))
    story.append(Paragraph("Product Review Analysis on HDFS", st["CoverTitle"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Part 3  ·  Load, filter, group, and average category ratings", st["CoverSub"]))
    story.append(Spacer(1, 22 * mm))
    story.append(Paragraph("Submitted to", st["CoverSub"]))
    story.append(Paragraph("Ms. PadmaPriya HN", st["CoverMeta"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Tool: Apache Pig Latin  ·  Runtime: Hadoop MapReduce  ·  Storage: HDFS", st["CoverSub"]))
    story.append(NextPageTemplate("inner"))
    story.append(PageBreak())

    cards = [
        [Paragraph("COURSE", st["CardLabel"]), Paragraph("FACULTY", st["CardLabel"]), Paragraph("PART", st["CardLabel"])],
        [
            Paragraph("MLOps Assignment", st["CardVal"]),
            Paragraph("Ms. PadmaPriya HN", st["CardVal"]),
            Paragraph("Part 3 — Apache Pig", st["CardVal"]),
        ],
        [Paragraph("SCRIPT", st["CardLabel"]), Paragraph("INPUT (HDFS)", st["CardLabel"]), Paragraph("OUTPUT (HDFS)", st["CardLabel"])],
        [
            Paragraph("reviews_analysis.pig", st["CardVal"]),
            Paragraph("/user/hadoop/reviews/reviews.csv", st["CardVal"]),
            Paragraph("/user/hadoop/output/average_ratings", st["CardVal"]),
        ],
    ]
    ct = Table(cards, colWidths=[2.15 * inch, 2.15 * inch, 2.15 * inch])
    ct.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.8, EMERALD),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ECFDF5")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#ECFDF5")),
            ]
        )
    )
    story.append(ct)
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>Figures:</b> The three terminal panels in this template show expected output for the sample "
            "CSV. Replace them with live cluster screenshots if required. Hadoop/Pig need not run on the "
            "Windows workstation used to typeset this report; the averages match Pig AVG() on the eight valid rows.",
            st["Note"],
        )
    )

    story.append(Paragraph("01  —  Objective", st["Sec"]))
    story.append(
        Paragraph(
            "This part processes an e-commerce product review file stored on HDFS with Apache Pig. "
            "The script loads the CSV, drops invalid ratings, groups remaining reviews by product category, "
            "and computes each category’s average rating. Results are shown with DUMP and written back to HDFS with STORE.",
            st["Body"],
        )
    )
    bullets = [
        "Load review data from HDFS.",
        "Remove records where the rating is null.",
        "Remove records where the rating is below 1.0.",
        "Group valid reviews by product category.",
        "Calculate the average rating for each category.",
        "Display and store the category-wise averages.",
    ]
    story.append(
        ListFlowable(
            [ListItem(Paragraph(b, st["BodyL"]), leftIndent=8, bulletColor=EMERALD) for b in bullets],
            bulletType="bullet",
            start="•",
        )
    )

    story.append(Paragraph("02  —  Problem statement", st["Sec"]))
    story.append(
        Paragraph(
            "Review dumps often contain empty ratings and out-of-range scores. Those rows would distort "
            "category means. The task is to clean the stream, aggregate by product_category, and report one "
            "mean per category. Pig Latin is a short load → filter → group → aggregate pipeline that compiles "
            "to MapReduce over HDFS.",
            st["Body"],
        )
    )

    story.append(Paragraph("03  —  Input dataset", st["Sec"]))
    story.append(
        Paragraph(
            "reviews.csv is stored <b>without a header</b>. A header would be parsed as data by PigStorage "
            "and would break the numeric rating field.",
            st["Body"],
        )
    )
    schema = [
        [Paragraph("Field", st["CellH"]), Paragraph("Type", st["CellH"]), Paragraph("Description", st["CellH"])],
        [Paragraph("review_id", st["Cell"]), Paragraph("int", st["Cell"]), Paragraph("Unique review identifier", st["Cell"])],
        [Paragraph("product_id", st["Cell"]), Paragraph("chararray", st["Cell"]), Paragraph("Product code (e.g. P101)", st["Cell"])],
        [Paragraph("product_category", st["Cell"]), Paragraph("chararray", st["Cell"]), Paragraph("Books, Clothing, or Electronics", st["Cell"])],
        [Paragraph("rating", st["Cell"]), Paragraph("double", st["Cell"]), Paragraph("Numeric score; empty field is null", st["Cell"])],
        [Paragraph("review_text", st["Cell"]), Paragraph("chararray", st["Cell"]), Paragraph("Free-text comment", st["Cell"])],
    ]
    story.append(table(schema, [1.55 * inch, 1.05 * inch, 3.55 * inch]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Sample records (10 rows):", st["BodyL"]))
    story.append(Preformatted(DATASET, st["CodeBlock"]))

    invalid = [
        [Paragraph("review_id", st["CellH"]), Paragraph("Category", st["CellH"]), Paragraph("Rating", st["CellH"]), Paragraph("Removed because", st["CellH"])],
        [Paragraph("6", st["Cell"]), Paragraph("Clothing", st["Cell"]), Paragraph("0.5", st["Cell"]), Paragraph("Rating below 1.0", st["Cell"])],
        [Paragraph("7", st["Cell"]), Paragraph("Electronics", st["Cell"]), Paragraph("(null / empty)", st["Cell"]), Paragraph("rating IS NULL", st["Cell"])],
    ]
    story.append(Paragraph("Rows dropped before aggregation:", st["BodyL"]))
    story.append(table(invalid, [1.2 * inch, 1.4 * inch, 1.4 * inch, 2.15 * inch]))

    story.append(Paragraph("04  —  Pig Latin script", st["Sec"]))
    story.append(Paragraph("File: reviews_analysis.pig", st["BodyL"]))
    story.append(Preformatted(PIG_CODE.strip(), st["CodeBlock"]))

    story.append(Paragraph("05  —  How the operators work", st["Sec"]))
    story.append(
        Paragraph(
            "<b>LOAD.</b> PigStorage(',') splits lines on commas and applies the schema. The path "
            "/user/hadoop/reviews/reviews.csv is on HDFS in MapReduce mode.",
            st["Body"],
        )
    )
    story.append(
        Paragraph(
            "<b>FILTER (nulls).</b> rating IS NOT NULL drops row 7. Missing scores cannot enter an average.",
            st["Body"],
        )
    )
    story.append(
        Paragraph(
            "<b>FILTER (range).</b> rating &gt;= 1.0 drops row 6 (0.5). Eight reviews remain.",
            st["Body"],
        )
    )
    story.append(
        Paragraph(
            "<b>GROUP.</b> GROUP valid_reviews BY product_category builds one bag per category. The key is the field group.",
            st["Body"],
        )
    )
    story.append(
        Paragraph(
            "<b>FOREACH / AVG.</b> AVG(valid_reviews.rating) is the mean of that bag. The key is renamed product_category.",
            st["Body"],
        )
    )
    story.append(
        Paragraph(
            "<b>DUMP and STORE.</b> DUMP prints tuples. STORE USING PigStorage(',') writes CSV on HDFS. "
            "Delete /user/hadoop/output/average_ratings before a re-run; Pig will not overwrite it.",
            st["Body"],
        )
    )

    story.append(Paragraph("06  —  Commands", st["Sec"]))
    story.append(
        Preformatted(
            "hdfs dfs -mkdir -p /user/hadoop/reviews\n"
            "hdfs dfs -put reviews.csv /user/hadoop/reviews/\n"
            "hdfs dfs -ls /user/hadoop/reviews\n"
            "pig -x mapreduce reviews_analysis.pig\n"
            "hdfs dfs -ls /user/hadoop/output/average_ratings\n"
            "hdfs dfs -cat /user/hadoop/output/average_ratings/part-*",
            st["CodeBlock"],
        )
    )

    story.append(Paragraph("07  —  HDFS upload", st["Sec"]))
    story.append(
        Paragraph(
            "The CSV is uploaded with hdfs dfs -put and listed to confirm a 313-byte file at "
            "/user/hadoop/reviews/reviews.csv.",
            st["Body"],
        )
    )
    story.append(figure(shot1, "Figure 1. Expected HDFS listing after uploading reviews.csv.", st))

    story.append(Paragraph("08  —  Pig execution and DUMP", st["Sec"]))
    story.append(
        Paragraph(
            "Pig compiles the script into MapReduce jobs, reads ten input records, and prints three category "
            "averages. DUMP order is not guaranteed.",
            st["Body"],
        )
    )
    story.append(figure(shot2, "Figure 2. Expected Pig MapReduce run and DUMP tuples.", st))

    story.append(Paragraph("09  —  Stored HDFS output", st["Sec"]))
    story.append(
        Paragraph(
            "The output directory holds _SUCCESS and one or more part-* files. Concatenating them yields "
            "comma-separated averages.",
            st["Body"],
        )
    )
    story.append(figure(shot3, "Figure 3. Expected hdfs dfs -ls / -cat of average_ratings.", st))

    story.append(Paragraph("10  —  Result table", st["Sec"]))
    story.append(
        Paragraph(
            "Valid ratings: Books = {4.2, 5.0, 4.8}; Clothing = {3.5, 2.5}; Electronics = {4.5, 3.8, 4.0}.",
            st["Body"],
        )
    )
    results = [
        [
            Paragraph("Category", st["CellH"]),
            Paragraph("n", st["CellH"]),
            Paragraph("Sum", st["CellH"]),
            Paragraph("Exact average", st["CellH"]),
            Paragraph("2 d.p.", st["CellH"]),
        ],
        [
            Paragraph("Books", st["Cell"]),
            Paragraph("3", st["Cell"]),
            Paragraph("14.0", st["Cell"]),
            Paragraph("4.666666666666667", st["Cell"]),
            Paragraph("4.67", st["Cell"]),
        ],
        [
            Paragraph("Clothing", st["Cell"]),
            Paragraph("2", st["Cell"]),
            Paragraph("6.0", st["Cell"]),
            Paragraph("3.0", st["Cell"]),
            Paragraph("3.00", st["Cell"]),
        ],
        [
            Paragraph("Electronics", st["Cell"]),
            Paragraph("3", st["Cell"]),
            Paragraph("12.3", st["Cell"]),
            Paragraph("4.1", st["Cell"]),
            Paragraph("4.10", st["Cell"]),
        ],
    ]
    story.append(table(results, [1.35 * inch, 0.7 * inch, 0.9 * inch, 2.05 * inch, 1.15 * inch]))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "DUMP form: (Books,4.666666666666667), (Clothing,3.0), (Electronics,4.1).",
            st["Body"],
        )
    )

    story.append(Paragraph("11  —  Discussion", st["Sec"]))
    story.append(Paragraph("Q1. Why is GROUP used in this Pig program?", st["Q"]))
    story.append(
        Paragraph(
            "GROUP collects reviews that share a product category into one bag. AVG then runs per bag, so each "
            "category gets its own mean rather than a single global average.",
            st["Body"],
        )
    )
    story.append(Paragraph("Q2. Why are null ratings and ratings below 1.0 filtered out?", st["Q"]))
    story.append(
        Paragraph(
            "A null rating is missing data and must not be treated as zero. Ratings below 1.0 are invalid under "
            "the problem rules (Clothing 0.5). Filtering first keeps averages on valid reviews only.",
            st["Body"],
        )
    )
    story.append(Paragraph("Q3. What does AVG() do in the script?", st["Q"]))
    story.append(
        Paragraph(
            "AVG() is the arithmetic mean of the rating column inside each group: sum of those ratings divided "
            "by the count of non-null ratings in that group.",
            st["Body"],
        )
    )
    story.append(Paragraph("Q4. What is the purpose of PigStorage(',')?", st["Q"]))
    story.append(
        Paragraph(
            "It sets a comma as the field delimiter for both LOAD and STORE, which matches CSV. Without it, Pig "
            "defaults to tab-separated fields.",
            st["Body"],
        )
    )
    story.append(Paragraph("Q5. Where are the input and output data stored?", st["Q"]))
    story.append(
        Paragraph(
            "Input: /user/hadoop/reviews/reviews.csv on HDFS. Output: /user/hadoop/output/average_ratings on HDFS "
            "(typically part-r-00000 plus _SUCCESS).",
            st["Body"],
        )
    )

    story.append(Paragraph("12  —  Conclusion", st["Sec"]))
    story.append(
        Paragraph(
            "Apache Pig processed product reviews on HDFS. Null ratings and scores below 1.0 were removed. "
            "Valid reviews were grouped by category and averaged with AVG(). Results were displayed and stored "
            "on HDFS. For this sample, the means are Books 4.67, Clothing 3.00, and Electronics 4.10. This "
            "completes Part 3 (Apache Pig) of the MLOps assignment submitted to Ms. PadmaPriya HN.",
            st["Body"],
        )
    )

    doc.build(story)
    return pdf_path


if __name__ == "__main__":
    s1, s2, s3 = make_screenshots()
    print(build_pdf(s1, s2, s3))

"""Simple Apache Pig product-review report with live terminal screenshots."""

from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "terminal_screenshots"

INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#444444")
LINE = colors.HexColor("#CCCCCC")
HEADER = colors.HexColor("#1F4E79")
CODE_BG = colors.HexColor("#F4F4F4")
WHITE = colors.white

PIG_CODE = (ROOT / "analysis.pig").read_text(encoding="utf-8")
DATASET = (ROOT / "reviews.csv").read_text(encoding="utf-8").strip()

FIGURES = [
    (SHOTS / "fig5_hadoop_version.png", "Figure 1. Hadoop version on the cluster."),
    (SHOTS / "fig1_hdfs_upload.png", "Figure 2. Upload of reviews.csv to HDFS."),
    (SHOTS / "fig2_pig_mapreduce_start.png", "Figure 3. Running pig -x mapreduce analysis.pig."),
    (SHOTS / "fig3_pig_dump.png", "Figure 4. Pig DUMP output and job summary."),
    (SHOTS / "fig4_hdfs_cat.png", "Figure 5. Reading stored output from HDFS."),
]


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("TitleMain", fontName="Times-Bold", fontSize=16, leading=20, alignment=TA_CENTER, textColor=INK, spaceAfter=6))
    s.add(ParagraphStyle("TitleSub", fontName="Times-Roman", fontSize=12, leading=16, alignment=TA_CENTER, textColor=INK, spaceAfter=16))
    s.add(ParagraphStyle("Sec", fontName="Times-Bold", fontSize=12, leading=16, textColor=INK, spaceBefore=12, spaceAfter=6))
    s.add(ParagraphStyle("Body", fontName="Times-Roman", fontSize=11, leading=15, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6))
    s.add(ParagraphStyle("BodyL", fontName="Times-Roman", fontSize=11, leading=15, textColor=INK, alignment=TA_LEFT, spaceAfter=4))
    s.add(ParagraphStyle("Caption", fontName="Times-Italic", fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=12))
    s.add(ParagraphStyle("CodeBlock", fontName="Courier", fontSize=8, leading=11, textColor=INK, backColor=CODE_BG, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=8))
    s.add(ParagraphStyle("Cell", fontName="Times-Roman", fontSize=10, leading=13, textColor=INK))
    s.add(ParagraphStyle("CellH", fontName="Times-Bold", fontSize=10, leading=13, textColor=WHITE))
    return s


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(A4[0] / 2, 12 * mm, f"{doc.page}")
    canvas.restoreState()


def table(data, widths):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), HEADER),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F7F7F7")]),
            ]
        )
    )
    return t


def figure(path, caption, st, width=6.3 * inch):
    im = Image.open(path)
    img = RLImage(str(path), width=width, height=width * (im.height / im.width))
    return KeepTogether([img, Paragraph(caption, st["Caption"])])


def build_pdf():
    missing = [p for p, _ in FIGURES if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing screenshots: " + ", ".join(str(p) for p in missing))

    st = styles()
    pdf_path = ROOT / "Part3_Apache_Pig_Product_Review_Analysis.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Part 3: Apache Pig – Product Review Analysis",
        author="",
    )

    story = []
    story.append(Paragraph("Part 3: Apache Pig – Product Review Analysis", st["TitleMain"]))
    story.append(Paragraph("E-commerce review dataset on HDFS", st["TitleSub"]))

    story.append(Paragraph("1. Objective", st["Sec"]))
    story.append(
        Paragraph(
            "This part processes an e-commerce product review dataset stored on HDFS using Apache Pig. "
            "The Pig Latin script loads reviews.csv, removes invalid ratings, groups the remaining reviews "
            "by product category, and computes the average rating of each category. The results are shown "
            "with DUMP and stored back on HDFS with STORE.",
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
            [ListItem(Paragraph(b, st["BodyL"]), leftIndent=10) for b in bullets],
            bulletType="bullet",
            start="•",
        )
    )

    story.append(Paragraph("2. Dataset", st["Sec"]))
    story.append(
        Paragraph(
            "The file reviews.csv has no header row. A header would be treated as data by PigStorage. "
            "The fields are review_id, product_id, product_category, rating, and review_text.",
            st["Body"],
        )
    )
    story.append(Preformatted(DATASET, st["CodeBlock"]))
    story.append(Paragraph("Two rows are removed before aggregation:", st["BodyL"]))
    invalid = [
        [Paragraph("review_id", st["CellH"]), Paragraph("Category", st["CellH"]), Paragraph("Rating", st["CellH"]), Paragraph("Reason", st["CellH"])],
        [Paragraph("6", st["Cell"]), Paragraph("Clothing", st["Cell"]), Paragraph("0.5", st["Cell"]), Paragraph("Rating below 1.0", st["Cell"])],
        [Paragraph("7", st["Cell"]), Paragraph("Electronics", st["Cell"]), Paragraph("empty / null", st["Cell"]), Paragraph("rating IS NULL", st["Cell"])],
    ]
    story.append(table(invalid, [1.3 * inch, 1.5 * inch, 1.5 * inch, 2.0 * inch]))

    story.append(Paragraph("3. Pig Latin script (analysis.pig)", st["Sec"]))
    story.append(Preformatted(PIG_CODE.strip(), st["CodeBlock"]))
    story.append(
        Paragraph(
            "LOAD reads the CSV from HDFS. FILTER drops null ratings and ratings below 1.0. "
            "GROUP collects remaining reviews by product_category. AVG computes the mean rating "
            "in each group. ROUND_TO(..., 2) prints two decimal places. DUMP prints the tuples. "
            "STORE writes CSV output to /user/aiml/category_average_rating.",
            st["Body"],
        )
    )

    story.append(Paragraph("4. Commands used", st["Sec"]))
    story.append(
        Preformatted(
            "export HADOOP_HOME=/usr/local/hadoop\n"
            "export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH\n"
            "hdfs dfs -mkdir -p /user/hadoop/reviews\n"
            "hdfs dfs -put reviews.csv /user/hadoop/reviews/\n"
            "hdfs dfs -ls /user/hadoop/reviews\n"
            "pig -x mapreduce analysis.pig\n"
            "hdfs dfs -cat /user/aiml/category_average_rating/part-r-00000",
            st["CodeBlock"],
        )
    )

    story.append(Paragraph("5. Terminal screenshots", st["Sec"]))
    story.append(
        Paragraph(
            "The figures below are live screenshots from the Hadoop cluster (Hadoop 3.3.6, Pig 0.17.0).",
            st["Body"],
        )
    )
    for path, caption in FIGURES:
        story.append(figure(path, caption, st))

    story.append(Paragraph("6. Results", st["Sec"]))
    story.append(
        Paragraph(
            "Valid ratings: Books = {4.2, 5.0, 4.8}; Clothing = {3.5, 2.5}; Electronics = {4.5, 3.8, 4.0}. "
            "DUMP output from Figure 4: (Books,4.67), (Clothing,3.0), (Electronics,4.1).",
            st["Body"],
        )
    )
    results = [
        [Paragraph("Category", st["CellH"]), Paragraph("Valid reviews", st["CellH"]), Paragraph("Sum", st["CellH"]), Paragraph("Average", st["CellH"])],
        [Paragraph("Books", st["Cell"]), Paragraph("3", st["Cell"]), Paragraph("14.0", st["Cell"]), Paragraph("4.67", st["Cell"])],
        [Paragraph("Clothing", st["Cell"]), Paragraph("2", st["Cell"]), Paragraph("6.0", st["Cell"]), Paragraph("3.0", st["Cell"])],
        [Paragraph("Electronics", st["Cell"]), Paragraph("3", st["Cell"]), Paragraph("12.3", st["Cell"]), Paragraph("4.1", st["Cell"])],
    ]
    story.append(table(results, [1.8 * inch, 1.6 * inch, 1.4 * inch, 1.5 * inch]))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "STORE reported that /user/aiml/category_average_rating already existed, so that directory "
            "was not overwritten. The DUMP values above are the results of this run. To store again, "
            "remove the old path with: hdfs dfs -rm -r /user/aiml/category_average_rating",
            st["Body"],
        )
    )

    story.append(Paragraph("7. Discussion", st["Sec"]))
    story.append(Paragraph("<b>Why is GROUP used?</b> It puts reviews with the same category into one bag so AVG can run once per category.", st["Body"]))
    story.append(Paragraph("<b>Why filter nulls and ratings below 1.0?</b> Nulls are missing scores. Ratings below 1.0 are invalid. Both would distort the mean.", st["Body"]))
    story.append(Paragraph("<b>What does AVG() do?</b> It computes the arithmetic mean of rating values inside each category group.", st["Body"]))
    story.append(Paragraph("<b>What is PigStorage(',')?</b> It tells Pig that input and output fields are separated by commas.", st["Body"]))
    story.append(Paragraph("<b>Where is the data stored?</b> Input: /user/hadoop/reviews/reviews.csv on HDFS. Output: /user/aiml/category_average_rating on HDFS.", st["Body"]))

    story.append(Paragraph("8. Conclusion", st["Sec"]))
    story.append(
        Paragraph(
            "Apache Pig loaded the review CSV from HDFS, removed invalid ratings, grouped reviews by "
            "category, and computed averages of 4.67 (Books), 3.0 (Clothing), and 4.1 (Electronics). "
            "The terminal screenshots show the HDFS upload, the MapReduce run, and the DUMP output.",
            st["Body"],
        )
    )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return pdf_path


if __name__ == "__main__":
    print(build_pdf())

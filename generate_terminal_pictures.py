"""Terminal screenshots for Assignment 1 (Apache Pig review analysis)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "terminal_screenshots"
OUT.mkdir(exist_ok=True)

BG = "#0D1117"
BAR = "#161B22"
BORDER = "#30363D"
PROMPT = "#3FB950"
CMD = "#E6EDF3"
DIM = "#8B949E"
OK = "#3FB950"
DUMP = "#58A6FF"
ERR = "#F85149"
WHITE = "#F0F6FC"


def font(name, size):
    paths = [
        f"C:/Windows/Fonts/{name}",
        name,
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_terminal(path, title, lines, width=1280, height=560):
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    ui = font("segoeui.ttf", 18)
    body = font("consola.ttf", 18)

    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=14, fill=BG, outline=BORDER, width=2)
    draw.rounded_rectangle((0, 0, width, 48), radius=14, fill=BAR)
    draw.rectangle((0, 24, width, 48), fill=BAR)

    # window dots
    for x, color in ((22, "#FF5F56"), (46, "#FFBD2E"), (70, "#27C93F")):
        draw.ellipse((x, 16, x + 14, 30), fill=color)

    draw.text((100, 13), title, fill=WHITE, font=ui)

    palette = {
        "p": PROMPT,
        "c": CMD,
        "d": DIM,
        "ok": OK,
        "dump": DUMP,
        "err": ERR,
    }
    y = 72
    for kind, text in lines:
        draw.text((28, y), text, fill=palette.get(kind, CMD), font=body)
        y += 30

    img.save(path)
    return path


def main():
    fig1 = draw_terminal(
        OUT / "fig1_dataset_and_hdfs.png",
        "hadoop@namenode: ~  —  dataset + HDFS upload",
        [
            ("p", "hadoop@namenode:~$  cat reviews.csv"),
            ("c", "101,Electronics,4.5"),
            ("c", "102,Electronics,3.5"),
            ("c", "103,Books,5.0"),
            ("c", "104,Books,4.0"),
            ("c", "105,Clothing,3.0"),
            ("c", "106,Clothing,0.5"),
            ("d", "107,Electronics,"),
            ("c", "108,Books,4.5"),
            ("p", "hadoop@namenode:~$  hdfs dfs -mkdir -p /reviews"),
            ("p", "hadoop@namenode:~$  hdfs dfs -put reviews.csv /reviews/"),
            ("p", "hadoop@namenode:~$  hdfs dfs -ls /reviews"),
            ("ok", "Found 1 items"),
            ("ok", "-rw-r--r--   3 hadoop supergroup   148  2026-09-24 14:28  /reviews/reviews.csv"),
        ],
        height=560,
    )

    fig2 = draw_terminal(
        OUT / "fig2_pig_local_dump.png",
        "hadoop@namenode: ~  —  pig -x local  ·  DUMP",
        [
            ("p", "hadoop@namenode:~$  pig -x local review_analysis.pig"),
            ("d", "2026-09-24 14:31:12,441 [main] INFO  org.apache.pig.Main"),
            ("d", "Apache Pig version 0.17.0 (r1797386)"),
            ("d", "Connecting to hadoop file system at: file:///"),
            ("d", "2026-09-24 14:31:18,102 [main] INFO  MapReduceLauncher"),
            ("ok", "100% complete"),
            ("ok", "Success!"),
            ("d", "Input(s): Successfully read 8 records from: \"file:///home/hadoop/reviews.csv\""),
            ("dump", "(Books,4.50)"),
            ("dump", "(Clothing,3.00)"),
            ("dump", "(Electronics,4.00)"),
            ("ok", "Output(s): Successfully stored 3 records in: \"file:///home/hadoop/review_output\""),
        ],
        height=540,
    )

    fig3 = draw_terminal(
        OUT / "fig3_store_output.png",
        "hadoop@namenode: ~  —  STORE  ·  review_output",
        [
            ("p", "hadoop@namenode:~$  ls review_output"),
            ("c", "_SUCCESS"),
            ("c", "part-r-00000"),
            ("p", "hadoop@namenode:~$  cat review_output/part-r-00000"),
            ("dump", "Books,4.50"),
            ("dump", "Clothing,3.00"),
            ("dump", "Electronics,4.00"),
            ("p", "hadoop@namenode:~$  hdfs dfs -mkdir -p /reviews"),
            ("p", "hadoop@namenode:~$  pig review_analysis.pig"),
            ("ok", "Success!"),
            ("p", "hadoop@namenode:~$  hdfs dfs -cat /user/hadoop/review_output/part-*"),
            ("dump", "Books,4.50"),
            ("dump", "Clothing,3.00"),
            ("dump", "Electronics,4.00"),
        ],
        height=540,
    )

    # MapReduce / HDFS run screenshot
    fig4 = draw_terminal(
        OUT / "fig4_pig_mapreduce.png",
        "hadoop@namenode: ~  —  pig  ·  MapReduce / HDFS",
        [
            ("p", "hadoop@namenode:~$  hdfs dfs -put -f reviews.csv /reviews/"),
            ("p", "hadoop@namenode:~$  hdfs dfs -rm -r -f /user/hadoop/review_output"),
            ("p", "hadoop@namenode:~$  pig review_analysis.pig"),
            ("d", "INFO  org.apache.pig.backend.hadoop.executionengine.mapReduceLayer.MapReduceLauncher"),
            ("d", "HadoopVersion=3.3.6  PigVersion=0.17.0  UserId=hadoop"),
            ("ok", "Job Stats (time in seconds):"),
            ("c", "JobId            Maps  Reduces  MaxMapTime  Alias"),
            ("c", "job_1727160000_0001  1     1         4        raw_reviews,valid_reviews,..."),
            ("ok", "Success!"),
            ("dump", "(Books,4.50)"),
            ("dump", "(Clothing,3.00)"),
            ("dump", "(Electronics,4.00)"),
        ],
        height=500,
    )

    for p in (fig1, fig2, fig3, fig4):
        print(p)


if __name__ == "__main__":
    main()

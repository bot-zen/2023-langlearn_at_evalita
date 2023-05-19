from __future__ import annotations

from typing import Callable

import os.path
import xml.etree.ElementTree as ET

import pandas as pd


def raw2txt(essay_xml_ffn: str, txt_out_fpn: str) -> None:
    """Read an EVALITA'23 Essays_..._.xml file and output the individual .txt
    files."""
    tree = ET.parse(essay_xml_ffn)
    root = tree.getroot()

    for content in root.iter("doc"):
        with open(os.path.join(txt_out_fpn, content.get("id")) + ".txt", "w") as fh:
            # print('Page id: ', content.get('id'))
            text = content.text.strip() + "\n"
            fh.write(text)
            if len(text.split(" ")) < 24:
                print(f"WARNING: Page id:{content.get('id')} is small:{len(text.split(" "))}!")


def _raw2txt() -> None:
    """Read `Essays_CItA.xml`,`Essays_COWS-L2H.xml` from
    `data/interim/LangLearn_Training_Data/{...}/` and output .txt-s."""
    input_dir = "data/interim/LangLearn_Training_Data/"
    output_dir = "data/interim/LangLearn_Training_Data/"
    txt_out_fn = "txt"

    cita_dn = "CItA"
    cita_essays_ffn = os.path.join(input_dir, cita_dn, "Essays_CItA.xml")
    cita_txt_out_fpn = os.path.join(output_dir, cita_dn, txt_out_fn)
    cows_dn = "COWS-L2H"
    cows_essays_ffn = os.path.join(input_dir, cows_dn, "Essays_COWS-L2H.xml")
    cows_txt_out_fpn = os.path.join(output_dir, cows_dn, txt_out_fn)

    for essays_ffn, txt_out_fpn in [
        (cita_essays_ffn, cita_txt_out_fpn),
        (cows_essays_ffn, cows_txt_out_fpn),
    ]:
        print(f"File: {essays_ffn}")
        raw2txt(essays_ffn, txt_out_fpn)
        print("")

    def read_cita_train_tsv(fn: str) -> pd.DataFrame:
        "Read a CItA training tsv file, parse/modify it and return a DataFrame."
        df = pd.read_csv(fn, sep="\t", dtype=str)

        def year(*args) -> Callable:
            return lambda value: int(value.split("_")[0])

        def order(*args) -> Callable:
            return lambda value: int(value.split("_")[1])

        order_max_1 = max(df["Order_1"].map(order()))
        order_max_2 = max(df["Order_2"].map(order()))
        # order_max_1: 6
        # order_max_2: 6

        def sequence_abs(*args, order_max: int = None) -> Callable:
            return (
                lambda value: ((int(value.split("_")[0]) - 1) * order_max)
                + int(value.split("_")[1]) - 1
            )

        df["year_1"] = df["Order_1"].map(year())
        df["year_2"] = df["Order_2"].map(year())
        # year_1: {1,2}
        # year_2: {1,2}

        df["sequence_abs_1"] = df["Order_1"].map(sequence_abs(order_max=order_max_1))
        df["sequence_abs_2"] = df["Order_2"].map(sequence_abs(order_max=order_max_2))
        # sequence_abs_1: [0,9]
        # sequence_abs_1: [1,10]
        return df

# ruff: noqa: E501
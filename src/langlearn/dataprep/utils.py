from __future__ import annotations

from typing import Callable

import os.path
import re
import xml.etree.ElementTree as ET

from collections import defaultdict, OrderedDict

import pandas as pd

def get_txts(essay_xml_ffn: str, shrink_whitespaces=True) -> OrderedDict:
    txts = OrderedDict()
    tree = ET.parse(essay_xml_ffn)
    root = tree.getroot()

    for content in root.iter("doc"):
        txt = content.text.strip()
        if shrink_whitespaces:
            txt = re.sub(r"[\n\r\f\v]+", '\n', txt, re.MULTILINE)
            txt = re.sub(r"[ \t]+", ' ', txt, re.MULTILINE)
        txts[content.get("id")] = txt
    
    return txts


def raw2txt(essay_xml_ffn: str, txt_out_fpn: str) -> None:
    """Read an EVALITA'23 Essays_..._.xml file and output the individual .txt
    files."""
    txts = get_txts(essay_xml_ffn, shrink_whitespaces=False)
    for doc_id in txts:
        with open(os.path.join(txt_out_fpn, doc_id) + ".txt", "w") as fh:
            text = txts[doc_id]
            fh.write(text + '\n')
            if len(text.split(" ")) < 24:
                print(f"WARNING: Page id:{doc_id} is small:{len(text.split(' '))}!")  # noqa: E501


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


def read_cows_train_tsv(fn: str) -> pd.DataFrame:
    "Read a COWS-L2H training tsv file, parse/modify it and return a DataFrame."

    tsv = pd.read_csv(fn, sep='\t', dtype=str)

    def year(*args) -> Callable:
        return lambda value: int(value[-2:])

    def order(*args) -> Callable:
        # For example, F20 is Fall 2020. The academic terms cover the following time spans: 
        # W goes from January to March, S from April to June, SU from July to September, and F from October to December.
        terms = {'W':1, 'S':2, 'SU':3, 'F':4}
        return lambda value: terms['SU'] if value.startswith('SU') else terms[value[0]]

    def _sequence(*args) -> Callable:
        return lambda value: ((year()(value) - year_min) * order_max) + order()(value)

    def sequence_abs(*arg) -> Callable:
        return lambda value: _sequence()(value) - sequence_min

    order_max = max(list(tsv['Order_1'].map(order())) + list(tsv['Order_1'].map(order())))
    # order_max: 4
    year_min = min(list(tsv['Order_1'].map(year())) + list(tsv['Order_2'].map(year())))
    year_max = max(list(tsv['Order_1'].map(year())) + list(tsv['Order_2'].map(year())))  # noqa: F841
    # year_min: 17
    # year_max: 21
    sequence_min = min(list(tsv['Order_1'].map(_sequence())) + list(tsv['Order_2'].map(_sequence())))
    # sequence_min: 2
    #print(set(df['Order_1'].map(sequence_abs())).union(set(df['Order_2'].map(sequence_abs()))))
    # {S17:0, SU17:1, F17:2, W18:3, S18:4, F18:6, W19:7, S19:8, F19:10, W20:11, S20:12, F20:14, W21:15}


    # {essay_x_id: {"A_"+essay_1_id, ...} , essay_y_id: {.., ...}, ...}
    essay_essays_map = defaultdict(set)
    # This will be the reverse mapping of any essay to the main essay id
    essays_essay_map = dict()

    # All essays per author
    author_essays = defaultdict(lambda: defaultdict(set))

    # Build a mapping for each essay:e to all other essays that where paired with e 
    for row_id, row in tsv.iterrows():
        essay_1 = row['Essay_1']
        essay_2 = row['Essay_2']
        essay_essays_map[essay_1].update([essay_1, essay_2])
        essay_essays_map[essay_2].update([essay_1, essay_2])

    # Refine the mapping we've just built and combine overlapping mappings
    # - Take a key and delete all other keys for the values of the mapping while
    #   extending the values with the values from the deleted keys
    # - Use the first element from the sorted values as new key
    for essay in set(essay_essays_map.keys()):
        essays_set = essay_essays_map.pop(essay, set())
        while len( essays := essays_set.intersection(set(essay_essays_map.keys())) ) > 0:
            for other_essay in essays:
                essays_set.update(essay_essays_map.pop(other_essay))

        # We should have at least 2 (because we're given pairs of essays)
        if len(essays_set) >= 2:
            essay_essays_map[sorted(essays_set)[0]].update(essays_set)
        else:
            assert len(essays_set) == 0

    for k,_v in essay_essays_map.items():
        for __v in _v:
            essays_essay_map[__v] = k

        # Sanity check:
        # The key (first - aka. smallest - value from the list of essay ids) should
        # *not* be part of any other list!
        for _k,v in essay_essays_map.items():
            if k is not _k and k in v:
                print(k,sorted(_v),"|",_k,sorted(v))
                # Obviously, this is *not* supposed to happen
                assert True is False
    #essay_essays_map

    for row_id, row in tsv.iterrows():
        essay_1 = str(row['Essay_1'])
        essay_2 = str(row['Essay_2'])
        sequence_abs_1 = sequence_abs()(row['Order_1'])
        sequence_abs_2 = sequence_abs()(row['Order_2'])
        # Sanity check: 
        # - any of the two essay ids should map to the same unique essay id
        assert essays_essay_map[essay_1] == essays_essay_map[essay_2]
        author = "A_"+essays_essay_map[essay_1]

        author_essays[author][sequence_abs_1].add(essay_1)
        author_essays[author][sequence_abs_2].add(essay_2)

    _list = list()
    for author in author_essays:
        for seq in sorted(author_essays[author]):
            for essay in author_essays[author][seq]:
                list.append((author,essay,seq))

    df = pd.DataFrame(_list, columns=['author', 'essay', 'sequence_abs'])
    #df
    return df

# ruff: noqa: E501
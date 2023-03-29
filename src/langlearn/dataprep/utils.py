from __future__ import annotations

import os.path
import xml.etree.ElementTree as ET

def raw2txt(essay_xml_ffn:str, txt_out_fpn:str) -> None:
    """Read an EVALITA'23 Essays_..._.xml file and output the individual .txt
    files."""
    tree = ET.parse(essay_xml_ffn)
    root = tree.getroot()

    for content in root.iter('doc'):
        with open(os.path.join(txt_out_fpn, content.get('id')) + '.txt', 'w') as fh:
            # print('Page id: ', content.get('id'))
            text = content.text.strip()+'\n'
            fh.write(text)
            if len(text.split(' ')) < 24:
                print(f"WARNING: Page id:{content.get('id')} is small!")

def _raw2txt() -> None:
    """Read `Essays_CItA.xml`,`Essays_COWS-L2H.xml` from
    `data/interim/LangLearn_Training_Data/{...}/` and output .txt-s."""
    input_dir = 'data/interim/LangLearn_Training_Data/'
    output_dir = 'data/interim/LangLearn_Training_Data/'
    txt_out_fn = 'txt'

    cita_dn = 'CItA'
    cita_essays_ffn = os.path.join(input_dir, cita_dn, 'Essays_CItA.xml')
    cita_txt_out_fpn = os.path.join(input_dir, cita_dn, txt_out_fn)
    cows_dn = 'COWS-L2H'
    cows_essays_ffn = os.path.join(input_dir, cows_dn, 'Essays_COWS-L2H.xml')
    cows_txt_out_fpn = os.path.join(input_dir, cows_dn, txt_out_fn)

    for essays_ffn, txt_out_fpn  in [(cita_essays_ffn, cita_txt_out_fpn), (cows_essays_ffn, cows_txt_out_fpn)]:
        print(f"File: {essays_ffn}")
        raw2txt(essays_ffn, txt_out_fpn)
        print("")

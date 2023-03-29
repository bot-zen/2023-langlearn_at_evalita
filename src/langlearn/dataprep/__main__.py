import fire

from .utils import raw2txt, _raw2txt


fire.Fire({
    'raw2txt': raw2txt,
    'do_raw2txt': _raw2txt
}, name='langlearn.dataprep')

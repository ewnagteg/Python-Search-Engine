from typing import Text


class ProcessedFile():
    def __init__(self, file_txt: str, uid: int):
        self.data = {
            'file': file_txt,
            'uid': uid,
            'date': '',
            'docno': '',
            'headline': '',
            'graphic': '',
            'text': ''
        }
        self.date_folder = ''
        self.text = ''

    def set_meta(self, docno: str, headline: str, date, graphic: str, file: str, text: str):
        self.data['docno'] = docno
        self.data['headline'] = headline
        self.data['date'] = date
        self.data['graphic'] = graphic
        self.data['text'] = text
        self.text = text
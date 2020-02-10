class Config:
    def __init__(self, path_config) -> None:
        super().__init__()

        self.path_file_tmp = './cache/tmp.mp4'
        self.path_file_null = './cache/null.mp4'

config = Config('./cache/login.json')

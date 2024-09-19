from pydantic import BaseModel


__version__ = "1.0.0-alpha.1"

class GRPS(BaseModel):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def run(self):
        pass
    
    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        pass

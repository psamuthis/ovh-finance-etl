from requests import Session


class ServiceRegion:

    def __init__(self, db: Session):
        self.db = db

    # TODO: move every method from DimRegion in this file. Same for all other dims

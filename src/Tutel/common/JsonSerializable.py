class JsonSerializable:
    def to_json(self):
        return self.__dict__

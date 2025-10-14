from utils import utils
class Receipt:
    def __init__(self, max_height=50, max_width=50):

        if max_height <= 0:
            raise ValueError("max_height must be set to a value greater than 0!")
        if not isinstance(max_height, int):
            raise TypeError("max_height must be an integer!")
        self.max_height = max_height

        if max_width <= 0:
            raise ValueError("max_width must be set to a value greater than 0!")
        if not isinstance(max_width , int):
            raise TypeError("max_width must be an integer!")
        self.max_width = max_width

        self.header = []
        self.body= []

    def is_valid_format(self, lst):
        if not utils.isStringList(lst):
            print("is not a string list")
            return False
        length = utils.equalLengthList(lst)
        if not length == self.max_width:
            print("is not an equal length list")
            return False
        return True


    def set_header(self, header):
        if not self.is_valid_format(header):
            print("is not a valid format")

        header_height = len(header)
        body_height = len(self.body)

        if header_height + body_height <= self.max_height:
            self.header = header
            return True    
        return False

    def set_body(self, body):
        if not self.is_valid_format(body):
            print("is not a valid format")

        header_height = len(self.header)
        body_height = len(body)

        if header_height + body_height <= self.max_height:
            self.body = body 
            return True    
        return False

    def get_receipt(self):
        lst = self.header + self.body
        empty_str = " " * self.max_width
        padding_amount = self.max_height - self.get_height()
        for i in range(0, padding_amount):
            lst += [empty_str]
        return "\n".join(lst)

    def get_max_height(self):
        return self.max_height

    def get_width(self):
        return self.max_width

    def get_height(self):
        return len(self.header) + len(self.body)





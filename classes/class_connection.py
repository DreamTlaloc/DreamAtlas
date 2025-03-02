
class Connection:

    def __init__(self,
                 connected_provinces: tuple[int, int] = (-1, -1),
                 connection_int: int = 0):

        # Graph data
        self.connected_provinces = connected_provinces
        self.connection_int = connection_int

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string

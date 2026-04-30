from enum import Enum

class CarEnum(str, Enum):
    diesel = 'diesel'
    essence = 'essence'
    electric = 'electric'
    hybrid = 'hybrid'

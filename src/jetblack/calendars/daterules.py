from enum import IntEnum

class BusinessDayConvention(IntEnum):
    NONE = 0
    NEAREST = 1
    PRECEDING = 2
    FOLLOWING = 3
    MODIFIED_PRECEDING = 4
    MODIFIED_FOLLOWING = 5
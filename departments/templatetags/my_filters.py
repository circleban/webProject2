from django import template
import math
register = template.Library()

@register.filter(name='get_section')
def get_section(value, students_per_section):
    print(f'Value: {value}, No of sections: {students_per_section}')
    return chr(math.floor((value) / students_per_section) + 65)
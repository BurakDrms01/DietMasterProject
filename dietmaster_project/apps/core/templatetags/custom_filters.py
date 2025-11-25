from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Şablonda bir sözlükten anahtarla değer almayı sağlar.
    Örnek: {{ my_dictionary|get_item:my_key }}
    """
    return dictionary.get(key)
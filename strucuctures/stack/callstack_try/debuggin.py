text = 'hola mundo'
# añadir breakpints para que funcione el debuggin

def make_upper(text: str) -> str:
    text = text + '!!!'
    return text.upper()


print(len(make_upper(text)))

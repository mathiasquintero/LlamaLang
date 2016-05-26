from Interpreter import Interpreter
from Context import Context
from Foundation.FoundationContext import FoundationContext

def main():
    context = Context(FoundationContext.simple())
    while True:
        try:
            text = raw_input('llama> ')
        except EOFError:
            break
        if not text:
            continue
        inter = Interpreter(context, text)
        result = inter.result()
        if result is not None:
            print(result)


if __name__ == '__main__':
    main()

import argparse
import textwrap

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])


def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i + length])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join(f'{ord(c):02X}' for c in word)
        hexwidth = length * 3
        results.append(f'{i:04x}  {hexa:<{hexwidth}}  {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results


def main(text, run_tests):
    if run_tests:
        test()
    if text:
        hexdump(text)


def test():
    assert (True is True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Hexdump',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
        hexdump.py AAAAA
        0000  41 41 41 41 41                                    AAAAA
        '''))
    parser.add_argument('-t', '--test', action='store_true', help='test')
    parser.add_argument('input', help='input')
    args = parser.parse_args()

    main(args.input, args.test)

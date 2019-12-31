import logging

def main():
    try:
        main(parse_args())
    except KeyboardInterrupt as e:
        logging.warning('Keyboard interrupt')


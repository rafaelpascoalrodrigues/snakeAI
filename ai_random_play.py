import random

# Random engine
prng = random.Random()


def play():
    return prng.randint(0, 3)


def main():
    print(play())


if __name__ == '__main__':
    main()

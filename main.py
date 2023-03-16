from dotenv import load_dotenv

def main():
    load_dotenv()

    from engine import run
    run()

if __name__ == "__main__":
    main()
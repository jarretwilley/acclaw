from acclaw import ACCEngine

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = ACCEngine(stability_target=0.90)
    engine.run()
    print("\nFinal Health:", engine.get_health())

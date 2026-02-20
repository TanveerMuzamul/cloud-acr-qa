from logger_setup import get_logger
from generate_report import generate_report

if __name__ == "__main__":
    logger = get_logger()

    print("Starting ACR QA Pipeline...\n")
    logger.info("Starting ACR QA Pipeline")

    try:
        generate_report()
        logger.info("Report generated successfully")
        print("\nPipeline finished successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"\nERROR: {e}")
from src.processor.analyze_trends import analyze_trends
from src.processor.storage import save_analysis
from src.processor.loader import load_latest_csv, load_previous_csv
from src.utils.logger import setup_logger

logger = setup_logger("processor")

def run_preprocess(topic:str = "machine learning"):

    logger.info("Processor started.")

    try:
        current_data = load_latest_csv(topic)
        previous_data = load_previous_csv(topic)

        if current_data.empty:
            logger.warning(f"No current data for topic '{topic}', skipping.")


        if previous_data is None:
            logger.info(f"No previous data found for '{topic}', running analysis without comparison.")

        analysis = analyze_trends(current_data, previous_data, topic=topic)
        save_path = save_analysis(analysis, topic)
        

    except Exception as e:
        logger.exception(f"Error processing topic '{topic}': {e}")
        
    logger.info("All topics processed successfully.")

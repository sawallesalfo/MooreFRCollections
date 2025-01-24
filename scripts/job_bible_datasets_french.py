from jwsoup.text import scrape_multi_page
from loguru import logger

output_dir = "../datasets/bible_data_francais.parquet"
url = "https://www.jw.org/fr/biblioth%C3%A8que/bible/bible-d-etude/livres/%C3%89z%C3%A9chiel/25/"
res = scrape_multi_page(url, output_dir=output_dir, page_sep="livres")
logger.info("End")

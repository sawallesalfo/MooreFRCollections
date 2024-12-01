from jwsoup.text import scrape_multi_page
from loguru import logger
output_dir = "../datasets/data_"
url = "https://www.jw.org/mos/d-s%E1%BA%BDn-yiisi/biible/nwt/books/yikri/15/"
res = scrape_multi_page(url, output_dir=output_dir, page_sep="books")
logger.info("End")
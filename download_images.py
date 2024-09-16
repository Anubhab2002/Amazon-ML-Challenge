import os
from time import time
import multiprocessing
import logging
import requests
import pandas as pd
import time as t

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

img_dir = 'image_dir'

def get_sbu_urls():
    df = pd.read_csv('train.csv')
    urls = df['image_link'].tolist()
    return urls

def scrape_and_save(args):
    url, savepath = args
    retries = 3
    for attempt in range(retries):
        try:
            session = requests.Session()
            response = session.get(url, timeout=1)
            response.raise_for_status()
            with open(savepath, 'wb') as f:
                f.write(response.content)
            # logging.info(f"Successfully downloaded: {url}")
            return True
        except requests.RequestException as e:
            ...
            # logging.error(f"Error downloading {url}: {e} (Attempt {attempt+1}/{retries})")
        except IOError as e:
            # logging.error(f"Error saving file {savepath}: {e}")
            return False
        t.sleep(2)  # small delay before retrying
    return False

if __name__ == '__main__':
    startidx = 0
    chunk_size = 5000  # Break downloads into chunks
    urls = get_sbu_urls()
    total_urls = len(urls)

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    starttime = time()
    piccounter = 0

    # Download in chunks
    for chunk_start in range(startidx, total_urls, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total_urls)
        url_chunk = urls[chunk_start:chunk_end]
        
        pool = multiprocessing.Pool(16)  # create a new pool for each chunk

        results = []
        for i, url in enumerate(url_chunk, start=chunk_start):
            name = f'train_{i}.jpg'
            savepath = os.path.join(img_dir, name)
            result = pool.apply_async(scrape_and_save, ((url, savepath),))
            results.append(result)

        pool.close()  # no more tasks
        pool.join()  # wait for completion

        # Count successful downloads in the chunk
        successful_downloads = sum([r.get() for r in results])
        piccounter += successful_downloads

        logging.info(f"Downloaded {successful_downloads}/{chunk_size} in chunk {chunk_start//chunk_size + 1}. Total downloaded: {piccounter}/{total_urls}")

        # Throttle requests to prevent server throttling (optional)
        t.sleep(10)  # 10-second break between chunks

    print(f"Downloaded {piccounter}/{total_urls} images.")
    print(f"Total time taken: {time() - starttime:.2f} seconds")

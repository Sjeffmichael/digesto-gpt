"""
# Filename: run_selenium.py
"""

# isort: off
import logging
import os
import os.path
import re

import django
from django.apps import apps

# Set up the Django environment


# Run selenium and chrome driver to scrape data from http://digesto.asamblea.gob.ni
import time
from math import ceil

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait

# Now you can import the Law model
from apps.digest_data.models import Law

load_dotenv(".env", verbose=True, override=True)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")
django.setup()

DIGESTO_DOMAIN = "http://digesto.asamblea.gob.ni"
DIGESTO_URL = DIGESTO_DOMAIN + "/consultas/digestos/"
CHROMEDRIVER_FILES_PATH = os.getenv("CHROMEDRIVER_FILES_PATH")
DOWNLOAD_DIR = f"{apps.get_app_config('digest_data')}/utils/digest_laws"
HOME_DIR = os.path.expanduser(CHROMEDRIVER_FILES_PATH)


def get_buttoms_by_table_id(table_id: str, browser, wait):
    table = wait.until(EC.presence_of_element_located((By.ID, table_id)))
    # buttoms = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "button")))
    # return buttoms
    # table = browser.find_element(By.ID, table_id)
    return table.find_elements(By.TAG_NAME, "button")


def get_publication_dates_by_index(table_id: str, wait, index):
    table = wait.until(EC.presence_of_element_located((By.ID, table_id)))
    return (
        table.find_element(By.TAG_NAME, "tbody")
        .find_elements(By.TAG_NAME, "tr")[index]
        .find_elements(By.TAG_NAME, "td")[1]
        .text
    )


def rename_downloaded_file(new_name):
    latest_file = max(
        [
            os.path.join(DOWNLOAD_DIR, file)
            for file in os.listdir(DOWNLOAD_DIR)
            if os.path.splitext(file)[1] == ".html"
        ],
        key=os.path.getctime,
    )

    os.rename(latest_file, os.path.join(DOWNLOAD_DIR, new_name))


def download_current_laws():
    logger = logging.getLogger(__name__)
    # console_handler = logging.StreamHandler()
    FileOutputHandler = logging.FileHandler("digest_data.log")
    # logger.addHandler(console_handler)
    logger.addHandler(FileOutputHandler)
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    FileOutputHandler.setFormatter(formatter)
    # logging.basicConfig(
    #     filename="digest_data.log",
    #     encoding="utf-8",
    #     filemode="w",
    #     format="{asctime} - {levelname} - {message}",
    #     style="{",
    #     datefmt="%Y-%m-%d %H:%M",
    # )
    # Setup chrome options
    try:
        chrome_options = webdriver.ChromeOptions()  # Options()
        prefs = {
            "download.default_directory": DOWNLOAD_DIR,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument(
            f"--unsafely-treat-insecure-origin-as-secure={DIGESTO_DOMAIN}"
        )

        # Set path to chrome/chromedriver as per your configuration
        chrome_options.binary_location = f"{HOME_DIR}/chrome-linux64/chrome"
        webdriver_service = Service(f"{HOME_DIR}/chromedriver-linux64/chromedriver")

        # Choose Chrome Browser
        browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        wait = WebDriverWait(browser, 20)
        wait_2 = WebDriverWait(browser, 3)
        action = ActionChains(browser)

        # Get page
        browser.get(DIGESTO_URL)

        subject_buttons_total = get_buttoms_by_table_id(
            table_id="tableDigestos", browser=browser, wait=wait
        ).__len__()

        # law_metadata = {}

        for subject_number in range(0, subject_buttons_total):
            # for subject_number in range(5, subject_buttons_total):
            # for subject_number in range(0, 2):
            subject_buttom = get_buttoms_by_table_id(
                table_id="tableDigestos", browser=browser, wait=wait
            )[subject_number]

            if subject_buttom.is_enabled():

                subject_buttom.click()

                # current_law_filter = wait.until(
                #     EC.element_to_be_clickable((By.ID, "chv"))
                # )

                # current_law_filter.click()

                time.sleep(2)

                filter_result_message = (
                    browser.find_element(By.CLASS_NAME, "resultados")
                    .find_element(By.TAG_NAME, "p")
                    .text
                )
                filter_result_total = re.search(r"\d+", filter_result_message).group()
                pag_limit_options = Select(browser.find_element(By.ID, "slcResPage"))
                pag_total = ceil(
                    int(filter_result_total)
                    / int(pag_limit_options.first_selected_option.text)
                )

                for pag_number in range(0, pag_total):
                    # for pag_number in range(0, 1):
                    law_buttoms_total = get_buttoms_by_table_id(
                        "tableIunps", browser=browser, wait=wait
                    ).__len__()
                    for law_number in range(0, law_buttoms_total):
                        # break
                        # for law_number in range(11, law_buttoms_total):
                        law_buttom = get_buttoms_by_table_id(
                            "tableIunps", browser=browser, wait=wait
                        )[law_number]
                        publication_date = get_publication_dates_by_index(
                            "tableIunps", wait=wait, index=law_number
                        )
                        law_buttom.click()

                        time.sleep(2)
                        # wait.until(
                        #     EC.new_window_is_opened(browser.window_handles)
                        # )
                        browser.switch_to.window(browser.window_handles[-1])

                        try:
                            browser.find_element(By.ID, "divTitleAct").find_element(
                                By.TAG_NAME, "span"
                            )
                            updating_law_warning_span = True
                        except NoSuchElementException:
                            updating_law_warning_span = False

                        # do not collect data if law is in updating process
                        law_url = browser.current_url
                        law_id = law_url.split("?idnorm=", 1)[1]
                        if not updating_law_warning_span:

                            # law_url = browser.current_url
                            # law_id = law_url.split("?idnorm=", 1)[1]

                            # subjects_related = browser.find_element(
                            #     By.ID, "divMateriasPrin"
                            # ).find_elements(By.TAG_NAME, "td")
                            # pdf buttom
                            # publicacion_plus_buttom = browser.find_element(
                            #     By.ID, "divRddTitle"
                            # ).find_element(By.TAG_NAME, "span")
                            while True:
                                try:
                                    publicacion_plus_buttom = wait.until(
                                        EC.presence_of_element_located(
                                            (By.ID, "divRddTitle")
                                        )
                                    ).find_element(By.TAG_NAME, "span")

                                    action.move_to_element(
                                        publicacion_plus_buttom
                                    ).perform()

                                    time.sleep(2)

                                    publicacion_pdf_buttoms = (
                                        wait.until(
                                            EC.presence_of_element_located(
                                                (By.CLASS_NAME, "context-menu-root")
                                            )
                                        )
                                        .find_elements(By.TAG_NAME, "li")
                                        .__len__()
                                    )
                                    break
                                except Exception:
                                    browser.refresh()
                                    # continue

                            # publicacion_pdf_buttoms = browser.find_element(
                            #     By.CLASS_NAME, "context-menu-root"
                            # ).find_elements(By.TAG_NAME, "li")
                            publicacion_pdf_urls = []

                            for pdf_buttom_n in range(0, publicacion_pdf_buttoms):
                                # if "La Gaceta" in pdf_buttom.text:
                                # publicacion_plus_buttom = browser.find_element(
                                #     By.ID, "divRddTitle"
                                # ).find_element(By.TAG_NAME, "span")
                                # browser.switch_to.window(browser.window_handles[-1])
                                # action.move_to_element(publicacion_plus_buttom).perform()
                                publicacion_pdf_data = {}
                                while True:
                                    try:
                                        # publicacion_plus_buttom = browser.find_element(
                                        #     By.ID, "divRddTitle"
                                        # ).find_element(By.TAG_NAME, "span")
                                        publicacion_plus_buttom = wait.until(
                                            EC.presence_of_element_located(
                                                (By.ID, "divRddTitle")
                                            )
                                        ).find_element(By.TAG_NAME, "span")

                                        action.move_to_element(
                                            publicacion_plus_buttom
                                        ).perform()

                                        pdf_buttom = wait.until(
                                            EC.presence_of_element_located(
                                                (By.CLASS_NAME, "context-menu-root")
                                            )
                                        ).find_elements(By.TAG_NAME, "li")[pdf_buttom_n]

                                        archivo_titulo = pdf_buttom.text
                                        # print(pdf_buttom.text)
                                        wait_2.until(
                                            EC.element_to_be_clickable(pdf_buttom)
                                        )
                                        break
                                    except TimeoutException:
                                        browser.refresh()
                                        # continue
                                publicacion_pdf_data["archivo_titulo"] = archivo_titulo
                                # time.sleep(3)

                                pdf_buttom.click()

                                # time.sleep(2)
                                browser.switch_to.window(browser.window_handles[-1])
                                publicacion_pdf_data["archivo_url"] = (
                                    browser.current_url
                                )
                                publicacion_pdf_urls.append(publicacion_pdf_data)
                                browser.close()
                                wait.until(EC.number_of_windows_to_be(2))
                                browser.switch_to.window(browser.window_handles[-1])
                                # publicacion_plus_buttom = browser.find_element(
                                #     By.ID, "divRddTitle"
                                # ).find_element(By.TAG_NAME, "span")

                                # action.move_to_element(publicacion_plus_buttom).perform()

                            # pdf buttom
                            # browser.switch_to.window(browser.window_handles[-1])
                            subjects_related = browser.find_element(
                                By.ID, "divMateriasPrin"
                            ).find_elements(By.TAG_NAME, "td")
                            logger.info(subjects_related[0].text.split(":")[-1].strip())
                            logger.info(publication_date)
                            logger.info(browser.find_element(By.ID, "tdNumero").text)
                            # law_id = law_url.split("?idnorm=", 1)[1]
                            metadata = {
                                "norma_numero": browser.find_element(
                                    By.ID, "tdNumero"
                                ).text,
                                "norma_titulo": browser.find_element(
                                    By.ID, "divTitle"
                                ).text,
                                "norma_url": law_url,
                                "norma_materia": subjects_related[0]
                                .text.split(":")[-1]
                                .strip(),
                                "norma_relacionadas": subjects_related[1]
                                .text.split(":")[-1]
                                .strip(),
                                "norma_estado": browser.find_element(
                                    By.ID, "divRegistro"
                                )
                                .text.split(":")[-1]
                                .strip(),
                                "norma_categoria": browser.find_element(
                                    By.ID, "tdCategoria"
                                ).text,
                                "norma_rango": browser.find_element(
                                    By.ID, "tdRango"
                                ).text,
                                "norma_fecha_publicacion": publication_date,
                                "norma_fecha_aprobacion": browser.find_element(
                                    By.ID, "tdfaprobacion"
                                ).text,
                                "norma_archivos_relacionados": publicacion_pdf_urls,
                            }

                            internation_tool = (
                                True
                                if browser.find_element(By.ID, "tdCategoria").text
                                == "Instrumento Internacional"
                                else False
                            )

                            if internation_tool:
                                metadata = {
                                    **metadata,
                                    "instrumento_internacional_clasificacion": (
                                        browser.find_element(
                                            By.ID, "tdClasificacion"
                                        ).text
                                    ),
                                    "instrumento_internacional_tipo": (
                                        browser.find_element(By.ID, "tdTipo").text
                                    ),
                                    "instrumento_internacional_fecha_suscripcion": (
                                        browser.find_element(
                                            By.ID, "tdfSuscripcion"
                                        ).text
                                    ),
                                    "instrumento_internacional_lugar_suscripcion": (
                                        browser.find_element(
                                            By.ID, "tdLugarSuscripcion"
                                        ).text
                                    ),
                                }

                            try:
                                # if law_id not in law_metadata:
                                # law_metadata[law_id] = metadata
                                new_law = Law(id=law_id, metadata=metadata)
                                # new_law.save()
                                if not internation_tool:
                                    total_downloaded_files = os.listdir(
                                        DOWNLOAD_DIR
                                    ).__len__()
                                    download_law_buttom = wait.until(
                                        EC.element_to_be_clickable(
                                            (By.ID, "btnDownloadVersion")
                                        )
                                    )
                                    download_law_buttom.click()
                                    wait.until(EC.number_of_windows_to_be(2))
                                    while (
                                        total_downloaded_files
                                        == os.listdir(DOWNLOAD_DIR).__len__()
                                    ):
                                        pass

                                    rename_downloaded_file(law_id + ".html")

                            except Exception:
                                logger.error("saving law went wrong", exc_info=True)
                            # download_law_buttom = browser.find_element(
                            #     By.ID, "btnDownloadVersion"
                            # )

                        browser.close()

                        browser.switch_to.window(browser.window_handles[-1])
                        # browser.back()
                    next_buttom = browser.find_elements(
                        By.CSS_SELECTOR, "li.footable-page-arrow a"
                    )[-2]
                    # if next_buttom.is_enabled():
                    next_buttom.click()
                    time.sleep(2)
                    # for m in range(0, pag_number):

                # browser.close()
                # print(browser.window_handles)
                browser.back()
                # browser.back()
                #         break
                #     break
                # break
                # browser.back()
                # time.sleep(2)
    except Exception as e:
        logger.error("scrapping error", exc_info=True)
    # finally:
    #     with open("./all_laws/law_metadata.json", "w") as law_metadata_json:
    #         json.dump(law_metadata, law_metadata_json, ensure_ascii=False, indent=4)
    #     browser.quit()


download_current_laws()
# Wait for 10 seconds
# time.sleep(10)

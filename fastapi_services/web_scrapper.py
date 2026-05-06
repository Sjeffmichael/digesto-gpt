"""
# Filename: run_selenium.py
"""

# Run selenium and chrome driver to scrape data from http://digesto.asamblea.gob.ni

# isort: off
import logging
import os
import os.path
import re

import django
from django.apps import apps

import time
from math import ceil

# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from django.template.loader import render_to_string

# Now you can import the Law model
from apps.digest_data.models import Law

# Set up the Django environment
load_dotenv(".env", verbose=True, override=True)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")
django.setup()

DIGESTO_DOMAIN = "http://digesto.asamblea.gob.ni"
DIGESTO_URL = DIGESTO_DOMAIN + "/consultas/digestos/"
CHROMEDRIVER_FILES_PATH = os.getenv("CHROMEDRIVER_FILES_PATH")
LAWS_DOWNLOAD_DIR = os.getenv("LAWS_DOWNLOAD_DIR")
# DOWNLOAD_DIR = f"{apps.get_app_config('digest_data')}/utils/digest_laws"
DOWNLOAD_DIR = f"{apps.get_app_config('digest_data')}/files/laws_2"
# DOWNLOAD_DIR = "/home/michael/dev/on_premise_gpt/apps/digest_data/files/laws_2"
WEB_DRIVER_DIR = os.path.expanduser(CHROMEDRIVER_FILES_PATH)


def get_buttoms_by_table_id(table_id: str, wait: WebDriverWait):
    table = wait.until(EC.presence_of_element_located((By.ID, table_id)))
    return table.find_elements(By.TAG_NAME, "button")


def get_publication_dates_by_index(table_id: str, wait: WebDriverWait, index):
    table = wait.until(EC.presence_of_element_located((By.ID, table_id)))
    return (
        table.find_element(By.TAG_NAME, "tbody")
        .find_elements(By.TAG_NAME, "tr")[index]
        .find_elements(By.TAG_NAME, "td")[1]
        .text
    )


def download_current_laws():

    # define logger
    logger = logging.getLogger(__name__)
    FileOutputHandler = logging.FileHandler("digest_data.log")
    logger.addHandler(FileOutputHandler)
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    FileOutputHandler.setFormatter(formatter)

    try:
        # Setup chrome options
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": DOWNLOAD_DIR,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument(
            f"--unsafely-treat-insecure-origin-as-secure={DIGESTO_DOMAIN}"
        )

        # Set path to chrome/chromedriver
        chrome_options.binary_location = f"{WEB_DRIVER_DIR}/chrome-linux64/chrome"
        webdriver_service = Service(
            f"{WEB_DRIVER_DIR}/chromedriver-linux64/chromedriver"
        )

        # Choose Chrome Browser
        browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)
        wait = WebDriverWait(browser, 20)

        # Get page
        browser.get(DIGESTO_URL)

        subject_buttons_total = get_buttoms_by_table_id(
            table_id="tableDigestos", wait=wait
        ).__len__()

        # iterate over subject table
        for subject_number in range(0, subject_buttons_total):
            subject_buttom = get_buttoms_by_table_id(
                table_id="tableDigestos", wait=wait
            )[subject_number]
            logger.info("-" * 20)
            logger.info(f"Materia {subject_number}")
            logger.info("-" * 20)

            if subject_buttom.is_enabled():

                subject_buttom.click()

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

                # iterate over subject pages
                for pag_number in range(0, pag_total):
                    logger.info("*" * 20)
                    logger.info(f"Número de página: {pag_number}")
                    logger.info("*" * 20)
                    law_buttoms_total = get_buttoms_by_table_id(
                        "tableIunps", wait=wait
                    ).__len__()

                    # iterate over elements per page
                    for law_number in range(0, law_buttoms_total):
                        law_buttom = get_buttoms_by_table_id("tableIunps", wait=wait)[
                            law_number
                        ]
                        publication_date = get_publication_dates_by_index(
                            "tableIunps", wait=wait, index=law_number
                        )
                        del browser.requests
                        law_buttom.click()

                        time.sleep(2)

                        browser.switch_to.window(browser.window_handles[-1])

                        law_url = browser.current_url
                        law_id = law_url.split("?idnorm=", 1)[1]
                        has_law_content = False
                        law_content_url = (
                            "http://digesto.asamblea.gob.ni/consultas/util/ws/proxy.php"
                        )
                        for request in browser.requests:
                            if request.url == law_content_url:
                                body = request.body.decode("utf-8").split("&")

                                for data in body:
                                    key, value = data.split("=")
                                    if (
                                        key == "hddQueryType"
                                        and value == "getVersionHtmlAccordion"
                                    ):
                                        has_law_content = True

                        # do not collect data if law has no content
                        if has_law_content:
                            subjects_related = browser.find_element(
                                By.ID, "divMateriasPrin"
                            ).find_elements(By.TAG_NAME, "td")
                            logger.info(f"Número de elemento: {law_number}")
                            logger.info(
                                "Nomar número: {}".format(
                                    browser.find_element(By.ID, "tdNumero").text
                                )
                            )
                            logger.info(
                                "Nomar título: {}".format(
                                    browser.find_element(By.ID, "divTitle").text
                                )
                            )

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
                                # save law
                                if not internation_tool:
                                    law_versions = wait.until(
                                        EC.element_to_be_clickable((By.ID, "slVersion"))
                                    )

                                    law_versions.click()

                                    law_version_select = Select(law_versions)
                                    law_version_select.options[-1].click()

                                    goto_version_buttom = wait.until(
                                        EC.element_to_be_clickable(
                                            (By.ID, "btnGoToVersion")
                                        )
                                    )

                                    goto_version_buttom.click()

                                    law_content = wait.until(
                                        EC.presence_of_element_located(
                                            (By.CSS_SELECTOR, ".document.act")
                                        )
                                    )

                                    filename = law_id + ".html"

                                    with open(
                                        LAWS_DOWNLOAD_DIR + "/" + filename, "w"
                                    ) as law_file:

                                        rendered_html = render_to_string(
                                            "digest_data/law_template.html",
                                            context={
                                                "law_corpus": law_content.get_attribute(
                                                    "outerHTML"
                                                )
                                            },
                                        )

                                        law_file.write(rendered_html)

                                        logger.info("File saved successfully")

                                    new_law = Law(
                                        id=law_id, metadata=metadata, filename=filename
                                    )
                                    new_law.save()

                                    logger.info("Data saved successfully into DB\n")

                            except Exception:
                                logger.error(
                                    "saving law went wrong",
                                    exc_info=True,
                                    stack_info=True,
                                )

                        browser.close()

                        browser.switch_to.window(browser.window_handles[-1])

                    next_buttom = browser.find_elements(
                        By.CSS_SELECTOR, "li.footable-page-arrow a"
                    )[-2]
                    next_buttom.click()
                    time.sleep(2)

                browser.back()
    except Exception as e:
        logger.error("scrapping error", exc_info=True, stack_info=True)


download_current_laws()

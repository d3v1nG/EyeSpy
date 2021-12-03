from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
import time
import csv
import subprocess
import sys

def run_urlcrazy(domain, outdir):
    out_file = open("{0}/Domain-Variations.csv".format(outdir), "w")
    subprocess.call(["urlcrazy", str(domain), "--format=CSV"], stdout=out_file)
    out_file.close()

def check_row_return_domain(row):
    if row[5] != "":
        return [row[0], row[1]]
    else:
        return None

def main(outdir):
    # outdir = "Results"

    file = open("Results/Domain-Variations.csv", 'r')
    csv_reader = csv.reader(file)
    
    # get to actual data row
    header = next(csv_reader)
    blank = next(csv_reader)
    columns = next(csv_reader)

    domain_names = []
    for row in csv_reader:
        domain_name = check_row_return_domain(row)
        if domain_name is not None:
            domain_names.append(domain_name)

    options = Options()
    options.add_argument("--headless")

    browser = webdriver.Firefox(options=options)
    
    results_file = open("{0}/results.html".format(outdir), 'a')
    results_file.writelines(html_header())

    for name in domain_names:
        try:
            results_file.writelines("<div style=\"text-align:center;border:1px solid black;\"><h3>{0}: {1}</h3></br>\n".format(name[0], name[1]))
            browser.get('http://{0}'.format(name[1]))
            browser.save_screenshot("{0}/{1}.png".format(outdir, name[1]))
            results_file.writelines("<img alt=\"unable to screenshot\" src=\"{0}\"></img></div></br>\n".format(str(name[1])+".png"))
        except WebDriverException as wde:
            print("[-] Unable to screenshot {0}".format(name[1]))

    results_file.writelines(html_footer())
    results_file.close()

    browser.close()
    

def html_header():
    temp = """<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>EyeSpy Results</title>
                </head>
                <body>
                <h1>Potential TypoSquatted Domains</h1></br>\n"""
    return temp

def html_footer():
    temp = "</body></html>"
    return temp


def help():
    print("[~] Usage: EyeSpy.py domain outdir")

if __name__ == "__main__":
    try:
        domain = sys.argv[1]
        outdir = sys.argv[2]
        run_urlcrazy(domain, outdir)
        main(outdir)
    except IndexError as ie:
        help()
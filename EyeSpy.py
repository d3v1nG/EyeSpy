from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
import time
import csv
import subprocess
import sys
import os
import hashlib

def run_urlcrazy(domain, outdir):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    
    out_file = open("{0}/Domain-Variations.csv".format(outdir), "w")
    subprocess.call(["urlcrazy", str(domain), "--format=CSV"], stdout=out_file)
    out_file.close()
    print("[~] URLCrazy finished")

def check_row_return_domain(row):
    if row[5] != "":
        return [row[0], row[1], row[4]]
    else:
        return None

def main(outdir):
    file = open("{0}/Domain-Variations.csv".format(outdir), 'r')
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

    
    try:
        for name in domain_names:
            print("[~] Attempting to screenshot: "+ name[1])
            browser.get('http://{0}'.format(name[1]))
            # time.sleep(5)
            current_path = "{0}/{1}.png".format(outdir, name[1])
            browser.save_screenshot(current_path)
            # check for blanks page - md5sum 986acbd0af09d08f821f62a9b6a67299
            is_blank = check_for_blank(current_path)
            if is_blank:
                continue
            else:
                results_file.writelines("<div style=\"text-align:center;border:1px solid black;\"><h3>{0} : {1} : {2}</h3></br>\n".format(name[0], name[1], name[2]))
                results_file.writelines("<img alt=\"unable to screenshot\" src=\"{0}\"></img></div></br>\n".format(str(name[1])+".png"))  
    except WebDriverException as wde:
        print("[-] Unable to screenshot {0}".format(name[1]))

    results_file.writelines(html_footer())
    results_file.close()

    browser.close()
    
def check_for_blank(path):
    blank_hash = "fa4316bd5905c0420c371b375e7df6ff"
    current = hashlib.md5(open(path, "rb").read()).hexdigest()
    print(current)
    if current == blank_hash:
        print("[-] Blank Screenshot, deleting.")
        os.remove(path)
        return True
    else:
        return False

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

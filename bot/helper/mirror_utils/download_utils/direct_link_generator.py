# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """

import json
import time
import re
import urllib.parse
from os import popen
from random import choice

import requests
from bs4 import BeautifulSoup

from bot.helper.ext_utils.exceptions import DirectDownloadLinkException


def direct_link_generator(link: str):
    """ direct links generator """
    if not link:
        raise DirectDownloadLinkException("`No links found!`")
    elif 'zippyshare.com' in link:
        return zippy_share(link), None
    elif 'yadi.sk' in link:
        return yandex_disk(link), None
    elif 'cloud.mail.ru' in link:
        return cm_ru(link), None
    elif 'mediafire.com' in link:
        return mediafire(link), None
    elif 'osdn.net' in link:
        return osdn(link), None
    elif 'github.com' in link:
        return github(link), None
    elif 'megaup.net' in link:
        return megaup(link)
    else:
        raise DirectDownloadLinkException(f'No Direct link function found for {link}')

def megaup(url: str) -> tuple:
    """ Megaup direct link generator"""
    r = requests.get(url)
    data = r.text.split("DeObfuscate_String_and_Create_Form_With_Mhoa_URL(", 2)[2].split(");")[0].split(",")
    data = [a.strip("' ") for a in data]

    idurl = "".join(data[0][i] for i in range(len(data[0]) // 4 - 1, -1, -1))
    for i in range(int(len(data[0]) / 4 * 3 - 1), int(len(data[0]) / 4 * 2) - 1, -1):
        idurl += data[0][i]

    for i in range(int((len(data[1]) - 3) / 2 + 2), 2, -1):
        idurl += data[1][i]

    new_url = f"https://download.megaup.net/?idurl={idurl}&idfilename={data[2]}&idfilesize={data[3]}"
    dl_url = requests.get(new_url).text.split('<a href="')[1].split('"')[0]
    final_request = requests.get(dl_url)
    cookie = final_request.headers['Set-Cookie'].split(" ")[0]
    time.sleep(10)
    return dl_url, cookie


def zippy_share(url: str) -> str:
    """ ZippyShare direct links generator
    Based on https://github.com/LameLemon/ziggy"""
    dl_url = ''
    try:
        link = re.findall(r'\bhttps?://.*zippyshare\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No ZippyShare links found`\n")
    session = requests.Session()
    base_url = re.search('http.+.com', link).group()
    response = session.get(link)
    page_soup = BeautifulSoup(response.content, "lxml")
    scripts = page_soup.find_all("script", {"type": "text/javascript"})
    for script in scripts:
        if "getElementById('dlbutton')" in script.text:
            url_raw = re.search(r'= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);',
                                script.text).group('url')
            math = re.search(r'= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);',
                             script.text).group('math')
            dl_url = url_raw.replace(math, '"' + str(eval(math)) + '"')
            break
    dl_url = base_url + eval(dl_url)
    name = urllib.parse.unquote(dl_url.split('/')[-1])
    return dl_url


def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct links generator
    Based on https://github.com/wldhx/yadisk-direct"""
    try:
        link = re.findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        return "`No Yandex.Disk links found`\n"
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        return requests.get(api.format(link)).json()['href']
    except KeyError:
        raise DirectDownloadLinkException("`Error: File not found / Download limit reached`\n")


def cm_ru(url: str) -> str:
    """ cloud.mail.ru direct links generator
    Using https://github.com/JrMasterModelBuilder/cmrudl.py"""
    reply = ''
    try:
        link = re.findall(r'\bhttps?://.*cloud\.mail\.ru\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No cloud.mail.ru links found`\n")
    command = f'vendor/cmrudl.py/cmrudl -s {link}'
    result = popen(command).read()
    result = result.splitlines()[-1]
    try:
        data = json.loads(result)
    except json.decoder.JSONDecodeError:
        raise DirectDownloadLinkException("`Error: Can't extract the link`\n")
    return data['download']


def mediafire(url: str) -> str:
    """ MediaFire direct links generator """
    try:
        link = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No MediaFire links found`\n")
    page = BeautifulSoup(requests.get(link).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    return info.get('href')


def osdn(url: str) -> str:
    """ OSDN direct links generator """
    try:
        link = re.findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No OSDN links found`\n")
    page = BeautifulSoup(
        requests.get(link, allow_redirects=True).content, 'lxml')
    info = page.find('a', {'class': 'mirror_link'})
    link = urllib.parse.unquote(f'https://osdn.net{info["href"]}')
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re.sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]


def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        re.findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("`No GitHub Releases links found`\n")
    download = requests.get(url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("`Error: Can't extract the link`\n")


def useragent():
    """
    useragent random setter
    """
    useragents = BeautifulSoup(
        requests.get(
            'https://developers.whatismybrowser.com/'
            'useragents/explore/operating_system_name/android/').content,
        'lxml').findAll('td', {'class': 'useragent'})
    user_agent = choice(useragents)
    return user_agent.text

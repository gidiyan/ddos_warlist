import os
from datetime import datetime
from os.path import basename
from zipfile import ZipFile

import requests
from bs4 import BeautifulSoup as bs
from git import Repo, exc

CommitMessage = 'Updating targets ' + datetime.now().strftime("%Y-%h-%m  %H:%M:%S")
HttpData = []
HttpsData = []
OtherData = []
url = "https://ddosukraine.com.ua/#ip_result"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
repo = ''
try:
    repo = Repo('./')
except exc.NoSuchPathError as error:
    print('Not git repository: {}'.format(error))
    exit(1)


def print_repository(remote_repo):
    try:
        print('\nInfo On Repo')
        print('Repo Active Branch Is {}'.format(remote_repo.active_branch))
        for remote in remote_repo.remotes:
            print('Remote Named "{}" With URL "{}"'.format(remote, remote.url))
        print('Last Commit For Repo Is {}  at {}.'.format(str(repo.head.commit.hexsha),
                                                          str(repo.head.commit.committed_datetime)))
    except AttributeError as e:
        print('An Exception Occurred In Getting Repository Info: {}'.format(e))


def git_push():
    try:
        repo.git.add(all=True)
        repo.index.commit(CommitMessage)
        origin = repo.remote(name='origin')
        origin.push()
        print('Successfully Pushed To Git')
    except:
        print('An Exception Cccurred: {}'.format(error))


def get_data():
    response = requests.request('GET', 'http://ddosukraine.com.ua/#ip_result', headers=headers)
    response_data = bs(response.content, "html.parser").find("div", class_="actualTarget").text
    e_data = (response_data.split())
    for item in e_data:
        if ":80" in item:
            HttpData.append(item)
        elif ":443" in item:
            HttpsData.append(item)
        else:
            OtherData.append(item)
    print('Port 80: \n', HttpData)
    print('Port 443: \n', HttpsData)
    print('Other Ports: \n', OtherData)


def create_file(data, file_name):
    output_file = open(file_name, 'w')
    if type(data) is list:
        for item in data:
            output_file.write(item + '\n')
        output_file.close()
    if type(data) is str:
        output_file.write(data)


def join_data():
    str_data = '#targets updated ' + datetime.now().strftime("%m-%h-%Y  %H:%M:%S") + '\n\n'
    str_data += ' '.join(HttpData)
    str_data += ' --http-methods STRESS GET \n'
    str_data = str_data.replace("tcp", "http")
    str_data += ' '.join(HttpsData)
    str_data += ' --http-methods STRESS GET \n'
    str_data = str_data.replace("tcp", "https")
    return str_data


def replace_data(file_in, file_out, paste):
    fin = open(file_in, 'rt')
    fout = open(file_out, 'wt')
    for line in fin:
        fout.write(line.replace('tcp', paste))
    fin.close()
    fout.close()



def FilesInDir(dirName, file_name, filter):
    with ZipFile(file_name, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(dirName):
            for filename in filenames:
                if filter(filename):
                    file_path = os.path.join(folderName, filename)
                    zipObj.write(file_path, basename(file_path))


def create_backup():
    file_name = 'target_before_' + datetime.now().strftime("%m_%h_%Y_%H-%M-%S") + '.zip'
    print('*** Creating A Zip Archive Of Targets Lists Before update ***')
    FilesInDir('./', file_name, lambda name: '.lst' in name)


if __name__ == '__main__':
    get_data()
    print_repository(repo)
    check_push = input('\npush to git?(y/n) ')
    if check_push.lower() == "y":
        create_backup()
        create_file(HttpData, 'l4_tcp_80.lst')  # put desired name and data
        create_file(HttpsData, 'l4_tcp_443.lst')  # put desired name and data
        create_file(OtherData, 'l4_tcp_other.lst')  # put desired name and data
        create_file(join_data(), 'targets.lst')  # put desired name
        replace_data('l4_tcp_80.lst', 'l7_80.lst', 'http')
        replace_data('l4_tcp_443.lst', 'l7_443.lst', 'https')
        git_push()
    else:
        print("You Didn't Type 'y' So Skipping Push")

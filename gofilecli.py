#!/usr/bin/env python3
import requests
import random
import time
import argparse
import os
import logging
import sys
import platform
import subprocess
import sys
import simpleaudio as sa
from tqdm import tqdm
import json
from dotenv import load_dotenv


def reqst(url, method ,headers=None, data=None, files=None, params=None, json=None, logger=None):
    try:
        if method == "get":
            response = requests.get(url, headers=headers, data=data, params=params, json=json)
        elif method == "post":
            response = requests.post(url, headers=headers, data=data, files=files, params=params, json=json)
        elif method == "put":
            response = requests.put(url, headers=headers, data=data, files=files, params=params, json=json)
        elif method == "delete":
            response = requests.delete(url, headers=headers, data=data, files=files, params=params, json=json)
        logger.debug(f"Request to {url} with method {method} returned status code {response.status_code}")
        json_response = response.json()  # If response content is not JSON, this will raise a ValueError
        return json_response
    except requests.exceptions.HTTPError as http_err:
        logger.debug(f"Response: {response.text}")
        logger.error(f"HTTP error occurred: {http_err}")  # Handles HTTP errors (e.g., 404, 500)
        sys.exit()
    except requests.exceptions.ConnectionError as conn_err:
        logger.debug(f"Response: {response.text}")
        logger.error(f"Connection error occurred: {conn_err}")  # Handles network-related errors
        sys.exit()
    except requests.exceptions.Timeout as timeout_err:
        logger.debug(f"Response: {response.text}")
        logger.error(f"Timeout error occurred: {timeout_err}")  # Handles request timeouts
        sys.exit()
    except requests.exceptions.RequestException as req_err:
        logger.debug(f"Response: {response.text}")
        logger.error(f"An error occurred: {req_err}")  # Catches any other requests-related errors
        sys.exit()
    except ValueError as json_err:
        logger.debug(f"Response: {response.text}")
        logger.error(f"JSON decode error: {json_err}")  # Handles issues with JSON decoding
        sys.exit()


def load_file(file_name: str) -> str:
    """
    Get the correct path to a file, regardless of development or compiled mode.
    """
    return os.path.join(os.path.dirname(__file__), file_name)


def play_sound():
    sound_path = load_file("assets/sounds/Blow_edited.wav")
    wave_obj = sa.WaveObject.from_wave_file(sound_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def set_env_var_unix(name, value, shell="bash"):
    home = os.path.expanduser("~")
    rc_file = f".{shell}rc"
    rc_path = os.path.join(home, rc_file)
    with open(rc_path, "a") as f:
        f.write(f'\nexport {name}="{value}"\n')
    os.system(f"source {rc_path}")


def set_env_var(name, value):
    system = platform.system()
    if system == "Windows":
        subprocess.run(["setx", name, value], shell=True)
    elif system in ["Linux", "Darwin"]:
        shell = os.getenv('SHELL', '/bin/bash').split('/')[-1]
        set_env_var_unix(name, value, shell=shell)
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")
    

def format_file_size(file=None, num_bytes=None):
    if num_bytes:
        file_size_bytes = num_bytes
    else:
        file_size_bytes = os.path.getsize(file)
    size_in_kb = file_size_bytes / 1024
    size_in_mb = file_size_bytes / (1024 * 1024)
    size_in_gb = file_size_bytes / (1024 * 1024 * 1024)
    if size_in_gb >= 1:
        return size_in_gb, "GB"
    elif size_in_mb >= 1:
        return size_in_mb, "MB"
    else:
        return size_in_kb, "KB"


def file_size(file=None, num_bytes=None):
    size, unit = format_file_size(file=file, num_bytes=num_bytes)
    return f"{size:.2f} {unit}"
    

def calculate_upload_speed(file, start_time):
    elapsed_time_seconds = time.time() - start_time
    file_size, size_unit = format_file_size(file)

    if size_unit == "GB":
        average_speed = (file_size * 1024) / elapsed_time_seconds  # Convert GB to MB and calculate MB/s
        speed_unit = "MB/s"
    else:
        average_speed = file_size / elapsed_time_seconds  # MB/s
        speed_unit = "MB/s"

    if elapsed_time_seconds >= 60:
        minutes = int(elapsed_time_seconds // 60)
        seconds = int(elapsed_time_seconds % 60)
        elapsed_time = f"{minutes}m {seconds}s"
    else:
        elapsed_time = f"{elapsed_time_seconds:.2f}s"
    
    return f"{average_speed:.2f} {speed_unit}", elapsed_time


def get_file_paths(folderPath):
    filePaths = []
    for root, directories, files in os.walk(folderPath):
        for file in files:
            if ".DS_Store" not in file:
                file_path = os.path.join(root, file)
                filePaths.append(file_path)
    return filePaths


def check_folderPath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def getservers(logger):
    servers = []
    # response = requests.get("https://api.gofile.io/servers").json()
    response = reqst("https://api.gofile.io/servers", logger=logger, method="get")
    if response["status"] == "ok":
        for server in response["data"]["servers"]:
            servers.append(server["name"])
        logger.debug(f"{response}")
        return servers
    else:
        logger.error(f"{response}")
        return None
    

def ping_server(url, logger, num_requests=4, delay=0.1):
    response_times = []
    for _ in range(num_requests):
        try:
            start_time = time.time()
            response = requests.head(url)
            response_time = time.time() - start_time
            if response.status_code == 200:
                response_times.append(response_time)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error: {e}")
        time.sleep(delay)
    if response_times:
        avg_response = sum(response_times) / len(response_times)
        return avg_response
    else:
        return float('inf')
    

def test_servers(servers, logger):
    best_server = None
    best_time = float('inf')
    for server in servers:
        logger.debug(f"Pinging {server}...")
        url = f"https://{server}.gofile.io"
        avg_time = ping_server(url, logger)
        logger.debug(f"Average response time for {server}: {avg_time:.2f} ms")
        if avg_time < best_time:
            best_time = avg_time
            best_server = server
    if best_server:
        logger.debug(f"\nThe best server is {best_server} with an average response time of {best_time:.2f} ms.")
    else:
        logger.error("All pings failed.")
    return best_server


def get_stats(logger):
    headers = {'authorization': f'Bearer {TOKEN}',}
    # data = requests.get(f'https://api.gofile.io/accounts/{ACCOUNT_ID}', headers=headers).json()
    data = reqst(f'https://api.gofile.io/accounts/{ACCOUNT_ID}', headers=headers, logger=logger, method="get")
    if data["status"] == "ok":
        stats = data["data"]["statsCurrent"]
        logger.info("Account stats:")
        logger.info(f"Total files: {stats['fileCount']}")
        logger.info(f"Total folders: {stats['folderCount']}")
        size = file_size(num_bytes=stats['storage'])
        logger.info(f"Total size: {size}")
        traffic = file_size(num_bytes=stats['trafficWebDownloaded'])
        logger.info(f"Total traffic: {traffic}")
    else:
        logger.error(f"{data}")
        return None


def get_rootfolder(logger):
    headers = {'authorization': f'Bearer {TOKEN}',}
    # data = requests.get(f'https://api.gofile.io/accounts/{ACCOUNT_ID}', headers=headers).json()
    data = reqst(f'https://api.gofile.io/accounts/{ACCOUNT_ID}', headers=headers, logger=logger, method="get")
    root_folder = data.get("data", {}).get("rootFolder", {})
    if root_folder:
        return root_folder
    else:
        logger.error(f"{data}")
        return None


def get_code(folderId, logger):
    headers = {'authorization': f'Bearer {TOKEN}',}
    params = (('wt', '4fd6sg89d7s6'),('cache', 'false'),)
    # data = requests.get(f'https://api.gofile.io/contents/{folderId}', headers=headers, params=params).json()
    data = reqst(f'https://api.gofile.io/contents/{folderId}', headers=headers, params=params, logger=logger, method="get")
    code = data.get("data", {}).get("code", {})
    if code:
        return code
    else:
        logger.error(f"{data}")
        return None


def get_children(id, logger):
    headers = {'authorization': f'Bearer {TOKEN}',}
    params = (('wt', '4fd6sg89d7s6'),('cache', 'false'),)
    # data = requests.get(f'https://api.gofile.io/contents/{id}', headers=headers, params=params).json()
    data = reqst(f'https://api.gofile.io/contents/{id}', headers=headers, params=params, logger=logger, method="get")
    children = data.get("data", {}).get("children", {})
    if children:
        return children
    else:
        if data["status"] == "error-rateLimit":
            logger.warning("Rate limit reached, waiting 30 seconds")
            time.sleep(30)
            return get_children(id, logger)
        else:
            logger.error(f"{data}")
            return None


def createfolder(parentFolderId, folderName, logger):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    if folderName:
        data = {"parentFolderId": parentFolderId, "folderName": folderName}
    else:
        data = {"parentFolderId": parentFolderId}
    # response = requests.post("https://api.gofile.io/contents/createFolder", headers=headers, json=data).json()
    response = reqst("https://api.gofile.io/contents/createFolder", headers=headers, json=data, logger=logger, method="post")
    if response["status"] == "ok":
        name = response["data"]["name"]
        code = response["data"]["code"]
        folderId = response["data"]["id"]
        logger.debug(f"""Folder {name} created with code {code} and folderId {folderId}""")
        return folderId
    else:
        logger.error(f"{response}")
        return None


def read_in_chunks(file_object, CHUNK_SIZE):
    while True:
        data = file_object.read(CHUNK_SIZE)
        if not data:
            break
        yield data


def uploadfile(serverName, folderId, filePath, logger):
    # reference : https://api.video/blog/tutorials/upload-a-big-video-file-using-python/
    start_time = time.time()
    # CHUNK_SIZE = 6000000
    # content_size = os.stat(filePath).st_size
    # f = open(filePath, "rb")
    # index = 0
    # offset = 0
    # headers = {"Authorization": f"Bearer {TOKEN}", 'content-type': 'multipart/form-data',}
    # with tqdm(total=content_size, unit='B', unit_scale=True, desc='Uploading', leave=False) as progress_bar:
    #     for chunk in read_in_chunks(f, CHUNK_SIZE):
    #         offset = index + len(chunk)
    #         headers['Content-Range'] = 'bytes %s-%s/%s' % (index, offset - 1, content_size)
    #         index = offset
    #         try:
    #             # file = {"file": chunk, 'folderId': (None, folderId)}
    #             # response = requests.post(f"https://{serverName}.gofile.io/contents/uploadfile", files=file, headers=headers)
    #             # files = {"file": chunk}
    #             # data = {"folderId": folderId}
    #             files = {"file": chunk,}
    #             response = requests.post(f"https://{serverName}.gofile.io/contents/uploadfile",files=files,headers=headers)
    #             logger.debug("r: %s, Content-Range: %s" % (response, headers['Content-Range']))
    #             progress_bar.update(len(chunk))
    #         except Exception as e:
    #             logger.error(f"Error: {e}")
    # logger.debug(f"{response.text}")
    # response = response.json()
    command = [
        "curl",
        "-X", "POST",
        f"https://{serverName}.gofile.io/contents/uploadfile",
        "-H", f"Authorization: Bearer {TOKEN}",
        "-F", f"file=@{filePath}",
        "-F", f"folderId={folderId}",
    ]
    response = subprocess.run(command, capture_output=True, text=True)
    try:
        response_json = json.loads(response.stdout)
    except json.JSONDecodeError:
        logger.error("Failed to parse response as JSON.")
        return None
    speed, elapsed_time = calculate_upload_speed(filePath, start_time)
    response = response_json
    if response["status"] == "ok":
        logger.debug(response)
        name = response["data"]["name"]
        downloadPage = response["data"]["downloadPage"]
        parentFolderId = response["data"]["parentFolder"]
        logger.debug(f"""File {name} uploaded to {downloadPage}""")
        return downloadPage, parentFolderId, speed, elapsed_time
    else:
        logger.error(f"{response}")
        return None


def actionFolder(folderId, attributeValue, logger):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    data = {"attribute": "public", "attributeValue": attributeValue}
    # response = requests.put(f"https://api.gofile.io/contents/{folderId}/update", headers=headers, json=data).json()
    response = reqst(f"https://api.gofile.io/contents/{folderId}/update", headers=headers, json=data, logger=logger, method="put")
    if response["status"] == "ok":
        return True
    else:
        return response


def upload(filePath, folderPath, folderName, parentFolderId, private, logger):
    files = []
    logger.info("Starting upload")
    logger.debug("File: %s", filePath)
    if folderPath:
        files = get_file_paths(folderPath)
        if not files:
            logger.error("No files found in folder")
            sys.exit()
    else:
        if os.path.exists(filePath):
            files = [filePath]
        else:
            logger.error("File not found")
            sys.exit()
    
    # Getting servers
    servers = getservers(logger)
    if servers:
        if len(servers) > 1: # If there are multiple servers, check the size of the files
            if max([os.path.getsize(file) for file in files]) > 100 * 1024 * 1024:  # 100 MB in bytes
                logger.debug("One of the file have a size > 100 MB. Fetching best server...")
                serverName = test_servers(servers, logger)
            else:
                serverName = random.choice(servers)
        else:
            serverName = servers[0]
        logger.debug(f"Selected server: {serverName}")

        if folderName and parentFolderId:
            logger.info(f"Creating folder: {folderName} for: {parentFolderId}")
            folderId = createfolder(parentFolderId, folderName, logger)
            logger.debug(f"FolderId: {folderId}")
            parentFolderId = folderId
        elif folderName:
            logger.info(f"Creating folder: {folderName} for PRIVATE_PARENT_ID: {PRIVATE_PARENT_ID}")
            folderId = createfolder(PRIVATE_PARENT_ID, folderName, logger)
            logger.debug(f"FolderId: {folderId}")
            parentFolderId = folderId
        elif parentFolderId and not folderName:
            parentFolderId = parentFolderId
            logger.debug(f"FolderId: {parentFolderId}")
        else:
            # parentFolderId = PRIVATE_PARENT_ID
            logger.info(f"Creating folder: {folderName} for PRIVATE_PARENT_ID: {PRIVATE_PARENT_ID}")
            folderId = createfolder(PRIVATE_PARENT_ID, None, logger)
            parentFolderId = folderId
            logger.debug(f"FolderId: {parentFolderId}")

        for file in files:
            if parentFolderId:
                logger.info(f"Uploading file: '{file}' ({file_size(file)}) to: '{parentFolderId}' on: '{serverName}'")
            else:
                logger.info(f"Uploading file: '{file}' ({file_size(file)}) on: '{serverName}'")
            downloadPage, parentFolderId, speed, elapsed_time = uploadfile(serverName, parentFolderId, file, logger)
            logger.info(f"File uploaded to: {downloadPage} in {elapsed_time} at {speed}")

        if not private:
            action = actionFolder(parentFolderId, "true", logger)
            if action:
                logger.info("Folder made public")
            else:
                logger.error(f"{action}")
        else:
            action = actionFolder(parentFolderId, "false", logger)
            if action:
                logger.info("Folder made private")
            else:
                logger.error(f"{action}")
        play_sound()
    else:
        time.sleep(10)
        sys.exit()


def downloadFile(downloadUrl, path, logger):
    start_time = time.time()
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(downloadUrl, headers=headers, stream=True)
    # response = reqst(downloadUrl, headers=headers, logger=logger, method="get")
    total_size = int(response.headers.get('content-length', 0))
    
    with open(path, "wb") as f, tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading', leave=False) as progress_bar:
        for chunk in response.iter_content(1024):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
    logger.debug(f"File downloaded: {path}")
    speed, elapsed_time = calculate_upload_speed(path, start_time)
    return speed, elapsed_time


def download(folderId, folderPath, force, logger):
    if 'https' in folderId:
        folderId = folderId.split('/')[-1]
    if len(folderId) == 36:
        folderId = get_code(folderId)
    files = []
    logger.info("Fetching files")
    logger.debug("FolderId: %s", folderId)
    folderIdList = [folderId]
    while folderIdList:
        for folderId in folderIdList:
            children = get_children(folderId, logger)
            folderIdList.remove(folderId)
            for child in children:
                if children[child]['type'] == "file":
                    files.append(children[child])
                else:
                    folderIdList.append(children[child]['id'])
    nbdone = 0
    logger.info(f"Starting download of {len(files)} files")
    for file in files:
        logger.info(f"Downloading file {nbdone}/{len(files)}: {file['name']} ({file_size(num_bytes=file['size'])})")
        downloadUrl = file['link']
        name = file['name']
        if folderPath:
            folderPath = check_folderPath(folderPath)
        else:
            folderPath = check_folderPath(os.path.join(os.getcwd(), folderId))
        path = os.path.join(folderPath, name)
        if os.path.exists(path) and not force:
            logger.warning(f"File {name} already exists skipping (set --force to overwrite)")
        elif os.path.exists(path) and force:
            logger.warning(f"File {name} already exists overwriting")
            speed, elapsed_time = downloadFile(downloadUrl, path, logger)
            logger.info(f"File download to: {path} in {elapsed_time} at {speed}")
        else:
            speed, elapsed_time = downloadFile(downloadUrl, path, logger)
            logger.info(f"File download to: {path} in {elapsed_time} at {speed}")
        nbdone += 1
    play_sound()


def opt():
    parser = argparse.ArgumentParser(description="Upload or download a file to GoFile.")

    exclusive_group = parser.add_mutually_exclusive_group()

    exclusive_group.add_argument("--file", "-i", type=str, help="Path to the file to be uploaded")
    exclusive_group.add_argument("--folder", "-f", type=str, help="Path to the folder to be uploaded")
    parser.add_argument("--name", "-n", type=str, help="Name of the folder on the server")
    parser.add_argument("--parent", "-p", type=str, help="Folder id to upload the file to")
    parser.add_argument("--private","-pr",action="store_true",help="Upload to private folder default=False",)
    parser.add_argument("--log-level",type=str,choices=["DEBUG", "ERROR", "INFO", "OFF", "WARN"],default="INFO",help="Set log level [default: INFO]",)
    parser.add_argument("--token", "-tk", type=str, help="GoFile API token")
    parser.add_argument("--private-parent-id", "-pp", type=str, help="GoFile private parent id")
    
    exclusive_group.add_argument('--stats', "-s",  action='store_true', help='Display account stats.')
    
    exclusive_group.add_argument("--download", "-d", type=str, help="Id or code to the folder to be downloaded")
    parser.add_argument("--output", "-o", type=str, help="¨Path to the folder to be downloaded")
    parser.add_argument("--force", "-fo", action="store_true", help="Overwrite existing files")

    return parser.parse_args()


def init():
    args = opt()
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),format=log_format,datefmt="%H:%M:%S",)
    logger = logging.getLogger(__name__)

    load_dotenv()

    global TOKEN
    global PRIVATE_PARENT_ID
    global ACCOUNT_ID
    TOKEN = os.getenv("GOPLOAD_TOKEN")
    PRIVATE_PARENT_ID = os.getenv("GOPLOAD_PRIVATE_PARENT_ID")
    ACCOUNT_ID = os.getenv("GOPLOAD_ACCOUNT_ID")
    if not TOKEN:
        if args.token:
            TOKEN = args.token
            # set_key(key_to_set='GOPLOAD_TOKEN', value_to_set=args.token)
            set_env_var("GOPLOAD_TOKEN", args.token)
        else:
            logger.error("Error: GOPLOAD_TOKEN not found, add GOPLOAD_TOKEN to your environment variables")
            sys.exit()

    if not PRIVATE_PARENT_ID:
        if args.private_parent_id:
            PRIVATE_PARENT_ID = args.private_parent_id
            # set_key(key_to_set='GOPLOAD_PRIVATE_PARENT_ID', value_to_set=args.private_parent_id)
            set_env_var("GOPLOAD_PRIVATE_PARENT_ID", args.private_parent_id)
        elif TOKEN:
            PRIVATE_PARENT_ID = get_rootfolder(logger)
            # set_key(key_to_set='GOPLOAD_PRIVATE_PARENT_ID', value_to_set=args.private_parent_id)
            set_env_var("GOPLOAD_PRIVATE_PARENT_ID", args.private_parent_id)
        else:
            logger.error("Error: GOPLOAD_PRIVATE_PARENT_ID not found, add GOPLOAD_PRIVATE_PARENT_ID to your environment variables")
            sys.exit()

    # No params:
    if len(sys.argv) == 1:
        logger.error("No arguments specified. Use -h for help")
        sys.exit("")
        
    # Stats section
    if args.stats:
        if len(sys.argv) == 2:
            get_stats(logger)
            sys.exit()
        else:
            logger.error("Use --stats without any other argument")

    # Upload section
    elif args.file:
        if args.folder:
            logger.error("Both file and folder specified")
            sys.exit()
        else:
            upload(args.file, args.folder, args.name, args.parent, args.private, logger)
    elif args.folder:
        if args.file:
            logger.error("Both file and folder specified")
            sys.exit()
        else:
            upload(args.file, args.folder, args.name, args.parent, args.private, logger)

    elif args.name:
        if not args.parent:
            logger.warning("Parent folder id not specified, GOPLOAD_PRIVATE_PARENT_ID will be used")

    # Download section
    elif args.download:
        download(args.download, args.output, args.force, logger)


if __name__ == "__main__":
    try:
        init()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()
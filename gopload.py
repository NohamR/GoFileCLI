import requests
import random
import time
import argparse
import os
from dotenv import load_dotenv
import logging


def format_file_size(file):
    file_size_bytes = os.path.getsize(file)
    size_in_mb = file_size_bytes / (1024 * 1024)
    size_in_gb = file_size_bytes / (1024 * 1024 * 1024)
    if size_in_gb >= 1:
        return size_in_gb, "GB"
    else:
        return size_in_mb, "MB"


def file_size(file):
    size, unit = format_file_size(file)
    return f"{size:.2f} {unit}"
    

def calculate_upload_speed(file, start_time):
    elapsed_time_seconds = time.time() - start_time
    file_size, size_unit = format_file_size(file)
    if size_unit == "GB":
        average_speed = file_size / elapsed_time_seconds  # GB/s
        speed_unit = "GB/s"
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


def getservers(logger):
    servers = []
    response = requests.get("https://api.gofile.io/servers").json()
    if response["status"] == "ok":
        for server in response["data"]["servers"]:
            servers.append(server["name"])
        logger.debug(f"{response}")
        return servers
    else:
        logger.error(f"{response}")
        return None


def createfolder(parentFolderId, folderName, logger):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    if folderName:
        data = {"parentFolderId": parentFolderId, "folderName": folderName}
    else:
        data = {"parentFolderId": parentFolderId}
    response = requests.post("https://api.gofile.io/contents/createFolder", headers=headers, json=data).json()
    if response["status"] == "ok":
        name = response["data"]["name"]
        code = response["data"]["code"]
        folderId = response["data"]["folderId"]
        logger.debug(f"""Folder {name} created with code {code} and folderId {folderId}""")
        return folderId
    else:
        logger.error(f"{response}")
        return None


def uploadfile(serverName, folderId, filePath, logger):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    files = {
        'file': (filePath, open(filePath, 'rb')),
        'folderId': (None, folderId),
    }
    start_time = time.time()
    response = requests.post(f"https://{serverName}.gofile.io/contents/uploadfile", headers=headers, files=files).json()
    speed, elapsed_time = calculate_upload_speed(filePath, start_time)
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


def actionFolder(folderId, attributeValue):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    data = {"attribute": "public", "attributeValue": attributeValue}
    response = requests.put(f"https://api.gofile.io/contents/{folderId}/update", headers=headers, json=data).json()
    if response["status"] == "ok":
        return True
    else:
        return response


def main(filePath, folderPath, folderName, parentFolderId, private, logger):
    files = []
    logger.info("Starting upload")
    logger.debug("File: %s", filePath)
    if folderPath:
        files = get_file_paths(folderPath)
        if not files:
            logger.error("No files found in folder")
            exit(1)
    else:
        if os.path.exists(filePath):
            files = [filePath]
        else:
            logger.error("File not found")
            exit(1)

    servers = getservers(logger)
    if servers:
        serverName = random.choice(servers)
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
            parentFolderId = None
            logger.debug(f"FolderId: {parentFolderId}")

        for file in files:
            if parentFolderId:
                logger.info(f"Uploading file: '{file}' ({file_size(file)}) to: '{parentFolderId}' on: '{serverName}'")
            else:
                logger.info(f"Uploading file: {file} ({file_size(file)}) on: {serverName}")
            downloadPage, parentFolderId, speed, elapsed_time = uploadfile(serverName, parentFolderId, file, logger)
            logger.info(f"File uploaded to: {downloadPage} in {elapsed_time} at {speed}")

        if not private:
            action = actionFolder(parentFolderId, "true")
            if action:
                logger.info("Folder made public")
            else:
                logger.error(f"{action}")
        else:
            action = actionFolder(parentFolderId, "false")
            if action:
                logger.info("Folder made private")
            else:
                logger.error(f"{action}")
    else:
        time.spleed(10)
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to GoFile.")
    parser.add_argument("--file", "-i", type=str, help="Path to the file to be uploaded")
    parser.add_argument("--folder", "-f", type=str, help="Path to the folder to be uploaded")
    parser.add_argument("--name", "-n", type=str, help="Name of the folder on the server")
    parser.add_argument("--parent", "-p", type=str, help="Folder id to upload the file to")
    parser.add_argument("--private","-pr",action="store_true",help="Upload to private folder default=False",)
    parser.add_argument("--log-level",type=str,choices=["DEBUG", "ERROR", "INFO", "OFF", "WARN"],default="INFO",help="Set log level [default: INFO]",)
    args = parser.parse_args()

    log_format = "%(asctime)s %(levelname)s: %(message)s"
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),format=log_format,datefmt="%H:%M:%S",)
    logger = logging.getLogger(__name__)

    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    PRIVATE_PARENT_ID = os.getenv("PRIVATE_PARENT_ID")
    if not TOKEN:
        logger.error("Error: TOKEN not found, create a .env file with TOKEN")
        exit(1)
    if not PRIVATE_PARENT_ID:
        logger.error("Error: PRIVATE_PARENT_ID not found, create a .env file with PRIVATE_PARENT_ID")
        exit(1)

    if args.name and not args.parent:
        logger.warning("Parent folder id not specified, PRIVATE_PARENT_ID will be used")

    if args.file:
        if args.folder:
            logger.error("Both file and folder specified")
            exit(1)
        else:
            main(args.file, args.folder, args.name, args.parent, args.private, logger)
    else:
        if args.folder:
            main(args.file, args.folder, args.name, args.parent, args.private, logger)
        else:
            logger.error("No file or folder specified")
            exit(1)
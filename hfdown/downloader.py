import os, json, sys, time, re, math, random, datetime, argparse, requests
from typing import List, Dict, Tuple, Union, Optional, Any, Callable, Iterable, TypeVar, Generic, Sequence, Mapping, Set, Deque
from bs4 import BeautifulSoup
from pydantic import BaseModel
from threading import Thread
from . import message

class HuggingfaceRepoPage:
    
    page: Optional[str] = None
    files: Optional[List[str]] = None
    subdirs: Optional[List["HuggingfaceRepoPage"]] = None
    fetch_thread: Optional[Thread] = None
    
    def __init__(
            self, 
            repo: str, 
            branch: str,
            location: str, 
            max_tries: int = 3,
    ) -> None:
        self.repo = repo
        self.branch = branch
        self.location = location
        self.max_tries = max_tries
    
    def fetch_page(self) -> str:
        if self.page is not None:
            return self.page
        url = f"https://huggingface.co/{self.repo}/tree/{self.branch}{self.location}"
        for tries in range(self.max_tries):
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    raise RuntimeError("Failed to fetch page {}. Status code: {}".format(url, response.status_code))
                self.page = response.text
                message.info("Fetched page {}".format(url))
                return self.page
            except KeyboardInterrupt:
                message.error("KeyboardInterrupt. Exiting...")
                break
            except:
                message.warn("({}/{}) Failed to fetch page {}. {}".format(
                    tries + 1, self.max_tries, url, "Retrying..." if tries + 1 < self.max_tries else "Failed."  
                ))
                time.sleep(1)
        raise RuntimeError("Failed to fetch page {}".format(url))
    
    def parse_recursively(self) -> None:
        self.parse_page()
        threads = []
        for subdir in self.subdirs:
            thread = Thread(target=subdir.parse_recursively)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
    
    def parse_page(self) -> Tuple[List[str], List["HuggingfaceRepoPage"]]:
        if self.files is not None and self.subdirs is not None:
            return self.files, self.subdirs
        page = self.fetch_page()
        soup = BeautifulSoup(page, 'html.parser')
        item_list = soup.select('div[data-target="ViewerIndexTreeList"] > ul > li')
        
        files = []
        folders = []
            
        file_regex = r"/{}/resolve/{}{}/([^/]*)\?download=true".format(self.repo, self.branch, self.location)
        folder_regex = r"/{}/tree/{}{}/([^/]*)".format(self.repo, self.branch, self.location)
            
        for idx, item in enumerate(item_list):
            all_a = item.select('a')
            all_hrefs = [a['href'] for a in all_a if "href" in a.attrs]
            is_file = False
            name = None
            for href in all_hrefs:
                file_match = re.match(file_regex, href)
                if file_match:
                    is_file = True
                    name = file_match.group(1)
                    break
                folder_match = re.match(folder_regex, href)
                if folder_match:
                    name = folder_match.group(1)
            if name is None:
                continue
            if is_file:
                files.append(name)
            else:
                folders.append(name)
                
        self.files = files
        self.subdirs = [
            HuggingfaceRepoPage(
                self.repo, self.branch, self.location + "/" + subdir,
                max_tries=self.max_tries,
            ) for subdir in folders
        ]
        return files, self.subdirs
    
    def print_file_structure(self, indent: int = 0):
        if self.files is None or self.subdirs is None:
            self.parse_page()
        message.cyan(" " * indent + self.location + "/")
        indent += 4
        for file in self.files:
            print(" " * indent + file)
        for subdir in self.subdirs:
            subdir.print_file_structure(indent)
    
    def download_files(self, target_dir: str, force: bool = False, skip_safetensor: bool = False):
        if self.files is None or self.subdirs is None:
            self.parse_page()
        target_dir = os.path.join(target_dir, self.location.removeprefix("/"))
        for file in self.files:
            if skip_safetensor and file.find("safetensor") != -1:
                message.info(f"Skip file {file}.")
                continue
            url = f"https://huggingface.co/{self.repo}/resolve/{self.branch}{self.location}/{file}?download=true"
            os.makedirs(target_dir, exist_ok=True)
            target_file = os.path.join(target_dir, file)
            # if os.path.exists(target_file) and not force:
            #     message.warn(f"File {target_file} already exists. Skip.")
            #     continue
            message.info(f"Downloading {url} to {target_file} ...")
            os.system(f"wget -c {url} -O {target_file}")
    
    def download_recursively(self, target_dir: str, force: bool = False, skip_safetensor: bool = False):
        if self.files is None or self.subdirs is None:
            self.parse_page()
        threads = []
        thread = Thread(target=self.download_files, args=(target_dir, force, skip_safetensor))
        thread.start()
        threads.append(thread)        
        for subdir in self.subdirs:
            thread = Thread(target=subdir.download_recursively, args=(target_dir, force, skip_safetensor))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()            

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=str, required=True, help="Name of Huggingface repo. e.g. THUDM/chatglm3-6b")
    parser.add_argument("--branch", type=str, default="main", help="Branch to download. Default: main")
    
    dir_group = parser.add_mutually_exclusive_group(required=True)
    dir_group.add_argument("--dir", type=str, help="Directory to save the files.")
    dir_group.add_argument("--base-dir", type=str, help="Base directory to save the files. The files will be saved to <base-dir>/<repo>.")
    
    parser.add_argument("--force", action="store_true", help="Force download even if the file already exists.")
    parser.add_argument("--skip-safetensor", action="store_true", help="Skip safetensor files.")
    
    args = parser.parse_args()
    
    hf_page = HuggingfaceRepoPage(args.repo, args.branch, "")
    hf_page.parse_recursively()
    hf_page.print_file_structure()
    hf_page.download_recursively(args.dir if args.dir is not None else os.path.join(args.base_dir, args.repo), args.force, args.skip_safetensor)

if __name__ == '__main__':
    main()
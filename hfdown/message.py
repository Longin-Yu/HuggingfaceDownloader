import os, json, sys, time, re, math, random, datetime, argparse, requests
from typing import List, Dict, Tuple, Union, Optional, Any, Callable, Iterable, TypeVar, Generic, Sequence, Mapping, Set, Deque

def log(type: str, content: str, color: str = "\033[0m"):
    contents = content.split("\n")
    if len(contents) == 0:
        return
    msg_str = f"[{type}] " + contents[0]
    msg_str += "".join(["\n" + " " * len(f"[{type}] ") + line for line in contents[1:]])
    
    print(color + msg_str + "\033[0m")

def info(content: Any):
    log("info", str(content), color="\033[36m")

def warn(content: Any):
    log("warn", str(content), color="\033[33m")

def error(content: Any):
    log("error", str(content), color="\033[31m")

def cyan(content: Any):
    print("\033[36m" + str(content) + "\033[0m")

def yellow(content: Any):
    print("\033[33m" + str(content) + "\033[0m")

def red(content: Any):
    print("\033[31m" + str(content) + "\033[0m")
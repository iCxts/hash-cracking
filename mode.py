from __future__ import annotations
from config import *

def mode_chooser() -> "terminal" | "api":
    print(r'''
 __    __       ___           _______. __    __                           
|  |  |  |     /   \         /       ||  |  |  |                          
|  |__|  |    /  ^  \       |   (----`|  |__|  |                          
|   __   |   /  /_\  \       \   \    |   __   |                          
|  |  |  |  /  _____  \  .----)   |   |  |  |  |                          
|__|  |__| /__/     \__\ |_______/    |__|  |__|                          
                                                                          
  ______ .______          ___       ______  __  ___  _______ .______      
 /      ||   _  \        /   \     /      ||  |/  / |   ____||   _  \     
|  ,----'|  |_)  |      /  ^  \   |  ,----'|  '  /  |  |__   |  |_)  |    
|  |     |      /      /  /_\  \  |  |     |    <   |   __|  |      /     
|  `----.|  |\  \----./  _____  \ |  `----.|  .  \  |  |____ |  |\  \----.
 \______|| _| `._____/__/     \__\ \______||__|\__\ |_______|| _| `._____|

    ''')
    print(f"[!] Supported Algorithm : {ALLOWED_ALGOS}")
    use_api = str(input('[?] Use Api? (y/n) > ')).lower()
    while use_api == 'n' or use_api == 'y':
        if use_api == 'y':
            return "api"
        elif use_api == 'n':
            return "terminal"

def terminal() -> tuple:
    target: str = str(input("[?] Target > "))
    algorithm: str = str(input("[?] Algorithm > "))
    return (
        target,
        algorithm
    )



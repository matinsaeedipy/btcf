import json
import time
from datetime import datetime, timezone
from decimal import Decimal

import requests
from bip_utils import (
    Bip39MnemonicGenerator, Bip39WordsNum, Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes,
)

# ================== رنگ‌ها (ANSI) ==================
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"


# ================== تنظیمات ==================
BTC_API = "https://blockchain.info/balance"
ETH_RPC = "https://ethereum-rpc.publicnode.com"
TIMEOUT = 15

SLEEP_BETWEEN_TRIES = 2
SAVE_FOUND_FILE = "found_wallets.jsonl"
SAVE_ALL_FILE = "all_attempts.jsonl"
SAVE_ALL = True


# ================== ظاهر گرافیکی ==================
def banner():
    print()
    print(f"{C.CYAN}{C.BOLD}╔{'═' * 60}╗{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║{C.RESET}  {C.YELLOW}{C.BOLD}₿  BTC / ETH  WALLET  SCANNER{C.RESET}"
          f"{' ' * 27}{C.CYAN}{C.BOLD}║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║{C.RESET}  {C.GRAY}HD wallet brute-force (educational){C.RESET}"
          f"{' ' * 23}{C.CYAN}{C.BOLD}║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}╚{'═' * 60}╝{C.RESET}")
    print()


def print_record(attempt: int, rec: dict):
    print()
    print(f"{C.BLUE}{C.BOLD}┌─[ attempt #{attempt} ]{'─' * 44}{C.RESET}")
    print(f"{C.BLUE}│{C.RESET}")

    print(f"{C.BLUE}│{C.RESET}  {C.MAGENTA}{C.BOLD}🔑 Seed (12 words){C.RESET}")
    print(f"{C.BLUE}│{C.RESET}     {C.WHITE}{rec['mnemonic']}{C.RESET}")
    print(f"{C.BLUE}│{C.RESET}")

    print(f"{C.BLUE}│{C.RESET}  {C.YELLOW}{C.BOLD}₿  BTC  (m/44'/0'/0'/0/0){C.RESET}")
    print(f"{C.BLUE}│{C.RESET}     {C.GRAY}addr :{C.RESET} {C.WHITE}{rec['btc_address']}{C.RESET}")
    b = rec["btc_balance"]
    cb = C.GREEN if b and Decimal(b) > 0 else C.GRAY
    print(f"{C.BLUE}│{C.RESET}     {C.GRAY}bal  :{C.RESET} {cb}{b} BTC{C.RESET}")
    print(f"{C.BLUE}│{C.RESET}")

    print(f"{C.BLUE}│{C.RESET}  {C.CYAN}{C.BOLD}Ξ  ETH  (m/44'/60'/0'/0/0){C.RESET}")
    print(f"{C.BLUE}│{C.RESET}     {C.GRAY}addr :{C.RESET} {C.WHITE}{rec['eth_address']}{C.RESET}")
    e = rec["eth_balance"]
    ce = C.GREEN if e and Decimal(e) > 0 else C.GRAY
    print(f"{C.BLUE}│{C.RESET}     {C.GRAY}bal  :{C.RESET} {ce}{e} ETH{C.RESET}")
    print(f"{C.BLUE}└{'─' * 60}{C.RESET}")


def print_summary(attempt: int, elapsed: float, found: bool):
    print()
    print(f"{C.CYAN}{'═' * 62}{C.RESET}")
    if found:
        print(f"{C.GREEN}{C.BOLD}  ✔ wallet with funds found at attempt #{attempt}{C.RESET}")
    else:
        print(f"{C.YELLOW}{C.BOLD}  ■ finished — no funded wallet found{C.RESET}")
    print(f"{C.GRAY}  attempts : {attempt}{C.RESET}")
    print(f"{C.GRAY}  time     : {elapsed:.1f} s{C.RESET}")
    if SAVE_ALL:
        print(f"{C.GRAY}  log file : {SAVE_ALL_FILE}{C.RESET}")
    print(f"{C.CYAN}{'═' * 62}{C.RESET}")
    print()


# ================== توابع ==================
def derive_address(seed: bytes, coin: Bip44Coins) -> str:
    ctx = (
        Bip44.FromSeed(seed, coin)
        .Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )
    return ctx.PublicKey().ToAddress()


def btc_balance(address: str) -> Decimal:
    r = requests.get(BTC_API, params={"active": address}, timeout=TIMEOUT)
    r.raise_for_status()
    satoshi = r.json()[address]["final_balance"]
    return Decimal(satoshi) / Decimal(10**8)


def eth_balance(address: str) -> Decimal:
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }
    r = requests.post(ETH_RPC, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return Decimal(int(data["result"], 16)) / Decimal(10**18)


def save_jsonl(path: str, record: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def try_once() -> dict:
    """یک ولت جدید می‌سازد و موجودی‌ها را برمی‌گرداند."""
    mnemonic_obj = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
    mnemonic_str = str(mnemonic_obj)                     # ← رفع TypeError
    seed = Bip39SeedGenerator(mnemonic_obj).Generate()

    btc_addr = derive_address(seed, Bip44Coins.BITCOIN)
    eth_addr = derive_address(seed, Bip44Coins.ETHEREUM)

    try:
        btc_bal = btc_balance(btc_addr)
    except Exception as e:
        btc_bal = None
        print(f"  {C.RED}[BTC] error: {e}{C.RESET}")

    try:
        eth_bal = eth_balance(eth_addr)
    except Exception as e:
        eth_bal = None
        print(f"  {C.RED}[ETH] error: {e}{C.RESET}")

    return {
        "time": datetime.now(timezone.utc).isoformat(),   # ← رفع DeprecationWarning
        "mnemonic": mnemonic_str,
        "btc_address": btc_addr,
        "btc_balance": str(btc_bal) if btc_bal is not None else None,
        "eth_address": eth_addr,
        "eth_balance": str(eth_bal) if eth_bal is not None else None,
    }


def has_funds(record: dict) -> bool:
    btc = Decimal(record["btc_balance"]) if record["btc_balance"] else Decimal(0)
    eth = Decimal(record["eth_balance"]) if record["eth_balance"] else Decimal(0)
    return btc > 0 or eth > 0


# ================== حلقه اصلی ==================
def main():
    banner()

    try:
        a = int(input(f"{C.YELLOW}{C.BOLD}tedad talash (0=binahayat): {C.RESET}").strip())
    except ValueError:
        a = 0
    MAX_TRIES = a

    attempt = 0
    found = False
    start = time.time()

    while True:
        attempt += 1
        try:
            rec = try_once()
        except Exception as e:
            print(f"{C.RED}general error: {e}{C.RESET}")
            time.sleep(SLEEP_BETWEEN_TRIES)
            continue

        print_record(attempt, rec)

        if SAVE_ALL:
            save_jsonl(SAVE_ALL_FILE, rec)

        if has_funds(rec):
            found = True
            print()
            print(f"{C.GREEN}{C.BOLD}╔{'═' * 60}╗{C.RESET}")
            print(f"{C.GREEN}{C.BOLD}║  ✅  WALLET WITH FUNDS FOUND!{' ' * 30}║{C.RESET}")
            print(f"{C.GREEN}{C.BOLD}╚{'═' * 60}╝{C.RESET}")
            print(json.dumps(rec, indent=2, ensure_ascii=False))
            save_jsonl(SAVE_FOUND_FILE, rec)
            break

        if MAX_TRIES and attempt >= MAX_TRIES:
            break

        time.sleep(SLEEP_BETWEEN_TRIES)

    print_summary(attempt, time.time() - start, found)


if __name__ == "__main__":
    main()
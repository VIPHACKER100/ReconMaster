# Hardcoded Paths Found - Summary

## Files with Issues

### 1. **reconmaster.py** ⚠️ **HAS MERGE CONFLICTS**
**Status:** Contains Git merge conflict markers (lines 997-1298)  
**Action Required:** Manual conflict resolution needed before fixing paths

**Hardcoded Path Found:**
- Line 1059: `/path/to/LinkFinder/linkfinder.py` (in commented code within conflict)

### 2. **reconmasterv2.py** 
**Hardcoded Paths Found:** 4 locations
- Line 57: `/path/to/n0kovo_subdomains/n0kovo_subdomains.txt` (default wordlist)
- Line 464: `/path/to/LinkFinder/linkfinder.py` (LinkFinder tool)
- Line 514: `/path/to/n0kovo_subdomains/fuzz/directory-list.txt` (directory wordlist)
- Line 924: `/path/to/n0kovo_subdomains/n0kovo_subdomains.txt` (duplicate default wordlist)
- Line 1331: `/path/to/LinkFinder/linkfinder.py` (duplicate LinkFinder)
- Line 1381: `/path/to/n0kovo_subdomains/fuzz/directory-list.txt` (duplicate directory wordlist)

### 3. **reconmasterv3.py**
**Hardcoded Paths Found:** 6 locations
- Line 54: `/path/to/n0kovo_subdomains/n0kovo_subdomains.txt` (default wordlist)
- Line 450: `/path/to/LinkFinder/linkfinder.py` (LinkFinder tool)
- Line 520: `/path/to/n0kovo_subdomains/fuzz/directory-list.txt` (directory wordlist)
- Line 1042: `/path/to/n0kovo_subdomains/n0kovo_subdomains.txt` (duplicate default wordlist)
- Line 1438: `/path/to/LinkFinder/linkfinder.py` (duplicate LinkFinder)
- Line 1508: `/path/to/n0kovo_subdomains/fuzz/directory-list.txt` (duplicate directory wordlist)

### 4. **recon_black.py**
**Hardcoded Paths Found:** 6 locations
- Line 52: `/path/to/n0kovo_subdomains/n0kovo_subdomains.txt` (default wordlist)
- Line 443: `/path/to/LinkFinder/linkfinder.py` (LinkFinder tool)
- Line 513: `/path/to/n0kovo_subdomains/fuzz/directory-list.txt` (directory wordlist)
- Line 975: `/path/to/n0kovo_subdomains/n0kovo_subdomains.txt` (duplicate default wordlist)
- Line 1366: `/path/to/LinkFinder/linkfinder.py` (duplicate LinkFinder)
- Line 1436: `/path/to/n0kovo_subdomains/fuzz/directory-list.txt` (duplicate directory wordlist)

### 5. **proreconmaster.py** ⚠️ **PARTIALLY FIXED**
**Remaining Hardcoded Paths:** 3 locations (old code not yet removed)
- Line 510: `/path/to/LinkFinder/linkfinder.py` (old code, needs removal)
- Line 580: `/path/to/n0kovo_subdomains/fuzz/directory-list.txt` (old code, needs removal)
- Line 1130: `/path/to/n0kovo_subdomains/n0kovo_subdomains.txt` (old code, needs removal)

**Note:** The main code has been fixed (lines 50-56, 1578-1609, 1674-1676), but old/duplicate code remains.

---

## Recommended Action Plan

1. **Resolve merge conflicts in `reconmaster.py` first** - Manual intervention required
2. **Fix `proreconmaster.py`** - Remove remaining old code
3. **Fix `reconmasterv2.py`** - Apply same fixes as proreconmaster.py
4. **Fix `reconmasterv3.py`** - Apply same fixes as proreconmaster.py
5. **Fix `recon_black.py`** - Apply same fixes as proreconmaster.py

---

## Standard Fix Pattern

For each file, apply these changes:

### Default Wordlist (in `__init__` method):
```python
# Before:
self.wordlist = wordlist if wordlist else "/path/to/n0kovo_subdomains/n0kovo_subdomains.txt"

# After:
if wordlist:
    self.wordlist = wordlist
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    self.wordlist = os.path.join(script_dir, "wordlists", "subdomains_new.txt")
```

### LinkFinder Dependency (in `crawl_endpoints` or similar):
```python
# Remove external LinkFinder calls
# Replace with regex-based endpoint extraction using aiohttp
```

### Directory Wordlist (in `directory_bruteforce` or similar):
```python
# Before:
wordlist = "/path/to/n0kovo_subdomains/fuzz/directory-list.txt"

# After:
script_dir = os.path.dirname(os.path.abspath(__file__))
wordlist = os.path.join(script_dir, "wordlists", "directory-list_new.txt")
```

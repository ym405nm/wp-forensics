# WP-FORENSICS : A Forensics Tool for WordPress

This tool is used when a WordPress website is hacked.   
It helps you to detect if your websites is hacked,
and which file is compromised or created.

Features:

* Detect compromised files with Diff from the WordPress official repository.
* Detect malicious file in upload directories.

## How To Use

Set your WordPress directory at the argv[1].

```
$ ./wp_forensics.py {Directory of WordPress}
```

### Output Sample

```
WordPress is found : ver -> 4.9.8
Download WordPress...
Success
Extract WordPress...

Added File(s)...
hacked.txt

Modifed File(s)...
wp-includes/functions.php

Unknown File(s)...
2018/12/b.png

```

This means the tool found a interesting file "hacked.txt",
changed file "functions.php", and unexpected binary "b.png".
(The b.png isn't seem a image file despite the extension.)

## Credit

@ym405nm

Special Thanks : @junk_coken 

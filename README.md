# manpdf.sh

Instead of displaying man pages in a terminal, pipe them to this script to
convert them to PDF and open them in Okular.

## Installation

```bash
XDG_LOCAL_BIN="${XDG_DATA_HOME%%share}bin"
cp manpdf.sh "$XDG_LOCAL_BIN"
cp rwlt.py "$XDG_LOCAL_BIN"
```

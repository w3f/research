#!/usr/bin/env bash
# Autogenerate dummy missing index pages

for dir in $(find docs -mindepth 1 -type d); do
  case $dir in
    */_static|*/_static/*|*/_templates|*/_templates/*|*/images|*/images/*|docs/papers|docs/papers/*) continue;;
    *)
      if [ -f "$dir/main.tex" ]; then
        continue
      elif [ ! -f "$dir.rst" ]; then
        name="$(basename "$dir")"
        read -p "create empty index \"$name\" for $dir [y/n]? " x
        if [ "$x" = "y" -o "$x" = "Y" ]; then
          if [ -f "$dir/index.md" ]; then
            nameindex="$(printf "%s/index\n   " "$name")"
            namerefresh='.. raw:: html

   <meta http-equiv="refresh" content="0; url=./'"${name}"'/index.html">

'
          else
            namerefresh=""
            nameindex=""
          fi
          titlebar="$(echo "$name" | sed s/./=/g)"
          cat > "$dir.rst" <<-eof
$titlebar
$name
$titlebar

${namerefresh}.. toctree::
   :glob:

   ${nameindex}$name/*
eof
        fi
      fi
      ;;
  esac
done

#!/bin/bash
# Autogenerate dummy missing index pages

for dir in $(find docs -mindepth 1 -type d); do
  case $dir in
    */_templates|*/images|*/images/*|*/pdf|*/pdf/*|*/stylesheets) continue;;
    *)
      if [ -f "$dir/main.tex" ]; then
        continue
      elif [ ! -f "$dir.rst" ]; then
        name="$(basename "$dir")"
        read -p "create empty index \"$name\" for $dir [y/n]? " x
        if [ "$x" = "y" -o "$x" = "Y" ]; then
          if [ -f "$dir/index.md" ]; then
            nameindex="$(printf "%s/index\n   " "$name")"
          else
            nameindex=""
          fi
          titlebar="$(echo "$name" | sed s/./=/g)"
          cat > "$dir.rst" <<-eof
$titlebar
$name
$titlebar

.. toctree::
   :glob:

   ${nameindex}$name/*
eof
        fi
      fi
      ;;
  esac
done

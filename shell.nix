{ pkgs ? import <nixpkgs> {} }:
let
  my-python = pkgs.python3;
  pymdown-extensions = pkgs.callPackage ./pymdown-extensions.nix {
    inherit(pkgs.python3Packages) buildPythonPackage markdown pygments
    pytestCheckHook pyyaml isPy3k;
  };
  python-with-my-packages = my-python.withPackages (p: with p; [
    sphinx
    sphinx-material
    (sphinx-markdown-parser.overrideAttrs(oldAttrs: {
      meta.priority = 10;
    }
      ))
    pymdown-extensions
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python-with-my-packages
  ];
  shellHook = ''
    PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
    # maybe set more env-vars
  '';
}

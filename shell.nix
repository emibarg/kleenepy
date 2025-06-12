{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.tkinter
    pkgs.python3Packages.graphviz
    pkgs.python3Packages.pillow
    pkgs.python3Packages.setuptools  # Needed for some Python tools
  ];

  shellHook = ''
    echo "Python environment ready. Run your script with: python kleene_gui.py"
  '';
}

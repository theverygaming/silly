with import (fetchTarball https://github.com/NixOS/nixpkgs/archive/5ad6a14c6bf098e98800b091668718c336effc95.tar.gz) { };
let
  sillyORMPackage = pkgs.python312Packages.buildPythonPackage rec {
    pname = "sillyorm";
    version = "0.4.0";
    pyproject = true;

    build-system = [
      python312Packages.setuptools
    ];

    src = fetchPypi {
      inherit pname version;
      hash = "sha256-Ap8gfExQnvucR5I0ydin9f3wTecoLHvvzxtAxkETHMc=";
    };
  };
in
stdenv.mkDerivation {
  name = "silly";
  buildInputs = [
    python312

    sillyORMPackage

    # lint, fmt, type, docs
    python312Packages.pylint
    python312Packages.mypy
    python312Packages.black
    sphinx
    gnumake

    # test
    python312Packages.coverage
    python312Packages.pytest

    # build
    python312Packages.build

    # deps
    python312Packages.flask

    # postgres
    python312Packages.psycopg2
    python312Packages.types-psycopg2
    postgresql_16

    # xml & web experiments
    python312Packages.lxml

    # for convenience
    sqlitebrowser
  ];
}

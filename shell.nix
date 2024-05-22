with import (fetchTarball https://github.com/NixOS/nixpkgs/archive/66adc1e47f8784803f2deb6cacd5e07264ec2d5c.tar.gz) { };
let
  sillyORMPackage = pkgs.python311Packages.buildPythonPackage rec {
    pname = "sillyorm";
    version = "0.1.0";
    pyproject = true;

    nativeBuildInputs = [
      python311Packages.setuptools
    ];

    src = fetchPypi {
      inherit pname version;
      hash = "sha256-Q/opMMklfM/PDJKZ2To1ohekU9YRau1JzaCVaZSKK0o=";
    };
  };
in
stdenv.mkDerivation {
  name = "silly";
  buildInputs = [
    python311

    sillyORMPackage

    # lint, fmt, type, docs
    python311Packages.pylint
    python311Packages.mypy
    python311Packages.black
    sphinx
    gnumake

    # test
    python311Packages.coverage
    python311Packages.pytest

    # build
    python311Packages.build

    # deps
    python311Packages.flask

    # postgres
    python311Packages.psycopg2
    python311Packages.types-psycopg2
    postgresql_16

    # xml & web experiments
    python311Packages.lxml

    # for convenience
    sqlitebrowser
  ];
}

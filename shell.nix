with import (fetchTarball https://github.com/NixOS/nixpkgs/archive/107d5ef05c0b1119749e381451389eded30fb0d5.tar.gz) { };
let
  sillyORMPackage = pkgs.python312Packages.buildPythonPackage rec {
    pname = "sillyorm";
    version = "0.9.0";
    pyproject = true;

    build-system = [
      python312Packages.setuptools
    ];

    propagatedBuildInputs = [
      python312Packages.alembic
      python312Packages.sqlalchemy
    ];

    # FIXME: release new sillyORM soon:tm:
    /*
    src = fetchPypi {
      inherit pname version;
      hash = "sha256-NRX+4IT+Wif3X5qlnShN+FT/kN4+gq7earT44mgxCVI=";
    };
    */
    src = fetchgit {
      url = "https://github.com/theverygaming/sillyORM.git";
      rev = "77a8c31fc44de527ba6934f0e90e13c066adb80f";
      hash = "sha256-26RkyS5YFYwX4XdkB8oTVyTzqKCQxrvLZUaHOc7TxYs=";
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

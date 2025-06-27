with import (fetchTarball https://github.com/NixOS/nixpkgs/archive/61c0f513911459945e2cb8bf333dc849f1b976ff.tar.gz) { };
let
  sillyORMPackage = pkgs.python313Packages.buildPythonPackage rec {
    pname = "sillyorm";
    version = "0.9.0";
    pyproject = true;

    build-system = [
      python313Packages.setuptools
    ];

    propagatedBuildInputs = [
      python313Packages.alembic
      python313Packages.sqlalchemy
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
      rev = "ae738f493a95b6b6ab4f7b920cfa9e43003aa81b";
      hash = "sha256-snKL/GFJIDLrY5QbW19Crbx9ytSZgctTUk9BMzP1ga4=";
    };
  };
in
stdenv.mkDerivation {
  name = "silly";
  buildInputs = [
    python313

    sillyORMPackage

    # lint, fmt, type, docs
    python313Packages.pylint
    python313Packages.mypy
    python313Packages.black
    sphinx
    gnumake

    # test
    python313Packages.coverage
    python313Packages.pytest

    # build
    python313Packages.build

    # deps
    python313Packages.flask
    python313Packages.hypercorn

    # postgres
    python313Packages.psycopg2
    python313Packages.types-psycopg2
    postgresql_16

    # xml & web experiments
    python313Packages.lxml

    # for convenience
    sqlitebrowser
  ];
}

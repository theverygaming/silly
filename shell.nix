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
      rev = "3a96f7a7a943e6aa54cfaa5f509cca292b025c7b";
      hash = "sha256-XdGWi4JU86gRaaMQkI3tJxD7TIkk+N+jXHREaCJ5KwU=";
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

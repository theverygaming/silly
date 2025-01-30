with import (fetchTarball https://github.com/NixOS/nixpkgs/archive/107d5ef05c0b1119749e381451389eded30fb0d5.tar.gz) { };
let
  sillyORMPackage = pkgs.python312Packages.buildPythonPackage rec {
    pname = "sillyorm";
    version = "0.8.1";
    pyproject = true;

    build-system = [
      python312Packages.setuptools
    ];

    # FIXME: release new sillyorm soon:tm:
    /*
    src = fetchPypi {
      inherit pname version;
      hash = "sha256-J/k/P178iNjoGApD0kj08uymqlftFXsqGfUoUIHhcIc=";
    };
    */
    src = fetchgit {
      url = "https://github.com/theverygaming/sillyORM.git";
      rev = "06b63004479fc6411db2a9c7002cc2ba0293968e";
      hash = "sha256-T40FncjSgEt6d8252zZVrGWW7BG4LNefUy1ZA1ZIokc=";
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
